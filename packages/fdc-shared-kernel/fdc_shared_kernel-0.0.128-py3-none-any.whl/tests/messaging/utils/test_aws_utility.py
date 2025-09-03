import json
import pytest
from unittest.mock import patch, MagicMock
from moto.sqs import mock_sqs
from moto.events import mock_events
from moto.s3 import mock_s3
import boto3

from shared_kernel.messaging.utils.aws_utility import AWSMessagingUtility, AWSQueue
from shared_kernel.messaging.utils.event_messages import AWSEventMessage, PublishEventMessage

@pytest.fixture
def aws_utility():
    mock_config = MagicMock()
    mock_config.get.side_effect = lambda key: {
        "APP_NAME": "test-app",
        "EVENT_BUS_NAME": "test-bus",
        "ACCOUNT_ID": "123456789012",
        "AWS_REGION": "us-east-1",
        "QUEUE_VISIBLITY_TIMEOUT": "30",
        "AWS_EVENT_PAYLOAD_BUCKET": "test-bucket"
    }[key]
    
    with patch('shared_kernel.messaging.utils.aws_utility.app_config', mock_config):
        utility = AWSMessagingUtility()
        return utility

@pytest.fixture
def sample_event_payload():
    return {
        "event_name": "test-event",
        "event_id": "test-event-id",
        "event_payload": {"key": "value"},
        "event_meta": {
            "trace_id": "test-trace-id",
            "span_id": "test-span-id",
            "timestamp": "2024-04-17T13:54:14.479Z"
        }
    }

@pytest.fixture
def setup_s3(aws_utility):
    with mock_s3():
        s3 = boto3.client('s3', region_name='us-east-1')
        s3.create_bucket(Bucket='test-bucket')
        yield s3

@pytest.fixture
def setup_sqs(aws_utility):
    with mock_sqs():
        sqs = boto3.client('sqs', region_name='us-east-1')
        yield sqs

@pytest.fixture
def setup_events(aws_utility):
    with mock_events():
        events = boto3.client('events', region_name='us-east-1')
        events.create_event_bus(Name='test-bus')
        yield events

class TestAWSQueue:
    def test_aws_queue_initialization(self):
        queue = AWSQueue("test-arn", "test-url", "test-event")
        assert queue.arn == "test-arn"
        assert queue.url == "test-url"
        assert queue.event_name == "test-event"

    def test_aws_queue_is_valid(self):
        valid_queue = AWSQueue("test-arn", "test-url", "test-event")
        assert valid_queue.is_valid()

        invalid_queue = AWSQueue(None, "test-url", "test-event")
        assert not invalid_queue.is_valid()

        invalid_queue = AWSQueue("test-arn", None, "test-event")
        assert not invalid_queue.is_valid()

class TestQueueOperations:
    def test_create_queue(self, aws_utility, setup_sqs):
        queue = aws_utility.create_queue("test-event")
        assert isinstance(queue, AWSQueue)
        assert queue.event_name == "test-event"
        assert "test-app-test-event" in queue.url

    def test_get_queue(self, aws_utility, setup_sqs):
        # First create a queue
        created_queue = aws_utility.create_queue("test-event")
        # Then get it
        queue = aws_utility.get_queue("test-event")
        assert queue.url == created_queue.url
        assert queue.arn == created_queue.arn

    def test_check_if_queue_exist(self, aws_utility, setup_sqs):
        # Queue doesn't exist initially
        assert aws_utility.check_if_queue_exist("test-event") is False
        
        # Create queue
        aws_utility.create_queue("test-event")
        assert aws_utility.check_if_queue_exist("test-event") is True

    def test_check_and_update_queue_config(self, aws_utility, setup_sqs):
        queue = aws_utility.create_queue("test-event")
        aws_utility.check_and_update_queue_config(queue)
        # No assertion needed as we're just ensuring no exceptions are raised

class TestEventBridgeOperations:
    def test_add_event_bridge_rule(self, aws_utility, setup_sqs, setup_events):
        queue = aws_utility.create_queue("test-event")
        aws_utility.add_event_bridge_rule(queue)
        # Verify rule was created by checking if we can get it
        rules = aws_utility.event_bridge.list_rules(EventBusName='test-bus', NamePrefix="test-event_rule")
        assert len(rules['Rules']) == 1
        rule = rules['Rules'][0]
        assert rule['Name'] == "test-event_rule"
        assert rule['State'] == "ENABLED"

    def test_publish_event_success(self, aws_utility, setup_events, sample_event_payload):
        success, result = aws_utility.publish_event("test-event", sample_event_payload)
        assert success is True
        assert result is not None

    def test_publish_event_failure(self, aws_utility):
        with patch('boto3.client') as mock_client:
            mock_client.return_value.put_events.return_value = {
                "FailedEntryCount": 1,
                "Entries": [{"ErrorMessage": "Test error"}]
            }
            success, result = aws_utility.publish_event("test-event", {})
            assert success is False
            assert result is None

