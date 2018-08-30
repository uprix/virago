import boto3
import json
def lambda_handler(event,context):
    cfclient = client = boto3.client('cloudformation') 
    response = cfclient.create_stack_instances(
    StackSetName='Baseline-PROD',
    Accounts=[
        str(event['accountId']),
    ],
    Regions=[
        "eu-central-1",
    ],
    OperationPreferences={
        'FailureTolerancePercentage': 0,
        'MaxConcurrentCount': 1,
    }
    )
    
    return(response)