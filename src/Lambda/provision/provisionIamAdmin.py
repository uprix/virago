import boto3
import json
def lambda_handler(event,context):
    accountId = str(event['accountId'])
    stsclient = boto3.client('sts')
    accountRole='TSI_Base_FullAccess'
    roleArn = 'arn:aws:iam::' + accountId + ':role/' + accountRole
    role = stsclient.assume_role(RoleArn=roleArn,RoleSessionName='accountprovision')
    iamclient = boto3.client('iam',aws_access_key_id=role['Credentials']['AccessKeyId'],aws_secret_access_key=role['Credentials']['SecretAccessKey'], aws_session_token=role['Credentials']['SessionToken'])
    rolepolicy =  {'Version': '2012-10-17', 'Statement': [{'Effect': 'Allow', 'Action': ['sts:AssumeRole'], 'Principal': {'AWS': '275662325630'}}]}
    encoded = json.dumps(rolepolicy)
    response = iamclient.create_role(AssumeRolePolicyDocument=encoded,RoleName='AWSCloudFormationStackSetExecutionRole')
    print(response)
    response = iamclient.attach_role_policy(
    RoleName='AWSCloudFormationStackSetExecutionRole',
    PolicyArn='arn:aws:iam::aws:policy/AdministratorAccess'
    )

    return(response)
