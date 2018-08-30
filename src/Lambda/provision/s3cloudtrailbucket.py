import boto3
import json
s3client=""

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
    accountId = event['accountId']
    secDevopsArn = "140492085282"
    bucketName = "d2c5c7cadcb30307b27eeb81491f1ccec47ab2b3-s3-cloudtrail"
    ROLE_ARN = 'arn:aws:iam::' + secDevopsArn +':role/TSI_Base_S3CloudtrailRole'
    session_assumed = aws_session(role_arn=ROLE_ARN, session_name='eventBusLambda')
    s3client = session_assumed.client('s3')
    bucketpolicy = s3client.get_bucket_policy(
    Bucket=bucketName
    )
    policy = json.loads(bucketpolicy['Policy'])
    for element in policy['Statement']:
        if(element['Sid'] == 'AWSCloudTrailWrite20150319'):
            if("arn:aws:s3:::{}/AWSLogs/{}/*".format(bucketName,accountId) in element['Resource']):
                return("Found")
            else:
                element['Resource'].append("arn:aws:s3:::{}/AWSLogs/{}/*".format(bucketName,accountId))
                s3client.put_bucket_policy(
                Bucket=bucketName,
                ConfirmRemoveSelfBucketAccess=False,
                Policy=json.dumps(policy)
                )
                return("Added permission")