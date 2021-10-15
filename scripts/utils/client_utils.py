import boto3
import os

AWS_REGION_ENV_VAR = "CDK_DEFAULT_REGION"

def get_aws_region() -> str:
    region = os.environ.get(AWS_REGION_ENV_VAR)
    if region is None:
        raise Exception(f"Missing {AWS_REGION_ENV_VAR} environment variable")
    return region

def get_nimble_client():
    return boto3.client('nimble', region_name=get_aws_region())

def get_identity_client():
    return boto3.client('identitystore', region_name=get_aws_region())

def get_cloudwatch_event_client():
    return boto3.client('events', region_name=get_aws_region())