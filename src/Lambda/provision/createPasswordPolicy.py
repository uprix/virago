import boto3
import json
def lambda_handler(event,context):
    accountId = str(event['accountId'])
    stsclient = boto3.client('sts')
    accountRole='TSI_Base_FullAccess'
    roleArn = 'arn:aws:iam::' + accountId + ':role/' + accountRole
    role = stsclient.assume_role(RoleArn=roleArn,RoleSessionName='accountprovision')
    iamclient = boto3.resource('iam',aws_access_key_id=role['Credentials']['AccessKeyId'],aws_secret_access_key=role['Credentials']['SecretAccessKey'], aws_session_token=role['Credentials']['SessionToken'])
    account_password_policy = iamclient.AccountPasswordPolicy()
    response = account_password_policy.update(
    MinimumPasswordLength=8,
    RequireSymbols=True,
    RequireNumbers=True,
    RequireUppercaseCharacters=True,
    RequireLowercaseCharacters=True,
    AllowUsersToChangePassword=True,
    MaxPasswordAge=90,
    PasswordReusePrevention=5,
    HardExpiry=False
    )
    
    return(response)