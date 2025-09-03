"""
File Operations Tool - Using OpenAI Agents SDK FunctionTool
"""

import logging
import asyncio
import json
import os
from pathlib import Path
from typing import Any, Optional, Literal
from pydantic import BaseModel, Field, validator
from agents import RunContextWrapper, FunctionTool


class FileOperationArgs(BaseModel):
    """Arguments for the file operations tool."""
    operation: Literal["read", "write", "list", "exists", "delete"] = Field(..., description="File operation to perform (read, write, list, exists, delete)")
    file_path: str = Field(..., description="Path to the file relative to the configured base directory")
    content: Optional[str] = Field(default=None, description="Content to write (required for write operation)")
    encoding: Optional[str] = Field(default="utf-8", description="File encoding (default: utf-8)")
    create_dirs: Optional[bool] = Field(default=True, description="Create parent directories if they don't exist (for write operation)")
    
    @validator('file_path')
    def validate_file_path(cls, v):
        """Validate file path to prevent directory traversal attacks."""
        # Normalize the path
        normalized = os.path.normpath(v)
        
        # Check for directory traversal attempts
        if '..' in normalized or normalized.startswith('/'):
            raise ValueError("File path cannot contain '..' or start with '/' for security reasons")
        
        return normalized
    
    @validator('content')
    def validate_write_content(cls, v, values):
        """Validate that content is provided for write operations."""
        if values.get('operation') == 'write' and v is None:
            raise ValueError("Content is required for write operation")
        return v
    
    class Config:
        extra = "forbid"


