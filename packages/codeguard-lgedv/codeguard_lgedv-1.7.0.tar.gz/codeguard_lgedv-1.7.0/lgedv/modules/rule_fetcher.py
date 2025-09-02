"""
Rule fetcher module for handling different coding standards
Module để fetch các rule từ local files hoặc remote URLs
"""
import os
from typing import List, Union
from mcp.shared._httpx_utils import create_mcp_http_client
from mcp import types
from lgedv.modules.config import RULE_PATHS, setup_logging
from lgedv.modules.file_utils import read_file_content, file_exists

logger = setup_logging()

class RuleFetcher:
    """Class để fetch rules từ nhiều nguồn khác nhau"""
    
    def __init__(self):
        self.headers = {"User-Agent": "MCP Rule Fetcher"}
    
    async def fetch_rule(self, rule_type: str, url: str = None) -> List[Union[
        types.TextContent, types.ImageContent, types.AudioContent, types.EmbeddedResource
    ]]:
        """
        Fetch rule content từ URL hoặc local file
        
        Args:
            rule_type: Loại rule (misra, lgedv, certcpp, etc.)
            url: URL hoặc file path (optional, sẽ dùng default nếu không có)
            
        Returns:
            List content của rule
        """
        if not url:
            url = RULE_PATHS.get(rule_type)
            if not url:
                raise ValueError(f"Unknown rule type: {rule_type}")
        
        logger.debug(f"Fetching {rule_type} rule from: {url}")
        
        if url.startswith("http://") or url.startswith("https://"):
            return await self._fetch_from_url(url)
        else:
            return await self._fetch_from_file(url)
    
    async def _fetch_from_url(self, url: str) -> List[types.TextContent]:
        """Fetch rule từ HTTP URL"""
        async with create_mcp_http_client(headers=self.headers) as client:
            response = await client.get(url)
            response.raise_for_status()
            text = response.text
        
        logger.debug("Fetched rule from URL successfully")
        return [types.TextContent(type="text", text=text)]
    
    async def _fetch_from_file(self, file_path: str) -> List[types.TextContent]:
        """Fetch rule từ local file"""
        if not file_exists(file_path):
            raise FileNotFoundError(f"Rule file not found: {file_path}")
        
        text = read_file_content(file_path)
        logger.debug("Fetched rule from local file successfully")
        return [types.TextContent(type="text", text=text)]

# Factory functions cho từng loại rule
async def fetch_misra_rule(url: str = None) -> List[Union[
    types.TextContent, types.ImageContent, types.AudioContent, types.EmbeddedResource
]]:
    """Fetch MISRA C++ 2008 rule"""
    fetcher = RuleFetcher()
    return await fetcher.fetch_rule("misra", url)

async def fetch_lgedv_rule(url: str = None) -> List[Union[
    types.TextContent, types.ImageContent, types.AudioContent, types.EmbeddedResource
]]:
    """Fetch LGEDV rule"""
    fetcher = RuleFetcher()
    return await fetcher.fetch_rule("lgedv", url)

async def fetch_certcpp_rule(url: str = None) -> List[Union[
    types.TextContent, types.ImageContent, types.AudioContent, types.EmbeddedResource
]]:
    """Fetch CERT C++ rule"""
    fetcher = RuleFetcher()
    return await fetcher.fetch_rule("certcpp", url)

async def fetch_custom_rule(url: str = None) -> List[Union[
    types.TextContent, types.ImageContent, types.AudioContent, types.EmbeddedResource
]]:
    """Fetch Custom rule"""
    fetcher = RuleFetcher()
    return await fetcher.fetch_rule("custom", url)
