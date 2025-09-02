import click

from botobuddy.common import get_dynamodb_resource, DynamoDBServiceResource
from botobuddy.logger import logger


def import_commands(parent):
    parent.add_command(dynamo_group)


@click.group(name='dynamo')
def dynamo_group():
    pass


@dynamo_group.command(name='truncate-table')
@click.pass_obj
@click.argument('table_name')
def truncate_table_cmd(obj, table_name):
    '''Truncate a DynamoDB table'''
    client = get_dynamodb_resource(obj)
    counter = truncate_table(client, table_name)
    logger.info(f'Deleted {counter} items')


def truncate_table(client: DynamoDBServiceResource, table_name: str):
    '''Implementation to truncate a DynamoDB table'''
    table = client.Table(table_name)

    # Get the table keys
    tableKeyNames = [key.get('AttributeName') for key in table.key_schema]

    # Only retrieve the keys for each item in the table (minimize data transfer)
    projectionExpression = ', '.join('#' + key for key in tableKeyNames)
    expressionAttrNames = {'#' + key: key for key in tableKeyNames}

    counter = 0

    page = table.scan(
        ProjectionExpression=projectionExpression,
        ExpressionAttributeNames=expressionAttrNames
    )

    with table.batch_writer() as batch:
        while page['Count'] > 0:
            counter += page['Count']

            # Delete items in batches
            for itemKeys in page['Items']:
                batch.delete_item(Key=itemKeys)

            # Fetch the next page
            if 'LastEvaluatedKey' in page:
                page = table.scan(
                    ProjectionExpression=projectionExpression,
                    ExpressionAttributeNames=expressionAttrNames,
                    ExclusiveStartKey=page['LastEvaluatedKey']
                )

            else:
                break

    return counter
