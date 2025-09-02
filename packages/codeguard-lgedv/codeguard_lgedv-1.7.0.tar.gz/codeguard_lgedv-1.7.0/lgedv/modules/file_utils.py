"""
File utilities for handling C++ files and content operations
Các tiện ích để xử lý file C++ và operations liên quan
"""
import os
import json
from typing import List, Dict
from .config import get_src_dir, setup_logging

logger = setup_logging()

def list_source_files(dir_path: str = None) -> List[str]:
    """
    Trả về danh sách file .cpp trong dir_path hoặc src_dir hoặc cwd.
    
    Args:
        dir_path: Thư mục cần tìm kiếm (optional)
        
    Returns:
        List[str]: Danh sách các file sources
    """
    if dir_path is None:
        dir_path = get_src_dir()
    
    SRC_EXTENSIONS = ('.cpp', '.h', '.hpp', '.cc', '.cxx', '.py', '.java', '.js', '.jsx', '.ts')
    src_files = []
    for root, dirs, files in os.walk(dir_path):
        for file in files:
            if file.endswith(SRC_EXTENSIONS):
                # Return relative path for better readability
                rel_path = os.path.relpath(os.path.join(root, file), dir_path)
                src_files.append(rel_path)
    return src_files

# def get_context(dir_path: str = None) -> str:
#     """
#     Lấy nội dung của tất cả file source trong thư mục
    
#     Args:
#         dir_path: Thư mục cần đọc (optional)
        
#     Returns:
#         str: Nội dung tất cả các file được nối lại
#     """
#     if dir_path is None:
#         dir_path = get_src_dir()
    
#     src_files = list_source_files(dir_path)
#     contents = []
    
#     for file in src_files:
#         abs_path = os.path.join(dir_path, file)
#         try:
#             with open(abs_path, "r", encoding="utf-8") as f:
#                 code = f.read()
#             contents.append(f"// File: {file}\n{code}\n")
#         except Exception as e:
#             contents.append(f"// Error reading {file}: {e}\n")
    
#     return "\n".join(contents)

def read_file_content(file_path: str) -> str:
    """
    Đọc nội dung của một file
    
    Args:
        file_path: Đường dẫn đến file
        
    Returns:
        str: Nội dung file
    """
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        raise FileNotFoundError(f"Cannot read file {file_path}: {e}")

def file_exists(file_path: str) -> bool:
    """
    Kiểm tra file có tồn tại không
    
    Args:
        file_path: Đường dẫn đến file
        
    Returns:
        bool: True nếu file tồn tại
    """
    return os.path.exists(file_path)