import os
import sys
import unittest
import json
import time
import uuid
import boto3
import datetime

from shared_kernel.config import Config
from shared_kernel.logger import Logger
from shared_kernel.messaging.aws_databus import AWSDataBus

app_config = Config()
logger = Logger(app_config.get("APP_NAME"))


class TestAWSDataBusIntegration(unittest.TestCase):

    def setUp(self):
        """Reset instance before each test"""
        self.databus = AWSDataBus()
        self.received_messages = []

    def test_end_to_end_event_flow(self):
        try:
            """Test complete flow of publishing and receiving events"""
            event_name = f"create-user"
            test_payload = {
                "timestamp": str(datetime.datetime.now(datetime.UTC)),
                "test_id": str(uuid.uuid4()),
                "data": "test message"
            }

            def callback(message):
                try:
                    logger.info("Reached callback")
                    body = json.loads(message['Body'])
                    detail = body["detail"]
                    self.received_messages.append(detail)
                    logger.info(f"Recieved message ----------> {detail}")
                except Exception as e:
                    logger.info(f"Error in callback ---------------> {str(e)}")
            
            # subscribe to events
            self.databus.subscribe_async_event(event_name, callback)
            
            # wait for queue and rule setup
            time.sleep(5)
            
            success = self.databus.publish_event(event_name, test_payload)
            self.assertTrue(success)
            
            # wait for message processing
            while not self.received_messages:
                time.sleep(1)
                
            # verify message was received
            self.assertEqual(len(self.received_messages), 1)
            received_payload = self.received_messages[0]
            self.assertEqual(received_payload['test_id'], test_payload['test_id'])
            self.assertEqual(received_payload['data'], test_payload['data'])

        except KeyboardInterrupt:
            logger.info("quit")

if __name__ == '__main__':
    unittest.main()