import boto3
from botocore.exceptions import ClientError

def lambda_handler(event, context):
    tagsetExists=False
    dpc=""
    dpcexists=False
    encryption="none"
    #print(event['detail']['requestParameters']['bucketName'])
    client = boto3.client('s3')
    try:
        tags = client.get_bucket_tagging(
            Bucket=event['detail']['requestParameters']['bucketName']
            )
    except ClientError as e:
        #print(e.response)
        if e.response['Error']['Code'] == 'NoSuchTagSet':
             tagsetExists=False
    else:
        tagsetExists=True
    if (tagsetExists):
        for tag in tags['TagSet']:
            #We have DPC tag
            if tag['Key'] == 'DPC':
                dpcexists=True
                dpc=tag['Value']
                #tag is internal
                if ((dpc.lower() == 'internal')):
                    try:
                        encryption = client.get_bucket_encryption(
    Bucket=event['detail']['requestParameters']['bucketName']
)
                    except ClientError as e:
                        if e.response['Error']['Code'] == 'ServerSideEncryptionConfigurationNotFoundError':
                            encryption = "none"
                    else:
                        for serversideenc in encryption['ServerSideEncryptionConfiguration']['Rules']:
                            if ((serversideenc['ApplyServerSideEncryptionByDefault']['SSEAlgorithm'] != 'AES256') or (serversideenc['ApplyServerSideEncryptionByDefault']['SSEAlgorithm'] != 'aws:kms')):
                                print("Here comes aes")
                                client.put_bucket_encryption(
    Bucket=event['detail']['requestParameters']['bucketName'],
    ServerSideEncryptionConfiguration={
        'Rules': [
            {
                'ApplyServerSideEncryptionByDefault': {
                    'SSEAlgorithm': 'AES256'
                }
            },
        ]
    }
)
                    if ((encryption=="none")):
                                print("Here comes aes")
                                client.put_bucket_encryption(
    Bucket=event['detail']['requestParameters']['bucketName'],
    ServerSideEncryptionConfiguration={
        'Rules': [
            {
                'ApplyServerSideEncryptionByDefault': {
                    'SSEAlgorithm': 'AES256'
                }
            },
        ]
    }
)
                    result = client.get_bucket_acl(Bucket=event['detail']['requestParameters']['bucketName'])
                    for grants in result['Grants']:
                        if((grants['Grantee']['Type']=='Group') and (grants['Grantee']['URI']=='http://acs.amazonaws.com/groups/global/AllUsers')):
                            client.put_bucket_acl(ACL='private',Bucket=event['detail']['requestParameters']['bucketName'])
                #tag is confidential
                elif ((dpc.lower() == 'confidential')):
                    try:
                        encryption = client.get_bucket_encryption(
    Bucket=event['detail']['requestParameters']['bucketName']
)
                    except ClientError as e:
                        if e.response['Error']['Code'] == 'ServerSideEncryptionConfigurationNotFoundError':
                            encryption = "none"
                    else:
                        print(encryption)
                        for serversideenc in encryption['ServerSideEncryptionConfiguration']['Rules']:
                            if serversideenc['ApplyServerSideEncryptionByDefault']['SSEAlgorithm'] != 'aws:kms':
                                print("Here comes aes")
                                client.put_bucket_encryption(
    Bucket=event['detail']['requestParameters']['bucketName'],
    ServerSideEncryptionConfiguration={
        'Rules': [
            {
                'ApplyServerSideEncryptionByDefault': {
                    'SSEAlgorithm': 'aws:kms',
                    'KMSMasterKeyID': 'arn:aws:kms:eu-centra-1:787043465971:alias/confidentialkey'
                }
            },
        ]
    }
)
                    if ((encryption=="none")):
                                print("Here comes aes")
                                client.put_bucket_encryption(
    Bucket=event['detail']['requestParameters']['bucketName'],
    ServerSideEncryptionConfiguration={
        'Rules': [
            {
                'ApplyServerSideEncryptionByDefault': {
                    'SSEAlgorithm': 'aws:kms',
                    'KMSMasterKeyID': 'arn:aws:kms:eu-centra-1:787043465971:alias/confidentialkey'
                }
            },
        ]
    }
)
                    result = client.get_bucket_acl(Bucket=event['detail']['requestParameters']['bucketName'])
                    for grants in result['Grants']:
                        if((grants['Grantee']['Type']=='Group') and (grants['Grantee']['URI']=='http://acs.amazonaws.com/groups/global/AllUsers')):
                            client.put_bucket_acl(ACL='private',Bucket=event['detail']['requestParameters']['bucketName'])
                #tag is open so can be public
                elif (dpc.lower() == 'public'):
                    result = client.get_bucket_acl(Bucket=event['detail']['requestParameters']['bucketName'])
                    for grants in result['Grants']:
                        if((grants['Grantee']['Type']=='Group') and (grants['Grantee']['URI']=='http://acs.amazonaws.com/groups/global/AllUsers')):
                            print("THIS IS FULLY OPEN!")
                elif (dpc == 'open'):
                    result = client.get_bucket_acl(Bucket=event['detail']['requestParameters']['bucketName'])
                    try:
                            encryption = client.get_bucket_encryption(
    Bucket=event['detail']['requestParameters']['bucketName']
)
                    except ClientError as e:
                            #print(e.response)
                            print("No encryption found and it's okay")
                    else:
                            print("It's encrypted, leaving as is it")
                    for grants in result['Grants']:
                        if((grants['Grantee']['Type']=='Group') and (grants['Grantee']['URI']=='http://acs.amazonaws.com/groups/global/AllUsers')):
                            client.put_bucket_acl(ACL='private',Bucket=event['detail']['requestParameters']['bucketName'])
                #dpc is not internal confidential or open            
                else:
                    print("neither")
                    encryption = client.get_bucket_encryption(
    Bucket=event['detail']['requestParameters']['bucketName']
)
                    for rules in encryption['ServerSideEncryptionConfiguration']['Rules']:
                        if rules['ApplyServerSideEncryptionByDefault']['SSEAlgorithm'] != "AES256":
                            client.put_bucket_encryption(
    Bucket=event['detail']['requestParameters']['bucketName'],
    ServerSideEncryptionConfiguration={
        'Rules': [
            {
                'ApplyServerSideEncryptionByDefault': {
                    'SSEAlgorithm': 'AES256'
                }
            },
        ]
    }
)
                    client.put_bucket_acl(ACL='private',Bucket=event['detail']['requestParameters']['bucketName'])
                    buckettags = client.get_bucket_tagging(Bucket=event['detail']['requestParameters']['bucketName'])
                    for idx, tagitem in enumerate(buckettags['TagSet']):
                        if tagitem['Key'] == 'DPC':
                            buckettags['TagSet'][idx]['Value'] = 'Internal'                     
                    client.put_bucket_tagging(Bucket=event['detail']['requestParameters']['bucketName'],
    Tagging={ 'TagSet' : buckettags['TagSet'] }
)
        if (not dpcexists):
            print("No DPC tagset adding private acl, and dpc tagset to the bucket")
            client.put_bucket_encryption(
    Bucket=event['detail']['requestParameters']['bucketName'],
    ServerSideEncryptionConfiguration={
        'Rules': [
            {
                'ApplyServerSideEncryptionByDefault': {
                    'SSEAlgorithm': 'AES256'
                }
            },
        ]
    }
)
  
            client.put_bucket_acl(ACL='private',Bucket=event['detail']['requestParameters']['bucketName'])
            buckettags = client.get_bucket_tagging(Bucket=event['detail']['requestParameters']['bucketName'])
            #print(buckettags)
            buckettags['TagSet'].append({
                'Key': 'DPC',
                'Value': 'Internal'
            })
            client.put_bucket_tagging(Bucket=event['detail']['requestParameters']['bucketName'],
    Tagging= { 'TagSet' : buckettags['TagSet'] }
)
    else:
        print("No tagset adding one to the bucket")
        client.put_bucket_encryption(
    Bucket=event['detail']['requestParameters']['bucketName'],
    ServerSideEncryptionConfiguration={
        'Rules': [
            {
                'ApplyServerSideEncryptionByDefault': {
                    'SSEAlgorithm': 'AES256'
                }
            },
        ]
    }
)
  
        client.put_bucket_acl(ACL='private',Bucket=event['detail']['requestParameters']['bucketName'])
        client.put_bucket_tagging(Bucket=event['detail']['requestParameters']['bucketName'],
    Tagging={
        'TagSet': [
            {
                'Key': 'DPC',
                'Value': 'Internal'
            },
        ]
    }
)
    
