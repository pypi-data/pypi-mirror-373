"""
Persistent storage for tracking analyzed files across chat sessions
"""
import os
import json
import hashlib
from datetime import datetime
from typing import List, Dict, Optional
from lgedv.modules.config import setup_logging

logger = setup_logging()

class PersistentTracker:
    """Track analyzed files across chat sessions"""
    
    def __init__(self, analysis_type: str = "memory_analysis", base_dir: str = None):
        import platform
        self.analysis_type = analysis_type
        if base_dir is None:
            if platform.system().lower().startswith("win"):
                base_dir = r"C:\\Program Files\\MCP Server CodeGuard\\tmp\\lgedv"
            else:
                base_dir = "/tmp/lgedv"
        self.base_dir = base_dir
        # Use simple, consistent filename based on analysis type only
        self.storage_file = os.path.join(base_dir, f"{analysis_type}_checked.json")
        # Ensure directory exists
        os.makedirs(base_dir, exist_ok=True)
        
    def get_checked_files(self, directory: str) -> List[str]:
        """Get list of already checked files for the given directory"""
        try:
            if os.path.exists(self.storage_file):
                with open(self.storage_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    
                # Check if same directory
                if data.get('directory') == directory:
                    checked_files = data.get('checked_files', [])
                    logger.info(f"Found {len(checked_files)} previously checked files: {checked_files}")
                    return checked_files
                else:
                    logger.info(f"Directory changed from {data.get('directory')} to {directory}, resetting")
                    return []
            else:
                logger.info("No previous analysis found, starting fresh")
                return []
        except Exception as e:
            logger.error(f"Error reading checked files: {e}")
            return []
    
    def save_checked_files(self, directory: str, checked_files: List[str]) -> None:
        """Save list of checked files to persistent storage"""
        try:
            data = {
                "timestamp": datetime.now().isoformat(),
                "analysis_type": self.analysis_type,
                "directory": directory,
                "checked_files": checked_files
            }
            
            with open(self.storage_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
                
            logger.info(f"Saved {len(checked_files)} checked files to {self.storage_file}")
            
        except Exception as e:
            logger.error(f"Error saving checked files: {e}")
    
    def add_checked_files(self, directory: str, new_files: List[str]) -> None:
        """Add new files to the checked list"""
        existing_files = self.get_checked_files(directory)
        all_checked = list(set(existing_files + new_files))  # Remove duplicates
        self.save_checked_files(directory, all_checked)
    
    def reset_checked_files(self, directory: str) -> None:
        """Reset checked files list (for new analysis)"""
        self.save_checked_files(directory, [])
        logger.info(f"Reset checked files for directory: {directory}")
    
    def get_analysis_stats(self, directory: str) -> Dict:
        """Get analysis statistics"""
        checked_files = self.get_checked_files(directory)
        return {
            "total_checked": len(checked_files),
            "storage_file": self.storage_file,
            "last_updated": datetime.now().isoformat()
        }

# standalone functions for utility operations
def _get_default_base_dir():
    import platform
    if platform.system().lower().startswith("win"):
        return r"C:\\Program Files\\MCP Server CodeGuard\\tmp\\lgedv"
    else:
        return "/tmp/lgedv"

def reset_all_analysis(base_dir: str = None) -> None:
    """Reset all analysis data - utility function"""
    if base_dir is None:
        base_dir = _get_default_base_dir()
    try:
        import glob
        pattern = os.path.join(base_dir, "*_checked.json")
        files = glob.glob(pattern)
        for file_path in files:
            os.remove(file_path)
            logger.info(f"Removed: {file_path}")
        logger.info(f"Reset {len(files)} analysis files")
    except Exception as e:
        logger.error(f"Error resetting analysis data: {e}")

def get_all_sessions(base_dir: str = None) -> List[Dict]:
    """Get all active analysis sessions"""
    if base_dir is None:
        base_dir = _get_default_base_dir()
    try:
        import glob
        pattern = os.path.join(base_dir, "*_checked.json")
        files = glob.glob(pattern)
        sessions = []
        for file_path in files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    sessions.append({
                        'file': os.path.basename(file_path),
                        'analysis_type': data.get('analysis_type', 'unknown'),
                        'directory': data.get('directory', 'unknown'),
                        'checked_files_count': len(data.get('checked_files', [])),
                        'timestamp': data.get('timestamp', 'unknown')
                    })
            except Exception as e:
                logger.error(f"Error reading {file_path}: {e}")
        return sessions
    except Exception as e:
        logger.error(f"Error listing sessions: {e}")
    return []