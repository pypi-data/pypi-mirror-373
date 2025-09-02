import tempfile
from typing import Callable
import uuid
from urllib.parse import urlparse
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import click
from benedict import benedict
from boto3.s3.transfer import TransferConfig
from types_boto3_s3 import S3Client

from botobuddy.common import get_s3_client
from botobuddy.logger import logger


class S3Uri:
    def __init__(self, s3_uri: str):
        self.s3_uri = s3_uri
        self.parsed_uri = urlparse(s3_uri)
        self.bucket = self.parsed_uri.netloc
        self.path = self.parsed_uri.path.lstrip('/')
        self.path_list = self.path.split('/')
        self.filename = self.path_list[-1] if self.path_list else None
        self.key = self.path

    def parent(self):
        if not self.path_list:
            return None

        parent_path = '/'.join(self.path_list[:-1])
        return S3Uri(f's3://{self.bucket}/{parent_path}')

    def __str__(self):
        return self.s3_uri

    def __div__(self, other):
        if isinstance(other, str):
            return S3Uri(self.s3_uri.rstrip('/') + '/' + other)
        else:
            raise ValueError(f'Invalid type: {type(other)}')


def import_commands(parent):
    parent.add_command(s3_group)


@click.group(name='s3')
def s3_group():
    pass


@s3_group.command(name='delete-bucket')
@click.argument('bucket_name')
@click.pass_obj
def delete_bucket_cmd(obj, bucket_name):
    '''Clean and delete an S3 bucket completely'''
    try:
        client = get_s3_client(obj)
        delete_bucket_contents(client, bucket_name)
        delete_bucket(client, bucket_name)

    except Exception as e:
        raise UserWarning(f'Error deleting bucket {bucket_name} {e}') from e


@s3_group.command(name='ls')
@click.argument('s3_path')
@click.pass_obj
def ls_cmd(obj, s3_path):
    client = get_s3_client(obj)

    def print_object(item):
        logger.info(item['Key'])  # type: ignore

    list_all_objects(s3_path, print_object, s3_client=client)


@s3_group.command(name='view-dict')
@click.pass_obj
@click.option(
    '--in-format', type=click.Choice(['auto', 'json', 'yaml', 'toml']), default='auto'
)
@click.option(
    '--out-format',
    type=click.Choice(['original', 'json', 'yaml', 'toml']),
    default='original'
)
@click.argument('s3_path')
def view_dict_cmd(obj, in_format, out_format, s3_path):
    loaders = {
        'json': benedict.from_json,
        'yaml': benedict.from_yaml,
        'toml': benedict.from_toml
    }

    dumpers = {
        'json': json_dumper,
        'yaml': benedict.to_yaml,
        'toml': benedict.to_toml
    }

    if in_format == 'auto':
        in_format = s3_path.split('.')[-1]
        logger.info(f'Inferred format: {in_format}')

        if in_format not in loaders:
            raise UserWarning(f'Unsupported format: {in_format}')

    s3_uri = S3Uri(s3_path)
    dirpath = tempfile.gettempdir()
    filename = str(uuid.uuid4())
    filepath = Path(dirpath) / filename
    s3 = get_s3_client(obj)
    s3.download_file(s3_uri.bucket, s3_uri.path, str(filepath))

    loader = loaders[in_format]
    dumper = dumpers[in_format]

    if out_format != 'original':
        dumper = dumpers[out_format]

    d = loader(str(filepath))
    click.echo(dumper(d))


@s3_group.command(name='sync')
@click.option(
    '--recursive', is_flag=True
)
@click.option(
    '--skip-existing', is_flag=True
)
@click.option(
    '--concurrency', type=int, default=100
)
@click.argument(
    's3_path'
)
@click.argument(
    'local_path', type=click.Path(file_okay=False, dir_okay=True, path_type=Path)
)
@click.pass_obj
def sync_cmd(obj, recursive, skip_existing, concurrency, s3_path, local_path):
    logger.info(f'Syncing {s3_path} to {local_path}')

    sync_folder_from_s3(
        s3_path, local_path,
        session_config=obj,
        recursive=recursive,
        skip_existing=skip_existing,
        concurrency=concurrency
    )


def json_dumper(d):
    return benedict.to_json(d, indent=2)


def list_all_objects(
    s3_path: str | S3Uri,
    on_object: Callable[[dict], None],
    *,
    s3_client: S3Client | None = None,
    session_config: dict = {}
):
    '''List all objects in an S3 bucket and call on_object for each'''
    if isinstance(s3_path, str):
        s3_uri = S3Uri(s3_path)
    else:
        s3_uri = s3_path

    client = s3_client or get_s3_client(session_config=session_config)

    paginator = client.get_paginator('list_objects_v2')
    page_iterator = paginator.paginate(
        Bucket=s3_uri.bucket,
        Prefix=s3_uri.path
    )

    for page in page_iterator:
        if 'Contents' in page:
            for obj in page['Contents']:
                on_object(dict(obj))


