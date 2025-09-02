"""
Resource handler for MCP server operations
Xử lý các MCP resources với khả năng mở rộng trong tương lai
"""
import os
from typing import List, Dict, Optional
from mcp import types
from lgedv.modules.config import RULE_PATHS, setup_logging
from lgedv.modules.file_utils import file_exists, read_file_content

logger = setup_logging()

class ResourceHandler:
    """
    Handler cho MCP resources với khả năng mở rộng
    Hiện tại đơn giản nhưng có thể thêm features như caching, validation, v.v.
    """
    
    def __init__(self):
        self._resource_cache: Dict[str, types.Resource] = {}
        self._content_cache: Dict[str, str] = {}
        
    def get_resource_metadata(self, name: str, file_path: str) -> types.Resource:
        """
        Get resource metadata for MCP resources
        
        Args:
            name: Resource name
            file_path: Path to resource file
            
        Returns:
            Resource metadata
        """
        cache_key = f"{name}:{file_path}"
        
        # Check cache first (future feature)
        if cache_key in self._resource_cache:
            logger.debug(f"Resource {name} loaded from cache")
            return self._resource_cache[cache_key]
        
        # Create resource metadata
        resource = types.Resource(
            uri=f"file://{file_path}",
            name=name,
            title=f"{name.upper()} Rule Guide",
            description=f"{name.upper()} rule guideline markdown resource.",
            mimeType="text/markdown",
        )
        
        # Cache for future use
        self._resource_cache[cache_key] = resource
        
        logger.debug(f"Resource {name} metadata created")
        return resource
    
    def get_all_resources(self) -> List[types.Resource]:
        """
        Get all available resources
        
        Returns:
            List of all resource metadata
        """
        resources = []
        
        for rule_type, path in RULE_PATHS.items():
            try:
                resource = self.get_resource_metadata(rule_type, path)
                resources.append(resource)
            except Exception as e:
                logger.error(f"Error creating resource for {rule_type}: {e}")
        
        logger.info(f"Loaded {len(resources)} resources")
        return resources
    
    def validate_resource(self, name: str) -> bool:
        """
        Validate if a resource exists and is accessible
        Future feature: thêm validation logic phức tạp
        
        Args:
            name: Resource name
            
        Returns:
            True if resource is valid
        """
        if name not in RULE_PATHS:
            logger.warning(f"Unknown resource: {name}")
            return False
        
        file_path = RULE_PATHS[name]
        exists = file_exists(file_path)
        
        if not exists:
            logger.warning(f"Resource file not found: {file_path}")
        
        return exists
    
    def get_resource_content(self, name: str) -> Optional[str]:
        """
        Get the actual content of a resource
        Future feature: có thể cache, compress, encrypt, v.v.
        
        Args:
            name: Resource name
            
        Returns:
            Resource content or None if not found
        """
        if not self.validate_resource(name):
            return None
        
        # Check content cache
        if name in self._content_cache:
            logger.debug(f"Resource content {name} loaded from cache")
            return self._content_cache[name]
        
        try:
            file_path = RULE_PATHS[name]
            content = read_file_content(file_path)
            
            # Cache content
            self._content_cache[name] = content
            
            logger.debug(f"Resource content {name} loaded: {len(content)} chars")
            return content
            
        except Exception as e:
            logger.error(f"Error reading resource {name}: {e}")
            return None
    
    def refresh_cache(self):
        """
        Clear and refresh resource cache
        Future feature: intelligent cache invalidation
        """
        self._resource_cache.clear()
        self._content_cache.clear()
        logger.info("Resource cache cleared")
    
    def get_resource_stats(self) -> Dict:
        """
        Get statistics about resources
        Future feature: monitoring và analytics
        
        Returns:
            Resource statistics
        """
        stats = {
            "total_resources": len(RULE_PATHS),
            "cached_metadata": len(self._resource_cache),
            "cached_content": len(self._content_cache),
            "available_resources": [],
            "missing_resources": []
        }
        
        for name in RULE_PATHS:
            if self.validate_resource(name):
                stats["available_resources"].append(name)
            else:
                stats["missing_resources"].append(name)
        
        return stats
    
    def add_custom_resource(self, name: str, file_path: str, description: str = None):
        """
        Add a custom resource dynamically
        Future feature: dynamic resource management
        
        Args:
            name: Resource name
            file_path: Path to resource file
            description: Optional description
        """
        if not file_exists(file_path):
            raise FileNotFoundError(f"Resource file not found: {file_path}")
        
        # Add to RULE_PATHS (in a real implementation, this would be more sophisticated)
        RULE_PATHS[name] = file_path
        
        # Clear cache to force reload
        cache_key = f"{name}:{file_path}"
        self._resource_cache.pop(cache_key, None)
        self._content_cache.pop(name, None)
        
        logger.info(f"Custom resource added: {name} -> {file_path}")

# Global instance for easy access
_resource_handler = ResourceHandler()

# Factory functions for backward compatibility
def get_resource_metadata(name: str, file_path: str) -> types.Resource:
    """Factory function for backward compatibility"""
    return _resource_handler.get_resource_metadata(name, file_path)

def get_all_resources() -> List[types.Resource]:
    """Factory function for backward compatibility"""
    return _resource_handler.get_all_resources()

def get_resource_content(name: str) -> Optional[str]:
    """Get resource content"""
    return _resource_handler.get_resource_content(name)

def validate_resource(name: str) -> bool:
    """Validate resource"""
    return _resource_handler.validate_resource(name)

def get_resource_stats() -> Dict:
    """Get resource statistics"""
    return _resource_handler.get_resource_stats()
