#!/usr/bin/env python

import boto3
import json

allaliases = {}
sts = boto3.client('sts')

with open('keys.json') as file:
    allaliases = json.load(file)

for accountalias in allaliases:
    print(accountalias['accountid'])
    stsresponse = sts.assume_role(
       RoleArn='arn:aws:iam::{}:role/TSI_Base_FullAccess'.format(accountalias['accountid']),
       RoleSessionName='string')
    session = boto3.Session(
       aws_access_key_id=stsresponse['Credentials']['AccessKeyId'],
       aws_secret_access_key=stsresponse['Credentials']['SecretAccessKey'],
       aws_session_token=stsresponse['Credentials']['SessionToken'])
    kms = session.client('kms')
#    kms.delete_alias(
#    AliasName='alias/TSI_Base_ConfidentialS3Key')
#    kms.delete_alias(
#    AliasName='alias/TSI_Base_InternalS3Key')
    for key in accountalias['keys']:
        for keyid in key.keys():
            try:
                response = kms.create_alias(
                    AliasName=keyid,
                    TargetKeyId=key[keyid]
                    )
                print(response)
                print(keyid)
                print(key[keyid])
            except:
                print("Skipping")

