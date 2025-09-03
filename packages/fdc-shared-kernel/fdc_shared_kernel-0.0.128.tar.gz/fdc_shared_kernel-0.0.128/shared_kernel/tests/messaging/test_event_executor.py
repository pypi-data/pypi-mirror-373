import json
import time
from typing import Dict, Any, List
import unittest
from unittest.mock import Mock
import uuid
import datetime

from shared_kernel.config import Config
from shared_kernel.logger import Logger
from shared_kernel.messaging import AWSDataBus
from shared_kernel.event_executor import EventExecutor
from shared_kernel.status_tracker.status_tracker import StatusTracker

app_config = Config()
logger = Logger(app_config.get("APP_NAME"))

class TestEventExecutor(unittest.TestCase):
    """
    Test suite for EventExecutor using real AWS services.
    Requires valid AWS credentials and permissions for EventBridge and SQS.
    """
    
    def setUp(self):
        self.status_tracker = StatusTracker()
        self.databus = AWSDataBus()
        self.event_executor = EventExecutor(databus=self.databus, status_tracker=self.status_tracker)
        self.processed_messages: List[Dict[str, Any]] = []


    # def test_basic_event_flow(self):
    #     """Test basic event publishing and processing"""
    #     event_name = "test_executor_basic"
    #     test_payload = {
    #         "test_id": self.test_id,
    #         "message": "Three body problem",
    #         "timestamp": str(datetime.datetime.now(datetime.UTC)),
    #     }
        
    #     def callback(payload: Dict[str, Any]):
    #         message_body = json.loads(payload["Body"])
    #         event_payload = message_body["detail"]
    #         self.processed_messages.append(event_payload)
        
    #     # register event handler
    #     self.event_executor.register_event(event_name, callback, max_concurrency=1)
        
    #     # allow time for subscription to complete
    #     time.sleep(2)
        
    #     # publish event
    #     success = self.databus.publish_event(event_name, test_payload)
    #     self.assertTrue(success)
        
    #     # wait for the messsage to be recieved
    #     time.sleep(2)
        
    #     self.assertEqual(len(self.processed_messages), 1)
    #     self.assertEqual(self.processed_messages[0], test_payload)

    # def test_register_duplicate_event(self):
    #     """Test registering an already registered event"""
    #     event_name = "test_executor_duplicate"
    #     callback = Mock()
    #     max_concurrency = 5

    #     # register first time
    #     self.event_executor.register_event(event_name, callback, max_concurrency)

    #     # try to register again
    #     with self.assertRaises(ValueError) as context:
    #         self.event_executor.register_event(event_name, callback, max_concurrency)
        
    #     self.assertEqual(str(context.exception), f"Event {event_name} is already registered")
        

    def test_concurrent_execution(self):
        "Test concurrent execution of an event"
        max_concurrency = 3
        num_msgs = 8
        event_name = "FETCH_ENTITY"

        def callback(payload: Dict[str, Any], flag=None):
            logger.info(f"Processing message: {payload}")
            # simulate processing time
            time.sleep(3)
            self.processed_messages.append(payload)

        # register event handler
        self.event_executor.register_event(event_name, callback, max_concurrency)

        messages = [{'entity_id': i, "event_name": "FETCH_ENTITY", "payload": {"id": i}} for i in range(num_msgs)]

        # publish event
        for message in messages:
            logger.info(f"message sent --> {message}")
            success = self.databus.publish_event(event_name, message)
            self.assertTrue(success)

        self.event_executor.shutdown()



if __name__ == '__main__':
    unittest.main()