import boto3
import secrets
import string
from random import shuffle
iam = boto3.client('iam')
sts = boto3.client('sts')
email = boto3.client('ses',region_name="eu-west-1")
accountId = ""


def lambda_handler(event, context):
    accountId = str(event['accountId'])
    accountRole='TSI_Base_FullAccess'
    roleArn = 'arn:aws:iam::' + accountId + ':role/' + accountRole
    role = sts.assume_role(RoleArn=roleArn,RoleSessionName='groupcreation')
    iamclient = boto3.client('iam',aws_access_key_id=role['Credentials']['AccessKeyId'],aws_secret_access_key=role['Credentials']['SecretAccessKey'], aws_session_token=role['Credentials']['SessionToken'])
    if event['action'] == 'provision':
        createuserresponse = iamclient.create_user(
        Path='/',
        UserName=event['username']
        )
        attachresponse = iamclient.add_user_to_group(
        GroupName='TSI_Base_Group_PowerUser',
        UserName=event['username']
        )
        upperchars = string.ascii_uppercase 
        lowerchars = string.ascii_lowercase 
        digits = string.digits 
        specchars = "#&@.!"
        password=''.join(secrets.choice(upperchars) for x in range(5))
        password=password+''.join(secrets.choice(lowerchars) for x in range(5))
        password=password+''.join(secrets.choice(digits) for x in range(5))
        password=password+specchars
        password=list(password)
        shuffle(password)
        password=''.join(password)
        profileresponse = iamclient.create_login_profile(
        UserName=event['username'],
        Password=password,
        PasswordResetRequired=True
        )
        logininformation  = """Dear Client,

below is the login information for your new AWS account. You can log in with the username requested as part of the on-boarding process.

URL: https://{}.signin.aws.amazon.com/console
Password: {}

Best regards,
Your T-Managed AWS Team""".format(event['accountId'],password)
        response = email.send_email(
        Source='aws-baseline-support@telekom.de',
        Destination={
            'ToAddresses': [
                event['email'] ],
            },
        Message={
            'Subject': {
                'Data': 'Login information'
            },
            'Body': {
                'Text': {
                    'Data': logininformation,
                }
            }
        })
        return(password)
    

    
    
