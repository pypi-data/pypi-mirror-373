import click
import json
from pathlib import Path

from botobuddy.common import get_aws_client
from botobuddy.logger import logger


def import_commands(parent):
    parent.add_command(route53_group)


@click.group()
def route53_group():
    pass


@route53_group.command()
@click.pass_obj
@click.argument('hosted_zone_id')
def export_hosted_zone(obj, hosted_zone_id):
    '''Export all resource record sets from a specified hosted zone'''
    client = get_aws_client('route53', obj)
    response = client.list_resource_record_sets(HostedZoneId=hosted_zone_id)  # type: ignore
    click.echo(json.dumps(response['ResourceRecordSets'], indent=2))


@route53_group.command()
@click.pass_obj
@click.option('--filename', '-f', required=True, type=str)
@click.argument('hosted_zone_id')
def import_hosted_zone(obj, hosted_zone_id, filename):
    '''Import resource record sets into a specified hosted zone from a file, skipping NS and SOA records'''
    client = get_aws_client('route53', obj)
    records = json.loads(Path(filename).read_text())

    logger.info(f'Importing {len(records)} records to {hosted_zone_id}')

    for record in records:
        if record['Type'] in ['NS', 'SOA']:
            continue

        client.change_resource_record_sets(  # type: ignore
            HostedZoneId=hosted_zone_id,
            ChangeBatch={'Changes': [
                {'Action': 'UPSERT', 'ResourceRecordSet': record}
            ]}
        )
