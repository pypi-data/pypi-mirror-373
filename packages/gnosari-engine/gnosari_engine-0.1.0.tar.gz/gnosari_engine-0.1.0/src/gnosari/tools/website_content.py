"""
OpenAI Website Content Tool - Using OpenAI Agents SDK FunctionTool
"""

import logging
import asyncio
import requests
from typing import Any
from pydantic import BaseModel, Field
from agents import RunContextWrapper, FunctionTool


class WebsiteContentArgs(BaseModel):
    """Arguments for the website content tool."""
    url: str = Field(..., description="The URL to fetch content from (will be appended to the base API URL)")


class WebsiteContentTool:
    """Configurable Website Content Tool that can be used in YAML configurations."""
    
    def __init__(self, base_url: str = "https://r.ai.neomanex.com", 
                 timeout: int = 30,
                 tool_name: str = "website_content",
                 tool_description: str = "Fetch the content of a given URL by querying an API"):
        """Initialize the website content tool.
        
        Args:
            base_url: Base URL for the API (defaults to https://r.ai.neomanex.com)
            timeout: Request timeout in seconds
            tool_name: Name of the tool
            tool_description: Description of the tool
        """
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        self.tool_name = tool_name
        self.tool_description = tool_description
        
        # Setup logger
        self.logger = logging.getLogger(__name__)
        
        # Create the FunctionTool
        self.tool = FunctionTool(
            name=self.tool_name,
            description=self.tool_description,
            params_json_schema=WebsiteContentArgs.model_json_schema(),
            on_invoke_tool=self._run_website_content_fetch
        )
    
    async def _run_website_content_fetch(self, ctx: RunContextWrapper[Any], args: str) -> str:
        """
        Fetch website content from for a given URL.
        
        Args:
            ctx: Run context wrapper
            args: JSON string containing WebsiteContentArgs
            
        Returns:
            Website content as string
        """
        try:
            # Parse arguments
            parsed_args = WebsiteContentArgs.model_validate_json(args)
            
            # Construct the full URL
            full_url = f"{self.base_url}/{parsed_args.url.lstrip('/')}"
            
            self.logger.info(f"🌐 WEBSITE CONTENT FETCH STARTED - URL: '{parsed_args.url}'")
            self.logger.debug(f"Full API URL: {full_url}")
            
            # Make the request (run synchronous code in executor)
            response = await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: requests.get(full_url, timeout=self.timeout)
            )
            
            # Log the response
            self.logger.info(f"HTTP Response received - Status: {response.status_code}")
            self.logger.debug(f"Response headers: {dict(response.headers)}")
            
            # Handle response
            response.raise_for_status()  # Raises an error for bad responses
            
            # Decode the content
            content = response.content.decode("utf-8")
            
            # Log successful result
            content_preview = content[:200] + "..." if len(content) > 200 else content
            self.logger.info(f"✅ WEBSITE CONTENT FETCH SUCCESSFUL - Retrieved {len(content)} characters")
            self.logger.info(f"📄 Content preview: {content_preview}")
            
            return content
            
        except requests.exceptions.RequestException as e:
            error_msg = f"Failed to fetch website content for URL '{parsed_args.url}': {str(e)}"
            self.logger.error(f"❌ WEBSITE CONTENT FETCH FAILED with RequestException: {error_msg}")
            if hasattr(e, 'response') and e.response is not None:
                self.logger.error(f"Response status code: {e.response.status_code}")
                self.logger.error(f"Response content: {e.response.text}")
                return f"Error: HTTP {e.response.status_code} - {e.response.text}"
            
            return f"Error fetching website content: {str(e)}"
            
        except Exception as e:
            error_msg = f"Unexpected error fetching website content for URL '{parsed_args.url}': {str(e)}"
            self.logger.error(f"❌ WEBSITE CONTENT FETCH FAILED with unexpected error: {error_msg}")
            return error_msg
    
    def get_tool(self) -> FunctionTool:
        """Get the FunctionTool instance.
        
        Returns:
            FunctionTool instance
        """
        return self.tool


def get_default_website_content_tool() -> FunctionTool:
    """Get a default website content tool instance.
    
    Returns:
        FunctionTool instance
    """
    return WebsiteContentTool().get_tool()