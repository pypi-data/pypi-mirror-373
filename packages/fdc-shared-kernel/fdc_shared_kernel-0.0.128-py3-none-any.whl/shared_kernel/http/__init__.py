from shared_kernel.http.httpx_http_client import HttpxHttpClient
from shared_kernel.http.request_http_client import RequestsHttpClient
from shared_kernel.interfaces.http import HttpApiClient


class HttpClient:
    @staticmethod
    def create_client(client_type: str = "requests") -> HttpApiClient:
        if client_type == 'requests':
            return RequestsHttpClient()
        elif client_type == 'httpx':
            return HttpxHttpClient()
        else:
            raise ValueError(f"Unknown client type: {client_type}")
