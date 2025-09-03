import json
from typing import Dict, Optional, Union
import uuid

import boto3
from botocore.exceptions import ClientError

from shared_kernel.config import Config
from shared_kernel.logger import Logger
from shared_kernel.messaging.utils.event_messages import AWSEventMessage, PublishEventMessage

app_config = Config()
logger = Logger(app_config.get("APP_NAME"))

class AWSQueue:
    def __init__(self, arn, url, event_name):
        self.arn = arn
        self.url = url
        self.event_name = event_name

    def is_valid(self):
        return self.arn and self.url


class AWSMessagingUtility:
    """
    Manages AWS operations such as EventBridge rules, SQS queue creation, and message handling.
    """

    def __init__(self):
        self.event_bridge = boto3.client("events")
        self.sqs = boto3.client("sqs")
        self.s3 = boto3.client("s3")
        self.event_bus_name = app_config.get("EVENT_BUS_NAME")
        self.service_identifier = app_config.get("APP_IDENTIFIER")
        self.account_id = app_config.get("ACCOUNT_ID")
        self.region = app_config.get("AWS_REGION")
        self.queue_visiblity_timeout = app_config.get("QUEUE_VISIBLITY_TIMEOUT")
        self.s3_bucket = app_config.get("AWS_EVENT_PAYLOAD_BUCKET")

    def create_queue(self, event_name: str) -> AWSQueue:
        """
        Create a new SQS queue for the event.
        Args:
            event_name (str): The name of the event for which the queue is created.
        """
        try:
            queue_name = f"{self.service_identifier}-{event_name}"
            queue_policy = {
                    "Version": "2012-10-17",
                    "Statement": [{
                        "Effect": "Allow",
                        "Principal": {"Service": "events.amazonaws.com"},
                        "Action": "sqs:SendMessage",
                        "Resource": f"arn:aws:sqs:{self.region}:{self.account_id}:{queue_name}",
                        "Condition": {
                            "ArnEquals": {
                                "aws:SourceArn": f"arn:aws:events:{self.region}:{self.account_id}:rule/{self.event_bus_name}/*"
                            }
                        }
                    }]
                }
            
            response = self.sqs.create_queue(
                    QueueName=queue_name,
                    Attributes={
                        'Policy': json.dumps(queue_policy),
                        'VisibilityTimeout': str(self.queue_visiblity_timeout),
                    }
                )
            queue_url = response["QueueUrl"]
            queue: AWSQueue = self.get_queue(event_name)
            logger.info(f"Queue '{queue_name}' created with URL: {queue_url}")
            return queue

        except ClientError as e:
            logger.error(f"Failed to create queue: {e}")
            raise

    def get_queue(self, event_name: str) -> AWSQueue:
        """
        Retrieve URL of an SQS queue given its name.

        Args:
            event_name (str): event name to generate the queue name

        Returns:
            str: The URL of the queue.
        """
        # unfortunately, there isn't a single direct API call to get both the ARN and URL
        queue_name = f"{self.service_identifier}-{event_name}"
        response_url = self.sqs.get_queue_url(QueueName=queue_name)
        queue_url = response_url["QueueUrl"]
        response_attributes = self.sqs.get_queue_attributes(
            QueueUrl=queue_url, AttributeNames=["All"]
        )
        queue_arn = response_attributes["Attributes"]["QueueArn"]

        return AWSQueue(queue_arn, queue_url, event_name)

    def check_if_queue_exist(self, event_name: str) -> bool:
        """
        Check if an SQS queue for a specific event exists by querying AWS SQS.
        Args:
            event_name (str): The name of the event.
        Returns:
            bool: True if the queue exists, otherwise False.
        """
        queue_name_prefix = f"{self.service_identifier}-{event_name}"

        response = self.sqs.list_queues(QueueNamePrefix=queue_name_prefix)
        queue_urls = response.get("QueueUrls", None)

        return True if queue_urls else False
    
    def check_and_update_queue_config(self, aws_queue: AWSQueue):
        """
        Check if the existing queue configuration matches the desired configuration and update if necessary.
        """
        queue_name = f"{self.service_identifier}-{aws_queue.event_name}"
        desired_queue_policy = {
            "Version": "2012-10-17",
            "Statement": [{
                "Effect": "Allow",
                "Principal": {"Service": "events.amazonaws.com"},
                "Action": "sqs:SendMessage",
                "Resource": f"arn:aws:sqs:{self.region}:{self.account_id}:{queue_name}",
                "Condition": {
                    "ArnEquals": {
                        "aws:SourceArn": f"arn:aws:events:{self.region}:{self.account_id}:rule/{self.event_bus_name}/*"
                    }
                }
            }]
        }

        # get the current queue policy and visibility timeout
        current_queue_attributes = self.sqs.get_queue_attributes(
            QueueUrl=aws_queue.url,
            AttributeNames=['Policy', 'VisibilityTimeout']
        )
        current_queue_policy = json.loads(current_queue_attributes['Attributes']['Policy'])
        current_visibility_timeout = int(current_queue_attributes['Attributes']['VisibilityTimeout'])

        # check if the current visibility timeout matches the desired timeout
        desired_visibility_timeout = int(self.queue_visiblity_timeout)
        if current_visibility_timeout != desired_visibility_timeout:
            logger.info(f"Updating queue visibility timeout for {aws_queue.url}")
            self.sqs.set_queue_attributes(
                QueueUrl=aws_queue.url,
                Attributes={
                    'VisibilityTimeout': str(desired_visibility_timeout)
                }
            )

        # compare the current policy with the desired policy
        if current_queue_policy != desired_queue_policy:
            logger.info(f"Updating queue policy for {aws_queue.url}")
            self.sqs.set_queue_attributes(
                QueueUrl=aws_queue.url,
                Attributes={
                    'Policy': json.dumps(desired_queue_policy)
                }
            )

    def add_event_bridge_rule(self, queue: AWSQueue):
        """
        Add an EventBridge rule to forward the event to the SQS queue.

        Args:
            queue (AWSQueue): AWSQueue object that contains arn, url and event name related to the queue
        """
        rule_name = f"{queue.event_name}_{self.service_identifier}"
        event_pattern = json.dumps({"detail-type": [queue.event_name]})
        self.event_bridge.put_rule(
            Name=rule_name,
            EventPattern=event_pattern,
            State="ENABLED",
            EventBusName=self.event_bus_name,
        )
        self.event_bridge.put_targets(
            Rule=rule_name,
            EventBusName=self.event_bus_name,
            Targets=[
                {
                    "Id": f"{queue.event_name}_{self.service_identifier}_sqs_target",
                    "Arn": queue.arn,
                }
            ],
        )
        logger.info(f"EventBridge rule '{rule_name}' added.")

    def get_message_from_queue(self, queue: AWSQueue):
        """
        Poll the SQS queue for messages.
        Returns:
            List[Dict]: A list of messages received from the SQS queue.
        """
        while True:
            # keep waiting for new messages
            response = self.sqs.receive_message(
                QueueUrl=queue.url,
                MaxNumberOfMessages=1,
                WaitTimeSeconds=20,
            )
            messages = response.get("Messages")
            if messages:
                return messages[0]

    def delete_message_from_queue(self, queue: AWSQueue, receipt_handle):
        """
        Delete a message from the SQS queue.
        Args:
            message (Dict): The message to be deleted.
        """
        self.sqs.delete_message(
            QueueUrl=queue.url, ReceiptHandle=receipt_handle
        )
        logger.info(
            f"Message deleted from queue with receipt handle '{receipt_handle}'."
        )

    def _check_payload_size(self, json_payload: str) -> bool:
        """
        Check if the payload size exceeds 256 KB.
        
        Args:
            json_payload (str): The JSON payload to check
            
        Returns:
            bool: True if payload size exceeds 256 KB, False otherwise
        """
        return len(json_payload.encode('utf-8')) > 262144  # 256 KB in bytes

    def _upload_payload_to_s3(self, json_payload: str) -> str:
        """
        Upload large payload to S3 and return the S3 path.
        
        Args:
            json_payload (str): The JSON payload to upload
            
        Returns:
            str: The S3 path where the payload is stored
        """
        try:
            # Generate a unique filename using UUID
            file_name = f"event_payload/{str(uuid.uuid4())}.txt"
            
            # Upload to S3
            self.s3.put_object(
                Bucket=self.s3_bucket,
                Key=file_name,
                Body=json_payload,
                ContentType='application/json'
            )
            
            # Return the S3 path
            s3_path = f"s3://{self.s3_bucket}/{file_name}"
            logger.info(f"Uploaded large payload to S3: {s3_path}")
            return s3_path
            
        except Exception as e:
            logger.error(f"Failed to upload payload to S3: {e}")
            raise

    def publish_event(self, event_name: str, event_payload: dict) -> Union[bool, Optional[dict]]:
        """
        Publish an event to EventBridge.
        Args:
            event_name (str): The name of the event.
            event_payload (dict): The payload of the event.
        Returns:
            bool: True if the event was successfully published.
        """
        try:
            publish_message = PublishEventMessage(event_payload)
            json_payload = publish_message.to_json()
            
            # Check if payload size exceeds 256 KB
            if self._check_payload_size(json_payload):
                # Upload to S3 and get the path
                s3_path = self._upload_payload_to_s3(json_payload)
                
                # Replace the payload with the S3 path and remove event_payload
                event_payload['event_payload_path'] = s3_path
                del event_payload['event_payload']
                publish_message = PublishEventMessage(event_payload)
                json_payload = publish_message.to_json()
                logger.warning(f"Event payload size exceeded 256 KB limit. Using S3 path: {s3_path}")
            
            response: dict = self.event_bridge.put_events(
                Entries=[
                    {
                        "Source": self.service_identifier,
                        "DetailType": event_name,
                        "Detail": json_payload,
                        "EventBusName": self.event_bus_name,
                    }
                ]
            )
            logger.info(f"Published event '{event_name}' with payload: {event_payload}")

            if response["FailedEntryCount"] > 0:
                logger.error(
                    f"Failed to publish event '{event_name}': {response['Entries'][0].get('ErrorMessage', 'Unknown error while publishing event')}"
                )
                return False, None
            else:
                event_id = response["Entries"][0].get("EventId")
                logger.info(
                    f"Successfully published event '{event_name}' with EventId: {event_id}"
                )
                return True, publish_message.event_dict
        except ClientError as e:
            logger.error(f"Failed to publish event: {e}")
            return False, None
        except Exception as e:
            logger.error(f"Failed to publish event: {e}")
            return False, None
        
    def _get_payload_from_s3(self, s3_path: str) -> str:
        """
        Retrieve and decode payload from S3 bucket.
        
        Args:
            s3_path (str): The S3 path where the payload is stored
            
        Returns:
            str: The decoded payload content
            
        Raises:
            ClientError: If there's an error accessing the S3 bucket
            ValueError: If the S3 path is invalid
        """
        try:
            # Extract bucket and key from s3:// path
            if not s3_path.startswith('s3://'):
                raise ValueError(f"Invalid S3 path format: {s3_path}")
                
            path_parts = s3_path.replace('s3://', '').split('/', 1)
            if len(path_parts) != 2:
                raise ValueError(f"Invalid S3 path format: {s3_path}")
                
            bucket, key = path_parts
            
            s3_object = self.s3.get_object(Bucket=bucket, Key=key)
            return s3_object["Body"].read().decode("utf-8")
            
        except ClientError as e:
            logger.error(f"Failed to retrieve payload from S3: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error while retrieving payload from S3: {e}")
            raise

    def receive_event(self, queue):
        """
        Receive and process an event from the queue, handling both direct payloads and S3-stored payloads.
        
        Args:
            queue (AWSQueue): The queue to receive the message from
            
        Returns:
            AWSEventMessage: The processed event message
        """
        deserialized_message = self.get_message_from_queue(queue)
        event_msg = AWSEventMessage(deserialized_message)
        
        if event_msg.event_payload_path:
            # raw message is passed into the callback function in job executor, hence adding the event payload inside raw message
            event_msg.raw_message["event_payload"] = json.loads(self._get_payload_from_s3(event_msg.event_payload_path))["event_payload"]
            
        return event_msg

    def get_queue_url_arn(self, event_name: str) -> dict:
        queue_name = f"{self.service_identifier}-{event_name}"
        queue_arn = f"arn:aws:sqs:{self.region}:{self.account_id}:{queue_name}"
        queue_url = f"https://sqs.{self.region}.amazonaws.com/{self.account_id}/{queue_name}"
        return {
            "queue_arn": queue_arn, 
            "queue_url": queue_url
        }
    
    def update_visibility_timeout(self, queue_url, receipt_handle, timeout_in_seconds):
        try:
            response = self.sqs.change_message_visibility(
                QueueUrl=queue_url,
                ReceiptHandle=receipt_handle,
                VisibilityTimeout=timeout_in_seconds
            )
            logger.info(f"Message visibility changed: {response}")
        
        except ClientError as e:
            logger.error(f"Error changing message visibility: {e}")
            raise e
    
    def get_queue_count(self, queue: AWSQueue) -> int:
        """
        Get the approximate number of messages in the queue for a specific event.
        
        Args:
            event_name (str): The name of the event to get the queue count for
            
        Returns:
            int: The approximate number of messages in the queue
            
        Raises:
            ClientError: If there's an error accessing the queue
        """
        try:
            
            # Get queue attributes including approximate message count
            response = self.sqs.get_queue_attributes(
                QueueUrl=queue.url,
                AttributeNames=['ApproximateNumberOfMessages']
            )

            # Return the count (default to 0 if not available)
            count = int(response['Attributes'].get(
                'ApproximateNumberOfMessages', 0))
            logger.info(
                f"Approximate message count for queue '{queue.arn}': {count}")
            return count

        except ClientError as e:
            if e.response['Error']['Code'] == 'AWS.SimpleQueueService.NonExistentQueue':
                logger.info(f"Queue '{queue.arn}' does not exist")
                return 0
            logger.error(
                f"Error getting queue count '{queue.arn}': {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error getting queue count: {e}")
            raise
