import json
from pathlib import Path

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from synapse_sdk.clients.exceptions import ClientError
from synapse_sdk.utils.file import files_url_to_path_from_objs


class BaseClient:
    name = None
    base_url = None
    page_size = 100

    def __init__(self, base_url, timeout=None):
        self.base_url = base_url.rstrip('/')
        # Set reasonable default timeouts for better UX
        self.timeout = timeout or {
            'connect': 5,  # Connection timeout: 5 seconds
            'read': 15,  # Read timeout: 15 seconds
        }

        # Create session with retry strategy
        requests_session = requests.Session()

        # Configure retry strategy for transient failures
        retry_strategy = Retry(
            total=3,  # Total retries
            backoff_factor=1,  # Backoff factor between retries
            status_forcelist=[502, 503, 504],  # HTTP status codes to retry
            allowed_methods=['GET', 'POST', 'PUT', 'DELETE', 'PATCH'],
        )

        adapter = HTTPAdapter(max_retries=retry_strategy)
        requests_session.mount('http://', adapter)
        requests_session.mount('https://', adapter)

        self.requests_session = requests_session

    def _get_url(self, path, trailing_slash=False):
        """Construct a full URL from a path.

        Args:
            path (str): URL path or full URL
            trailing_slash (bool): Whether to ensure URL ends with trailing slash

        Returns:
            str: Complete URL
        """
        # Use the path as-is if it's already a full URL, otherwise construct from base_url and path
        url = path if path.startswith(('http://', 'https://')) else f'{self.base_url}/{path.lstrip("/")}'

        # Add trailing slash if requested and not present
        if trailing_slash and not url.endswith('/'):
            url += '/'

        return url

    def _get_headers(self):
        return {}

    def _request(self, method: str, path: str, **kwargs) -> dict | str:
        """Request handler for all HTTP methods.

        Args:
            method (str): HTTP method to use.
            path (str): URL path to request.
            **kwargs: Additional keyword arguments to pass to the request.

        Returns:
            dict | str: JSON response or text response.
        """
        url = self._get_url(path)
        headers = self._get_headers()
        headers.update(kwargs.pop('headers', {}))

        # Set timeout if not provided in kwargs
        if 'timeout' not in kwargs:
            kwargs['timeout'] = (self.timeout['connect'], self.timeout['read'])

        # List to store opened files to close after request
        opened_files = []

        if method in ['post', 'put', 'patch']:
            # If files are included in the request, open them as binary files
            if kwargs.get('files') is not None:
                for name, file in kwargs['files'].items():
                    # Handle both string and Path object cases
                    if isinstance(file, str):
                        file = Path(file)
                    if isinstance(file, Path):
                        opened_file = file.open(mode='rb')
                        kwargs['files'][name] = (file.name, opened_file)
                        opened_files.append(opened_file)
                if 'data' in kwargs:
                    for name, value in kwargs['data'].items():
                        if isinstance(value, dict):
                            kwargs['data'][name] = json.dumps(value)
            else:
                headers['Content-Type'] = 'application/json'
                if 'data' in kwargs:
                    kwargs['data'] = json.dumps(kwargs['data'])

        try:
            # Send request
            response = getattr(self.requests_session, method)(url, headers=headers, **kwargs)
            if not response.ok:
                raise ClientError(
                    response.status_code, response.json() if response.status_code == 400 else response.reason
                )
        except requests.exceptions.ConnectTimeout:
            raise ClientError(408, f'{self.name} connection timeout (>{self.timeout["connect"]}s)')
        except requests.exceptions.ReadTimeout:
            raise ClientError(408, f'{self.name} read timeout (>{self.timeout["read"]}s)')
        except requests.exceptions.ConnectionError as e:
            # More specific error handling for different connection issues
            if 'Name or service not known' in str(e) or 'nodename nor servname provided' in str(e):
                raise ClientError(503, f'{self.name} host unreachable')
            elif 'Connection refused' in str(e):
                raise ClientError(503, f'{self.name} connection refused')
            else:
                raise ClientError(503, f'{self.name} connection error: {str(e)[:100]}')
        except requests.exceptions.RequestException as e:
            # Catch all other requests exceptions
            raise ClientError(500, f'{self.name} request failed: {str(e)[:100]}')

        # Close all opened files
        for opened_file in opened_files:
            opened_file.close()

        return self._post_response(response)

    def _post_response(self, response):
        try:
            return response.json()
        except ValueError:
            return response.text

    def _get(self, path, url_conversion=None, response_model=None, **kwargs):
        """Perform a GET request and optionally convert response to a pydantic model.

        Args:
            path (str): URL path to request.
            url_conversion (dict, optional): Configuration for URL to path conversion.
            request_model (pydantic.BaseModel, optional): Pydantic model to validate the request.
            response_model (pydantic.BaseModel, optional): Pydantic model to validate the response.
            **kwargs: Additional keyword arguments to pass to the request.

        Returns:
            The response data, optionally converted to a pydantic model.
        """
        response = self._request('get', path, **kwargs)

        if url_conversion:
            if url_conversion['is_list']:
                files_url_to_path_from_objs(response['results'], **url_conversion, is_async=True)
            else:
                files_url_to_path_from_objs(response, **url_conversion)

        if response_model:
            return self._validate_response_with_pydantic_model(response, response_model)

        return response

    def _post(self, path, request_model=None, response_model=None, **kwargs):
        """Perform a POST request and optionally convert response to a pydantic model.

        Args:
            path (str): URL path to request.
            request_model (pydantic.BaseModel, optional): Pydantic model to validate the request.
            response_model (pydantic.BaseModel, optional): Pydantic model to validate the response.
            **kwargs: Additional keyword arguments to pass to the request.

        Returns:
            The response data, optionally converted to a pydantic model.
        """
        if kwargs.get('data') and request_model:
            kwargs['data'] = self._validate_request_body_with_pydantic_model(kwargs['data'], request_model)
        response = self._request('post', path, **kwargs)
        if response_model:
            return self._validate_response_with_pydantic_model(response, response_model)
        else:
            return response

    def _put(self, path, request_model=None, response_model=None, **kwargs):
        """Perform a PUT request to the specified path.

        Args:
            path (str): The URL path for the request.
            request_model (Optional[Type[BaseModel]]): A Pydantic model class to validate the request body against.
            response_model (Optional[Type[BaseModel]]): A Pydantic model class to validate and parse the response.
            **kwargs: Additional arguments to pass to the request method.
                - data: The request body to be sent. If provided along with request_model, it will be validated.

        Returns:
            Union[dict, BaseModel]:
                If response_model is provided, returns an instance of that model populated with the response data.
        """
        if kwargs.get('data') and request_model:
            kwargs['data'] = self._validate_request_body_with_pydantic_model(kwargs['data'], request_model)
        response = self._request('put', path, **kwargs)
        if response_model:
            return self._validate_response_with_pydantic_model(response, response_model)
        else:
            return response

    def _patch(self, path, request_model=None, response_model=None, **kwargs):
        """Perform a PATCH HTTP request to the specified path.

        Args:
            path (str): The API endpoint path to make the request to.
            request_model (Optional[Type[BaseModel]]): A Pydantic model class used to validate the request body.
            response_model (Optional[Type[BaseModel]]): A Pydantic model class used to validate and parse the response.
            **kwargs: Additional keyword arguments to pass to the request method.
                - data: The request body data. If provided along with request_model, it will be validated.

        Returns:
            Union[dict, BaseModel]: If response_model is provided, returns an instance of that model.
                Otherwise, returns the raw response data.
        """
        if kwargs.get('data') and request_model:
            kwargs['data'] = self._validate_request_body_with_pydantic_model(kwargs['data'], request_model)
        response = self._request('patch', path, **kwargs)
        if response_model:
            return self._validate_response_with_pydantic_model(response, response_model)
        else:
            return response

    def _delete(self, path, request_model=None, response_model=None, **kwargs):
        """Performs a DELETE request to the specified path.

        Args:
            path (str): The API endpoint path to send the DELETE request to.
            request_model (Optional[Type[BaseModel]]): Pydantic model to validate the request data against.
            response_model (Optional[Type[BaseModel]]): Pydantic model to validate and convert the response data.
            **kwargs: Additional keyword arguments passed to the request method.
                - data: Request payload to send. Will be validated against request_model if both are provided.

        Returns:
            Union[dict, BaseModel]: If response_model is provided, returns an instance of that model.
                                   Otherwise, returns the raw response data as a dictionary.
        """
        if kwargs.get('data') and request_model:
            kwargs['data'] = self._validate_request_body_with_pydantic_model(kwargs['data'], request_model)
        response = self._request('delete', path, **kwargs)
        if response_model:
            return self._validate_response_with_pydantic_model(response, response_model)
        else:
            return response

    def _list(self, path, url_conversion=None, list_all=False, **kwargs):
        response = self._get(path, **kwargs)
        if list_all:
            return self._list_all(path, url_conversion, **kwargs), response['count']
        else:
            return response

    def _list_all(self, path, url_conversion=None, params={}, **kwargs):
        params['page_size'] = self.page_size
        response = self._get(path, url_conversion, params=params, **kwargs)
        yield from response['results']
        if response['next']:
            yield from self._list_all(response['next'], url_conversion, **kwargs)

    def exists(self, api, *args, **kwargs):
        return getattr(self, api)(*args, **kwargs)['count'] > 0

    def _validate_response_with_pydantic_model(self, response, pydantic_model):
        """Validate a response with a pydantic model."""
        # Check if model is a pydantic model (has the __pydantic_model__ attribute)
        if (
            hasattr(pydantic_model, '__pydantic_model__')
            or hasattr(pydantic_model, 'model_validate')
            or hasattr(pydantic_model, 'parse_obj')
        ):
            pydantic_model.model_validate(response)
            return response
        else:
            # Not a pydantic model
            raise TypeError('The provided model is not a pydantic model')

    def _validate_request_body_with_pydantic_model(self, request_body, pydantic_model):
        """Validate a request body with a pydantic model."""
        # Check if model is a pydantic model (has the __pydantic_model__ attribute)
        if (
            hasattr(pydantic_model, '__pydantic_model__')
            or hasattr(pydantic_model, 'model_validate')
            or hasattr(pydantic_model, 'parse_obj')
        ):
            # Validate the request body and convert to model instance
            model_instance = pydantic_model.model_validate(request_body)
            # Convert model to dict and remove None values
            return {k: v for k, v in model_instance.model_dump().items() if v is not None}
        else:
            # Not a pydantic model
            raise TypeError('The provided model is not a pydantic model')
