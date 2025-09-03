from abc import ABC, abstractmethod
from typing import Any, Callable


class DataBus(ABC):
    """
    An abstract base class for a DataBus interface that handles both asynchronous and synchronous messaging.

    Methods
    -------
    __init__() -> None:
        Initializes the DataBus instance.

    make_connection():
        Connects to the DataBus server.

    close_connection():
        Closes the connection to the DataBus server.

    publish_event(event_name: str, event_payload: dict):
        Publishes an asynchronous message to a DataBus event_name.

    request_event(event_name: str, event_payload: dict) -> Any:
        Sends a synchronous request/message to a DataBus event_name and receives a response.

    subscribe_sync_event(event_name: str, callback: Callable[[Any], None]):
        Subscribes to a DataBus event_name and processes messages synchronously.

    subscribe_async_event(event_name: str, callback: Callable[[Any], None]):
        Subscribes to a DataBus event_name and processes messages asynchronously.

    delete_message(message_id: str):
        Deletes a message from the DataBus.
    """

    @abstractmethod
    def __init__(self) -> None:
        """
        Initializes the DataBus instance.
        """
        pass

    @abstractmethod
    def make_connection(self):
        """
        Connect to the DataBus server.
        """
        pass

    @abstractmethod
    def close_connection(self):
        """
        Close the connection to the DataBus server.
        """
        pass

    @abstractmethod
    def publish_event(self, event_name: str, event_payload: dict):
        """
        Publish an asynchronous message to a DataBus event_name.

        Parameters:
        - event_name (str): The event name to publish the message to.
        - event_payload (dict): The message to be published.
        """
        pass

    @abstractmethod
    def request_event(self, event_name: str, event_payload: dict) -> Any:
        """
        Send a synchronous request/message to a DataBus event name and receive a response.

        Parameters:
        - event_name (str): The event name to send the message to.
        - event_payload (dict): The message to be sent.

        Returns:
        - Any: The response received from the server.
        """
        pass

    @abstractmethod
    def subscribe_sync_event(self, event_name: str, callback: Callable[[Any], None]):
        """
        Subscribe to a DataBus event name and process messages synchronously.

        Parameters:
        - event_name (str): The event name to subscribe to.
        - callback (Callable[[Any], None]): A callback function to handle received messages.
        """
        pass

    @abstractmethod
    def subscribe_async_event(self, event_name: str, callback: Callable[[Any], None]):
        """
        Subscribe to a DataBus event name and process messages asynchronously.

        Parameters:
        - event_name (str): The event name to subscribe to.
        - callback (Callable[[Any], None]): A callback function to handle received messages.
        """
        pass

    @abstractmethod
    def delete_message(self, message: object):
        """
        Delete a message from the DataBus.

        Parameters:
        - message (object): message object which contains the ID or receipt handle of the message to delete.
        """
        pass
