# services/s3_uploader.py
import boto3, os
S3 = boto3.client("s3", region_name=os.getenv("AWS_REGION","us-east-1"))
BUCKET = os.getenv("S3_BUCKET")

def upload_file(local_path, key=None):
    if key is None:
        key = os.path.basename(local_path)
    S3.upload_file(local_path, BUCKET, key)
    url = f"https://{BUCKET}.s3.amazonaws.com/{key}"
    return url
