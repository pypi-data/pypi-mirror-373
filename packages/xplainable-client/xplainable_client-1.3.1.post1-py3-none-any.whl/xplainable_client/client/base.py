"""
Base client class with common request handling functionality.
"""
import json
from typing import Any, Dict, Optional, Type, TypeVar, Union
from pydantic import BaseModel
import requests
from requests import Response

T = TypeVar('T', bound=BaseModel)


class XplainableAPIError(Exception):
    """Custom exception for Xplainable API errors."""
    def __init__(self, status_code: int, message: str, details: Optional[Dict] = None):
        self.status_code = status_code
        self.message = message
        self.details = details
        super().__init__(f"HTTP {status_code}: {message}")


class BaseClient:
    """Base client class with common functionality for all API clients."""
    
    def __init__(self, session):
        """
        Initialize the base client.
        
        Args:
            session: The session object containing authentication and connection details
        """
        self.session = session
    
    def _build_url(self, endpoint: str, **kwargs) -> str:
        """
        Build a complete URL from an endpoint template.
        
        Args:
            endpoint: The endpoint template (may contain {placeholders})
            **kwargs: Values to substitute for placeholders
            
        Returns:
            The complete URL
        """
        # Replace placeholders in the endpoint
        url = endpoint
        for key, value in kwargs.items():
            url = url.replace(f"{{{key}}}", str(value))
        
        # Replace {ext} with the session extension if present
        if hasattr(self.session, '_ext'):
            url = url.replace("{ext}", self.session._ext)
            
        return f"{self.session.hostname}{url}"
    
    def _make_request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Union[BaseModel, Dict]] = None,
        params: Optional[Dict] = None,
        response_model: Optional[Type[T]] = None,
        **url_kwargs
    ) -> Union[T, Dict, Any]:
        """
        Make an HTTP request to the API.
        
        Args:
            method: HTTP method (GET, POST, PUT, PATCH, DELETE)
            endpoint: The endpoint template
            data: Request body data (can be a Pydantic model or dict)
            params: Query parameters
            response_model: Optional Pydantic model to parse the response
            **url_kwargs: Values to substitute in the endpoint URL
            
        Returns:
            Parsed response (as response_model if provided, otherwise as dict)
            
        Raises:
            XplainableAPIError: If the request fails
        """
        url = self._build_url(endpoint, **url_kwargs)
        
        # Convert Pydantic model to dict if necessary
        json_data = None
        if data:
            if isinstance(data, BaseModel):
                json_data = data.model_dump(exclude_none=True)
            else:
                json_data = data
        
        # Make the request
        method_func = getattr(self.session._session, method.lower())
        response = method_func(url=url, json=json_data, params=params)
        
        # Handle the response
        return self._handle_response(response, response_model)
    
    def _handle_response(
        self, 
        response: Response,
        response_model: Optional[Type[T]] = None
    ) -> Union[T, Dict, Any]:
        """
        Handle the API response and parse it.
        
        Args:
            response: The HTTP response
            response_model: Optional Pydantic model to parse the response
            
        Returns:
            Parsed response
            
        Raises:
            XplainableAPIError: If the response indicates an error
        """
        # Check for success
        if response.status_code >= 200 and response.status_code < 300:
            # Parse the response
            try:
                if response.content:
                    data = response.json()
                    
                    # If a response model is provided, parse into it
                    if response_model:
                        return response_model(**data)
                    return data
                return None
            except json.JSONDecodeError:
                # Return raw text if not JSON
                return response.text
        
        # Handle errors
        self._handle_error(response)
    
    def _handle_error(self, response: Response):
        """
        Handle error responses from the API.
        
        Args:
            response: The error response
            
        Raises:
            XplainableAPIError: Always raises with error details
        """
        try:
            error_data = response.json()
            message = error_data.get('detail', 'Unknown error')
            details = error_data
        except (json.JSONDecodeError, AttributeError):
            message = response.text or f"HTTP {response.status_code} error"
            details = None
        
        # Special handling for common status codes
        if response.status_code == 401:
            message = f"Unauthorized: {message}"
        elif response.status_code == 403:
            message = f"Forbidden: {message}"
        elif response.status_code == 404:
            message = f"Not found: {message}"
        elif response.status_code == 409:
            message = f"Conflict: {message}"
        elif response.status_code == 422:
            message = f"Validation error: {message}"
        
        raise XplainableAPIError(response.status_code, message, details)
    
    def get(self, endpoint: str, response_model: Optional[Type[T]] = None, **kwargs) -> Union[T, Dict]:
        """Convenience method for GET requests."""
        return self._make_request("GET", endpoint, response_model=response_model, **kwargs)
    
    def post(self, endpoint: str, data: Union[BaseModel, Dict], response_model: Optional[Type[T]] = None, **kwargs) -> Union[T, Dict]:
        """Convenience method for POST requests."""
        return self._make_request("POST", endpoint, data=data, response_model=response_model, **kwargs)
    
    def put(self, endpoint: str, data: Union[BaseModel, Dict], response_model: Optional[Type[T]] = None, **kwargs) -> Union[T, Dict]:
        """Convenience method for PUT requests."""
        return self._make_request("PUT", endpoint, data=data, response_model=response_model, **kwargs)
    
    def patch(self, endpoint: str, data: Union[BaseModel, Dict], response_model: Optional[Type[T]] = None, **kwargs) -> Union[T, Dict]:
        """Convenience method for PATCH requests."""
        return self._make_request("PATCH", endpoint, data=data, response_model=response_model, **kwargs)
    
    def delete(self, endpoint: str, **kwargs) -> Dict:
        """Convenience method for DELETE requests."""
        return self._make_request("DELETE", endpoint, **kwargs)