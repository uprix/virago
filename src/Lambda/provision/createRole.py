<<<<<<< HEAD
import boto3
from time import sleep
from botocore.exceptions import ClientError
iam = boto3.client('iam')
sts = boto3.client('sts')
accountId = ""


def lambda_handler(event, context):
    accountId = str(event['accountId'])
    accountRole='TSI_Base_FullAccess'
    roleArn = 'arn:aws:iam::' + accountId + ':role/' + accountRole
    role = sts.assume_role(RoleArn=roleArn,RoleSessionName='rolereation')
    iamclient = boto3.client('iam',aws_access_key_id=role['Credentials']['AccessKeyId'],aws_secret_access_key=role['Credentials']['SecretAccessKey'], aws_session_token=role['Credentials']['SessionToken'])
    if event['action'] == 'provision':
        for i in range(1,6):
            responserolcreate = iamclient.create_role(
            RoleName='{}{}'.format('Role',i),
            AssumeRolePolicyDocument="""{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Service": "ec2.amazonaws.com"
      },
      "Action": "sts:AssumeRole"
    }
  ]
}"""
            )

            iamclient.create_instance_profile(
            InstanceProfileName='Role{}'.format(i),
            )

            iamclient.add_role_to_instance_profile(
            InstanceProfileName='Role{}'.format(i),
            RoleName='Role{}'.format(i)
            )
            for i in range(0,50):
                try:
                    responsepolattach = iamclient.attach_role_policy(
                    RoleName=responserolcreate['Role']['RoleName'],
                    PolicyArn='arn:aws:iam::{}:policy/TSI_Base_Deny'.format(accountId)
                    )
                except iamclient.exceptions.NoSuchEntityException as e:
                    continue
                else:
                    break
        for i in range(6,11):
            responserolcreate = iamclient.create_role(
            RoleName='{}{}'.format('Role',i),
            AssumeRolePolicyDocument="""{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Service": "lambda.amazonaws.com"
      },
      "Action": "sts:AssumeRole"
    }
  ]
}"""
            )
            for i in range(0,50):
                try:
                    responsepolattach = iamclient.attach_role_policy(
                    RoleName=responserolcreate['Role']['RoleName'],
                    PolicyArn='arn:aws:iam::{}:policy/TSI_Base_Deny'.format(accountId)
                    )
                except iamclient.exceptions.NoSuchEntityException:
                    continue
                else:
                    break
=======
import boto3
from time import sleep
from botocore.exceptions import ClientError
iam = boto3.client('iam')
sts = boto3.client('sts')
accountId = ""


def lambda_handler(event, context):
    accountId = str(event['accountId'])
    accountRole='TSI_Base_FullAccess'
    roleArn = 'arn:aws:iam::' + accountId + ':role/' + accountRole
    role = sts.assume_role(RoleArn=roleArn,RoleSessionName='rolereation')
    iamclient = boto3.client('iam',aws_access_key_id=role['Credentials']['AccessKeyId'],aws_secret_access_key=role['Credentials']['SecretAccessKey'], aws_session_token=role['Credentials']['SessionToken'])
    if event['action'] == 'provision':
        for i in range(1,6):
            responserolcreate = iamclient.create_role(
            RoleName='{}{}'.format('Role',i),
            AssumeRolePolicyDocument="""{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Service": "ec2.amazonaws.com"
      },
      "Action": "sts:AssumeRole"
    }
  ]
}"""
            )

            iamclient.create_instance_profile(
            InstanceProfileName='Role{}'.format(i),
            )

            iamclient.add_role_to_instance_profile(
            InstanceProfileName='Role{}'.format(i),
            RoleName='Role{}'.format(i)
            )
            for i in range(0,50):
                try:
                    responsepolattach = iamclient.attach_role_policy(
                    RoleName=responserolcreate['Role']['RoleName'],
                    PolicyArn='arn:aws:iam::{}:policy/TSI_Base_Deny'.format(accountId)
                    )
                except iamclient.exceptions.NoSuchEntityException as e:
                    continue
                else:
                    break
        for i in range(6,11):
            responserolcreate = iamclient.create_role(
            RoleName='{}{}'.format('Role',i),
            AssumeRolePolicyDocument="""{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Service": "lambda.amazonaws.com"
      },
      "Action": "sts:AssumeRole"
    }
  ]
}"""
            )
            for i in range(0,50):
                try:
                    responsepolattach = iamclient.attach_role_policy(
                    RoleName=responserolcreate['Role']['RoleName'],
                    PolicyArn='arn:aws:iam::{}:policy/TSI_Base_Deny'.format(accountId)
                    )
                except iamclient.exceptions.NoSuchEntityException:
                    continue
                else:
                    break
    

    
    
>>>>>>> develop
