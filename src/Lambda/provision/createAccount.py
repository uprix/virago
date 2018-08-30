<<<<<<< HEAD
import boto3
import json
import uuid
import secrets

organizations = boto3.client('organizations')
cloudformation = boto3.client('cloudformation')
stepfunctions = boto3.client('stepfunctions')
s3 = boto3.client('s3')
email = boto3.client('ses',region_name="eu-west-1")


response = {}

def createTypeA(accountid,securityemail):
    accountids = json.loads(s3.get_object(
    Bucket='27565630-provision-confidential',
    Key='provision/accountids.json')['Body'].read())
    if (accountid in accountids['accountids']):
        return("FAILURE")
    else:
        accountids['accountids'].append(accountid)
        s3.put_object(
            Bucket='27565630-provision-confidential',
            Key='provision/accountids.json',
            Body=json.dumps(accountids))
        uuidstring = str(uuid.uuid4())
        content = { 'accountid' : accountid, 'status': "IN_PROGRESS", 'securityemail' : securityemail}
        s3.put_object(
            Bucket='27565630-provision-confidential',
            Key='provision/TYPEA-{}-{}.json'.format(accountid,uuidstring),
            Body=json.dumps(content))
        email.send_email(
        Source='aws-baseline-support@telekom.de',
        Destination={
            'ToAddresses': [
                'aws-baseline-support@telekom.de' ],
            },
        Message={
            'Subject': {
                'Data': 'New Account: TYPEA-{}-{}'.format(accountid,uuidstring)
            },
            'Body': {
                'Text': {
                    'Data': json.dumps(content),
                }
            }
        })
        return("createNewAccount:TYPEA-{}-{}".format(accountid,uuidstring))

def getStatusA(id):
    try:
        status = json.loads(s3.get_object(
    Bucket='27565630-provision-confidential',
    Key='provision/{}.json'.format(id))['Body'].read())
    except:
        return("FAILURE")
    else:
        if(status['status'] == 'SUCCESS'):
            return("SUCCESS:{}".format(status['accountid']))
        else:
            return(status['status'])

def createTypeB(accountid,accountemail,securityemail):
    accountids = json.loads(s3.get_object(
    Bucket='27565630-provision-confidential',
    Key='provision/accountids.json')['Body'].read())
    if (accountid in accountids['accountids']):
        return("FAILURE")
    else:
        accountids['accountids'].append(accountid)
        s3.put_object(
            Bucket='27565630-provision-confidential',
            Key='provision/accountids.json',
            Body=json.dumps(accountids))
        uuidstring = str(uuid.uuid4())
        content = { 'accountid' : accountid, 'status': "IN_PROGRESS", 'accountemail' : accountemail, 'securityemail' : securityemail}
        s3.put_object(
            Bucket='27565630-provision-confidential',
            Key='provision/TYPEB-{}-{}.json'.format(accountid,uuidstring),
            Body=json.dumps(content))
        email.send_email(
        Source='aws-baseline-support@telekom.de',
        Destination={
            'ToAddresses': [
                'aws-baseline-support@telekom.de' ],
            },
        Message={
            'Subject': {
                'Data': 'New Account: TYPEB-{}-{}'.format(accountid,uuidstring)
            },
            'Body': {
                'Text': {
                    'Data': json.dumps(content),
                }
            }
        })
        return("createNewAccount:TYPEB-{}-{}".format(accountid,uuidstring))

def getStatusB(id):
    try:
        status = json.loads(s3.get_object(
    Bucket='27565630-provision-confidential',
    Key='provision/{}.json'.format(id))['Body'].read())
    except:
        return("FAILURE")
    else:
        if(status['status'] == 'SUCCESS'):
            return("SUCCESS:{}".format(status['accountid']))
        else:
            return(status['status'])

def createAccount(accountemail,accountname,username,securityemail):
    uuidname = ''.join(accountname.split())
    inputjson = { 'accountemail' : accountemail , 'accountname' : accountname, 'username' : username, 'securityemail' : securityemail }
    response = stepfunctions.start_execution(
        stateMachineArn='arn:aws:states:eu-central-1:275662325630:stateMachine:createNewAccount',
        name='{}-{}'.format(uuidname,str(uuid.uuid4())),
        input=json.dumps(inputjson)
    )

    return("createNewAccount:"+response['executionArn'])

