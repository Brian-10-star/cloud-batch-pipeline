import boto3
import os
import logging
import pandas as pd
from io import StringIO
from dotenv import load_dotenv

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


def list_raw_files(s3_client):
    response = s3_client.list_objects_v2(Bucket=S3_BUCKET_NAME, Prefix="raw/")

    if "Contents" not in response:
        logger.warning("No files found in s3://kenya-sales-bucket/raw/")
        return []

    files = [obj["Key"] for obj in response["Contents"] if obj["Key"].endswith(".csv")]
    logger.info(f"Found {len(files)} CSV files in S3: {files}")
    return files


def download_file(s3_client, s3_key):
    response = s3_client.get_object(Bucket=S3_BUCKET_NAME, Key=s3_key)
    content = response["Body"].read().decode("utf-8")
    df = pd.read_csv(StringIO(content))
    logger.info(f"Downloaded {s3_key} with {len(df)} rows")
    return df


def extract():
    logger.info("Starting extraction from S3")
    s3_client = get_s3_client()
    files = list_raw_files(s3_client)

    if not files:
        logger.error("Extraction failed: no files to process")
        return None

    dataframes = [download_file(s3_client, key) for key in files]
    combined = pd.concat(dataframes, ignore_index=True)
    logger.info(f"Extraction complete. Total rows: {len(combined)}")
    return combined


if __name__ == "__main__":
    df = extract()
    if df is not None:
        print(df.head())