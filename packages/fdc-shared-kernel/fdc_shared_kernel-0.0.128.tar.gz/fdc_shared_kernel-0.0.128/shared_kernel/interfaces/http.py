from abc import ABC, abstractmethod
from requests import Response


class HttpApiClient(ABC):
    """
    An abstract base class for an HTTP API client that defines the interface for various HTTP methods.
    Subclasses must implement these methods to interact with APIs.

    Methods
    -------
    get(url: str, params: dict = None, headers: dict = None) -> dict:
        Sends a GET request to the specified URL.

    post(url: str, data: dict = None, json: dict = None, headers: dict = None) -> dict:
        Sends a POST request to the specified URL with optional data or JSON payload.

    put(url: str, data: dict = None, json: dict = None, headers: dict = None) -> dict:
        Sends a PUT request to the specified URL with optional data or JSON payload.

    delete(url: str, headers: dict = None) -> dict:
        Sends a DELETE request to the specified URL.

    patch(url: str, data: dict = None, json: dict = None, headers: dict = None) -> dict:
        Sends a PATCH request to the specified URL with optional data or JSON payload.

    head(url: str, headers: dict = None) -> dict:
        Sends a HEAD request to the specified URL.

    upload_file(url: str, file_path: str, filename: str, headers: dict = None) -> dict:
        Uploads a file to the specified URL.

    download_file(url: str, save_path: str, headers: dict = None) -> None:
        Downloads a file from the specified URL and saves it to the given path.
    """

    @abstractmethod
    def get(self, url: str, params: dict = None, headers: dict = None) -> Response:
        """
        Sends a GET request to the specified URL.

        Parameters:
        - url (str): The URL to send the GET request to.
        - params (dict, optional): URL parameters to include in the request.
        - headers (dict, optional): HTTP headers to include in the request.

        Returns:
        - Response: Http response object
        """
        pass

    @abstractmethod
    def post(self, url: str, data: dict = None, json: dict = None, headers: dict = None) -> Response:
        """
        Sends a POST request to the specified URL with optional data or JSON payload.

        Parameters:
        - url (str): The URL to send the POST request to.
        - data (dict, optional): The form data to send in the body of the request.
        - json (dict, optional): A JSON object to send in the body of the request.
        - headers (dict, optional): HTTP headers to include in the request.

        Returns:
        - Response: Http response object
        """
        pass

    @abstractmethod
    def put(self, url: str, data: dict = None, json: dict = None, headers: dict = None) -> Response:
        """
        Sends a PUT request to the specified URL with optional data or JSON payload.

        Parameters:
        - url (str): The URL to send the PUT request to.
        - data (dict, optional): The form data to send in the body of the request.
        - json (dict, optional): A JSON object to send in the body of the request.
        - headers (dict, optional): HTTP headers to include in the request.

        Returns:
        - Response: Http response object
        """
        pass

    @abstractmethod
    def delete(self, url: str, headers: dict = None) -> Response:
        """
        Sends a DELETE request to the specified URL.

        Parameters:
        - url (str): The URL to send the DELETE request to.
        - headers (dict, optional): HTTP headers to include in the request.

        Returns:
        - Response: Http response object
        """
        pass

    @abstractmethod
    def patch(self, url: str, data: dict = None, json: dict = None, headers: dict = None) -> Response:
        """
        Sends a PATCH request to the specified URL with optional data or JSON payload.

        Parameters:
        - url (str): The URL to send the PATCH request to.
        - data (dict, optional): The form data to send in the body of the request.
        - json (dict, optional): A JSON object to send in the body of the request.
        - headers (dict, optional): HTTP headers to include in the request.

        Returns:
        - Response: Http response object
        """
        pass

    @abstractmethod
    def head(self, url: str, headers: dict = None) -> Response:
        """
        Sends a HEAD request to the specified URL.

        Parameters:
        - url (str): The URL to send the HEAD request to.
        - headers (dict, optional): HTTP headers to include in the request.

        Returns:
        - Response: Http response object
        """
        pass

    @abstractmethod
    def upload_file(self, url: str, file_path: str, filename: str, headers: dict = None) -> Response:
        """
        Uploads a file to the specified URL.

        Parameters:
        - url (str): The URL to send the file to.
        - file_path (str): The local path of the file to be uploaded.
        - filename (str): The name of the file to be uploaded.
        - headers (dict, optional): HTTP headers to include in the request.

        Returns:
        - Response: Http response object
        """
        pass

    @abstractmethod
    def download_file(self, url: str, save_path: str, headers: dict = None) -> None:
        """
        Downloads a file from the specified URL and saves it to the given path.

        Parameters:
        - url (str): The URL to download the file from.
        - save_path (str): The local path where the file should be saved.
        - headers (dict, optional): HTTP headers to include in the request.

        Returns:
        - None
        """
        pass
