"""
Configuration module for LGEDV MCP Server
Quản lý tất cả các cấu hình và đường dẫn
"""
import os
import sys
import logging
from pydantic import FileUrl
import mcp.types as types

# Thiết lập cấu hình logging
def setup_logging():
    """Setup logging configuration"""
    log_path = os.path.join(os.getcwd(), "mcp_simple_prompt.log")
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s [%(levelname)s] %(message)s",
        handlers=[
            logging.StreamHandler(sys.stderr),
            # logging.FileHandler(log_path) # disable file logging, uncomment to enable
        ]
    )
    return logging.getLogger(__name__)

# Đặt BASE_DIR là thư mục chứa file server.py
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Đường dẫn đến các file rule
RULE_PATHS = {
    "misra": os.path.join(BASE_DIR, "resources", "Misracpp2008Guidelines_en.md"),
    "lgedv": os.path.join(BASE_DIR, "resources", "LGEDVRuleGuide.md"),
    "certcpp": os.path.join(BASE_DIR, "resources", "CertcppGuidelines_en.md"),
    "custom": os.environ.get("custom_path", os.path.join(BASE_DIR, "resources", "CustomRule.md"))
}

# Legacy compatibility
MISRA_RULE_URL = RULE_PATHS["misra"]
LGEDV_RULE_URL = RULE_PATHS["lgedv"]
CERTCPP_RULE_URL = RULE_PATHS["certcpp"]
CUSTOM_RULE_URL = RULE_PATHS["custom"]

RESOURCE_FILES = RULE_PATHS

def get_src_dir():
    """Get the CPP directory from environment or current working directory"""
    return os.environ.get("src_dir", os.getcwd())

# NOTE: MCP Resource handling is now in handlers/resource_handler.py
# This provides better separation and allows for future expansion like:
# - Resource caching
# - Dynamic resource loading  
# - Resource validation
# - Resource permissions
# - Resource versioning
