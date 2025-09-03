from dataclasses import dataclass, field
from datetime import datetime, timedelta
import json
import uuid
from shared_kernel.messaging.utils.event_messages import AzureEventMessage, EventMessage, PublishEventMessage
from shared_kernel.config import Config
from shared_kernel.logger import Logger
from azure.identity import DefaultAzureCredential
from azure.servicebus.management import ServiceBusAdministrationClient
from azure.core.exceptions import ResourceNotFoundError
from azure.mgmt.eventgrid import EventGridManagementClient
from azure.mgmt.servicebus import ServiceBusManagementClient
from azure.mgmt.eventgrid.models import EventSubscription, ServiceBusQueueEventSubscriptionDestination
from azure.servicebus import ServiceBusClient, AutoLockRenewer, ServiceBusMessage
from azure.eventgrid import EventGridPublisherClient
from azure.core.credentials import AzureKeyCredential

config = Config()
logger = Logger(config.get("APP_NAME"))


@dataclass
class AzureUtility:
    service_identifier: str = config.get("APP_IDENTIFIER","")
    azure_service_bus: str = config.get("AZURE_SERVICE_BUS","")
    azure_service_bus_namespace: str = config.get("AZURE_SERVICE_BUS_NAMESPACE","")
    topic_name: str = config.get("AZURE_SERVICE_BUS_TOPIC_NAME","")
    app_identifier: str = config.get("APP_IDENTIFIER","")
    resource_group: str = config.get("AZURE_RESOURCE_GROUP","")
    subscription_id: str = config.get("AZURE_SUBSCRIPTION_ID","")
    topic_key: str = config.get("TOPIC_KEY","")
    topic_endpoint: str = config.get("TOPIC_ENDPOINT","")
    
    # These are initialized after dataclass fields
    credential: DefaultAzureCredential = field(init=False)
    admin_client: ServiceBusAdministrationClient = field(init=False)
    event_grid_client: EventGridManagementClient = field(init=False)
    service_bus_mgmt_client: ServiceBusManagementClient = field(init=False)
    auto_renewer: AutoLockRenewer = AutoLockRenewer()
    def __post_init__(self):
        # Init credential and clients after the basic config values are loaded
        self.credential = DefaultAzureCredential()
        self.admin_client = ServiceBusAdministrationClient(
            self.azure_service_bus, self.credential
        )
        self.event_grid_client = EventGridManagementClient(
            self.credential, self.subscription_id
        )
        self.service_bus_mgmt_client = ServiceBusManagementClient(
            self.credential, self.subscription_id
        )

    def check_queue_exist(self, queue_name: str) -> bool:
        """Check if queue exists in the specified resource group"""
        try:
            namespace_name = config.get("AZURE_SERVICE_BUS_NAMESPACE")
            
            # Check using management client (resource group aware)
            queue = self.service_bus_mgmt_client.queues.get(
                self.resource_group,
                namespace_name,
                queue_name
            )
            logger.info(f"Queue '{queue_name}' exists in resource group '{self.resource_group}'.")
            return True
            
        except ResourceNotFoundError:
            logger.info(f"Queue '{queue_name}' does not exist in resource group '{self.resource_group}'.")
            return False
        except Exception as e:
            logger.error(f"Failed to check queue '{queue_name}' in resource group '{self.resource_group}': {e}")
            raise

    def create_queue(self, queue_name: str) -> None:
        """Create queue in the specified resource group"""
        try:
            namespace_name = config.get("AZURE_SERVICE_BUS_NAMESPACE")
            
            # Create queue using management client (resource group aware)
            self.service_bus_mgmt_client.queues.create_or_update(
                self.resource_group,
                namespace_name,
                queue_name,
                parameters={
                    "max_size_in_megabytes": 1024,
                    "lock_duration": "PT5M"
                }
            )
            logger.info(f"Queue '{queue_name}' created in resource group '{self.resource_group}'.")
            
        except Exception as e:
            logger.error(f"Failed to create queue '{queue_name}' in resource group '{self.resource_group}': {e}")
            raise

    def create_update_subscription(self, subscription_name: str, event_type: str, queue_name: str) -> None:
        """
        Create an Event Grid subscription that routes events to a Service Bus queue
        
        Args:
            subscription_name: Name for the Event Grid subscription
            event_type: The event type to filter on (e.g., "MyCustomEvent")
            queue_name: Name of the Service Bus queue to route events to
        """
        try:
            # Check if subscription already exists
            try:
                existing_sub = self.event_grid_client.event_subscriptions.get(
                    scope=self._get_event_grid_topic_scope(),
                    event_subscription_name=subscription_name
                )
                
                # Validate if existing subscription matches desired configuration
                if self._subscription_matches_config(existing_sub, event_type, queue_name):
                    logger.info(f"Event Grid subscription '{subscription_name}' already exists with correct configuration.")
                    return
                else:
                    logger.info(f"Event Grid subscription '{subscription_name}' exists but configuration differs. Updating...")
                    # Continue to create/update with correct configuration
                    
            except ResourceNotFoundError:
                logger.info(f"Event Grid subscription '{subscription_name}' does not exist. Creating...")
                
            # Create Service Bus queue destination
            destination = ServiceBusQueueEventSubscriptionDestination(
                resource_id=self._get_service_bus_queue_resource_id(queue_name)
            )

            # Create event subscription with filter
            event_subscription = EventSubscription(
                destination=destination,
                filter=self._create_event_filter(event_type)
            )

            # Create the Event Grid subscription
            self.event_grid_client.event_subscriptions.begin_create_or_update(
                scope=self._get_event_grid_topic_scope(),
                event_subscription_name=subscription_name,
                event_subscription_info=event_subscription
            )

            logger.info(
                f"Event Grid subscription '{subscription_name}' created successfully. "
                f"Events of type '{event_type}' will be routed to queue '{queue_name}'."
            )

        except Exception as e:
            logger.error(f"Failed to create Event Grid subscription '{subscription_name}': {e}")
            raise
    
    def receive_event(self, queue_name: str) -> dict:
        """Receive and process an event from the queue."""
        
        service_bus_messaging_client = ServiceBusClient.from_connection_string(
            config.get("AZURE_SERVICE_BUS_CONNECTION_STRING"),
        )

        with service_bus_messaging_client:
            receiver = service_bus_messaging_client.get_queue_receiver(queue_name=queue_name)
            sender = service_bus_messaging_client.get_queue_sender(queue_name=queue_name)
            
            received_messages = receiver.receive_messages(max_message_count=1, max_wait_time=20)
            
            if received_messages:
                msg = received_messages[0]
                self.auto_renewer.register(receiver, msg, max_lock_renewal_duration=timedelta(seconds=10))
                
                # Convert the message to a string representation FIRST
                try:
                    # Read the entire message content into a string
                    if hasattr(msg, 'body') and hasattr(msg.body, '__iter__'):
                        # For generator/iterable bodies
                        body_chunks = []
                        for chunk in msg.body:
                            if isinstance(chunk, bytes):
                                body_chunks.append(chunk.decode('utf-8'))
                            else:
                                body_chunks.append(str(chunk))
                        body_content = ''.join(body_chunks)
                    else:
                        # For regular bodies
                        if isinstance(msg.body, bytes):
                            body_content = msg.body.decode('utf-8')
                        else:
                            body_content = str(msg.body)
                except Exception as e:
                    logger.error(f"Error reading message body: {e}")
                    body_content = ""
                
                # Schedule the message for later
                hide_duration_minutes = int(config.get("QUEUE_MESSAGE_LOCK_TIME_SPAN_MINUTES"))
                scheduled_time = datetime.utcnow() + timedelta(minutes=hide_duration_minutes)
                
                # Create new message with the string content
                scheduled_msg = ServiceBusMessage(
                    body=body_content,
                    content_type=msg.content_type,
                    message_id=msg.message_id,
                    session_id=msg.session_id,
                    application_properties=msg.application_properties,
                    time_to_live=msg.time_to_live
                )
                
                # Schedule and complete
                sequence_number = sender.schedule_messages(scheduled_msg, scheduled_time)
                receiver.complete_message(msg)
                
                logger.info(f"Message {msg.message_id} rescheduled for {scheduled_time}")
                
                # Parse and return
                try:
                    event_msg_obj = AzureEventMessage(json.loads(body_content))
                    event_msg_obj.event_meta.scheduler_id = sequence_number
                    return event_msg_obj
                except json.JSONDecodeError:
                    logger.warning(f"Message {msg.message_id} is not valid JSON")
                    return None
        
        return None

    def publish_message(self, event_name: str, event_payload: dict) -> bool:
        """
        Publish a message to the Service Bus topic.

        Args:
            event_name (str): Logical name of the event (used in metadata).
            event_payload (dict): Actual data to send.

        Returns:
            bool: True if sent successfully, False otherwise.
        """
        try:
            publish_message = PublishEventMessage(event_payload)
            json_payload = publish_message.to_json()

            credential = AzureKeyCredential(self.topic_key)
            client = EventGridPublisherClient(self.topic_endpoint, credential)

            event = {
                "id": publish_message.event_dict.get("event_meta").get("job_id"),
                "eventType": event_name,
                "subject": event_name,
                "eventTime": datetime.utcnow().isoformat(),
                "data": json_payload,
                "dataVersion": "1.0"
            }
            client.send([event])
            logger.info(f"Published event '{event_name}' with payload: {event_payload}")
            return True, publish_message.event_dict
        except Exception as e:
            logger.error(f"Error while publishing message: {event}")
            raise
    
    def delete_scheduled_msg(self, queue_name: str, sequence_number: int):
        """
        Remove a specific scheduled message from the queue using its sequence number.
        
        Args:
            queue_name: Name of the queue
            sequence_number: Sequence number of the scheduled message to remove
        
        Returns:
            bool: True if successfully removed, False otherwise
        """
        service_bus_messaging_client = ServiceBusClient.from_connection_string(
            config.get("AZURE_SERVICE_BUS_CONNECTION_STRING"),
        )
        
        try:
            with service_bus_messaging_client:
                sender = service_bus_messaging_client.get_queue_sender(queue_name=queue_name.lower())
                
                # Cancel the scheduled message using its sequence number
                sender.cancel_scheduled_messages(sequence_number)
                
                logger.info(f"Successfully removed scheduled message with sequence number: {sequence_number} from queue: {queue_name}")
                return True
                
        except Exception as e:
            logger.error(f"Error removing scheduled message with sequence number {sequence_number}: {e}")
            return False

    def _create_event_filter(self, event_type: str) -> dict:
        """Create event filter for the specific event type"""
        return {
            "included_event_types": [event_type],
        }

    def _get_event_grid_topic_scope(self) -> str:
        """Get the resource ID scope for the Event Grid topic"""
        return (
            f"/subscriptions/{self.subscription_id}/resourceGroups/{self.resource_group}/"
            f"providers/Microsoft.EventGrid/topics/{self.topic_name}"
        )

    def _get_service_bus_queue_resource_id(self, queue_name: str) -> str:
        """Get the resource ID for the Service Bus queue"""
        return (
            f"/subscriptions/{self.subscription_id}/resourceGroups/{self.resource_group}/"
            f"providers/Microsoft.ServiceBus/namespaces/{self.azure_service_bus_namespace}/"
            f"queues/{queue_name}"
        )

    def _subscription_matches_config(self, existing_subscription: EventSubscription, 
                               desired_event_type: str, desired_queue_name: str) -> bool:
        """
        Check if existing subscription matches the desired configuration
        
        Returns:
            bool: True if configuration matches, False otherwise
        """
        try:
            # Check destination (Service Bus queue)
            if (not hasattr(existing_subscription.destination, 'resource_id') or 
                existing_subscription.destination.resource_id != self._get_service_bus_queue_resource_id(desired_queue_name)):
                logger.info(f"Queue destination differs. Current: {getattr(existing_subscription.destination, 'resource_id', 'None')}, Desired: {self._get_service_bus_queue_resource_id(desired_queue_name)}")
                return False

            # Check event type filter
            if (not hasattr(existing_subscription.filter, 'included_event_types') or 
                not existing_subscription.filter.included_event_types or 
                existing_subscription.filter.included_event_types[0] != desired_event_type):
                logger.info(f"Event type filter differs. Current: {getattr(existing_subscription.filter, 'included_event_types', [])}, Desired: [{desired_event_type}]")
                return False

            # Check if there are multiple event types (we want only one)
            if (hasattr(existing_subscription.filter, 'included_event_types') and 
                len(existing_subscription.filter.included_event_types) > 1):
                logger.info("Multiple event types detected, needs update to single event type.")
                return False

            return True

        except Exception as e:
            logger.warning(f"Error validating existing subscription configuration: {e}")
            return False
