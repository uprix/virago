import boto3
import json
def lambda_handler(event,context):
    cfclient = client = boto3.client('cloudformation') 
    response = cfclient.create_stack_instances(
    StackSetName='fullv3',
    Accounts=[
        str(event['accountId']),
    ],
    Regions=[
        str(event['region']),
    ],
    OperationPreferences={
        'FailureTolerancePercentage': 0,
        'MaxConcurrentCount': 1,
    }
    )
    
    #return(json.dumps(response))
    finalresponse = response
    finalresponse['accountId'] = event['accountId']
    finalresponse['region'] = event['region']
    return(finalresponse)
