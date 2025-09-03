from shared_kernel.enums.status_tracker import TaskStatus
from shared_kernel.messaging.utils.event_messages import AWSEventMessage, EventMessage
from shared_kernel.messaging.utils.azure_utility import AzureUtility
from shared_kernel.interfaces.databus import DataBus
from typing import Any, Callable, Dict
from shared_kernel.config import Config
from shared_kernel.logger import Logger


app_config = Config()
logger = Logger(app_config.get("APP_NAME"))

class AzureDataBus(DataBus):
    """
    A Service bus and queue interface class to handle event-driven communication.
    """

    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(AzureDataBus, cls).__new__(cls)
        return cls._instance

    def __init__(self, config: Dict = None):
        """
        Initialize the AzureDataBus and start listening to multiple Service bus queues.

        Args:
            config (Dict): A dictionary containing the Service bus and queue configuration.
        """
        ## Importing here to avoid circular import error since status_tracker depends on DataBusFactory
        from shared_kernel.status_tracker.status_tracker import StatusTracker

        if not hasattr(self, "initialized"):  # Prevent reinitialization
            super().__init__()
            self.azure_utility = AzureUtility()
            self.app_identifier: str = app_config.get("APP_IDENTIFIER")
            self.status_tracker = StatusTracker()
            self.initialized = True

    def make_connection(self):
        pass

    def close_connection(self):
        pass

    def publish_event(self, event_name: str, event_payload: dict):
        """
        Publish an event to the EventBridge and check if it was successful.

        Args:
            event_name (str): The name of the event to publish.
            event_payload (dict): The payload of the event.

        Returns:
            bool: True if the event was published successfully, False otherwise.
        """
        is_success, validated_event_dict = self.azure_utility.publish_message(
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

    def request_event(self, event_name: str, event_payload: dict) -> Any:
        pass

    def subscribe_sync_event(self, event_name: str, callback: Callable[[Any], None]):
        pass
    
    def subscribe_async_event(self, event_name: str, callback: Callable[[Any], None]):
        """
        This function subscribes a callback function to an asynchronous event specified by its name.
        
        :param event_name: The `event_name` parameter is a string that represents the name of the event
        to which you want to subscribe. This could be any unique identifier for the event that you are
        interested in listening to
        :type event_name: str
        :param callback: The `callback` parameter is a function that will be called when the specified
        `event_name` occurs. It takes one argument of type `Any` and does not return any value (`None`).
        This function is responsible for handling the event when it is triggered
        :type callback: Callable[[Any], None]
        """
        actual_queue_name = f"{self.app_identifier}-{event_name}"
        # check the queue exists or not. if not then create the queue.
        if not self.azure_utility.check_queue_exist(actual_queue_name):
            logger.info(f"Queue '{actual_queue_name}' does not exist. Creating...")
            self.azure_utility.create_queue(actual_queue_name)
        
        # create or update the subscription
        subscription_name = f"SUB-{self.app_identifier}-{event_name}"
        self.azure_utility.create_update_subscription(subscription_name, event_name, actual_queue_name)
        
    def delete_message(self, message: AWSEventMessage):
        """
        Remove a specific scheduled message from the queue using its sequence number.
        
        Args:
            queue_name: Name of the queue
            sequence_number: Sequence number of the scheduled message to remove
        
        Returns:
            bool: True if successfully removed, False otherwise
        """
        event_name = message.event_name
        sequence_id = message.event_meta.scheduler_id
        actual_queue_name = f"{self.app_identifier}-{event_name}"
        self.azure_utility.delete_scheduled_msg(actual_queue_name, sequence_id)

    def get_message(self, event_name: str):
        actual_queue_name = f"{self.app_identifier}-{event_name}"
        return self.azure_utility.receive_event(actual_queue_name)