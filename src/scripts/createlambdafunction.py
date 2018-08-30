#!/usr/bin/env python

import boto3
import json

regionlist=[]

ec2client = boto3.client('ec2')
ec2regionlist = ec2client.describe_regions()['Regions']
for region in ec2regionlist:
      regionlist.append(region['RegionName'])
for region in regionlist:
	l = boto3.client('lambda',region_name=region)
	file =  open('./TSI_Base_S3DPC.zip', 'rb').read()
	try:
	    response = l.create_function(
	        FunctionName= 'TSI_Base_S3DPC',
	        Handler= 'lambda_function.lambda_handler',
	        Runtime= 'python3.6',
	        Role='arn:aws:iam::140492085282:role/TSI_Base_S3_DPC_Enforcement_role',
	        Timeout=10,
	        Code= {'ZipFile': file}
	    )
	except:
	    response = l.update_function_code(
	            FunctionName= 'TSI_Base_S3DPC',
	            ZipFile = file)
	    print(response)
	    response = l.update_function_configuration(
	            FunctionName= 'TSI_Base_S3DPC',
	            Handler= 'lambda_function.lambda_handler',
	            Role='arn:aws:iam::140492085282:role/TSI_Base_S3_DPC_Enforcement_role',
	            Runtime= 'python3.6',
	            Timeout=10)
	    print(response)
	response  = l.add_permission(
                Action='lambda:InvokeFunction',
                FunctionName='TSI_Base_S3DPC',
                Principal='events.amazonaws.com',
                SourceArn='arn:aws:events:{}:140492085282:rule/S3_DPC_Enforce_Baseline'.format(region),
                StatementId='ID-1'
                )
	print(response)

	
	events = boto3.client('events',region_name=region)
	
	response = events.put_rule(
	        Name  = 'S3_DPC_Enforce_Baseline',
	        EventPattern="""{
	  "account": [
	    "808065542248",
	    "787043465971",
	    "140492085282",
	    "049587108390",
	    "005765539777",
	    "275662325630",
	    "982628642532",
	    "333212656060"
	  ],
	  "source": [
	    "aws.s3"
	  ],
	  "detail-type": [
	    "AWS API Call via CloudTrail"
	  ],
	  "detail": {
	    "eventSource": [
	      "s3.amazonaws.com"
	    ],
	    "eventName": [
	      "DeleteBucketCors",
	      "DeleteBucketTagging",
	      "CreateBucket",
	      "PutBucketAcl",
	      "PutBucketCors",
	      "PutBucketPolicy",
	      "PutBucketTagging",
	      "PutBucketWebsite",
	      "DeleteBucketEncryption"
	    ]
	  }
	}""",
	State='ENABLED',
	        Description='Enforce s3 bucket policy on customer accounts'
	        )
	
	response = events.put_targets(
	        Rule='S3_DPC_Enforce_Baseline',
	        Targets=[
	        {
	            'Id' : 'S3_DPC_Enforce_Baseline',
	            'Arn' : 'arn:aws:lambda:{}:140492085282:function:TSI_Base_S3DPC'.format(region)
	            }
	            ]
	            )	
