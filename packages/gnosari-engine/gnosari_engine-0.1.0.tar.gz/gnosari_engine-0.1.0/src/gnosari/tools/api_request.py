"""
OpenAI API Request Tool - Using OpenAI Agents SDK FunctionTool
"""

import logging
import asyncio
import json
import requests
from typing import Any, Dict, Optional
from pydantic import BaseModel, Field
from agents import RunContextWrapper, FunctionTool


class APIRequestArgs(BaseModel):
    """Arguments for the API request tool."""
    endpoint: str = Field(..., description="The API endpoint path (e.g., '/users', '/posts/123')")
    method: str = Field(default="GET", description="HTTP method to use (GET, POST, PUT, DELETE, PATCH, etc.)")
    body_params: Optional[str] = Field(default=None, description="JSON body parameters for POST/PUT/PATCH requests as JSON string")
    headers: Optional[str] = Field(default=None, description="Custom headers for the request as JSON string")
    base_url: Optional[str] = Field(default=None, description="Base URL (overrides configured base_url)")
    timeout: Optional[int] = Field(default=None, description="Request timeout (overrides configured timeout)")
    verify_ssl: Optional[bool] = Field(default=None, description="SSL verification (overrides configured verify_ssl)")
    
    class Config:
        extra = "forbid"  # Prevent additional properties


class APIRequestTool:
    """Configurable API Request Tool that can be used in YAML configurations."""
    
    def __init__(self, base_url: str = "https://api.example.com", 
                 base_headers: Optional[Dict[str, str]] = None,
                 timeout: int = 30, 
                 verify_ssl: bool = True,
                 tool_name: str = "api_request",
                 tool_description: str = "Make HTTP requests to API endpoints"):
        """Initialize the configurable API request tool.
        
        Args:
            base_url: Base URL for the API
            base_headers: Base headers to include in all requests
            timeout: Request timeout in seconds
            verify_ssl: Whether to verify SSL certificates
            tool_name: Name of the tool
            tool_description: Description of the tool
        """
        self.base_url = base_url.rstrip('/')
        self.base_headers = base_headers or {}
        self.timeout = timeout
        self.verify_ssl = verify_ssl
        self.tool_name = tool_name
        self.tool_description = tool_description
        
        # Setup logger
        self.logger = logging.getLogger(__name__)
        
        # Create the FunctionTool
        self.tool = FunctionTool(
            name=self.tool_name,
            description=self.tool_description,
            params_json_schema=APIRequestArgs.model_json_schema(),
            on_invoke_tool=self._run_api_request
        )
    
    async def _run_api_request(self, ctx: RunContextWrapper[Any], args: str) -> str:
        """Execute the API request.
        
        Args:
            ctx: Run context wrapper
            args: JSON string containing APIRequestArgs
            
        Returns:
            API response as string
        """
        try:
            # Parse arguments
            parsed_args = APIRequestArgs.model_validate_json(args)
            
            # Use config values as defaults, allow per-call overrides
            final_base_url = parsed_args.base_url or self.base_url
            final_timeout = parsed_args.timeout or self.timeout
            final_verify_ssl = parsed_args.verify_ssl if parsed_args.verify_ssl is not None else self.verify_ssl
            
            # Parse headers if provided
            final_headers = self.base_headers.copy()
            if parsed_args.headers:
                try:
                    headers_dict = json.loads(parsed_args.headers)
                    final_headers.update(headers_dict)
                except json.JSONDecodeError:
                    self.logger.warning(f"Invalid JSON in headers: {parsed_args.headers}")
            
            # Log the API request
            self.logger.info(f"🌐 API REQUEST STARTED - {parsed_args.method.upper()} {parsed_args.endpoint}")
            self.logger.debug(f"API Request details - URL: {final_base_url}/{parsed_args.endpoint.lstrip('/')}, Headers: {final_headers}, Body: {parsed_args.body_params}")
            
            # Construct full URL
            full_url = f"{final_base_url}/{parsed_args.endpoint.lstrip('/')}"
            
            # Prepare request parameters
            default_headers = {
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            }
            
            # Merge base headers with default headers
            default_headers.update(final_headers)
            
            request_kwargs = {
                'timeout': final_timeout,
                'headers': default_headers,
                'verify': final_verify_ssl
            }
            
            # Add body parameters if provided
            if parsed_args.body_params and parsed_args.method.upper() in ['POST', 'PUT', 'PATCH']:
                try:
                    body_dict = json.loads(parsed_args.body_params)
                    request_kwargs['json'] = body_dict
                except json.JSONDecodeError:
                    self.logger.warning(f"Invalid JSON in body_params: {parsed_args.body_params}")
                    # Fallback to sending as raw text
                    request_kwargs['data'] = parsed_args.body_params
            
            # Log the actual HTTP request being made
            self.logger.info(f"Making HTTP {parsed_args.method.upper()} request to: {full_url}")
            self.logger.debug(f"Request kwargs: {request_kwargs}")
            
            # Make the request (run synchronous code in executor)
            response = await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: requests.request(
                    method=parsed_args.method.upper(),
                    url=full_url,
                    **request_kwargs
                )
            )
            
            # Log the response
            self.logger.info(f"HTTP Response received - Status: {response.status_code}")
            self.logger.debug(f"Response headers: {dict(response.headers)}")
            
            # Handle response
            response.raise_for_status()
            
            # Try to return JSON, fallback to text
            try:
                response_data = json.dumps(response.json(), indent=2)
                self.logger.debug(f"Response data (JSON): {response_data[:500]}...")  # Log first 500 chars
            except json.JSONDecodeError:
                response_data = response.text
                self.logger.debug(f"Response data (text): {response_data[:500]}...")  # Log first 500 chars
            
            self.logger.info(f"✅ API REQUEST SUCCESSFUL - Status: {response.status_code}")
            
            return f"Status: {response.status_code}\nResponse: {response_data}"
                    
        except requests.exceptions.RequestException as e:
            self.logger.error(f"❌ API REQUEST FAILED with RequestException: {str(e)}")
            if hasattr(e, 'response') and e.response is not None:
                self.logger.error(f"Response status code: {e.response.status_code}")
                self.logger.error(f"Response content: {e.response.text}")
                return f"Error: HTTP {e.response.status_code} - {e.response.text}"
            
            return f"Error making API request: {str(e)}"
            
        except Exception as e:
            self.logger.error(f"❌ API REQUEST FAILED with unexpected error: {str(e)}")
            return f"Unexpected error: {str(e)}"
    
    def get_tool(self) -> FunctionTool:
        """Get the FunctionTool instance.
        
        Returns:
            FunctionTool instance
        """
        return self.tool


def get_default_api_request_tool() -> FunctionTool:
    """Get a default API request tool instance.
    
    Returns:
        FunctionTool instance
    """
    return APIRequestTool().get_tool()
