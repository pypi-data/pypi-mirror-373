"""
Race condition analyzer module
Module chuyên dụng để phân tích race conditions trong C++ code
"""
import os
import re
from typing import Dict, List
from lgedv.modules.config import get_src_dir, setup_logging
from lgedv.modules.data_models import SharedResource, ThreadUsage, RaceCondition, AnalysisResult
from lgedv.modules.file_utils import list_source_files
from lgedv.modules.persistent_storage import PersistentTracker

logger = setup_logging()

class CppParser:
    """Parser để phân tích C++ code"""
    
    def __init__(self):
        self.patterns = {
            # Global variable detection (chỉ ở file scope)
            'global_var': r'^\s*(?:extern\s+)?(?:const\s+)?(?:static\s+)?(?:const\s+)?([a-zA-Z_:][a-zA-Z0-9_:<>*&\s]*)\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*(?:\[.*\])?\s*(?:=.*)?;',
            # Static variables
            'static_var': r'^\s*static\s+(?:const\s+)?([a-zA-Z_:][a-zA-Z0-9_:<>*&\s]*)\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*(?:\[.*\])?\s*(?:=.*)?;',
            # Function/method detection
            'function_start': r'^\s*(?:.*\s+)?(\w+)\s*\([^)]*\)\s*(?:const\s*)?(?:override\s*)?(?:final\s*)?(?:noexcept\s*)?(?:\s*->\s*\w+\s*)?\s*\{',
            # Class detection
            'class_start': r'^\s*(?:class|struct)\s+(\w+)',
            # Namespace detection
            'namespace_start': r'^\s*namespace\s+(\w+)',
            # Thread creation patterns
            'thread_create': r'std::thread|pthread_create|std::async|CreateThread',
            # Mutex and synchronization
            'mutex_usage': r'std::mutex|std::recursive_mutex|pthread_mutex|std::shared_mutex|std::lock_guard|std::unique_lock',
            # Atomic operations
            'atomic_usage': r'std::atomic|atomic_|std::memory_order',
            # Smart pointers
            'shared_ptr': r'std::shared_ptr|std::unique_ptr|std::weak_ptr',
            # Singleton patterns
            'singleton': r'class\s+\w+.*singleton|getInstance\(\)|static\s+\w+\s*\*\s*instance',
            # --- Tiger framework patterns ---
            # SLLooper abstraction (user code)
            'tiger_looper_var': r'\bSLLooper\s+\w+\s*(=|;|\()',
            'tiger_looper_ptr': r'\bsp<SLLooper>\s+\w+\s*(=|;|\()',
            'tiger_looper_new': r'\bnew\s+SLLooper\s*\(',
            'tiger_looper_mylooper': r'\bSLLooper::myLooper\s*\(',
            # Tiger message handler
            'tiger_handler_class': r'^\s*class\s+\w+\s*:\s*public\s+sl::Handler',
            'tiger_handle_message': r'\bvoid\s+handleMessage\s*\(\s*const\s+sp<sl::Message>&',
            # Binder/ServiceStub (Binder thread pool)
            'tiger_binder_stub_class': r'^\s*class\s+\w+::ServiceStub\b',
            'tiger_binder_stub_method': r'^\s*(?:\w+\s+)+\w+::ServiceStub::\w+\s*\(',
        }
        self.thread_entrypoints = set()  # Lưu tên hàm entrypoint thread phụ
    
    def parse_file(self, file_path: str) -> Dict:
        """
        Parse C++ file để tìm shared resources và thread usage
        
        Args:
            file_path: Đường dẫn đến file C++
            
        Returns:
            Dict: Kết quả phân tích file
        """
        logger.info(f"Đang phân tích file: {file_path}")
        result = {
            "shared_resources": [],
            "thread_usage": [],
            "mutex_usage": [],
            "atomic_usage": [],
            "thread_entry_functions": []  # Thông tin các hàm chạy trong context multi-thread
        }
        thread_vector_names = set()  # Lưu tên biến vector kiểu thread
        global_vars = set()
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                lines = content.split('\n')
            # Context tracking để phân biệt global vs function scope
            brace_level = 0
            in_function = False
            in_class = False
            in_namespace = False
            in_tiger_handler = False
            in_binder_stub = False
            in_binder_stub_class = False
            current_function = ""
            current_class_name = ""
            entry_func_map = {}
            # Chỉ track các hàm entrypoint thread, ghi ra file và line, không check bên trong nữa
            # Clean code: chỉ lưu thông tin hàm entrypoint
            for i, line in enumerate(lines, 1):
                stripped_line = line.strip()
                # Skip empty lines and comments
                if not stripped_line or stripped_line.startswith('//') or stripped_line.startswith('/*'):
                    continue
                # Count braces để track scope
                brace_level += stripped_line.count('{') - stripped_line.count('}')
                # --- Detect ServiceStub method outside class scope ---
                m_servicestub_func = re.search(r'(\w+)::ServiceStub::(\w+)\s*\(', stripped_line)
                if m_servicestub_func:
                    class_name = m_servicestub_func.group(1)
                    func_name = m_servicestub_func.group(2)
                    result["thread_entry_functions"].append({
                        "file": file_path,
                        "function": f"{class_name}::ServiceStub::{func_name}",
                        "line": i
                    })
                # --- Detect handleMessage method outside class scope ---
                # m_handlemsg_func = re.search(r'(\w+)::(\w+)::handleMessage\s*\(', stripped_line)
                # if m_handlemsg_func:
                #     class_name = m_handlemsg_func.group(1)
                #     handler_name = m_handlemsg_func.group(2)
                #     result["thread_entry_functions"].append({
                #         "file": file_path,
                #         "function": f"{class_name}::{handler_name}::handleMessage",
                #         "line": i
                #     })
                # --- Detect handleMessage method outside class scope ---
                # Trường hợp 1: SomeClass::SomeHandler::handleMessage(
                m_handlemsg_func2 = re.search(r'(\w+)::(\w+)::handleMessage\s*\(', stripped_line)
                if m_handlemsg_func2:
                    class_name = m_handlemsg_func2.group(1)
                    handler_name = m_handlemsg_func2.group(2)
                    result["thread_entry_functions"].append({
                        "file": file_path,
                        "function": f"{class_name}::{handler_name}::handleMessage",
                        "line": i
                    })
                # Trường hợp 2: ECallNGCallProcess::handleMessage(
                m_handlemsg_func1 = re.search(r'(\w+)::handleMessage\s*\(', stripped_line)
                if m_handlemsg_func1:
                    class_name = m_handlemsg_func1.group(1)
                    result["thread_entry_functions"].append({
                        "file": file_path,
                        "function": f"{class_name}::handleMessage",
                        "line": i
                    })
                # Detect class start
                m_class = re.search(self.patterns['class_start'], stripped_line)
                if m_class:
                    current_class_name = m_class.group(1)
                    if current_class_name.endswith('ServiceStub'):
                        in_binder_stub_class = True
                # Detect function/class/namespace starts
                if re.search(self.patterns['function_start'], stripped_line):
                    in_function = True
                    m_func = re.search(self.patterns['function_start'], stripped_line)
                    if m_func:
                        func_name = m_func.group(1)
                        # Đánh dấu hàm trong ServiceStub là thread entrypoint
                        if in_binder_stub_class:
                            result["thread_entry_functions"].append({
                                "file": file_path,
                                "function": f"{current_class_name}::{func_name}",
                                "line": i
                            })
                elif re.search(self.patterns['class_start'], stripped_line):
                    in_class = True
                elif re.search(self.patterns['namespace_start'], stripped_line):
                    in_namespace = True
                # Tiger handler class
                if re.search(self.patterns['tiger_handler_class'], stripped_line):
                    in_tiger_handler = True
                # Binder ServiceStub class (legacy)
                if re.search(self.patterns['tiger_binder_stub_class'], stripped_line):
                    in_binder_stub = True
                # handleMessage function
                if re.search(self.patterns['tiger_handle_message'], stripped_line):
                    current_function = "handleMessage"
                # ServiceStub method (legacy)
                if re.search(self.patterns['tiger_binder_stub_method'], stripped_line):
                    current_function = "ServiceStub"
                # Nhận diện tên biến vector kiểu thread
                m_vec = re.search(r'std::vector\s*<\s*std::thread\s*>\s+(\w+)', stripped_line)
                if m_vec:
                    thread_vector_names.add(m_vec.group(1))
                # Nếu phát hiện dòng tạo thread, lưu tên hàm entrypoint hoặc lambda
                if re.search(self.patterns['thread_create'], stripped_line) or re.search(r'emplace_back', stripped_line):
                    entry_func = self.extract_entrypoint_func(stripped_line)
                    if entry_func:
                        self.thread_entrypoints.add(entry_func)
                        # Tìm vị trí khai báo hàm entrypoint trong file hiện tại
                        for j, l in enumerate(lines, 1):
                            if re.search(rf'\b{entry_func}\b\s*\(', l):
                                result["thread_entry_functions"].append({
                                    "file": file_path,
                                    "function": entry_func,
                                    "line": j
                                })
                                break
                    # Nhận diện emplace_back với tên hàm, chỉ khi biến là vector thread
                    m_emp = re.search(r'(\w+)\.emplace_back\s*\((\w+)\)', stripped_line)
                    if m_emp:
                        vec_name = m_emp.group(1)
                        func_name = m_emp.group(2)
                        if vec_name in thread_vector_names:
                            for j, l in enumerate(lines, 1):
                                if re.search(rf'\b{func_name}\b\s*\(', l):
                                    result["thread_entry_functions"].append({
                                        "file": file_path,
                                        "function": func_name,
                                        "line": j
                                    })
                                    break
                    # Nếu là lambda thì chỉ log vị trí dòng
                    elif re.search(r'\[.*\]\s*\(.*\)\s*\{', stripped_line):
                        result["thread_entry_functions"].append({
                            "file": file_path,
                            "function": "lambda",
                            "line": i
                        })
                # Nhận diện tạo thread trực tiếp
                if re.search(r'std::thread\s+\w+\s*\(', stripped_line):
                    result["thread_entry_functions"].append({
                        "file": file_path,
                        "function": "lambda_or_func",
                        "line": i
                    })
                # Reset scope flags when braces close
                if brace_level == 0:
                    in_function = False
                    in_class = False
                    in_tiger_handler = False
                    in_binder_stub = False
                    in_binder_stub_class = False
                    current_function = ""
                    current_class_name = ""
                # Analyze patterns with context
                context = self.get_thread_context(stripped_line, in_function, current_function, in_tiger_handler, in_binder_stub, entry_func_map, i)
                # Ghi nhận biến toàn cục
                if not in_function and not in_class:
                    if match := re.search(self.patterns['global_var'], line):
                        var_type, var_name = match.groups()
                        if not any(keyword in var_type.lower() for keyword in ['include', 'define', 'pragma']):
                            global_vars.add(var_name)
                            entry = {
                                'file': file_path,
                                'line': i,
                                'type': 'global_var',
                                'name': var_name,
                                'var_type': var_type.strip(),
                                'scope': 'global',
                                'thread_context': context
                            }
                            result["shared_resources"].append(entry)
                # Ghi nhận mọi lần truy cập biến toàn cục
                for var in global_vars:
                    # Truy cập đọc/ghi (simple): tìm tên biến đứng độc lập hoặc với toán tử =, ++, --, +=, -=
                    if re.search(rf'\b{re.escape(var)}\b', stripped_line):
                        entry = {
                            'file': file_path,
                            'line': i,
                            'type': 'access',
                            'name': var,
                            'scope': 'global',
                            'thread_context': context
                        }
                        result["shared_resources"].append(entry)
                # Analyze patterns with context
                context = self.get_thread_context(stripped_line, in_function, current_function, in_tiger_handler, in_binder_stub, entry_func_map, i)
                self._analyze_line(stripped_line, i, file_path, result, 
                                 in_function, in_class, in_namespace, in_tiger_handler, in_binder_stub, current_function, context)
            # Xóa toàn bộ logic cache hàm, không còn dùng file_path_def
            # Danh sách các keyword C++ cần loại bỏ khi nhận diện hàm
            cpp_keywords = {"for", "if", "while", "switch", "return", "sizeof", "catch", "try", "else", "case", "break", "continue", "do", "goto", "new", "delete", "throw", "static_cast", "dynamic_cast", "reinterpret_cast", "const_cast", "typedef", "struct", "class", "enum", "union", "namespace", "public", "private", "protected", "template", "typename", "using", "this", "operator", "default", "virtual", "override", "final", "noexcept", "static", "const", "volatile", "extern", "inline", "friend", "explicit", "register", "mutable", "thread_local", "asm", "export"}
            # Danh sách các hàm thực sự chạy trong multi-thread context
            multi_thread_functions = []
            # Xóa toàn bộ phần truy vết hàm bên trong, chỉ giữ lại log entrypoint
            result["multi_thread_functions"] = []
        except Exception as e:
            logger.error(f"Error parsing {file_path}: {e}")
        if result["thread_entry_functions"]:
            logger.info(f"[THREAD ENTRY] Thread entry functions in {file_path}: {result['thread_entry_functions']}")
        return result

    def extract_entrypoint_func(self, line: str) -> str:
        # Đơn giản: tìm tên hàm truyền vào pthread_create/std::thread
        # Ví dụ: pthread_create(&tid, NULL, thread_func, NULL);
        m = re.search(r'pthread_create\s*\([^,]+,[^,]+,[^,]+,', line)
        if m:
            args = line.split(',')
            if len(args) >= 3:
                func = args[2].strip().replace(')', '').replace('(', '')
                return func
        # std::thread t(thread_func, ...)
        m2 = re.search(r'std::thread\s+\w+\s*\((\w+)', line)
        if m2:
            return m2.group(1)
        return None

    def get_thread_context(self, line, in_function, current_function, in_tiger_handler, in_binder_stub, entry_func_map, line_num):
        # Ưu tiên context đặc biệt
        if in_tiger_handler or current_function == "handleMessage":
            return "tiger_handler"
        if in_binder_stub or current_function == "ServiceStub":
            return "binder_stub"
        # Nếu đang trong hàm entrypoint thread phụ
        if current_function in self.thread_entrypoints:
            return "std_thread"
        return "main"

    def _analyze_line(self, line: str, line_num: int, file_path: str, result: Dict,
                     in_function: bool, in_class: bool, in_namespace: bool, in_tiger_handler: bool = False, in_binder_stub: bool = False, current_function: str = "", thread_context: str = None):
        """Phân tích một dòng code"""
        # Global variables (chỉ khi không trong function/class)
        if not in_function and not in_class:
            if match := re.search(self.patterns['global_var'], line):
                var_type, var_name = match.groups()
                if not any(keyword in var_type.lower() for keyword in ['include', 'define', 'pragma']):
                    entry = {
                        'file': file_path,
                        'line': line_num,
                        'type': 'global_var',
                        'name': var_name,
                        'var_type': var_type.strip(),
                        'scope': 'global'
                    }
                    if thread_context and thread_context != "main":
                        entry['thread_context'] = thread_context
                    result["shared_resources"].append(entry)
        # Static variables
        if match := re.search(self.patterns['static_var'], line):
            var_type, var_name = match.groups()
            scope = 'function_static' if in_function else 'file_static'
            entry = {
                'file': file_path,
                'line': line_num,
                'type': 'static_var',
                'name': var_name,
                'var_type': var_type.strip(),
                'scope': scope
            }
            if thread_context and thread_context != "main":
                entry['thread_context'] = thread_context
            result["shared_resources"].append(entry)
        # Thread usage
        if re.search(self.patterns['thread_create'], line, re.IGNORECASE):
            result["thread_usage"].append({
                'file': file_path,
                'line': line_num,
                'type': 'thread_creation',
                'code': line[:100]  # Limit length
            })
        # Tiger SLLooper usage
        for key in ['tiger_looper_var', 'tiger_looper_ptr', 'tiger_looper_new', 'tiger_looper_mylooper']:
            if key in self.patterns and re.search(self.patterns[key], line):
                result["thread_usage"].append({
                    'file': file_path,
                    'line': line_num,
                    'type': 'tiger_looper_thread',
                    'code': line[:100]
                })
        # Tiger handleMessage
        if re.search(self.patterns['tiger_handle_message'], line):
            result["thread_usage"].append({
                'file': file_path,
                'line': line_num,
                'type': 'tiger_handle_message',
                'code': line[:100]
            })
        # Binder ServiceStub method
        if re.search(self.patterns['tiger_binder_stub_method'], line):
            result["thread_usage"].append({
                'file': file_path,
                'line': line_num,
                'type': 'binder_stub_method',
                'code': line[:100]
            })
        # Mutex usage
        if re.search(self.patterns['mutex_usage'], line, re.IGNORECASE):
            result["mutex_usage"].append({
                'file': file_path,
                'line': line_num,
                'type': 'mutex_usage',
                'code': line[:100]
            })
        # Atomic usage
        if re.search(self.patterns['atomic_usage'], line, re.IGNORECASE):
            result["atomic_usage"].append({
                'file': file_path,
                'line': line_num,
                'type': 'atomic_usage',
                'code': line[:100]
            })

    def generate_thread_entry_markdown(self, thread_entry_functions: List[Dict]) -> str:
        """
        Sinh chuỗi markdown report cho các hàm entrypoint thread của một file
        Args:
            thread_entry_functions: List các dict chứa thông tin hàm entrypoint thread
        Returns:
            str: Chuỗi markdown
        """
        if not thread_entry_functions:
            return "No detect thread entrypoint functions."
        lines = []
        for entry in thread_entry_functions:
            func = entry.get("function", "?")
            line = entry.get("line", "?")
            lines.append(f"- {func} (line {line})")
        return '\n'.join(lines)