def accountStatus(operation_id):
    response=""
    try:
        sfnresponse = stepfunctions.describe_execution(
        executionArn=operation_id
        )
    except:
        return("INVALID_TASK")
    if(sfnresponse['status']=='SUCCEEDED'):
        if('Failed' in sfnresponse['output']):
           outputjson = json.loads(sfnresponse['output'])
           return(outputjson['accountcreate']['CreateAccountStatus']['FailureReason'])
        baselinestepjson=json.loads(sfnresponse['output'])
        baselinestep=baselinestepjson['executionArn']
        sfnresponsebaseline = stepfunctions.describe_execution(
        executionArn=baselinestep
        )
        if(sfnresponsebaseline['status']=='SUCCEEDED'):
            respjson = json.loads(sfnresponsebaseline['input'])
            response="SUCCESS:{}".format(respjson['accountId'])
        elif (sfnresponsebaseline['status']=='RUNNING'):
            response="IN_PROGRESS"
        else:
            response="FAILURE"
    elif(sfnresponse['status']=='RUNNING'):
        response="IN_PROGRESS"
    else:
        return("INTERNAL_FAILURE")
    return(response)

def lambda_handler(event, context):
    if('task' in list(event.keys())):
        pass
    else:
        return("INVALID_TASK")
    if(event['task'] == 'create'):
        params=["accounttype"]
        bparamslistparams = []
        for param in params:
            if(param in event.keys()):
                bparamslistparams.append(True)
            else:
                bparamslistparams.append(False)
        print(bparamslistparams)
        print(all(bparamslistparams))
        if(not(all(bparamslistparams))):
            return("MISSING_PARAMETERS")
        accounttype=event['accounttype']
        if(accounttype == "A"):
            params=["accountid", "securityemail"]
            bparamslistparams = []
            for param in params:
                if(param in event.keys()):
                    bparamslistparams.append(True)
                else:
                    bparamslistparams.append(False)
            print(bparamslistparams)
            print(all(bparamslistparams))
            if(not(all(bparamslistparams))):
                return("MISSING_PARAMETERS")
            accountid = event['accountid']
            securityemail=event['securityemail']
            return(createTypeA(accountid,securityemail))
        elif(accounttype == "B"):
            #Send invitation to AWS organizations
            #http://boto3.readthedocs.io/en/latest/reference/services/organizations.html#Organizations.Client.invite_account_to_organization
            params=["accountid", "accountemail", "securityemail"]
            bparamslistparams = []
            for param in params:
                if(param in event.keys()):
                    bparamslistparams.append(True)
                else:
                    bparamslistparams.append(False)
            print(bparamslistparams)
            print(all(bparamslistparams))
            if(not(all(bparamslistparams))):
                return("MISSING_PARAMETERS")
            return(createTypeB(event['accountid'],event['accountemail'],event['securityemail']))
        elif(accounttype == "C"):
            #Create new account
            params=["accountemail","accountname","username","securityemail"]
            bparamslistparams = []
            for param in params:
                if(param in event.keys()):
                    bparamslistparams.append(True)
                else:
                    bparamslistparams.append(False)
            print(bparamslistparams)
            print(all(bparamslistparams))
            if(not(all(bparamslistparams))):
                return("MISSING_PARAMETERS")
            creationstatus = createAccount(event['accountemail'],event['accountname'], event['username'],event['securityemail'])
            return(creationstatus)
        elif(accounttype == "0"):
            #Create new account - internal
            params=["accountemail","accountname","username","securityemail"]
            bparamslistparams = []
            for param in params:
                if(param in event.keys()):
                    bparamslistparams.append(True)
                else:
                    bparamslistparams.append(False)
            print(bparamslistparams)
            print(all(bparamslistparams))
            if(not(all(bparamslistparams))):
                return("MISSING_PARAMETERS")
            creationstatus = createAccount(event['accountemail'],event['accountname'], event['username'],event['securityemail'])
            return(creationstatus)
    elif(event['task'] == 'status'):
        if ("operation_id" in event.keys()):
            if event['operation_id'].startswith("TYPEA"):
                return(getStatusA(event['operation_id']))
            elif event['operation_id'].startswith("TYPEB"):
                return(getStatusB(event['operation_id']))
            else:
                return(accountStatus(event['operation_id']))
        else:
            return("MISSING_PARAMETERS")
    elif(event['task'] == 'close'):
        if ("account_id" in event.keys()):
            return("SUCCESS")
        else:
            return("MISSING_PARAMETERS")
    else:
        return("INVALID_TASK")
