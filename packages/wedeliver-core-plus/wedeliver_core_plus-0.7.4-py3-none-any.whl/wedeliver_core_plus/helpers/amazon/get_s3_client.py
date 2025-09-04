import boto3
from app import app


def get_s3_client():
    region_name = app.config.get("S3_REGION") or 'eu-west-1'
    identity_path = app.config.get("AWS_WEB_IDENTITY_TOKEN_FILE")
    if identity_path:
        sts_file = open(identity_path, "r")
        sts_token = sts_file.read()

        role_arn = app.config.get("AWS_ROLE_ARN")

        sts_client = boto3.client("sts")
        response = sts_client.assume_role_with_web_identity(
            RoleArn=role_arn,
            RoleSessionName="sdd-s3",
            WebIdentityToken=sts_token,
            DurationSeconds=3600,
        )
        credential_dict = response["Credentials"]
        s3_client = boto3.client(
            "s3",
            aws_access_key_id=credential_dict["AccessKeyId"],
            aws_secret_access_key=credential_dict["SecretAccessKey"],
            aws_session_token=credential_dict["SessionToken"],
            region_name=region_name,
        )
    elif app.config.get("AWS_SESSION_TOKEN"):
        s3_client = boto3.client(
            "s3",
            aws_access_key_id=app.config.get("AWS_ACCESS_KEY_ID"),
            aws_secret_access_key=app.config.get("AWS_SECRET_ACCESS_KEY"),
            aws_session_token=app.config.get("AWS_SESSION_TOKEN"),
            region_name=region_name,
        )
    else:
        s3_client = boto3.client(
            "s3",
            aws_access_key_id=app.config.get("AWS_ACCESS_KEY_ID"),
            aws_secret_access_key=app.config.get("AWS_SECRET_ACCESS_KEY"),
            region_name=region_name,
        )

    return s3_client