class RaceConditionAnalyzer:
    """Analyzer chính để phát hiện race conditions"""
    
    def __init__(self):
        self.parser = CppParser()
        self.tracker = PersistentTracker(analysis_type="race_analysis")

    def analyze_codebase(self, dir_path: str = None) -> AnalysisResult:
        """
        Phân tích thread entry points trong toàn bộ codebase - incremental analysis
        
        Args:
            dir_path: Thư mục cần phân tích
            
        Returns:
            AnalysisResult: Kết quả phân tích với thread entry points
        """
        # Always use src_dir from config
        target_dir = get_src_dir()
        
        logger.info(f"Starting incremental thread entry analysis: {target_dir}")
        
        # Collect all C++ files
        all_src_files = list_source_files(target_dir)
        
        # Get previously checked files from persistent storage
        checked_files = self.tracker.get_checked_files(target_dir)
        
        # Filter out files that haven't been checked (relative paths)
        remaining_files = [f for f in all_src_files if f not in checked_files]
        
        logger.info(f"Total source files: {len(all_src_files)}")
        logger.info(f"Previously checked files: {len(checked_files)}")
        logger.info(f"Remaining files to analyze: {len(remaining_files)}")
        
        # Handle case when all files have been checked
        if not remaining_files:
            return AnalysisResult(
                thread_usage={},
                summary={
                    "analysis_method": "incremental_thread_entry_analysis",
                    "status": "all_files_already_checked",
                    "directory": target_dir,
                    "total_files_in_directory": len(all_src_files),
                    "previously_checked_files": len(checked_files),
                    "newly_analyzed_files": 0,
                    "remaining_files": [],
                    "files_with_threads": 0,
                    "analysis_completeness": "all_files_checked",
                    "recommendations": ["All files have been analyzed in previous sessions"],
                    "session_stats": self.tracker.get_analysis_stats(target_dir),
                    "markdown_reports": {},
                    "file_summaries": {},
                    "all_src_files": all_src_files  # For tool handler context selection
                }
            )
        
        # Handle case when no C++ files found
        if len(all_src_files) == 0:
            return AnalysisResult(
                thread_usage={},
                summary={
                    "analysis_method": "incremental_thread_entry_analysis",
                    "status": "no_src_files_found",
                    "directory": target_dir,
                    "total_files_in_directory": 0,
                    "newly_analyzed_files": 0,
                    "files_with_threads": 0,
                    "recommendations": ["No C++ files found in the specified directory"],
                    "all_src_files": []
                }
            )
        
        # Only analyze remaining files (not checked yet)
        full_paths = [os.path.join(target_dir, f) for f in remaining_files]
        
        # Analyze each remaining file for thread entry points only
        all_resources = {}
        all_threads = {}
        markdown_reports = {}
        
        logger.info(f"Analyzing {len(remaining_files)} remaining files for thread entry points...")
        
        for i, file_path in enumerate(full_paths, 1):
            logger.info(f"Analyzing file {i}/{len(full_paths)}: {os.path.basename(file_path)}")
            analysis = self.parser.parse_file(file_path)
            all_resources[file_path] = analysis["shared_resources"]
            all_threads[file_path] = analysis["thread_usage"]
            
            # Generate markdown for thread entry functions
            markdown_md = self.parser.generate_thread_entry_markdown(analysis.get("thread_entry_functions", []))
            markdown_reports[file_path] = markdown_md
            
            # Log thread entry markdown for each file
            logger.info("[THREAD ENTRY MARKDOWN] File: %s\n%s", file_path, markdown_md)
        
        # Create detailed file summaries (focus on thread entry points only)
        file_summaries = {}
        for file_path in full_paths:
            file_name = os.path.basename(file_path)
            thread_count = len(all_threads.get(file_path, []))
            thread_entry_md = markdown_reports[file_path]
            
            summary_text = (
                f"### 1. 📁 **{file_name}**\n"
                f"**Path**: `{file_path}`\n"
                f"**Thread Usage**: {thread_count} thread-related operations"
            )
            if thread_entry_md and thread_entry_md.strip() and thread_entry_md.strip() != "No detect thread entrypoint functions.":
                summary_text += f"\n**Thread Entrypoints:**\n{thread_entry_md}"
            summary_text += "\n"
            file_summaries[file_path] = summary_text
        
        # Create comprehensive summary (no race detection)
        summary = {
            "analysis_method": "incremental_thread_entry_analysis",
            "directory": target_dir,
            "total_files_in_directory": len(all_src_files),
            "total_files_analyzed": len(remaining_files),
            "previously_checked_files": len(checked_files),
            "newly_analyzed_files": len(remaining_files),
            "remaining_files": remaining_files,
            "files_with_threads": len([f for f, threads in all_threads.items() if threads]),
            "analysis_completeness": "incremental_analysis",
            "markdown_reports": markdown_reports,
            "file_summaries": file_summaries,
            "session_stats": self.tracker.get_analysis_stats(target_dir),
            "all_src_files": all_src_files  # For tool handler context selection
        }
        
        logger.info(f"Thread entry analysis completed for {len(remaining_files)} files")
        
        return AnalysisResult(
            thread_usage=all_threads,
            summary=summary
        )
    
    def _build_resource_access_map(self, all_resources: Dict) -> Dict:
        """Xây dựng map của shared resources"""
        resource_access_map = {}
        
        for file_path, resources in all_resources.items():
            for resource in resources:
                resource_name = resource.get('name', 'unknown')
                if resource_name not in resource_access_map:
                    resource_access_map[resource_name] = []
                resource_access_map[resource_name].append(resource)
        
        return resource_access_map
    
    
    def _assess_severity(self, resource_name: str, accesses: List[Dict], all_threads: Dict) -> str:
        """Đánh giá mức độ nghiêm trọng của race condition"""
        # Lấy tập hợp các thread context truy cập biến
        contexts = set(access.get('thread_context', 'main') for access in accesses)
        if len(contexts) > 1:
            return "high"
        if any('global' in access.get('scope', '') for access in accesses):
            return "high"
        elif any('static' in access.get('type', '') for access in accesses):
            return "medium"
        else:
            return "low"

# Factory function
def analyze_race_conditions_in_codebase(dir_path: str = None) -> Dict:
    """
    Main entry point để phân tích race conditions
    
    Args:
        dir_path: Thư mục cần phân tích
        
    Returns:
        Dict: Kết quả phân tích dưới dạng dictionary
    """
    analyzer = RaceConditionAnalyzer()
    result = analyzer.analyze_codebase(dir_path)
    return result.to_dict()
