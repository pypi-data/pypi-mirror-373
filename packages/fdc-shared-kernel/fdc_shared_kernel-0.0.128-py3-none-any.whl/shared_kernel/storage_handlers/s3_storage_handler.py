"""
File name: s3_file_handler.py
 * Last upadted: 18/07/2025
 * Author: Sanjeev Shaji
 * Last Change: BI-2135 - Added AWS Batch job handling modules to shared_kernel
"""

import boto3
import json
from shared_kernel.config import Config
from shared_kernel.logger import Logger

config = Config()
logger = Logger(config.get("APP_NAME"))
AWS_REGION =  config.get("AWS_REGION")
DATALAKE_BUCKET = config.get("FDC_DATA_LAKE_BUCKET")

class S3FileHandler:
    """
    Utility class for handling JSON file operations in S3.

    Provides methods to upload and download JSON content to/from the
    configured data lake S3 bucket.
    """
    def __init__(self):
        """
        Initializes the S3 client and sets the target bucket from configuration.
        """
        self.s3_client = boto3.client("s3", region_name=AWS_REGION)
        self.bucket = config.get("FDC_DATA_LAKE_BUCKET")

    def upload_json(self, key: str, data: dict):
        """
        Uploads a dictionary as a JSON file to the configured S3 bucket.

        Args:
            key (str): The S3 object key (path) to store the file.
            data (dict): The Python dictionary to upload as JSON.

        Returns:
            bool: True if upload is successful.

        Raises:
            Exception: Any error raised by boto3 during upload.
        """
        try:
            self.s3_client.put_object(
                Bucket=self.bucket,
                Key=key,
                Body=json.dumps(data),
                ContentType="application/json"
            )
            logger.info(f"Uploaded json file to S3: s3://{DATALAKE_BUCKET}/{key}")
            return True
        except Exception as e:
            logger.error(f"Failed to upload anomaly result to S3: {str(e)}")
            raise

    def download_json(self, key: str):
        """
        Downloads a JSON file from the configured S3 bucket and returns it as a dictionary.

        Args:
            key (str): The S3 object key (path) to fetch.

        Returns:
            dict: Parsed JSON content as a Python dictionary.

        Raises:
            Exception: Any error raised by boto3 or JSON decoding.
        """
        try:
            obj = self.s3_client.get_object(Bucket=self.bucket, Key=key)
            result = json.loads(obj["Body"].read())
            return result
        except Exception as e:
            logger.error(f"Failed to download json from S3: {str(e)}")
            raise