class FileOperationsTool:
    """Configurable File Operations Tool that can be used in YAML configurations."""
    
    def __init__(self, 
                 base_directory: str = "./workspace",
                 allowed_extensions: Optional[list] = None,
                 max_file_size: int = 10 * 1024 * 1024,  # 10MB default
                 tool_name: str = "file_operations",
                 tool_description: str = "Read, write, and manage files in the configured directory"):
        """Initialize the configurable file operations tool.
        
        Args:
            base_directory: Base directory for file operations (relative paths are resolved from here)
            allowed_extensions: List of allowed file extensions (e.g., ['.txt', '.json', '.py']). None allows all.
            max_file_size: Maximum file size in bytes for read/write operations
            tool_name: Name of the tool
            tool_description: Description of the tool
        """
        self.base_directory = Path(base_directory).resolve()
        self.allowed_extensions = allowed_extensions
        self.max_file_size = max_file_size
        self.tool_name = tool_name
        self.tool_description = tool_description
        
        # Setup logger
        self.logger = logging.getLogger(__name__)
        
        # Ensure base directory exists
        self.base_directory.mkdir(parents=True, exist_ok=True)
        
        # Create the FunctionTool
        self.tool = FunctionTool(
            name=self.tool_name,
            description=self.tool_description,
            params_json_schema=FileOperationArgs.model_json_schema(),
            on_invoke_tool=self._run_file_operation
        )
    
    def _validate_file_path(self, file_path: str, operation: str) -> Path:
        """Validate and resolve file path within base directory."""
        # For list operations on directories, use "." to list base directory
        if operation == "list" and file_path in ["", ".", "./"]:
            file_path = "."
        
        # Resolve the full path
        full_path = (self.base_directory / file_path).resolve()
        
        # Ensure the path is within the base directory (security check)
        try:
            full_path.relative_to(self.base_directory)
        except ValueError:
            raise ValueError(f"File path '{file_path}' is outside the allowed base directory")
        
        # Check file extension if restrictions are configured (skip for directories and list operations)
        if (self.allowed_extensions and 
            operation not in ["list", "exists"] and 
            full_path.suffix and 
            full_path.suffix not in self.allowed_extensions):
            raise ValueError(f"File extension '{full_path.suffix}' not allowed. Allowed extensions: {self.allowed_extensions}")
        
        return full_path
    
    async def _run_file_operation(self, ctx: RunContextWrapper[Any], args: str) -> str:
        """Execute the file operation.
        
        Args:
            ctx: Run context wrapper
            args: JSON string containing FileOperationArgs
            
        Returns:
            Operation result as string
        """
        try:
            # Parse arguments
            parsed_args = FileOperationArgs.model_validate_json(args)
            
            # Validate and resolve file path
            full_path = self._validate_file_path(parsed_args.file_path, parsed_args.operation)
            
            self.logger.info(f"📁 FILE OPERATION - {parsed_args.operation.upper()} on {parsed_args.file_path}")
            
            if parsed_args.operation == "read":
                return await self._read_file(full_path, parsed_args.encoding)
            elif parsed_args.operation == "write":
                return await self._write_file(full_path, parsed_args.content, parsed_args.encoding, parsed_args.create_dirs)
            elif parsed_args.operation == "list":
                return await self._list_directory(full_path)
            elif parsed_args.operation == "exists":
                return await self._check_exists(full_path)
            elif parsed_args.operation == "delete":
                return await self._delete_file(full_path)
            else:
                return f"Error: Unknown operation '{parsed_args.operation}'"
                
        except ValueError as e:
            self.logger.error(f"❌ FILE OPERATION FAILED with validation error: {str(e)}")
            return f"Validation error: {str(e)}"
        except Exception as e:
            self.logger.error(f"❌ FILE OPERATION FAILED with unexpected error: {str(e)}")
            return f"Unexpected error: {str(e)}"
    
    async def _read_file(self, file_path: Path, encoding: str) -> str:
        """Read file content."""
        try:
            if not file_path.exists():
                return f"Error: File '{file_path.relative_to(self.base_directory)}' does not exist"
            
            if not file_path.is_file():
                return f"Error: '{file_path.relative_to(self.base_directory)}' is not a file"
            
            # Check file size
            file_size = file_path.stat().st_size
            if file_size > self.max_file_size:
                return f"Error: File too large ({file_size} bytes). Maximum allowed: {self.max_file_size} bytes"
            
            # Read file content (run in executor for async)
            content = await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: file_path.read_text(encoding=encoding)
            )
            
            self.logger.info(f"✅ FILE READ SUCCESSFUL - {len(content)} characters read")
            return f"File content ({len(content)} characters):\n{content}"
            
        except UnicodeDecodeError as e:
            self.logger.error(f"❌ FILE READ FAILED with encoding error: {str(e)}")
            return f"Error: Could not decode file with encoding '{encoding}': {str(e)}"
        except Exception as e:
            self.logger.error(f"❌ FILE READ FAILED: {str(e)}")
            return f"Error reading file: {str(e)}"
    
    async def _write_file(self, file_path: Path, content: str, encoding: str, create_dirs: bool) -> str:
        """Write content to file."""
        try:
            # Check content size
            content_size = len(content.encode(encoding))
            if content_size > self.max_file_size:
                return f"Error: Content too large ({content_size} bytes). Maximum allowed: {self.max_file_size} bytes"
            
            # Create parent directories if needed
            if create_dirs:
                file_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Write file content (run in executor for async)
            await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: file_path.write_text(content, encoding=encoding)
            )
            
            self.logger.info(f"✅ FILE WRITE SUCCESSFUL - {len(content)} characters written")
            return f"Successfully wrote {len(content)} characters to '{file_path.relative_to(self.base_directory)}'"
            
        except Exception as e:
            self.logger.error(f"❌ FILE WRITE FAILED: {str(e)}")
            return f"Error writing file: {str(e)}"
    
    async def _list_directory(self, dir_path: Path) -> str:
        """List directory contents."""
        try:
            # If path is a file, list its parent directory
            if dir_path.is_file():
                dir_path = dir_path.parent
            
            if not dir_path.exists():
                return f"Error: Directory '{dir_path.relative_to(self.base_directory)}' does not exist"
            
            if not dir_path.is_dir():
                return f"Error: '{dir_path.relative_to(self.base_directory)}' is not a directory"
            
            # List directory contents (run in executor for async)
            entries = await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: sorted([
                    f"{'📁' if entry.is_dir() else '📄'} {entry.name}" + 
                    (f" ({entry.stat().st_size} bytes)" if entry.is_file() else "")
                    for entry in dir_path.iterdir()
                ])
            )
            
            rel_path = dir_path.relative_to(self.base_directory)
            self.logger.info(f"✅ DIRECTORY LIST SUCCESSFUL - {len(entries)} entries")
            return f"Directory listing for '{rel_path}' ({len(entries)} entries):\n" + "\n".join(entries)
            
        except Exception as e:
            self.logger.error(f"❌ DIRECTORY LIST FAILED: {str(e)}")
            return f"Error listing directory: {str(e)}"
    
    async def _check_exists(self, file_path: Path) -> str:
        """Check if file or directory exists."""
        try:
            exists = await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: file_path.exists()
            )
            
            if exists:
                if file_path.is_file():
                    size = file_path.stat().st_size
                    return f"File '{file_path.relative_to(self.base_directory)}' exists ({size} bytes)"
                elif file_path.is_dir():
                    return f"Directory '{file_path.relative_to(self.base_directory)}' exists"
                else:
                    return f"Path '{file_path.relative_to(self.base_directory)}' exists (unknown type)"
            else:
                return f"Path '{file_path.relative_to(self.base_directory)}' does not exist"
                
        except Exception as e:
            self.logger.error(f"❌ FILE EXISTS CHECK FAILED: {str(e)}")
            return f"Error checking file existence: {str(e)}"
    
    async def _delete_file(self, file_path: Path) -> str:
        """Delete file or directory."""
        try:
            if not file_path.exists():
                return f"Error: Path '{file_path.relative_to(self.base_directory)}' does not exist"
            
            # Delete file or directory (run in executor for async)
            if file_path.is_file():
                await asyncio.get_event_loop().run_in_executor(
                    None,
                    lambda: file_path.unlink()
                )
                self.logger.info(f"✅ FILE DELETE SUCCESSFUL")
                return f"Successfully deleted file '{file_path.relative_to(self.base_directory)}'"
            elif file_path.is_dir():
                # Only delete empty directories for safety
                try:
                    await asyncio.get_event_loop().run_in_executor(
                        None,
                        lambda: file_path.rmdir()
                    )
                    self.logger.info(f"✅ DIRECTORY DELETE SUCCESSFUL")
                    return f"Successfully deleted empty directory '{file_path.relative_to(self.base_directory)}'"
                except OSError:
                    return f"Error: Directory '{file_path.relative_to(self.base_directory)}' is not empty. Only empty directories can be deleted for safety."
            else:
                return f"Error: Cannot delete '{file_path.relative_to(self.base_directory)}' - unknown file type"
                
        except Exception as e:
            self.logger.error(f"❌ FILE DELETE FAILED: {str(e)}")
            return f"Error deleting file: {str(e)}"
    
    def get_tool(self) -> FunctionTool:
        """Get the FunctionTool instance.
        
        Returns:
            FunctionTool instance
        """
        return self.tool


def get_default_file_operations_tool() -> FunctionTool:
    """Get a default file operations tool instance.
    
    Returns:
        FunctionTool instance
    """
    return FileOperationsTool().get_tool()