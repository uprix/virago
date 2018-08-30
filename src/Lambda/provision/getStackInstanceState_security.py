import boto3
import json
def lambda_handler(event,context):
    cfclient = client = boto3.client('cloudformation') 
    response = client.describe_stack_set_operation(
    StackSetName='SecurityAlert-PROD',
    OperationId=event['securitystack']['OperationId']
    )
    
    return(response['StackSetOperation']['Status'])