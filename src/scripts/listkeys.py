#!/usr/bin/env python

import boto3
import json

cf = boto3.client('cloudformation')
response = cf.list_stack_instances(
    StackSetName='Baseline-PROD',
    MaxResults=100,
    )

allaliases = []


for stackset in response['Summaries']:
    accountinfo = {}
    accountinfo['accountid'] = stackset['Account']
    accountinfo['keys'] = []
    print(stackset['Account'])
    sts = boto3.client('sts')
    stsresponse = sts.assume_role(
            RoleArn='arn:aws:iam::{}:role/TSI_Base_FullAccess'.format(stackset['Account']),
            RoleSessionName='string')
    session = boto3.Session(
            aws_access_key_id=stsresponse['Credentials']['AccessKeyId'],
            aws_secret_access_key=stsresponse['Credentials']['SecretAccessKey'],
            aws_session_token=stsresponse['Credentials']['SessionToken'])
    kms = session.client('kms')
    aliases = kms.list_aliases()
    for alias in aliases['Aliases']:
        if (alias['AliasName']=='alias/TSI_Base_ConfidentialS3Key' or alias['AliasName']=='alias/TSI_Base_InternalS3Key'):
            key = {alias['AliasName'] : alias['TargetKeyId']}
            accountinfo['keys'].append(key)
    allaliases.append(accountinfo)

with open('keys.json', 'w') as outfile:
    json.dump(allaliases,outfile)
