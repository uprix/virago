import boto3
import json
def lambda_handler(event,context):
    cfclient = client = boto3.client('cloudformation') 
    response = client.describe_stack_set_operation(
    StackSetName='fullv2',
    OperationId=event['OperationId']
    )
    
    fornextStep = {'accountId': event['accountId'],'region': event['region'], 'OperationId' : event['OperationId'], 'Status' : response['StackSetOperation']['Status']}
    return fornextStep