=======
import boto3
import json
import uuid
import secrets

organizations = boto3.client('organizations')
cloudformation = boto3.client('cloudformation')
stepfunctions = boto3.client('stepfunctions')
s3 = boto3.client('s3')

response = {}

def createTypeA(accountid,securityemail):
    accountids = json.loads(s3.get_object(
    Bucket='27565630-provision-confidential',
    Key='provision/accountids.json')['Body'].read())
    if (accountid in accountids['accountids']):
        return("FAILURE")
    else:
        accountids['accountids'].append(accountid)
        s3.put_object(
            Bucket='27565630-provision-confidential',
            Key='provision/accountids.json',
            Body=json.dumps(accountids))
        uuidstring = str(uuid.uuid4())
        content = { 'accountid' : accountid, 'status': "IN_PROGRESS", 'securityemail' : securityemail}
        s3.put_object(
            Bucket='27565630-provision-confidential',
            Key='provision/TYPEA-{}-{}.json'.format(accountid,uuidstring),
            Body=json.dumps(content))
        email.send_email(
        Source='aws-baseline-support@telekom.de',
        Destination={
            'ToAddresses': [
                'aws-baseline-support@telekom.de' ],
            },
        Message={
            'Subject': {
                'Data': 'New Account: TYPEA-{}-{}'.format(accountid,uuidstring)
            },
            'Body': {
                'Text': {
                    'Data': json.dumps(content),
                }
            }
        })
        return("createNewAccount:TYPEA-{}-{}".format(accountid,uuidstring))

def getStatusA(id):
    try:
        status = json.loads(s3.get_object(
    Bucket='27565630-provision-confidential',
    Key='provision/{}.json'.format(id))['Body'].read())
    except:
        return("FAILURE")
    else:
        if(status['status'] == 'SUCCESS'):
            return("SUCCESS:{}".format(status['accountid']))
        else:
            return(status['status'])

def createTypeB(accountid,accountemail,securityemail):
    accountids = json.loads(s3.get_object(
    Bucket='27565630-provision-confidential',
    Key='provision/accountids.json')['Body'].read())
    if (accountid in accountids['accountids']):
        return("FAILURE")
    else:
        accountids['accountids'].append(accountid)
        s3.put_object(
            Bucket='27565630-provision-confidential',
            Key='provision/accountids.json',
            Body=json.dumps(accountids))
        uuidstring = str(uuid.uuid4())
        content = { 'accountid' : accountid, 'status': "IN_PROGRESS", 'accountemail' : accountemail, 'securityemail' : securityemail}
        s3.put_object(
            Bucket='27565630-provision-confidential',
            Key='provision/TYPEB-{}-{}.json'.format(accountid,uuidstring),
            Body=json.dumps(content))
        email.send_email(
        Source='aws-baseline-support@telekom.de',
        Destination={
            'ToAddresses': [
                'aws-baseline-support@telekom.de' ],
            },
        Message={
            'Subject': {
                'Data': 'New Account: TYPEB-{}-{}'.format(accountid,uuidstring)
            },
            'Body': {
                'Text': {
                    'Data': json.dumps(content),
                }
            }
        })
        return("createNewAccount:TYPEB-{}-{}".format(accountid,uuidstring))

def getStatusB(id):
    try:
        status = json.loads(s3.get_object(
    Bucket='27565630-provision-confidential',
    Key='provision/{}.json'.format(id))['Body'].read())
    except:
        return("FAILURE")
    else:
        if(status['status'] == 'SUCCESS'):
            return("SUCCESS:{}".format(status['accountid']))
        else:
            return(status['status'])

def createAccount(accountemail,accountname,username,securityemail):
    uuidname = ''.join(accountname.split())
    inputjson = { 'accountemail' : accountemail , 'accountname' : accountname, 'username' : username, 'securityemail' : securityemail }
    response = stepfunctions.start_execution(
        stateMachineArn='arn:aws:states:eu-central-1:275662325630:stateMachine:createNewAccount',
        name='{}-{}'.format(uuidname,str(uuid.uuid4())),
        input=json.dumps(inputjson)
    )

    return("createNewAccount:"+response['executionArn'])
    
