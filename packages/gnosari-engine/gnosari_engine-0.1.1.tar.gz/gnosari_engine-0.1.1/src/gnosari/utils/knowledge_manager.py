import logging
import sys
import threading
import time
from typing import Dict, Any, Optional
import os
import tempfile
import re
from pathlib import Path

try:
    from embedchain import App
    from embedchain.config import AddConfig
    EMBEDCHAIN_AVAILABLE = True
except ImportError:
    EMBEDCHAIN_AVAILABLE = False


class KnowledgeManager:
    """Manages knowledge bases using Embedchain."""
    
    def __init__(self, storage_path: Optional[str] = None):
        """
        Initialize the knowledge manager.
        
        Args:
            storage_path: Path to store knowledge base data (optional)
        """
        if not EMBEDCHAIN_AVAILABLE:
            raise ImportError("Embedchain is not available. Please install it with: pip install embedchain")
        
        self.storage_path = storage_path or os.path.join(tempfile.gettempdir(), "gnosari_knowledge")
        self.knowledge_bases: Dict[str, Dict[str, Any]] = {}
        
        # Ensure storage directory exists
        os.makedirs(self.storage_path, exist_ok=True)
        
        # Setup logger
        self.logger = logging.getLogger(__name__)
    
    def _create_knowledge_slug(self, name: str) -> str:
        """
        Create a filesystem-safe slug from knowledge base name.
        
        Args:
            name: Knowledge base name
            
        Returns:
            Filesystem-safe slug
        """
        # Convert to lowercase and replace spaces/special chars with hyphens
        slug = re.sub(r'[^a-zA-Z0-9\s-]', '', name.lower())
        slug = re.sub(r'[\s-]+', '-', slug).strip('-')
        
        # Ensure it's not empty and not too long
        if not slug:
            slug = 'knowledge-base'
        
        # Limit length to avoid filesystem issues
        slug = slug[:50]
        
        return slug
    
    def _get_knowledge_directory(self, name: str) -> str:
        """
        Get the directory path for a knowledge base.
        
        Args:
            name: Knowledge base name
            
        Returns:
            Directory path for the knowledge base
        """
        slug = self._create_knowledge_slug(name)
        return os.path.join(self.storage_path, "knowledge", slug)
    
    def _get_default_config(self, name: str) -> Dict[str, Any]:
        """
        Get default configuration for a knowledge base with ChromaDB directory separation.
        
        Args:
            name: Knowledge base name
            
        Returns:
            Default configuration dictionary
        """
        kb_directory = self._get_knowledge_directory(name)
        
        return {
            "vectordb": {
                "provider": "chroma",
                "config": {
                    "dir": kb_directory,
                    "allow_reset": True
                }
            },
            "chunker": {
                "chunk_size": 700,
                "chunk_overlap": 250,
                "length_function": "len",
                "min_chunk_size": 300
            }
        }
    
    def _merge_configs(self, default_config: Dict[str, Any], user_config: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Merge user configuration with default configuration.
        User config takes precedence over defaults.
        
        Args:
            default_config: Default configuration
            user_config: User-provided configuration (optional)
            
        Returns:
            Merged configuration dictionary
        """
        if not user_config:
            return default_config.copy()
        
        # Deep merge - user config overrides defaults
        merged = default_config.copy()
        
        for key, value in user_config.items():
            if key in merged and isinstance(merged[key], dict) and isinstance(value, dict):
                # Recursively merge nested dictionaries
                merged[key] = self._merge_configs(merged[key], value)
            else:
                # Direct override for non-dict values or new keys
                merged[key] = value
        
        return merged
    
    def create_knowledge_base(self, name: str, knowledge_type: str, config: Optional[Dict[str, Any]] = None) -> None:
        """
        Create a new knowledge base with directory-separated ChromaDB storage.
        
        Args:
            name: Name of the knowledge base
            knowledge_type: Type of knowledge base (sitemap, website, etc.)
            config: Embedchain configuration (optional, will be merged with defaults)
        """
        if name in self.knowledge_bases:
            self.logger.warning(f"Knowledge base '{name}' already exists. Skipping creation.")
            return
        
        try:
            # Get default configuration with directory separation
            default_config = self._get_default_config(name)
            
            # Merge user config with defaults (user config takes precedence)
            final_config = self._merge_configs(default_config, config)
            
            # Ensure the knowledge base directory exists
            kb_directory = self._get_knowledge_directory(name)
            os.makedirs(kb_directory, exist_ok=True)
            
            # Log configuration details
            if config:
                self.logger.info(f"Creating knowledge base '{name}' with merged configuration")
                self.logger.debug(f"User config: {config}")
                self.logger.debug(f"Final config: {final_config}")
            else:
                self.logger.info(f"Creating knowledge base '{name}' with default configuration")
                self.logger.debug(f"Default config: {final_config}")
            
            self.logger.info(f"ChromaDB directory for '{name}': {kb_directory}")
            
            # Create Embedchain app with final configuration
            app = App.from_config(config=final_config)
            
            # Store the app and configuration
            self.knowledge_bases[name] = {
                'app': app,
                'type': knowledge_type,
                'config': final_config,
                'directory': kb_directory
            }
            
            self.logger.info(f"Created knowledge base '{name}' of type '{knowledge_type}' with directory separation")
            
        except Exception as e:
            self.logger.error(f"Failed to create knowledge base '{name}': {e}")
            raise
    
    def add_data_to_knowledge_base(self, name: str, data: str, data_type: Optional[str] = None, progress_callback: Optional[callable] = None, **kwargs) -> None:
        """
        Add data to a knowledge base.
        
        Args:
            name: Name of the knowledge base
            data: Data to add (URL, text, file path, etc.)
            data_type: Type of data (optional, will be auto-detected if not provided)
            progress_callback: Optional callback to report progress during loading
            **kwargs: Additional configuration for adding data
        """
        if name not in self.knowledge_bases:
            raise ValueError(f"Knowledge base '{name}' does not exist")
        
        try:
            app = self.knowledge_bases[name]['app']
            
            # Check if collection already exists and has data
            try:
                # Check if collection has data using the correct path
                if hasattr(app, 'db') and hasattr(app.db, 'count') and app.db.count() > 0:
                    self.logger.info(f"Knowledge base '{name}' already has data. Skipping addition of: {data}")
                    return
            except Exception as check_error:
                # If check fails, proceed with adding (fallback)
                self.logger.debug(f"Could not check existing data: {check_error}")
            
            # Notify progress callback if provided
            if progress_callback:
                progress_callback(f"Loading knowledge {name}...")
            
            # Add data to the app with any additional configuration
            self.logger.info(f'Adding data to knowledge base {name} with type {data_type}')
            
            if data_type:
                app.add(data, data_type=data_type, **kwargs)
            else:
                app.add(data, **kwargs)
            
            # Notify completion if callback provided
            if progress_callback:
                progress_callback(f"Knowledge {name} loaded successfully")
            
            self.logger.info(f"Added data to knowledge base '{name}': {data}")
            
        except Exception as e:
            self.logger.error(f"Failed to add data to knowledge base '{name}': {e}")
            raise
    
    def query_knowledge(self, name: str, query: str) -> str:
        """
        Query a knowledge base.
        
        Args:
            name: Name of the knowledge base
            query: Query string
            
        Returns:
            Query result as string
        """
        if name not in self.knowledge_bases:
            raise ValueError(f"Knowledge base '{name}' does not exist")
        
        try:
            app = self.knowledge_bases[name]['app']
            result = app.query(query)
            
            self.logger.info(f"Queried knowledge base '{name}' with: '{query}'")
            self.logger.info(f"RESULT: '{result}''")
            return result
            
        except Exception as e:
            self.logger.error(f"Failed to query knowledge base '{name}': {e}")
            raise
    
    def get_knowledge_base_info(self, name: str) -> Dict[str, Any]:
        """
        Get information about a knowledge base.
        
        Args:
            name: Name of the knowledge base
            
        Returns:
            Dictionary with knowledge base information
        """
        if name not in self.knowledge_bases:
            raise ValueError(f"Knowledge base '{name}' does not exist")
        
        kb_info = self.knowledge_bases[name]
        return {
            'name': name,
            'type': kb_info['type'],
            'config': kb_info['config'],
            'directory': kb_info.get('directory', self._get_knowledge_directory(name)),
            'slug': self._create_knowledge_slug(name)
        }
    
    def list_knowledge_bases(self) -> list:
        """
        List all available knowledge bases.
        
        Returns:
            List of knowledge base names
        """
        return list(self.knowledge_bases.keys())
    
    def get_knowledge_base_directory(self, name: str) -> str:
        """
        Get the directory path for a knowledge base.
        
        Args:
            name: Name of the knowledge base
            
        Returns:
            Directory path for the knowledge base
            
        Raises:
            ValueError: If knowledge base does not exist
        """
        if name not in self.knowledge_bases:
            raise ValueError(f"Knowledge base '{name}' does not exist")
        
        return self._get_knowledge_directory(name)
    
    def debug_knowledge_bases(self) -> Dict[str, Any]:
        """
        Debug method to show all knowledge bases and their details.
        
        Returns:
            Dictionary with debug information
        """
        debug_info = {
            'count': len(self.knowledge_bases),
            'names': list(self.knowledge_bases.keys()),
            'details': {}
        }
        
        for name, kb_info in self.knowledge_bases.items():
            debug_info['details'][name] = {
                'type': kb_info.get('type'),
                'config': kb_info.get('config'),
                'has_app': 'app' in kb_info,
                'app_type': type(kb_info.get('app')).__name__ if 'app' in kb_info else None,
                'directory': kb_info.get('directory', self._get_knowledge_directory(name)),
                'slug': self._create_knowledge_slug(name)
            }
        
        return debug_info
    
    def remove_knowledge_base(self, name: str) -> None:
        """
        Remove a knowledge base and its associated directory.
        
        Args:
            name: Name of the knowledge base to remove
        """
        if name not in self.knowledge_bases:
            self.logger.warning(f"Knowledge base '{name}' does not exist. Nothing to remove.")
            return
        
        try:
            # Get the directory path before removing from memory
            kb_directory = self._get_knowledge_directory(name)
            
            # Remove from memory
            del self.knowledge_bases[name]
            
            # Remove the knowledge base directory if it exists
            if os.path.exists(kb_directory):
                import shutil
                shutil.rmtree(kb_directory)
                self.logger.info(f"Removed knowledge base directory: {kb_directory}")
            
            # Also check for legacy storage path (backward compatibility)
            legacy_path = os.path.join(self.storage_path, name)
            if os.path.exists(legacy_path):
                import shutil
                shutil.rmtree(legacy_path)
                self.logger.info(f"Removed legacy knowledge base directory: {legacy_path}")
            
            self.logger.info(f"Removed knowledge base '{name}'")
            
        except Exception as e:
            self.logger.error(f"Failed to remove knowledge base '{name}': {e}")
            raise

