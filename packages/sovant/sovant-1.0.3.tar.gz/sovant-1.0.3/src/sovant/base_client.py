"""Base client for making API requests."""

import asyncio
import json
import os
from typing import Any, Dict, Optional, TypeVar, Union
from urllib.parse import urlencode

import httpx

from .exceptions import (
    AuthenticationError,
    NetworkError,
    NotFoundError,
    RateLimitError,
    SovantError,
    ValidationError,
)
from .types import Config

T = TypeVar("T")


class BaseClient:
    """Base client for synchronous API requests."""
    
    def __init__(self, config: Union[str, Config]):
        if isinstance(config, str):
            self.config = Config(api_key=config)
        elif isinstance(config, Config):
            self.config = config
        else:
            # Try to get from environment
            api_key = os.environ.get("SOVANT_API_KEY")
            if not api_key:
                raise AuthenticationError("API key is required")
            self.config = Config(api_key=api_key)
        
        # Ensure HTTPS is used for security
        if not self.config.base_url.startswith("https://"):
            raise SovantError("API base URL must use HTTPS for security")
        
        self.client = httpx.Client(
            timeout=self.config.timeout,
            headers=self._get_headers(),
        )
    
    def _get_headers(self) -> Dict[str, str]:
        return {
            "Authorization": f"Bearer {self.config.api_key}",
            "Content-Type": "application/json",
            "X-SDK-Version": "1.0.0",
            "X-SDK-Language": "python",
        }
    
    def _build_url(self, path: str) -> str:
        return f"{self.config.base_url}{path}"
    
    def _build_query_string(self, params: Dict[str, Any]) -> str:
        filtered_params = {
            k: v for k, v in params.items() 
            if v is not None
        }
        
        # Handle list values
        processed_params = {}
        for k, v in filtered_params.items():
            if isinstance(v, list):
                # Convert list to comma-separated string
                processed_params[k] = ",".join(str(item) for item in v)
            elif isinstance(v, bool):
                processed_params[k] = str(v).lower()
            else:
                processed_params[k] = str(v)
        
        return f"?{urlencode(processed_params)}" if processed_params else ""
    
    def _handle_response(self, response: httpx.Response) -> Any:
        if response.status_code >= 200 and response.status_code < 300:
            try:
                return response.json()
            except json.JSONDecodeError:
                return None
        
        # Handle error responses
        try:
            error_data = response.json()
            message = error_data.get("message", f"HTTP {response.status_code}")
            details = error_data.get("details", {})
        except json.JSONDecodeError:
            message = f"HTTP {response.status_code} {response.reason_phrase}"
            details = {}
        
        if response.status_code == 401:
            raise AuthenticationError(message)
        elif response.status_code == 404:
            raise NotFoundError(message)
        elif response.status_code == 429:
            retry_after = response.headers.get("Retry-After")
            raise RateLimitError(
                message,
                int(retry_after) if retry_after else None
            )
        elif response.status_code in (400, 422):
            raise ValidationError(message, details.get("errors"))
        else:
            raise SovantError(message, response.status_code, details)
    
    def request(
        self,
        method: str,
        path: str,
        data: Optional[Dict[str, Any]] = None,
        retry_count: int = 0,
    ) -> Any:
        url = self._build_url(path)
        
        try:
            response = self.client.request(
                method,
                url,
                json=data if data else None,
            )
            return self._handle_response(response)
        except httpx.TimeoutException:
            raise NetworkError("Request timeout")
        except httpx.RequestError as e:
            if retry_count < self.config.max_retries:
                # Exponential backoff
                delay = self.config.retry_delay * (2 ** retry_count)
                import time
                time.sleep(delay)
                return self.request(method, path, data, retry_count + 1)
            raise NetworkError(str(e))
    
    def __del__(self):
        if hasattr(self, "client"):
            self.client.close()


class AsyncBaseClient:
    """Base client for asynchronous API requests."""
    
    def __init__(self, config: Union[str, Config]):
        if isinstance(config, str):
            self.config = Config(api_key=config)
        elif isinstance(config, Config):
            self.config = config
        else:
            # Try to get from environment
            api_key = os.environ.get("SOVANT_API_KEY")
            if not api_key:
                raise AuthenticationError("API key is required")
            self.config = Config(api_key=api_key)
        
        # Ensure HTTPS is used for security
        if not self.config.base_url.startswith("https://"):
            raise SovantError("API base URL must use HTTPS for security")
        
        self.client = httpx.AsyncClient(
            timeout=self.config.timeout,
            headers=self._get_headers(),
        )
    
    def _get_headers(self) -> Dict[str, str]:
        return {
            "Authorization": f"Bearer {self.config.api_key}",
            "Content-Type": "application/json",
            "X-SDK-Version": "1.0.0",
            "X-SDK-Language": "python",
        }
    
    def _build_url(self, path: str) -> str:
        return f"{self.config.base_url}{path}"
    
    def _build_query_string(self, params: Dict[str, Any]) -> str:
        filtered_params = {
            k: v for k, v in params.items() 
            if v is not None
        }
        
        # Handle list values
        processed_params = {}
        for k, v in filtered_params.items():
            if isinstance(v, list):
                # Convert list to comma-separated string
                processed_params[k] = ",".join(str(item) for item in v)
            elif isinstance(v, bool):
                processed_params[k] = str(v).lower()
            else:
                processed_params[k] = str(v)
        
        return f"?{urlencode(processed_params)}" if processed_params else ""
    
    async def _handle_response(self, response: httpx.Response) -> Any:
        if response.status_code >= 200 and response.status_code < 300:
            try:
                return response.json()
            except json.JSONDecodeError:
                return None
        
        # Handle error responses
        try:
            error_data = response.json()
            message = error_data.get("message", f"HTTP {response.status_code}")
            details = error_data.get("details", {})
        except json.JSONDecodeError:
            message = f"HTTP {response.status_code} {response.reason_phrase}"
            details = {}
        
        if response.status_code == 401:
            raise AuthenticationError(message)
        elif response.status_code == 404:
            raise NotFoundError(message)
        elif response.status_code == 429:
            retry_after = response.headers.get("Retry-After")
            raise RateLimitError(
                message,
                int(retry_after) if retry_after else None
            )
        elif response.status_code in (400, 422):
            raise ValidationError(message, details.get("errors"))
        else:
            raise SovantError(message, response.status_code, details)
    
    async def request(
        self,
        method: str,
        path: str,
        data: Optional[Dict[str, Any]] = None,
        retry_count: int = 0,
    ) -> Any:
        url = self._build_url(path)
        
        try:
            response = await self.client.request(
                method,
                url,
                json=data if data else None,
            )
            return await self._handle_response(response)
        except httpx.TimeoutException:
            raise NetworkError("Request timeout")
        except httpx.RequestError as e:
            if retry_count < self.config.max_retries:
                # Exponential backoff
                delay = self.config.retry_delay * (2 ** retry_count)
                await asyncio.sleep(delay)
                return await self.request(method, path, data, retry_count + 1)
            raise NetworkError(str(e))
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.client.aclose()