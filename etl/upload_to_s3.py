import boto3
import os
import logging
from dotenv import load_dotenv
from botocore.exceptions import ClientError

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(module)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
AWS_DEFAULT_REGION = os.getenv("AWS_DEFAULT_REGION")
AWS_ENDPOINT_URL = os.getenv("AWS_ENDPOINT_URL")
S3_BUCKET_NAME = os.getenv("S3_BUCKET_NAME")


def get_s3_client():
    return boto3.client(
        "s3",
        endpoint_url=AWS_ENDPOINT_URL,
        aws_access_key_id=AWS_ACCESS_KEY_ID,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
        region_name=AWS_DEFAULT_REGION,
    )


def create_bucket(s3_client):
    try:
        s3_client.head_bucket(Bucket=S3_BUCKET_NAME)
        logger.info(f"Bucket '{S3_BUCKET_NAME}' already exists")
    except ClientError:
        s3_client.create_bucket(Bucket=S3_BUCKET_NAME)
        logger.info(f"Created bucket '{S3_BUCKET_NAME}'")


def upload_csv_files(s3_client):
    data_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data")
    csv_files = [f for f in os.listdir(data_dir) if f.endswith(".csv")]

    if not csv_files:
        logger.warning("No CSV files found in data/ folder")
        return

    for filename in csv_files:
        local_path = os.path.join(data_dir, filename)
        s3_key = f"raw/{filename}"
        s3_client.upload_file(local_path, S3_BUCKET_NAME, s3_key)
        logger.info(f"Uploaded {filename} to s3://{S3_BUCKET_NAME}/{s3_key}")


def main():
    logger.info("Starting S3 upload")
    s3_client = get_s3_client()
    create_bucket(s3_client)
    upload_csv_files(s3_client)
    logger.info("Upload complete")


if __name__ == "__main__":
    main()