import boto3
iam = boto3.client('iam')
sts = boto3.client('sts')
accountId = ""


def lambda_handler(event, context):
    accountId = str(event['accountId'])
    accountRole='TSI_Base_FullAccess'
    roleArn = 'arn:aws:iam::' + accountId + ':role/' + accountRole
    role = sts.assume_role(RoleArn=roleArn,RoleSessionName='groupcreation')
    iamclient = boto3.client('iam',aws_access_key_id=role['Credentials']['AccessKeyId'],aws_secret_access_key=role['Credentials']['SecretAccessKey'], aws_session_token=role['Credentials']['SessionToken'])
    if event['action'] == 'provision':
        for i in range(1,11):
            responsegrcreate = iamclient.create_group(
            GroupName='{}{}'.format('Group',i)
            )
            responsepolattach = iamclient.attach_group_policy(
            GroupName=responsegrcreate['Group']['GroupName'],
            PolicyArn='arn:aws:iam::{}:policy/TSI_Base_Deny'.format(accountId)
            )
            responsepolattachmfa = iamclient.attach_group_policy(
            GroupName=responsegrcreate['Group']['GroupName'],
            PolicyArn='arn:aws:iam::{}:policy/TSI_Base_Policy_MFA'.format(accountId)
            )
    

    
    