def accountStatus(operation_id):
    response=""
    try:
        sfnresponse = stepfunctions.describe_execution(
        executionArn=operation_id
        )
    except:
        return("INVALID_TASK")
    if(sfnresponse['status']=='SUCCEEDED'):
        if('Failed' in sfnresponse['output']):
           outputjson = json.loads(sfnresponse['output'])
           return(outputjson['accountcreate']['CreateAccountStatus']['FailureReason']) 
        baselinestepjson=json.loads(sfnresponse['output'])
        baselinestep=baselinestepjson['executionArn']
        sfnresponsebaseline = stepfunctions.describe_execution(
        executionArn=baselinestep
        )
        if(sfnresponsebaseline['status']=='SUCCEEDED'):
            respjson = json.loads(sfnresponsebaseline['input'])
            response="SUCCESS:{}".format(respjson['accountId'])
        elif (sfnresponsebaseline['status']=='RUNNING'):
            response="IN_PROGRESS"
        else:
            response="FAILURE"
    elif(sfnresponse['status']=='RUNNING'):
        response="IN_PROGRESS"
    else:
        return("INTERNAL_FAILURE")
    return(response)

def lambda_handler(event, context):
    if('task' in list(event.keys())):
        pass
    else:
        return("INVALID_TASK")
    if(event['task'] == 'create'):
        params=["accounttype"]
        bparamslistparams = []
        for param in params:
            if(param in event.keys()):
                bparamslistparams.append(True)
            else:
                bparamslistparams.append(False)
        print(bparamslistparams)
        print(all(bparamslistparams))
        if(not(all(bparamslistparams))):
            return("MISSING_PARAMETERS")
        accounttype=event['accounttype']
        if(accounttype == "A"):
            params=["accountid", "securityemail"]
            bparamslistparams = []
            for param in params:
                if(param in event.keys()):
                    bparamslistparams.append(True)
                else:
                    bparamslistparams.append(False)
            print(bparamslistparams)
            print(all(bparamslistparams))
            if(not(all(bparamslistparams))):
                return("MISSING_PARAMETERS")
            accountid = event['accountid']
            securityemail=event['securityemail']
            return(createTypeA(accountid,securityemail))
        elif(accounttype == "B"):
            #Send invitation to AWS organizations
            #http://boto3.readthedocs.io/en/latest/reference/services/organizations.html#Organizations.Client.invite_account_to_organization
            params=["accountid", "accountemail", "securityemail"]
            bparamslistparams = []
            for param in params:
                if(param in event.keys()):
                    bparamslistparams.append(True)
                else:
                    bparamslistparams.append(False)
            print(bparamslistparams)
            print(all(bparamslistparams))
            if(not(all(bparamslistparams))):
                return("MISSING_PARAMETERS")
            return(createTypeB(event['accountid'],event['accountemail'],event['securityemail']))
        elif(accounttype == "C"):
            #Create new account
            params=["accountemail","accountname","username","securityemail"]
            bparamslistparams = []
            for param in params:
                if(param in event.keys()):
                    bparamslistparams.append(True)
                else:
                    bparamslistparams.append(False)
            print(bparamslistparams)
            print(all(bparamslistparams))
            if(not(all(bparamslistparams))):
                return("MISSING_PARAMETERS")
            creationstatus = createAccount(event['accountemail'],event['accountname'], event['username'],event['securityemail'])
            return(creationstatus)
        elif(accounttype == "0"):
            #Create new account - internal
            params=["accountemail","accountname","username","securityemail"]
            bparamslistparams = []
            for param in params:
                if(param in event.keys()):
                    bparamslistparams.append(True)
                else:
                    bparamslistparams.append(False)
            print(bparamslistparams)
            print(all(bparamslistparams))
            if(not(all(bparamslistparams))):
                return("MISSING_PARAMETERS")
            creationstatus = createAccount(event['accountemail'],event['accountname'], event['username'],event['securityemail'])
            return(creationstatus)
    elif(event['task'] == 'status'):
        if ("operation_id" in event.keys()):
            if event['operation_id'].startswith("TYPEA"):
                return(getStatusA(event['operation_id']))
            elif event['operation_id'].startswith("TYPEB"):
                return(getStatusB(event['operation_id']))
            else:
                return(accountStatus(event['operation_id']))
        else:
            return("MISSING_PARAMETERS")
    elif(event['task'] == 'close'):
        if ("account_id" in event.keys()):
            return("SUCCESS")
        else:
            return("MISSING_PARAMETERS")
    else:
        return("INVALID_TASK")
    
>>>>>>> develop
