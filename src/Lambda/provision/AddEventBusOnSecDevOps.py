import boto3
import json

regionlist = []

def aws_session(role_arn=None, session_name='my_session'):
    """
    If role_arn is given assumes a role and returns boto3 session
    otherwise return a regular session with the current IAM user/role
    """
    if role_arn:
        client = boto3.client('sts')
        response = client.assume_role(RoleArn=role_arn, RoleSessionName=session_name)
        session = boto3.Session(
            aws_access_key_id=response['Credentials']['AccessKeyId'],
            aws_secret_access_key=response['Credentials']['SecretAccessKey'],
            aws_session_token=response['Credentials']['SessionToken'])
        return session
    else:
        return boto3.Session()

def createEventBus(customerAccountID,secDevopsArn,region):
    print("{} not found in event bus adding it".format(customerAccountID))
    ROLE_ARN = 'arn:aws:iam::' + secDevopsArn +':role/TSI_Base_EventBusHandlerRole'
    session_assumed = aws_session(role_arn=ROLE_ARN, session_name='eventBusLambda')
    client = session_assumed.client('events',region_name=region)
    response = client.put_permission(
    Action='events:PutEvents',
    Principal=customerAccountID,
    StatementId=customerAccountID
    )


def lambda_handler(event, context):
    eventbusarn = ""
    secDevopsArn = "140492085282"
    if 'accountId' in event:
        eventbusarn="arn:aws:iam::{}:root".format(event['accountId'])
    else:
        raise ValueError("No accountID provided")
    if 'secDevopsArn' in event:
        secDevopsArn = event['secDevopsArn']
    accountId = str(event['accountId'])

    ROLE_ARN = 'arn:aws:iam::' + secDevopsArn +':role/TSI_Base_EventBusHandlerRole'

    session_assumed = aws_session(role_arn=ROLE_ARN, session_name='eventBusLambda')

    ec2client = session_assumed.client('ec2')
    ec2regionlist = ec2client.describe_regions()['Regions']
    for region in ec2regionlist:
        regionlist.append(region['RegionName'])

    print(regionlist)

    for region in regionlist:
        found = False
        client = session_assumed.client('events',region_name=region)
        response = client.describe_event_bus()
        if 'Policy' in response:
            policy=json.loads(response['Policy'])
            for policies in policy['Statement']:
                if eventbusarn in policies['Principal']['AWS']:
                    print("Prinicpal found already in {}".format(region))
                    found = True
                    break
            if(found):
                pass
            else:
                createEventBus(accountId,secDevopsArn,region)
                print("Created in region {}".format(region))
        else:
            print("kulso")
            createEventBus(accountId,secDevopsArn,region)
            print("Created in region {}".format(region))