class TestS3Operations:
    def test_check_payload_size(self, aws_utility):
        small_payload = json.dumps({"key": "value"})
        large_payload = json.dumps({"key": "x" * 300000})  # > 256KB
        
        assert aws_utility._check_payload_size(small_payload) is False
        assert aws_utility._check_payload_size(large_payload) is True

    def test_upload_payload_to_s3(self, aws_utility, setup_s3):
        payload = json.dumps({"key": "value"})
        s3_path = aws_utility._upload_payload_to_s3(payload)
        
        assert s3_path.startswith("s3://")
        assert aws_utility.s3_bucket in s3_path

    def test_get_payload_from_s3(self, aws_utility, setup_s3):
        # First upload a payload
        original_payload = json.dumps({"key": "value"})
        s3_path = aws_utility._upload_payload_to_s3(original_payload)
        
        # Then retrieve it
        retrieved_payload = aws_utility._get_payload_from_s3(s3_path)
        assert retrieved_payload == original_payload

    def test_get_payload_from_s3_invalid_path(self, aws_utility):
        with pytest.raises(ValueError):
            aws_utility._get_payload_from_s3("invalid-path")

class TestMessageOperations:
    def test_get_message_from_queue(self, aws_utility, setup_sqs):
        queue = aws_utility.create_queue("test-event")
        # Send a message to the queue
        aws_utility.sqs.send_message(
            QueueUrl=queue.url,
            MessageBody=json.dumps({"test": "message"})
        )
        message = aws_utility.get_message_from_queue(queue)
        assert message is not None
        assert "test" in json.loads(message["Body"])

    def test_delete_message_from_queue(self, aws_utility, setup_sqs):
        queue = aws_utility.create_queue("test-event")
        # Send and receive a message
        aws_utility.sqs.send_message(
            QueueUrl=queue.url,
            MessageBody=json.dumps({"test": "message"})
        )
        message = aws_utility.get_message_from_queue(queue)
        # Delete the message
        aws_utility.delete_message_from_queue(queue, message["ReceiptHandle"])
        # Try to receive messages again, should be empty
        response = aws_utility.sqs.receive_message(QueueUrl=queue.url)
        assert "Messages" not in response

    def test_recieve_event_with_direct_payload(self, aws_utility, setup_sqs):
        queue = aws_utility.create_queue("test-event")
        # Send a message with the correct event structure
        aws_utility.sqs.send_message(
            QueueUrl=queue.url,
            MessageBody=json.dumps({
                "detail": {
                    "event_name": "test-event",
                    "event_payload": "test",
                    "metadata": {
                        "trace_id": "test-trace-id",
                        "timestamp": "2024-04-17T13:54:14.479Z"
                    }
                }
            })
        )
        event_msg = aws_utility.recieve_event(queue)
        assert event_msg is not None
        assert event_msg.event_name == "test-event"
        assert event_msg.event_payload == "test"

    def test_recieve_event_with_s3_payload(self, aws_utility, setup_sqs, setup_s3):
        queue = aws_utility.create_queue("test-event")
        # Upload payload to S3 with proper JSON format
        payload = json.dumps({"event_payload": "test payload"})
        s3_path = aws_utility._upload_payload_to_s3(payload)
        # Send a message with S3 path
        aws_utility.sqs.send_message(
            QueueUrl=queue.url,
            MessageBody=json.dumps({
                "detail": {
                    "event_name": "test-event",
                    "event_payload_path": s3_path,
                    "event_meta": {
                        "trace_id": "test-trace-id",
                        "span_id": "test-span-id",
                        "timestamp": "2024-04-17T13:54:14.479Z"
                    }
                }
            })
        )
        event_msg = aws_utility.recieve_event(queue)
        assert event_msg.event_payload == "test payload"

    def test_update_visibility_timeout(self, aws_utility, setup_sqs):
        queue = aws_utility.create_queue("test-event")
        # Send and receive a message
        aws_utility.sqs.send_message(
            QueueUrl=queue.url,
            MessageBody=json.dumps({"test": "message"})
        )
        message = aws_utility.get_message_from_queue(queue)
        # Update visibility timeout
        aws_utility.update_visibility_timeout(queue.url, message["ReceiptHandle"], 30)
        # No assertion needed as we're just ensuring no exceptions are raised

    def test_get_queue_url_arn(self, aws_utility):
        result = aws_utility.get_queue_url_arn("test-event")
        assert "queue_arn" in result
        assert "queue_url" in result
        assert "test-event" in result["queue_arn"]
        assert "test-event" in result["queue_url"] 