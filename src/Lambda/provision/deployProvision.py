import boto3
import uuid
import json

stepfunctions = boto3.client('stepfunctions')

def lambda_handler(event, context):
    finalresponse={}
    accountid = event['accountcreate']['CreateAccountStatus']['AccountId']
    state = event['accountcreate']['CreateAccountStatus']['State']
    accountemail =event['accountemail']
    accountname = ''.join(event['accountname'].split())
    uuidname = ''.join(accountname.split())
    baselineparms = {}
    baselineparms['accountId'] = accountid
    baselineparms['email']=event['securityemail']
    baselineparms['action']="provision"
    baselineparms['username']=event['username']
    if(state == 'SUCCEEDED'):
        response = stepfunctions.start_execution(
    stateMachineArn='arn:aws:states:eu-central-1:275662325630:stateMachine:PROD-Provision_Baseline_Release_1',
    name='{}-{}'.format(uuidname,str(uuid.uuid4())),
    input=json.dumps(baselineparms)
)
        finalresponse = {'executionArn' : response['executionArn']}
    else:
        response = 'FAILED'
    #return(response['executionArn'])
    return(finalresponse)
