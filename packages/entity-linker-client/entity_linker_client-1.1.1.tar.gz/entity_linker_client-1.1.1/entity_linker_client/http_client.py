import httpx
from typing import Dict, Any, Optional

class HttpClient:
    """A client for making HTTP requests to the Entity Linker API."""

    def __init__(self, base_url: str):
        """
        Initializes the HttpClient.

        Args:
            base_url: The base URL for the API.
        """
        self.base_url = base_url.rstrip('/')
        self.client = httpx.Client(timeout=120.0)

    def request(self, method: str, endpoint: str, **kwargs) -> Optional[Any]:
        """
        Sends a request to the specified endpoint.

        Args:
            method: The HTTP method to use (e.g., 'GET', 'POST').
            endpoint: The API endpoint to send the request to.
            **kwargs: Additional keyword arguments to pass to the httpx request.

        Returns:
            The JSON response from the API, or None if the response has no content.

        Raises:
            httpx.HTTPStatusError: If the request returns an unsuccessful status code.
            httpx.RequestError: If an error occurs during the request.
        """
        url = f"{self.base_url}{endpoint}"
        try:
            response = self.client.request(method, url, **kwargs)
            response.raise_for_status()
            if response.status_code == 204:
                return None
            return response.json()
        except httpx.HTTPStatusError as e:
            print(f"HTTP error occurred: {e.response.status_code} - {e.response.text}")
            raise
        except httpx.RequestError as e:
            print(f"An error occurred while requesting {e.request.url!r}.")
            raise

    def get(self, endpoint: str, **kwargs) -> Optional[Any]:
        """Sends a GET request."""
        return self.request('GET', endpoint, **kwargs)

    def post(self, endpoint: str, **kwargs) -> Optional[Any]:
        """Sends a POST request."""
        return self.request('POST', endpoint, **kwargs)

    def put(self, endpoint: str, **kwargs) -> Optional[Any]:
        """Sends a PUT request."""
        return self.request('PUT', endpoint, **kwargs)

    def delete(self, endpoint: str, **kwargs) -> Optional[Any]:
        """Sends a DELETE request."""
        return self.request('DELETE', endpoint, **kwargs)
    
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def close(self):
        """Closes the HTTP client."""
        self.client.close() 