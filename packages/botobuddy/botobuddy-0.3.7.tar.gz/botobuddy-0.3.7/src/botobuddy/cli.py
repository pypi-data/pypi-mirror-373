import sys
import traceback
from argparse import ArgumentParser
from importlib.metadata import version

import click
from botocore.exceptions import TokenRetrievalError

from botobuddy.logger import setup_logging, logger
import botobuddy.s3 as s3
import botobuddy.dynamo as dynamo
import botobuddy.route53 as route53
import botobuddy.auth as auth
import botobuddy.sagemaker as sagemaker


@click.group()
@click.option('--verbose', is_flag=True, help='Enable debug logging')
@click.option('--traceback', is_flag=True, help='Enable traceback on error')
@click.option('--profile', help='AWS profile name to use')
@click.option('--region', help='AWS region to use')
@click.option('--assume-role', help='AWS role ARN to assume')
@click.version_option(version=version('botobuddy'))
@click.pass_context
def cli(ctx, verbose, **kwargs):
    '''Extended AWS Operations CLI'''
    setup_logging(verbose)
    ctx.ensure_object(dict)
    ctx.obj.update(kwargs)


def main():
    try:
        s3.import_commands(cli)
        dynamo.import_commands(cli)
        route53.import_commands(cli)
        auth.import_commands(cli)
        sagemaker.import_commands(cli)
        cli()
        sys.exit(0)

    except TokenRetrievalError:
        logger.error('Failed to retrieve AWS credentials, please check or re-login')
        sys.exit(1)

    except Exception as e:
        parser = ArgumentParser()
        parser.add_argument('--traceback', action='store_true')
        args, _ = parser.parse_known_args()

        if args.traceback:  # type: ignore
            traceback.print_exc()

        logger.error(e)
        sys.exit(100)


if __name__ == '__main__':
    main()
