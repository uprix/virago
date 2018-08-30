import boto3

def lambda_handler(event, context):
    client = boto3.client('organizations')
    response = client.describe_account(
        AccountId=event['accountId']
    )

    return(response['Account']['Email'])

