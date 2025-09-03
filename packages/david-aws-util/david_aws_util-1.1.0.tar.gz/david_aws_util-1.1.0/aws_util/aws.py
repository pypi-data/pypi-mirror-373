import boto3

def get_sts_assume_role(aws_access_key, aws_secret_key, role_arn, role_session_name = 'aws_session'):

    sts_client = boto3.client('sts', aws_access_key_id=aws_access_key, aws_secret_access_key=aws_secret_key)

    response = sts_client.assume_role(
        RoleArn=role_arn,
        RoleSessionName=role_session_name
    )

    return response['Credentials']
