#!/usr/bin/env python

import boto3
import json
import time
import sys

sts = boto3.client('sts')
regionlist=[]
accountid="787043465971"

stsresponse = sts.assume_role(
       RoleArn='arn:aws:iam::{}:role/TSI_Base_FullAccess'.format(accountid),
       RoleSessionName='string')
session = boto3.Session(
       aws_access_key_id=stsresponse['Credentials']['AccessKeyId'],
       aws_secret_access_key=stsresponse['Credentials']['SecretAccessKey'],
       aws_session_token=stsresponse['Credentials']['SessionToken'])

###BASELINE DELETION
#
cf = boto3.client('cloudformation')
cfresp = cf.delete_stack_instances(StackSetName='Baseline-PROD',
Accounts=[
        accountid,
    ],
Regions=[
        'eu-central-1',
    ],
RetainStacks=False
)

cfstatus = cf.describe_stack_set_operation(StackSetName='Baseline-PROD',OperationId=cfresp['OperationId'])

while(cfstatus['StackSetOperation']['Status']=='RUNNING'):
    time.sleep(5)
    cfstatus = cf.describe_stack_set_operation(StackSetName='Baseline-PROD',OperationId=cfresp['OperationId'])
    print(cfstatus)

if (cfstatus['StackSetOperation']['Status'] != 'SUCCEEDED'):
    print(cfstatus['StackSetOperation']['Status'])
    exit(1)

##SecurityStack DELETION
cf = boto3.client('cloudformation')
cfresp = cf.delete_stack_instances(StackSetName='SecurityAlert-PROD',
Accounts=[
        accountid,
    ],
Regions=[
        'us-east-1',
    ],
RetainStacks=False
)

cfstatus = cf.describe_stack_set_operation(StackSetName='SecurityAlert-PROD',OperationId=cfresp['OperationId'])

while(cfstatus['StackSetOperation']['Status']=='RUNNING'):
    time.sleep(5)
    cfstatus = cf.describe_stack_set_operation(StackSetName='SecurityAlert-PROD',OperationId=cfresp['OperationId'])
    print(cfstatus)

if (cfstatus['StackSetOperation']['Status'] != 'SUCCEEDED'):
    print(cfstatus['StackSetOperation']['Status'])
    exit(1)

#fetch regions
ec2client = session.client('ec2')
ec2regionlist = ec2client.describe_regions()['Regions']
for region in ec2regionlist:
    regionlist.append(region['RegionName'])

#delete kms keys
for region in regionlist:
    kms = session.client('kms',region_name=region)
    aliasesresp = kms.list_aliases()
    aliases = aliasesresp['Aliases']
    for alias in aliases:
        if 'TSI_Base' in alias['AliasName']:
            print(alias['AliasName'])
            print(alias['TargetKeyId'])
            kms.delete_alias(AliasName=alias['AliasName'])
            try:
                kms.schedule_key_deletion(KeyId=alias['TargetKeyId'],PendingWindowInDays=7)
            except: 
                print("Key is already in deletion {}".format(alias['TargetKeyId']))

iam = session.client('iam')
#delete users
users = iam.list_users()
for user in users['Users']:
    for group in iam.list_groups_for_user(UserName=user['UserName'])['Groups']:
       iam.remove_user_from_group(GroupName=group['GroupName'],UserName=user['UserName'])
    try:
        iam.delete_login_profile(UserName=user['UserName'])
    except:
        print("profile already deleted")
    iam.delete_user(UserName=user['UserName'])
#delete groups
iamresponse = iam.list_groups()
for group in iamresponse['Groups']:
    attachedpolicies = iam.list_attached_group_policies(GroupName=group['GroupName'])
    for attachedpolicy in attachedpolicies['AttachedPolicies']:
        iam.detach_group_policy(GroupName=group['GroupName'],PolicyArn=attachedpolicy['PolicyArn'])
    iam.delete_group(GroupName=group['GroupName'])

#delete roles

roleslist = ["AWSCloudFormationStackSetExecutionRole", "Role1", "Role2", "Role3", "Role4", "Role5", "Role6", "Role7", "Role8", "Role9", "Role10", "TSI_Base_2ndLevel_Role", "TSI_Base_BackOffice_Role", "TSI_Base_CloudTrail_CloudWatchLogs_Role", "TSI_Base_ManagedServices", "TSI_Base_ReadOnlySwitchRole", "TSI_Base_S3_DPC_SecDevOps_Role"]

for role in roleslist:
    try:
        attachedrolepolicies = iam.list_attached_role_policies( RoleName=role)
        for attachedpolicy in attachedrolepolicies['AttachedPolicies']:
            iam.detach_role_policy(RoleName=role,PolicyArn=attachedpolicy['PolicyArn'])
        inlinepols = iam.list_role_policies(RoleName=role)
        for inlinepolicyname in inlinepols['PolicyNames']:
            print(inlinepolicyname)
            print(iam.delete_role_policy(RoleName=role,PolicyName=inlinepolicyname))
        iam.delete_role(RoleName=role)
    except:
        print("Skipping {}".format(role))
        print(sys.exc_info()[0])

#delete policies
iamresponse = iam.list_policies(Scope='Local')
for policy in iamresponse['Policies']:
    if(('TSI' in policy['PolicyName']) and ('Billing' not in policy['PolicyName'])):
        iam.delete_policy(PolicyArn=policy['Arn'])


#delete log group
cw = session.client('logs')
try:
    cw.delete_log_group(
    logGroupName='CloudTrail/DefaultLogGroup'
    )
except:
    print("skipping loggroup")

cloudtrail = session.client('cloudtrail')
try:
    cloudtrail.delete_trail(
    Name='TSI_Base_MasterAccountTrail'
    )
except:
    print("skipping cloudtrail")
