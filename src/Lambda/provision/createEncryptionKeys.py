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
    if 'accountId' in event:
        accountId = str(event['accountId'])
    else:
        raise ValueError("No accountID provided")
    
    
    ROLE_ARN = 'arn:aws:iam::' + accountId +':role/TSI_Base_FullAccess'
    
    session_assumed = aws_session(role_arn=ROLE_ARN, session_name='kmskey')
    
    ec2client = session_assumed.client('ec2')
    ec2regionlist = ec2client.describe_regions()['Regions']
    for region in ec2regionlist:
        regionlist.append(region['RegionName'])
    for region in regionlist:
        client = session_assumed.client('kms',region_name=region)
        internalkeyresponse = client.create_key(
        Description='Internal Key',
        KeyUsage='ENCRYPT_DECRYPT',
        Origin='AWS_KMS',
        BypassPolicyLockoutSafetyCheck=False,
        Tags=[
            {
                'TagKey': 'TSI_KEY',
                'TagValue': 'Internal'
            },
        ]
        )
        confidentialkeyresponse = client.create_key(
        Description='Confidential Key',
        KeyUsage='ENCRYPT_DECRYPT',
        Origin='AWS_KMS',
        BypassPolicyLockoutSafetyCheck=False,
        Tags=[
            {
                'TagKey': 'TSI_KEY',
                'TagValue': 'Confidential'
            },
        ]
        )   
        try:
            aliasintresponse = client.create_alias(
            AliasName='alias/TSI_Base_InternalS3Key',
            TargetKeyId=internalkeyresponse['KeyMetadata']['Arn']
            )
        except:
            print("{} already have internal key with this alias".format(region))
        try:
            aliasconfresponse = client.create_alias(
            AliasName='alias/TSI_Base_ConfidentialS3Key',
            TargetKeyId=confidentialkeyresponse['KeyMetadata']['Arn']
            )
        except:
            print("{} already have confidential key with this alias".format(region))
