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
    
    session_assumed = aws_session(role_arn=ROLE_ARN, session_name='s3dpcLambda')
    
    ec2client = session_assumed.client('ec2')
    ec2regionlist = ec2client.describe_regions()['Regions']
    for region in ec2regionlist:
        regionlist.append(region['RegionName'])
    for region in regionlist:
        client = session_assumed.client('events',region_name=region)
        response = client.put_rule(
        Name='TSI_Base_CW_Rule_S3_ACL_Send_SecDevops',
        EventPattern="""{
  "detail-type": [
    "AWS API Call via CloudTrail"
  ],
  "source": [
    "aws.s3"
  ],
  "detail": {
    "eventSource": [
      "s3.amazonaws.com"
    ],
    "eventName": [
      "DeleteBucketCors",
      "DeleteBucketTagging",
      "CreateBucket",
      "PutBucketAcl",
      "PutBucketCors",
      "PutBucketPolicy",
      "PutBucketTagging",
      "PutBucketWebsite",
      "DeleteBucketEncryption"
    ]
  }
}""",
        State='ENABLED',
        Description='Send bucket level changes to secdevops'
        )
        print(response)
        response = client.put_targets(
        Rule='TSI_Base_CW_Rule_S3_ACL_Send_SecDevops',
        Targets=[
        {
            'Id' : 'TSI_Base_CW_Rule_S3_ACL_Send_SecDevops',
            'Arn' : 'arn:aws:events:{}:140492085282:event-bus/default'.format(region)
            }
            ]
            )

