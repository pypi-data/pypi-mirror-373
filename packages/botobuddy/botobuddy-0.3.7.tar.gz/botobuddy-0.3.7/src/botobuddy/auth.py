import json
import click

from botobuddy.common import get_sts_client


def import_commands(parent):
    parent.add_command(auth_group)


@click.group(name='auth')
def auth_group():
    pass


@auth_group.command()
@click.pass_obj
def caller(obj):
    sts_client = get_sts_client(obj)
    caller_identity = sts_client.get_caller_identity()
    click.echo(json.dumps(caller_identity, indent=4))
