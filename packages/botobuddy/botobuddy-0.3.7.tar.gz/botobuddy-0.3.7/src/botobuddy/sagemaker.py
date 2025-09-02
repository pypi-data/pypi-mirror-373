import json
from pathlib import Path
from collections import Counter

import click
import rich
from rich.table import Table
from rich.progress import track
from rich.spinner import Spinner
from rich.live import Live

from botobuddy.logger import logger
from botobuddy.common import get_sagemaker_client, get_cognito_client, get_s3_client
from botobuddy.s3 import fast_download_s3_files, S3Uri


def import_commands(parent):
    parent.add_command(sagemaker_group)


@click.group(name='sagemaker')
def sagemaker_group():
    pass


@sagemaker_group.command(
    name='human-effort',
    help='Analyse human effort for the labelling job'
)
@click.pass_obj
@click.option('--output-json', is_flag=True, help='Output the report as JSON')
@click.option(
    '--data-dir', type=click.Path(exists=True), default='temp',
    help='Path to the dataset directory'
)
@click.argument('job_name', type=str)
def analyse_human_effort_command(obj, job_name, output_json, data_dir):
    data_dir = Path(data_dir)
    report_data = analyse_human_effort(job_name, data_dir, session_config=obj)

    if output_json:
        click.echo(json.dumps(report_data, indent=4))
    else:
        table = Table(title=f'Human Effort Report ({job_name})')
        table.add_column('Worker Email', justify='left', style='cyan', no_wrap=True)
        table.add_column('Annotations', justify='right', style='magenta')
        table.add_column('Time Spent', justify='right', style='green')

        for worker_email, data in report_data.items():
            time_spent_hours = int(data['time_spent_seconds'] // 3600)
            time_spent_minutes = int((data['time_spent_seconds'] % 3600) // 60)

            table.add_row(
                worker_email,
                str(data['label_count']),
                f'{time_spent_hours}h {time_spent_minutes}m'
            )

        rich.print(table)


def analyse_human_effort(job_name: str, data_dir: Path, session_config: dict = {}):
    '''Analyse human effort for the labelling job.

    Args:
        job_name: Name of the labelling job
        data_dir: Path to the dataset directory
        session_config: Configuration for the AWS session (profile, region, etc.)

    Returns:
        dict: A dictionary with the worker data:

        {
            'worker_email': {
                'label_count': int,
                'time_spent_seconds': int
            }
        }
    '''

    s3 = get_s3_client(session_config)
    sagemaker = get_sagemaker_client(session_config)

    try:
        response = sagemaker.describe_labeling_job(LabelingJobName=job_name)

        if response['LabelingJobStatus'] != 'Completed':
            raise UserWarning(f'Labelling job {job_name} is not completed')

        manifest_uri = S3Uri(response['LabelingJobOutput']['OutputDatasetS3Uri'])
        path_list = manifest_uri.path.split('/')
        manifests_index = path_list.index('manifests')
        labelling_results_prefix = '/'.join(path_list[:manifests_index]).lstrip('/')
        logger.info(f'Labelling results prefix: {labelling_results_prefix}')

        target_dir = data_dir / 'metadata' / job_name / 'human-effort'
        target_dir.mkdir(parents=True, exist_ok=True)
        targets = []

        paginator = s3.get_paginator('list_objects_v2')

        with Live(Spinner('aesthetic', text='Collecting content...'), transient=True):
            for page in paginator.paginate(
                Bucket=manifest_uri.bucket, Prefix=labelling_results_prefix
            ):
                for item in page.get('Contents', []):
                    key = item['Key']  # type: ignore

                    if 'worker-response' in key:
                        s3_relative_path = Path(key).relative_to(labelling_results_prefix)

                        # Replace colons with underscores to avoid issues with Windows paths
                        target_file_path = Path(
                            str(target_dir / s3_relative_path).replace(':', '_')
                        )

                        targets.append((manifest_uri.bucket, key, target_file_path))

            fast_download_s3_files(
                targets=targets,
                skip_existing=True,
                session_config=session_config
            )

        annotations = Counter()
        time_spent = Counter()
        cognito_user_ids = dict()

        for target in track(targets, description='Analyzing...', transient=True):
            target_data = json.loads(target[2].read_text())

            for answer in target_data['answers']:
                worker_id = answer['workerId']
                annotations[worker_id] += 1
                time_spent[worker_id] += answer['timeSpentInSeconds']
                cognito_user_ids[worker_id] = answer['workerMetadata']['identityData']['sub']

        workforce = sagemaker.describe_workforce(WorkforceName='default')
        user_pool_id = workforce['Workforce']['CognitoConfig']['UserPool']  # type: ignore
        logger.info(f'Using Cognito user pool ID: {user_pool_id}')
        sub_to_email_mapping = get_sub_to_email_mapping(user_pool_id, session_config)

        def worker_id_to_email(worker_id):
            if worker_id not in cognito_user_ids:
                logger.warning(f'No email found for worker ID: {worker_id}')
                return worker_id

            cognito_user_id = cognito_user_ids[worker_id]

            if cognito_user_id not in sub_to_email_mapping:
                logger.warning(f'No email found for worker ID: {worker_id}')
                return cognito_user_id

            return sub_to_email_mapping[cognito_user_id]

        report_data = {
            worker_id_to_email(worker_id): {
                'label_count': label_count,
                'time_spent_seconds': time_spent[worker_id]
            }
            for worker_id, label_count in annotations.items()
        }

        return report_data

    except Exception as e:
        raise UserWarning(f'Failed to analyse human effort for job {job_name}: {e}') from e


def get_sub_to_email_mapping(user_pool_id: str, session_config: dict = {}):
    '''Generates a mapping from 'sub' (UUID) to email address for all users
    in a given AWS Cognito User Pool.

    This function iterates through all users in the user pool.
    It is suitable for small to medium-sized user pools.
    For very large user pools, consider maintaining an external mapping.

    Args:
        user_pool_id (str): The ID of your Cognito User Pool.
        session_config: Configuration for the AWS session (profile, region, etc.)

    Returns:
        dict: A dictionary where keys are 'sub' (UUIDs) and values are email addresses.
              Returns an empty dictionary if no users are found or on error.
    '''

    client = get_cognito_client(session_config)
    sub_email_map = {}
    pagination_token = None

    try:
        while True:
            if pagination_token:
                response = client.list_users(
                    UserPoolId=user_pool_id,
                    PaginationToken=pagination_token
                )
            else:
                response = client.list_users(
                    UserPoolId=user_pool_id
                )

            users = response.get('Users', [])

            for user_entry in users:
                username = user_entry.get('Username')
                sub = None

                # Find the 'sub' attribute in the UserAttributes list
                for attr in user_entry.get('Attributes', []):
                    if attr['Name'] == 'sub':
                        sub = attr['Value']  # type: ignore
                        break  # Found the sub, no need to check other attributes for this user

                if sub and username:
                    sub_email_map[sub] = username
                elif sub:
                    print(f"Warning: User with sub '{sub}' found but no Username (email) to map.")

            pagination_token = response.get('PaginationToken')
            if not pagination_token:
                break  # No more pages

        return sub_email_map

    except Exception as e:
        raise UserWarning(f"Error: User Pool with ID '{user_pool_id}' not found.") from e
