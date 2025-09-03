import json
from nats.aio.client import Client as NATS
from nats.js.api import StreamConfig, ConsumerConfig, DeliverPolicy, AckPolicy
from typing import Callable, Any, Dict, List, Optional, Union
from nats.js.errors import (
    BadRequestError as JetstreamBadRequestError,
    NotFoundError as JetstreamNotFoundError,
)
from nats.errors import TimeoutError as NATSTimeoutError
from nats.js.client import JetStreamContext
from nats.aio.msg import Msg

from shared_kernel.config import Config
from shared_kernel.interfaces.databus import DataBus
from shared_kernel.logger import Logger

app_config = Config()
logger = Logger(app_config.get("APP_NAME"))


class NATSDataBus(DataBus):
    """
    A NATS interface class to handle both standard NATS and JetStream operations.
    """

    def __init__(self, config: Dict = None):
        """
        Initialize the NATSDataBus.

        Args:
            config (Dict): A dictionary containing the NATS configuration.
        """
        super().__init__()
        self.nats_client = NATS()
        self.servers = config.get("servers")
        self.user = config.get("user")
        self.password = config.get("password")
        self.connected = False
        self.nats_jet_stream_context = None  # JetStream context
        self.max_delivery_count = app_config.get("MAX_DELIVERY_COUNT")

    async def _connection_error_callback(self, e: Exception) -> None:
        """
        Callback function for connection errors.

        Args:
            e (Exception): The exception that occurred during connection.
        """
        logger.error(f"Unable to connect to NATS server - {str(e)}")

    async def _create_consumer(self, consumer_name: str, subject: str):
        try:
            # check if the consumer already exists
            try:
                await self.nats_jet_stream_context.consumer_info(
                    app_config.get("NATS_STREAM_NAME"), consumer_name
                )
                logger.info(f"Consumer {consumer_name} already exists")
                return
            except JetstreamNotFoundError as e:
                # case where the consumer doesn't exists (error code 10014)
                if e.err_code == 10014:
                    consumer_config = ConsumerConfig(
                        durable_name=consumer_name,
                        ack_policy=AckPolicy.EXPLICIT,
                        deliver_policy=DeliverPolicy.ALL,
                        filter_subject=subject,
                        ack_wait=3600,
                        max_ack_pending=5,
                    )
                    await self.nats_jet_stream_context.add_consumer(
                        stream=app_config.get("NATS_STREAM_NAME"),
                        config=consumer_config,
                    )
                    logger.info(f"Consumer {consumer_name} created")
        except Exception as e:
            logger.error(f"Error creating consumer: {e}")
            raise

    async def _create_dlq_stream(self) -> None:
        """
        Create a Dead Letter Queue stream if it doesn't exist.

        Raises:
            Exception: If an error occurs while creating the DLQ stream.
        """
        try:
            dlq_config = StreamConfig(
                name=app_config.get("NATS_DLQ_STREAM_NAME"),
                subjects=[f"{app_config.get('NATS_DLQ_STREAM_NAME')}.>"],
                max_age=86400 * 7,  # Keep messages for 7 days
            )
            await self.nats_jet_stream_context.add_stream(dlq_config)
            logger.info(
                f"DLQ Stream [{app_config.get('NATS_DLQ_STREAM_NAME')}] created"
            )
        except JetstreamBadRequestError as e:
            if e.err_code == 10058:  # Stream already exists
                logger.info(
                    f"DLQ Stream [{app_config.get('NATS_DLQ_STREAM_NAME')}] already exists"
                )
            else:
                raise

    async def _create_update_stream(self, topic: Optional[str]):
        """
        Create or update a JetStream stream.
        The function attempts to create a JetStream stream with the provided topic.
        If a stream with the same name already exists but does not include the topic,
        the stream is updated by adding the new topic.

        Args:
            topic (Optional[str]): The topic to add to the stream.

        Raises:
            RuntimeError: If unable to create or update the stream.
        """
        try:
            # ensure that the topic is a list (empty if None)
            topic = [] if topic is None else [topic]
            stream_config = StreamConfig(
                name=app_config.get("NATS_STREAM_NAME"),
                subjects=topic,
                max_age=600,
            )
            await self.nats_jet_stream_context.add_stream(stream_config)
            logger.info(f"Stream [{app_config.get('NATS_STREAM_NAME')}] created")
        except JetstreamBadRequestError as e:
            # case where the stream already exists (error code 10058)
            if e.err_code == 10058:
                logger.info(f"Stream [{app_config.get('NATS_STREAM_NAME')}] already exists with other topics")
                # retrieve the existing stream's information
                stream_info = await self.nats_jet_stream_context.stream_info(
                    app_config.get("NATS_STREAM_NAME")
                )
                # get the current list of topics associated with the stream
                topics: list = stream_info.config.subjects
                # if the new topic is not already in the stream's subjects, add it
                if topic[0] not in topics:
                    topics.append(topic[0])
                    # update the stream configuration to include the new topic
                    stream_config = StreamConfig(
                        name=app_config.get("NATS_STREAM_NAME"),
                        subjects=topics,
                        max_age=600,
                    )
                    # apply the updated configuration to the existing stream
                    await self.nats_jet_stream_context.update_stream(stream_config)
                    logger.info(f"Added topic: [{topic[0]}] to the stream [{app_config.get('NATS_STREAM_NAME')}]")
        except Exception as e:
            logger.error(f"Error creating/updating stream: {e}")
            raise e

    async def _move_to_dlq(
        self, original_subject: str, message: Dict[str, Any]
    ) -> None:
        """
        Move a message to the Dead Letter Queue.

        Args:
            original_subject (str): The original subject of the message.
            message (Dict[str, Any]): The message to be moved to DLQ.
        """
        dlq_subject = f"{app_config.get('NATS_DLQ_STREAM_NAME')}.{original_subject}"
        await self.nats_jet_stream_context.publish(dlq_subject, json.dumps(message).encode())
        logger.info(f"Moved message to DLQ: {dlq_subject}")

    async def _register_topic_and_consumer(
        self, consumer_name: str, event_name: str
    ) -> None:
        """
        Register a topic and create a consumer for it.

        Args:
            consumer_name (str): The name of the consumer to create.
            event_name (str): The event name (subject) to register.
        """
        await self._create_update_stream(topic=event_name)
        await self._create_consumer(consumer_name=consumer_name, subject=event_name)

    async def _fetch_messages(
        self, pull_subscription_object: JetStreamContext.PullSubscription
    ) -> Msg:
        # fetch only one message
        msgs: List[Msg] = await pull_subscription_object.fetch(batch=1, timeout=3600)
        # get the message object from the list
        message_object = msgs.pop()
        # process the message
        return message_object

    async def make_connection(self):
        """
        Connect to the NATS server.
        """
        if not self.nats_client.is_connected:
            await self.nats_client.connect(
                servers=self.servers,
                user=self.user,
                password=self.password,
                error_cb=self._connection_error_callback,
            )
            self.nats_jet_stream_context: JetStreamContext = self.nats_client.jetstream(timeout=10)
            self.connected = True

    async def close_connection(self):
        """
        Close the connection to the NATS server.
        """
        if self.connected:
            try:
                await self.nats_client.close()
                self.connected = False
            except Exception as e:
                raise e

    async def publish_event(
        self, event_name: str, event_payload: dict
    ) -> Union[bool, Exception]:
        """
        Publish a message to a JetStream subject.

        Args:
            event_name (str): The subject to publish the message to.
            event_payload (dict): The message to be published.

        Returns:
            bool: True if the event was published successfully.
        """
        # acknowledgement from the jetstream after successful publish
        ack = await self.nats_jet_stream_context.publish(
            event_name, json.dumps(event_payload).encode("utf-8")
        )
        logger.info(
            f"""Published event [{event_payload.get('event_name')}] to subject [{event_name}], ack: {ack}"""
        )
        return ack

    async def request_event(
        self, event_name: str, event_payload: dict, timeout: float = 10.0
    ) -> Union[dict, Exception]:
        """
        Send a request and wait for a response.

        Args:
            event_name (str): The subject to publish the message to.
            event_payload (dict): The message to be published.
            timeout (float): The timeout for the request.

        Returns:
            dict: The response message.
        """
        response = await self.nats_client.request(
            event_name, json.dumps(event_payload).encode("utf-8"), timeout=timeout
        )
        return json.loads(response.data.decode("utf-8"))

    async def subscribe_async_event(
        self, event_name: str, callback: Callable[[Any], None]
    ):
        """
        Subscribe to a JetStream subject with a durable consumer and process messages asynchronously.

        Args:
            event_name (str): The subject to subscribe to.
            callback (Callable[[Any], None]): A callback function to handle received messages.

        Raises:
            RuntimeError: If unable to subscribe to the event.
        """
        # consumer_name is a persistent identifier for a consumer that ensures message
        # consumption state is retained even if the client disconnects or the server restarts.
        consumer_name = app_config.get("APP_NAME") + f"-{event_name}"

        await self._register_topic_and_consumer(
            consumer_name=consumer_name, event_name=event_name
        )

        pull_subscription_object: JetStreamContext.PullSubscription = (
            await self.nats_jet_stream_context.pull_subscribe(subject=event_name, durable=consumer_name)
        )
        logger.info(f"""Subscribed to async event on subject [{event_name}]""")
        while True:
            try:
                message_object: Msg = await self._fetch_messages(
                    pull_subscription_object
                )
                # process the message
                event_data: dict = json.loads(message_object.data.decode())
                has_job_failed = False
                try:
                    await callback(event_data)
                    # acknowledge the message after processing and finishing the job
                    await message_object.ack()
                    logger.info(f"Acknowledged job: {event_data}")
                except Exception as e:
                    logger.error(
                        f"Invoking callback during execution of [{event_name}] failed due to {str(e)}"
                    )
                    has_job_failed = True

                if (
                    has_job_failed
                    and message_object.metadata.num_delivered == self.max_delivery_count
                ):
                    logger.warning("Moving event to the dead letter topic after max retries")
                    await self._create_dlq_stream()
                    await self._move_to_dlq(event_name, event_data)
                    await message_object.ack()  # acknowledge to remove from original queue

            # TODO - What to do failed jobs ?
            # failed jobs are moved to dead letter topic after max retries for now
            except NATSTimeoutError:
                logger.info("No more messages, will pull again...")

    async def subscribe_sync_event(
        self, event_name: str, callback: Callable[[Any], None]
    ):
        """
        Subscribe to a NATS subject and process the message synchronously.

        Args:
            event_name (str): The subject to subscribe to.
            callback (Callable[[Any], None]): A callback function to handle received messages.
        """
        await self.nats_client.subscribe(event_name, cb=callback)
        logger.info(f"Subscribed to sync event on subject [{event_name}]")

    def delete_message(self, receipt_handle: str):
        pass
