from typing import cast

import randomname
import boto3
from botocore.config import Config
from types_boto3_s3 import S3Client
from types_boto3_dynamodb import DynamoDBClient, DynamoDBServiceResource
from types_boto3_route53 import Route53Client
from types_boto3_sts import STSClient
from types_boto3_sagemaker import SageMakerClient
from types_boto3_cognito_idp import CognitoIdentityProviderClient

from botobuddy.logger import logger


type AWSClient = (
    S3Client |
    DynamoDBClient |
    DynamoDBServiceResource |
    Route53Client |
    STSClient |
    SageMakerClient |
    CognitoIdentityProviderClient
)


def get_aws_session(session_config: dict = {}) -> boto3.Session:
    '''Create and return an AWS session with optional profile and region

    Args:
        session_config: A dictionary of session configuration options:
        - profile: The AWS profile to use
        - region: The AWS region to use
        - assume_role: The AWS role ARN to assume
        - session_name: The name of the session

    Returns:
        A boto3.Session object
    '''

    profile = session_config.get('profile')
    region = session_config.get('region')

    params = {}

    if profile:
        logger.info(f'Using AWS profile: {profile}')
        params['profile_name'] = profile

    if region:
        logger.info(f'Using AWS region: {region}')
        params['region_name'] = region

    logger.info('Creating AWS session')
    session = boto3.Session(**params)

    if assume_role := session_config.get('assume_role'):
        session_name = randomname.get_name()
        sts_client = session.client('sts')

        assumed_role_object = sts_client.assume_role(
            RoleArn=assume_role,
            RoleSessionName=session_name
        )

        logger.info(f'Assumed role {assume_role} with session name {session_name}')
        logger.debug(f'Assumed role object: {assumed_role_object}')
        credentials = assumed_role_object['Credentials']

        assume_params = {
            'aws_access_key_id': credentials['AccessKeyId'],
            'aws_secret_access_key': credentials['SecretAccessKey'],
            'aws_session_token': credentials['SessionToken']
        }

        if region:
            logger.info(f'Using AWS region: {region} for assumed role')
            assume_params['region_name'] = region

        logger.info('Creating AWS session with assumed role')
        session = boto3.Session(**assume_params)  # type: ignore

    return session


def get_aws_client(
    service,
    session_config={},
    resource=False,
    core_config: dict | None = None
) -> AWSClient:
    '''Create and return an AWS client with optional profile and region'''
    session = get_aws_session(session_config)

    client_params = {
        'service_name': service
    }

    if core_config:
        logger.debug(f'Using core session config: {core_config}')
        botocore_config = Config(**core_config)
        client_params['config'] = botocore_config

    if resource:
        result = session.resource(**client_params)
    else:
        result = session.client(**client_params)

    return result


# Client factories
def get_sts_client(session_config={}) -> STSClient:
    return cast(STSClient, get_aws_client('sts', session_config))


def get_s3_client(session_config={}, core_config: dict | None = None) -> S3Client:
    return cast(S3Client, get_aws_client('s3', session_config, core_config=core_config))


def get_dynamodb_client(session_config={}) -> DynamoDBClient:
    return cast(DynamoDBClient, get_aws_client('dynamodb', session_config))


def get_route53_client(session_config={}) -> Route53Client:
    return cast(Route53Client, get_aws_client('route53', session_config))


def get_sagemaker_client(session_config={}) -> SageMakerClient:
    return cast(SageMakerClient, get_aws_client('sagemaker', session_config))


def get_cognito_client(session_config={}) -> CognitoIdentityProviderClient:
    return cast(CognitoIdentityProviderClient, get_aws_client('cognito-idp', session_config))


# Resource factories
def get_dynamodb_resource(session_config={}) -> DynamoDBServiceResource:
    return cast(
        DynamoDBServiceResource,
        get_aws_client('dynamodb', session_config, resource=True)
    )