def delete_bucket_contents(client, bucket_name):
    '''
    Deletes all objects and object versions from the specified S3 bucket
    '''
    logger.debug(f'Deleting all objects in bucket: {bucket_name}')

    # Delete all objects and their versions
    paginator = client.get_paginator('list_object_versions')
    page_iterator = paginator.paginate(Bucket=bucket_name)

    for page in page_iterator:
        # Delete object versions if they exist
        if 'Versions' in page:
            for version in page['Versions']:
                client.delete_object(
                    Bucket=bucket_name,
                    Key=version['Key'],
                    VersionId=version['VersionId']
                )

                logger.debug(
                    f'Deleted object: {version["Key"]} (version {version["VersionId"]})'
                )

        # Delete delete markers if they exist
        if 'DeleteMarkers' in page:
            for marker in page['DeleteMarkers']:
                client.delete_object(
                    Bucket=bucket_name,
                    Key=marker['Key'],
                    VersionId=marker['VersionId']
                )

                logger.debug(
                    f'Deleted delete marker: {marker["Key"]} (version {marker["VersionId"]})'
                )

    # Delete objects in a non-versioned bucket
    paginator = client.get_paginator('list_objects_v2')
    page_iterator = paginator.paginate(Bucket=bucket_name)

    objects_to_delete = []
    for page in page_iterator:
        if 'Contents' in page:
            for obj in page['Contents']:
                objects_to_delete.append({'Key': obj['Key']})

            if objects_to_delete:
                # Delete in batches of 1000 (AWS limit)
                for i in range(0, len(objects_to_delete), 1000):
                    batch = objects_to_delete[i:i + 1000]

                    client.delete_objects(
                        Bucket=bucket_name,
                        Delete={'Objects': batch}
                    )

                    logger.debug(f'Deleted {len(batch)} objects')

                objects_to_delete = []


def delete_bucket(client, bucket_name):
    '''
    Deletes the specified S3 bucket after emptying it
    '''

    # Delete the bucket
    logger.debug(f'Deleting bucket: {bucket_name}')
    client.delete_bucket(Bucket=bucket_name)
    logger.debug(f'Bucket {bucket_name} has been deleted successfully')


def fast_download_s3_files(
    targets: list[tuple[str, str, str | Path]],
    *,
    skip_existing: bool = False,
    create_folders: bool = True,
    concurrency: int = 100,
    session_config: dict = {}
):
    '''Download a list of files from S3 in parallel.

    Args:
        targets: List of tuples containing (bucket, key, local_path)
        skip_existing: Skip files that already exist locally
        create_folders: Create the folders for the files
        concurrency: Number of concurrent downloads
        session_config: Configuration for the AWS session (profile, region, etc.)
        s3_client: S3 client to use for the download (None uses the default client)
    '''

    boto_config = {
        'max_pool_connections': int(1.5 * concurrency)
    }

    client = get_s3_client(session_config, core_config=boto_config)
    transfer_config = TransferConfig(use_threads=False)

    logger.debug(f'Fast downloading {len(targets)} files')

    if create_folders:
        folders = set()

        for target in targets:
            folders.add(Path(target[2]).parent)

        for folder in folders:
            logger.debug(f'Creating folder {folder}')
            folder.mkdir(parents=True, exist_ok=True)

    def download_file(bucket_name, key, local_path):
        if isinstance(local_path, Path):
            local_path = str(local_path)

        if skip_existing and Path(local_path).exists():
            return f'Skipping {key} because it already exists'

        client.download_file(
            bucket_name, key, local_path, Config=transfer_config
        )

        return f'Successfully downloaded {key}'

    with ThreadPoolExecutor(max_workers=concurrency) as executor:
        futures = [
            executor.submit(
                download_file,
                target[0],
                target[1],
                target[2],
            ) for target in targets
        ]

        for future in futures:
            logger.debug(future.result())


def sync_folder_from_s3(
    s3_uri: str | S3Uri,
    local_dir: Path,
    *,
    session_config={},
    recursive: bool = False,
    skip_existing: bool = True,
    concurrency: int = 100
):
    '''Recursively download a folder from S3 using fast_download_s3_files

    Args:
        s3_uri: S3 URI to the folder
        local_dir: Local directory to save the folder
        s3_client: S3 client to use for the download (None uses the default client)
        recursive: Recursively download the folder
        concurrency: Number of concurrent downloads

    Note: This function always preserves the folder structure in the local directory,
        including filenames.
    '''

    if isinstance(s3_uri, str):
        s3_uri = S3Uri(s3_uri)

    # List all objects in the S3 folder using list_all_objects
    targets = []

    logger.debug(f'Listing objects in {s3_uri}')

    def on_object(obj):
        key = obj['Key']
        relative_path = Path(key).relative_to(s3_uri.path)

        if not recursive and relative_path.parent != Path('.'):
            return

        local_path = local_dir / relative_path
        targets.append((s3_uri.bucket, key, local_path))

    s3_client = get_s3_client(session_config)
    list_all_objects(s3_uri, on_object, s3_client=s3_client)

    if not targets:
        logger.debug(f'No files found in {s3_uri}')
        return

    logger.debug(f'Syncing {s3_uri} to {local_dir} with {len(targets)} files')

    # Use fast_download_s3_files to download all files
    fast_download_s3_files(
        targets,
        create_folders=True,
        skip_existing=skip_existing,
        session_config=session_config,
        concurrency=concurrency
    )
