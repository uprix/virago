import boto3
import json
from botocore.exceptions import ClientError
from datetime import datetime, timedelta
from os import environ

# Numer of days after which an access key is declared "expired" and a notification is being sent
MAX_NR_OF_DAYS=60

# set Environment variable "MAIL" to "no" if you don't want to send the mail, but rather only have the output

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


def check_keys (session, account):
    expired_keys = []
    client = session.client('iam')
    user_list = client.list_users()
    for user in user_list['Users']:
        key_list = client.list_access_keys(UserName=user['UserName'])
        for key in key_list['AccessKeyMetadata']:
            if ( key['Status'] == "Active" and key['CreateDate'] < datetime.now(key['CreateDate'].tzinfo) - timedelta(days=MAX_NR_OF_DAYS)):
                exp_key = { "account" : account, "user" : user, "key" : key }
                expired_keys.append(exp_key)

    mailbody = ""
    for key in expired_keys:
        account = key["account"]
        user = key["user"]
        key2 = key["key"]
        mailbody += "Account:" + account["accountNr"] + "\tUser:" + user['UserName'] + "\tKey:" + str(key2['AccessKeyId']) + "\n"

    if (mailbody != ""):
        mailbody = "Following keys are older than " + str(MAX_NR_OF_DAYS) + " days, please rotate: \n\n" + mailbody
        print (mailbody)
        # create SNS client in region N. Virginia, otherwise publishing to N.Virginia topic doesn't work
        if (environ['MAIL'] != "no"):
            client = session.client('sns', region_name='us-east-1')
            sns_topic_arn = "arn:aws:sns:us-east-1:" + account["accountNr"] + ":TSI_Base_Security_Incident"
            try:
                response = client.publish( TopicArn=sns_topic_arn, Message=mailbody, Subject="Expired AccessKeys" )
        
            except Exception as e:
                print ("Cannot publish to topic " + sns_topic_arn + " with error: ")
                print (e)


def lambda_handler(event, context):
    s3 = boto3.client('s3')

    bucketName="s3-confidential"
    key="accounts.json"

    try:
        data = s3.get_object(Bucket=bucketName, Key=key)
        json_object = json.loads(data['Body'].read())
                
    except Exception as e:
        print(e)
        raise e
    
    # First for the current (master?) account
    session_regular = aws_session()
    account = {}
    account["accountNr"] = session_regular.client('sts').get_caller_identity()['Account']
    check_keys(session_regular, account )   
    
    # Secondly, for the accounts listed in the JSON file
    for account in json_object:
        ROLE_ARN = 'arn:aws:iam::' + account["accountNr"] +':role/' + account['readonlyRole']
        try: 
            session_assumed = aws_session(role_arn=ROLE_ARN, session_name='TSI_check_accesskeys')
            check_keys(session_assumed, account)
        except Exception as e:
            print ("Cannot assume role " + ROLE_ARN + " in account " + account["accountNr"] + " with exception: ")
            print (e)
        
    return "success"
