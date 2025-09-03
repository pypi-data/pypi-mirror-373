import httpx
from shared_kernel.interfaces import HttpApiClient


class HttpxHttpClient(HttpApiClient):
    """
    An implementation of the HttpApiClient interface using httpx for asynchronous HTTP requests.
    This class provides methods to interact with HTTP endpoints using common HTTP methods.

    Methods
    -------
    get(url: str, params: dict = None, headers: dict = None) -> dict:
        Sends an asynchronous GET request to the specified URL.

    post(url: str, data: dict = None, json: dict = None, headers: dict = None) -> dict:
        Sends an asynchronous POST request to the specified URL.

    put(url: str, data: dict = None, json: dict = None, headers: dict = None) -> dict:
        Sends an asynchronous PUT request to the specified URL.

    delete(url: str, headers: dict = None) -> dict:
        Sends an asynchronous DELETE request to the specified URL.

    patch(url: str, data: dict = None, json: dict = None, headers: dict = None) -> dict:
        Sends an asynchronous PATCH request to the specified URL.

    head(url: str, headers: dict = None) -> dict:
        Sends an asynchronous HEAD request to the specified URL.

    upload_file(url: str, file_path: str, filename: str, headers: dict = None) -> dict:
        Uploads a file asynchronously to the specified URL.

    download_file(url: str, save_path: str, headers: dict = None) -> None:
        Downloads a file asynchronously from the specified URL and saves it to the given path.
    """

    async def get(self, url: str, params: dict = None, headers: dict = None) -> dict:
        """
        Sends an asynchronous GET request to the specified URL.

        Parameters:
        - url (str): The URL to send the GET request to.
        - params (dict, optional): URL parameters to include in the request.
        - headers (dict, optional): HTTP headers to include in the request.

        Returns:
        - dict: The response from the server as a JSON-decoded dictionary.
        """
        async with httpx.AsyncClient() as client:
            response = await client.get(url, params=params, headers=headers)
        return response.json()

    async def post(
        self, url: str, data: dict = None, json: dict = None, headers: dict = None
    ) -> dict:
        """
        Sends an asynchronous POST request to the specified URL.

        Parameters:
        - url (str): The URL to send the POST request to.
        - data (dict, optional): The form data to send in the body of the request.
        - json (dict, optional): A JSON object to send in the body of the request.
        - headers (dict, optional): HTTP headers to include in the request.

        Returns:
        - dict: The response from the server as a JSON-decoded dictionary.
        """
        async with httpx.AsyncClient() as client:
            response = await client.post(url, data=data, json=json, headers=headers)
        return response.json()

    async def put(
        self, url: str, data: dict = None, json: dict = None, headers: dict = None
    ) -> dict:
        """
        Sends an asynchronous PUT request to the specified URL.

        Parameters:
        - url (str): The URL to send the PUT request to.
        - data (dict, optional): The form data to send in the body of the request.
        - json (dict, optional): A JSON object to send in the body of the request.
        - headers (dict, optional): HTTP headers to include in the request.

        Returns:
        - dict: The response from the server as a JSON-decoded dictionary.
        """
        async with httpx.AsyncClient() as client:
            response = await client.put(url, data=data, json=json, headers=headers)
        return response.json()

    async def delete(self, url: str, headers: dict = None) -> dict:
        """
        Sends an asynchronous DELETE request to the specified URL.

        Parameters:
        - url (str): The URL to send the DELETE request to.
        - headers (dict, optional): HTTP headers to include in the request.

        Returns:
        - dict: The response from the server as a JSON-decoded dictionary.
        """
        async with httpx.AsyncClient() as client:
            response = await client.delete(url, headers=headers)
        return response.json()

    async def patch(
        self, url: str, data: dict = None, json: dict = None, headers: dict = None
    ) -> dict:
        """
        Sends an asynchronous PATCH request to the specified URL.

        Parameters:
        - url (str): The URL to send the PATCH request to.
        - data (dict, optional): The form data to send in the body of the request.
        - json (dict, optional): A JSON object to send in the body of the request.
        - headers (dict, optional): HTTP headers to include in the request.

        Returns:
        - dict: The response from the server as a JSON-decoded dictionary.
        """
        async with httpx.AsyncClient() as client:
            response = await client.patch(url, data=data, json=json, headers=headers)
        return response.json()

    async def head(self, url: str, headers: dict = None) -> dict:
        """
        Sends an asynchronous HEAD request to the specified URL.

        Parameters:
        - url (str): The URL to send the HEAD request to.
        - headers (dict, optional): HTTP headers to include in the request.

        Returns:
        - dict: The response from the server as a JSON-decoded dictionary.
        """
        async with httpx.AsyncClient() as client:
            response = await client.head(url, headers=headers)
        return response.json()

    async def upload_file(
        self, url: str, file_path: str, filename: str, headers: dict = None
    ) -> dict:
        """
        Uploads a file asynchronously to the specified URL.

        Parameters:
        - url (str): The URL to send the file to.
        - file_path (str): The local path of the file to be uploaded.
        - filename (str): The name of the file to be uploaded.
        - headers (dict, optional): HTTP headers to include in the request.

        Returns:
        - dict: The response from the server as a JSON-decoded dictionary.
        """
        async with httpx.AsyncClient() as client:
            with open(file_path, "rb") as file:
                response = await client.post(
                    url, files={filename: file}, headers=headers
                )
        return response.json()

    async def download_file(
        self, url: str, save_path: str, headers: dict = None
    ) -> None:
        """
        Downloads a file asynchronously from the specified URL and saves it to the given path.

        Parameters:
        - url (str): The URL to download the file from.
        - save_path (str): The local path where the file should be saved.
        - headers (dict, optional): HTTP headers to include in the request.

        Returns:
        - None
        """
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=headers)
            with open(save_path, "wb") as file:
                file.write(await response.aread())
