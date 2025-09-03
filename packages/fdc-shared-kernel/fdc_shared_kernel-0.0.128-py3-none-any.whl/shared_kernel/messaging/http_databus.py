import asyncio
import logging
from typing import Callable, Any, Dict
from shared_kernel.exceptions.http_exceptions import BadRequest, InternalServerError, NotFound
from shared_kernel.interfaces import DataBus
from concurrent.futures import ThreadPoolExecutor
from shared_kernel.http import HttpClient

logging.getLogger().setLevel(logging.INFO)


class HTTPDataBus(DataBus):
    """
    A class to handle HTTP-based event operations, including EventBridge and SQS.
    """

    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(HTTPDataBus, cls).__new__(cls)
        return cls._instance

    def __init__(self, config: Dict = None):
        """
        Initialize the HTTPDataBus.

        Args:
            config (Dict): A dictionary containing the HTTP client configuration.
        """
        if not hasattr(self, "initialized"):  # Prevent reinitialization
            super().__init__()
            self.http_client = HttpClient().create_client()
            self.initialized = True

    async def publish_event(self, event_name: str, event_payload: dict):
        """
        Send an event payload to multiple HTTP endpoints and return the responses.

        Args:
            event_name (str): The URLs to invoke the HTTP endpoints.
            event_payload (dict): The payload containing all necessary information for the HTTP requests.

        Returns:
            None
        """
        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(self.http_client.post, url=url, json=event_payload) for url in event_name]
            for future in futures:
                future.result()

    def subscribe_async_event(self, event_name: str, callback: Callable[[Any], None]):
        """
        Subscribe to asynchronous events and invoke the provided callback upon receiving an event.

        Args:
            event_name (str): The event name or URL to subscribe to.
            callback (Callable[[Any], None]): The callback function to invoke with the event data.

        Returns:
            asyncio.Task: The task handling the asynchronous event subscription.
        """
        return asyncio.create_task(callback(event_name))

    def request_event(self, event_name: str, event_payload: dict) -> Any:
        """
        Send an event payload to an HTTP endpoint and return the response.

        Args:
            event_name (str): The URL to invoke the HTTP endpoint.
            event_payload (dict): The payload containing all necessary information for the HTTP request.

        Returns:
            Any: The response from the HTTP endpoint.
        """
        response = self.http_client.post(url=event_name, json=event_payload)

        # handling success cases
        if response.status_code in [200, 201, 204]:
            return response.json()

        # default error handling
        response_data: Dict[str, Any] = response.json()
        error_message: str = response_data.get('message', 'An error occurred')
        # handling common HTTP errors
        if response.status_code == 400:
            raise BadRequest(error_message)
        elif response.status_code == 404:
            raise NotFound(error_message)
        elif response.status_code == 500:
            raise InternalServerError(error_message)

    def subscribe_sync_event(self, event_name: str, callback: Callable[[Any], None]):
        """
        Subscribe to synchronous events and invoke the provided callback upon receiving an event.

        Args:
            event_name (str): The event name or URL to subscribe to.
            callback (Callable[[Any], None]): The callback function to invoke with the event data.

        Returns:
            Any: The result of the callback function.
        """
        return callback(event_name)

    def delete_message(self, receipt_handle: str):
        """
        Placeholder method for deleting a message.

        Args:
            receipt_handle (str): The receipt handle of the message to be deleted.

        Returns:
            None
        """
        pass

    def make_connection(self, receipt_handle: str):
        """
        Placeholder method for establishing a connection.

        Args:
            receipt_handle (str): The receipt handle related to the connection.

        Returns:
            None
        """
        pass

    def close_connection(self, receipt_handle: str):
        """
        Placeholder method for closing a connection.

        Args:
            receipt_handle (str): The receipt handle related to the connection.

        Returns:
            None
        """
        pass
