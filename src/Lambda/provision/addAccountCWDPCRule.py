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
    

def lambda_handler(event, context):
    regionlist.clear()
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
        response = client.describe_rule(Name='S3_DPC_Enforce_Baseline')
        eventrule = json.loads(response['EventPattern'])
        #print (eventrule['account'])
        for account in eventrule['account']:
            if(account==accountId):
                found = True
                print("Account found in {}".format(region))
                break
        if(found==False):
            print("Account not found in {}".format(region))
            eventrule['account'].append(accountId)
            client.put_rule(Name  = 'S3_DPC_Enforce_Baseline',
                            EventPattern = json.dumps(eventrule),
                            State='ENABLED',
                            Description='Enforce s3 bucket policy on customer accounts')
            
            