from typing import Callable, Any, Dict
from botocore.exceptions import ClientError
import json

from shared_kernel.config import Config
from shared_kernel.interfaces.databus import DataBus
from shared_kernel.logger import Logger
from shared_kernel.messaging.utils.aws_utility import AWSMessagingUtility, AWSQueue
from shared_kernel.messaging.utils.event_messages import AWSEventMessage, EventMessage
from shared_kernel.enums import TaskStatus

app_config = Config()
logger = Logger(app_config.get("APP_NAME"))


class AWSDataBus(DataBus):
    """
    An EventBridge and SQS interface class to handle event-driven communication.
    """

    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(AWSDataBus, cls).__new__(cls)
        return cls._instance

    def __init__(self, config: Dict = None):
        """
        Initialize the AWSDataBus and start listening to multiple SQS queues.

        Args:
            config (Dict): A dictionary containing the EventBridge and SQS configuration.
        """
        ## Importing here to avoid circular import error since status_tracker depends on DataBusFactory
        from shared_kernel.status_tracker.status_tracker import StatusTracker

        if not hasattr(self, "initialized"):  # Prevent reinitialization
            super().__init__()
            self.aws_utility = AWSMessagingUtility()
            self.event_queue_mapper = {}
            self.status_tracker = StatusTracker()
            self.initialized = True

    def make_connection(self):
        pass

    def close_connection(self):
        pass

    def request_event(self, event_name: str, event_payload: dict) -> Any:
        pass

    def publish_event(self, event_name: str, event_payload: dict) -> bool:
        """
        Publish an event to the EventBridge and check if it was successful.

        Args:
            event_name (str): The name of the event to publish.
            event_payload (dict): The payload of the event.

        Returns:
            bool: True if the event was published successfully, False otherwise.
        """
        is_success, validated_event_dict = self.aws_utility.publish_event(
            event_name, event_payload
        )
        if is_success and event_name != "DLQ":
            # we dont want to create status tracker entries for messages sent to DLQ
            event_msg_object = EventMessage(validated_event_dict)
            self.status_tracker.create_task(
                event_msg=event_msg_object,
                status=TaskStatus.QUEUED.value,
            )

            self.status_tracker.set_event_meta_and_message_receipt_handle(event_msg=event_msg_object)
            logger.info(
                f"Updated event: {validated_event_dict['event_name']} with meta: {validated_event_dict['event_meta']}"
            )
            return validated_event_dict["event_meta"]["job_id"]
        return None

    def subscribe_sync_event(self, event_name: str, callback: Callable[[Any], None]):
        """
        Not applicable
        """
        pass

    def sent_to_dead_letter_queue(self, event_name, message, failure_reason):
        pass

    def subscribe_async_event(self, event_name: str, callback: Callable[[Any], None]):
        """
        Subscribe to an event by creating an SQS queue for the event-specific queue
        and EventBridge rule.

        Args:
            event_name (str): The name of the event to subscribe to.
            callback (Callable): Included to comply with the DataBus interface but is not used
            in AWSDataBus as events are handled differently.
        """
        aws_queue = None
        if not self.aws_utility.check_if_queue_exist(event_name):
            aws_queue: AWSQueue = self.aws_utility.create_queue(event_name)
        else:
            aws_queue = self.aws_utility.get_queue(event_name)
            logger.info(f"Queue already exists: {aws_queue.url}")
            # check and update the queue configuration if necessary
            self.aws_utility.check_and_update_queue_config(aws_queue)

        self.aws_utility.add_event_bridge_rule(aws_queue)

        self.event_queue_mapper[event_name] = aws_queue

    def get_message(self, event_name):
        queue = self.event_queue_mapper[event_name]
        # get_message_from_queue should be blocking
        message = self.aws_utility.receive_event(queue)
        # message = self.aws_utility.get_message_from_queue(queue)
        return message

    def delete_message(self, message: AWSEventMessage):
        """
        Delete a message from the SQS queue.

        Args:
            message (AWSEventMessage): AWSEventMessage object which contains event_name and
            receipt_handle associated with the message
        """
        try:
            queue: AWSQueue = self.event_queue_mapper.get(message.event_name)
            self.aws_utility.delete_message_from_queue(queue, message.receipt_handle)
        except ClientError as e:
            logger.error(f"Failed to delete message from SQS: {e}")

    def get_queued_count(self, event_name):
        queue: AWSQueue = self.event_queue_mapper.get(event_name)
        return self.aws_utility.get_queue_count(queue)
