"""
AI-Powered Resource Leak Analyzer for Linux C++
Comprehensive analyzer for file descriptors, sockets, memory mappings, and other Linux resources
Modular architecture similar to memory_analyzer.py and race_analyzer.py
"""
import os
import re
from typing import Dict, List, Optional, Set, Tuple
from lgedv.modules.config import get_src_dir, setup_logging
from lgedv.modules.file_utils import list_source_files
from lgedv.modules.persistent_storage import PersistentTracker

logger = setup_logging()

class ResourceOperation:
    """Represent a Linux resource operation (open/close)"""
    def __init__(self, file_path: str, line_num: int, operation_type: str, 
                 variable: str, resource_type: str, details: str = ""):
        self.file_path = file_path
        self.line_num = line_num
        self.operation_type = operation_type  # 'open', 'close'
        self.variable = variable
        self.resource_type = resource_type  # 'file_descriptor', 'socket', etc.
        self.details = details
        self.scope = "unknown"

class ResourceFlow:
    """Represent resource flow across files"""
    def __init__(self, variable: str, resource_type: str):
        self.variable = variable
        self.resource_type = resource_type
        self.open_operations = []  # List of ResourceOperation
        self.close_operations = []  # List of ResourceOperation
        self.cross_file_transfers = []  # List of cross-file movements
        self.files_involved = set()
        
    def add_open_operation(self, operation: ResourceOperation):
        self.open_operations.append(operation)
        self.files_involved.add(operation.file_path)
        
    def add_close_operation(self, operation: ResourceOperation):
        self.close_operations.append(operation)
        self.files_involved.add(operation.file_path)
        
    def is_cross_file(self) -> bool:
        return len(self.files_involved) > 1
        
    def has_potential_leak(self) -> bool:
        #return len(self.open_operations) > len(self.close_operations)
        return len(self.open_operations) > 0 or  len(self.close_operations) > 0

class LinuxResourceParser:
    """Parser for Linux C++ resource operations"""
    
    def __init__(self):
        self.patterns = {
            # File descriptors - various open functions
            'file_open': r'(\w+)\s*=\s*open\s*\(',
            'file_open64': r'(\w+)\s*=\s*open64\s*\(',
            'file_creat': r'(\w+)\s*=\s*creat\s*\(',
            'file_openat': r'(\w+)\s*=\s*openat\s*\(',
            # POSIX shared memory open
            'shm_open': r'(\w+)\s*=\s*shm_open\s*\(',
            # epoll
            'epoll_create': r'(\w+)\s*=\s*epoll_create\s*\(',
            'epoll_create1': r'(\w+)\s*=\s*epoll_create1\s*\(',
            # eventfd
            'eventfd': r'(\w+)\s*=\s*eventfd\s*\(',
            # timerfd
            'timerfd_create': r'(\w+)\s*=\s*timerfd_create\s*\(',
            # signalfd
            'signalfd': r'(\w+)\s*=\s*signalfd\s*\(',
            # inotify
            'inotify_init': r'(\w+)\s*=\s*inotify_init\s*\(',
            'inotify_init1': r'(\w+)\s*=\s*inotify_init1\s*\(',
            # POSIX message queue
            'mq_open': r'(\w+)\s*=\s*mq_open\s*\(',
            # POSIX semaphore
            'sem_open': r'(\w+)\s*=\s*sem_open\s*\(',
            # dup/dup2/dup3
            'dup': r'(\w+)\s*=\s*dup\s*\(',
            'dup2': r'(\w+)\s*=\s*dup2\s*\(',
            'dup3': r'(\w+)\s*=\s*dup3\s*\(',
            # FILE streams
            'fopen': r'(\w+)\s*=\s*fopen\s*\(',
            'fdopen': r'(\w+)\s*=\s*fdopen\s*\(',
            'freopen': r'(\w+)\s*=\s*freopen\s*\(',
            # Socket operations
            'socket_create': r'(\w+)\s*=\s*socket\s*\(',
            'socket_accept': r'(\w+)\s*=\s*accept\s*\(',
            'socket_accept4': r'(\w+)\s*=\s*accept4\s*\(',
            # Memory mapping
            'mmap': r'(\w+)\s*=\s*mmap\s*\(',
            'mmap64': r'(\w+)\s*=\s*mmap64\s*\(',
            # Directory handles
            'opendir': r'(\w+)\s*=\s*opendir\s*\(',
            'fdopendir': r'(\w+)\s*=\s*fdopendir\s*\(',
            # IPC resources
            'shmget': r'(\w+)\s*=\s*shmget\s*\(',
            'semget': r'(\w+)\s*=\s*semget\s*\(',
            'msgget': r'(\w+)\s*=\s*msgget\s*\(',
            'shmat': r'(\w+)\s*=\s*shmat\s*\(',
            # Pipes
            'pipe_create': r'pipe\s*\(\s*(\w+)\s*\)',
            'pipe2_create': r'pipe2\s*\(\s*(\w+)\s*,',
            # Close patterns
            'close_fd': r'close\s*\(\s*(\w+)\s*\)',
            'fclose_stream': r'fclose\s*\(\s*(\w+)\s*\)',
            'munmap_mapping': r'munmap\s*\(\s*(\w+)\s*,',
            'closedir_dir': r'closedir\s*\(\s*(\w+)\s*\)',
            'shmdt_shm': r'shmdt\s*\(\s*(\w+)\s*\)',
            # POSIX shared memory unlink
            'shm_unlink': r'shm_unlink\s*\(\s*([\w\d_]+)\s*\)',
            # POSIX message queue close/unlink
            'mq_close': r'mq_close\s*\(\s*(\w+)\s*\)',
            'mq_unlink': r'mq_unlink\s*\(\s*([\w\d_]+)\s*\)',
            # POSIX semaphore close/unlink
            'sem_close': r'sem_close\s*\(\s*(\w+)\s*\)',
            'sem_unlink': r'sem_unlink\s*\(\s*([\w\d_]+)\s*\)',
            'shmctl_remove': r'shmctl\s*\([^,]+,\s*IPC_RMID',
            'semctl_remove': r'semctl\s*\([^,]+,\s*[^,]+,\s*IPC_RMID',
            'msgctl_remove': r'msgctl\s*\([^,]+,\s*IPC_RMID',
            # Function signatures that return resources
            'return_resource': r'^\s*([^=]*\*[^=]*|int|FILE\*)\s+(\w+)\s*\([^)]*\)',
            'function_call': r'(\w+)\s*\([^)]*\)',
            # Cross-file indicators
            'extern_decl': r'extern\s+([^;]+);',
            'include_header': r'#include\s*[<"]([^>"]+)[>"]',
        }
    
    def parse_file(self, file_path: str) -> Dict:
        """Parse file for Linux resource operations"""
        result = {
            "resource_operations": [],
            "function_definitions": [],
            "includes": [],
            "cross_file_calls": []
        }
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                lines = content.split('\n')
            
            current_function = None
            brace_level = 0
            
            for i, line in enumerate(lines, 1):
                stripped_line = line.strip()
                
                # Skip comments and empty lines
                if not stripped_line or stripped_line.startswith('//') or stripped_line.startswith('/*'):
                    continue
                
                # Track braces for scope
                brace_level += stripped_line.count('{') - stripped_line.count('}')
                
                # Parse resource operations
                self._parse_line(stripped_line, i, file_path, result, current_function)
                
                # Update function context
                if match := re.search(self.patterns['return_resource'], stripped_line):
                    current_function = match.group(2)
                elif brace_level == 0:
                    current_function = None
        
        except Exception as e:
            logger.error(f"Error parsing {file_path}: {e}")
        
        return result
    
    def _parse_line(self, line: str, line_num: int, file_path: str, result: Dict, current_function: str):
        """Parse a single line for resource operations"""
        
        # Resource open operations
        resource_open_map = {
            'file_open': 'file_descriptor',
            'file_open64': 'file_descriptor',
            'file_creat': 'file_descriptor',
            'file_openat': 'file_descriptor',
            'shm_open': 'shared_memory',
            'epoll_create': 'epoll_fd',
            'epoll_create1': 'epoll_fd',
            'eventfd': 'event_fd',
            'timerfd_create': 'timer_fd',
            'signalfd': 'signal_fd',
            'inotify_init': 'inotify_fd',
            'inotify_init1': 'inotify_fd',
            'mq_open': 'posix_mq',
            'sem_open': 'posix_sem',
            'dup': 'file_descriptor',
            'dup2': 'file_descriptor',
            'dup3': 'file_descriptor',
            'fopen': 'file_stream',
            'fdopen': 'file_stream',
            'freopen': 'file_stream',
            'socket_create': 'socket',
            'socket_accept': 'socket',
            'socket_accept4': 'socket',
            'mmap': 'memory_mapping',
            'mmap64': 'memory_mapping',
            'opendir': 'directory_handle',
            'fdopendir': 'directory_handle',
            'shmget': 'shared_memory',
            'semget': 'semaphore',
            'msgget': 'message_queue',
            'shmat': 'shared_memory_attach',
        }
        
        for pattern_name, resource_type in resource_open_map.items():
            if match := re.search(self.patterns[pattern_name], line):
                var_name = match.group(1)
                operation = ResourceOperation(
                    file_path=file_path,
                    line_num=line_num,
                    operation_type='open',
                    variable=var_name,
                    resource_type=resource_type,
                    details=pattern_name
                )
                operation.scope = current_function or "global"
                result["resource_operations"].append(operation)
        
        # Special case for pipe operations
        if match := re.search(self.patterns['pipe_create'], line):
            pipe_var = match.group(1)
            operation = ResourceOperation(
                file_path=file_path,
                line_num=line_num,
                operation_type='open',
                variable=pipe_var,
                resource_type='pipe',
                details="pipe"
            )
            operation.scope = current_function or "global"
            result["resource_operations"].append(operation)
        
        # Resource close operations
        resource_close_map = {
            'close_fd': ['file_descriptor', 'socket', 'pipe', 'shared_memory', 'epoll_fd', 'event_fd', 'timer_fd', 'signal_fd', 'inotify_fd'],
            'fclose_stream': ['file_stream'],
            'munmap_mapping': ['memory_mapping'],
            'closedir_dir': ['directory_handle'],
            'shmdt_shm': ['shared_memory_attach'],
            'shm_unlink': ['shared_memory'],
            'mq_close': ['posix_mq'],
            'mq_unlink': ['posix_mq'],
            'sem_close': ['posix_sem'],
            'sem_unlink': ['posix_sem'],
        }
        
        for pattern_name, resource_types in resource_close_map.items():
            if match := re.search(self.patterns[pattern_name], line):
                var_name = match.group(1)
                for resource_type in resource_types:
                    operation = ResourceOperation(
                        file_path=file_path,
                        line_num=line_num,
                        operation_type='close',
                        variable=var_name,
                        resource_type=resource_type,
                        details=pattern_name
                    )
                    operation.scope = current_function or "global"
                    result["resource_operations"].append(operation)
        
        # IPC cleanup operations
        if re.search(self.patterns['shmctl_remove'], line):
            result["resource_operations"].append(ResourceOperation(
                file_path=file_path,
                line_num=line_num,
                operation_type='close',
                variable='ipc_shm',
                resource_type='shared_memory',
                details='shmctl_remove'
            ))
        
        # Function calls (potential cross-file operations)
        if match := re.search(self.patterns['function_call'], line):
            func_name = match.group(1)
            if not func_name.startswith('std::') and func_name not in ['printf', 'scanf', 'strlen']:
                result["cross_file_calls"].append({
                    'line': line_num,
                    'function': func_name,
                    'context': line[:100]
                })
        
        # Includes
        if match := re.search(self.patterns['include_header'], line):
            header = match.group(1)
            result["includes"].append(header)

class ResourceAnalyzer:
    """
    Linux C++ Resource Leak Analyzer with full codebase analysis
    Modular architecture similar to memory_analyzer.py
    """
    
    def __init__(self):
        self.parser = LinuxResourceParser()
        self.tracker = PersistentTracker(analysis_type="resource_analysis")  # Add persistent storage

    
    def analyze_codebase(self, dir_path: str = None) -> Dict:
        """
        Analyze resource leaks in entire codebase - always uses src_dir from config
        
        Args:
            dir_path: IGNORED - always uses src_dir from config like check_leaks
            
        Returns:
            Dict: Comprehensive analysis results
        """
        # Always use src_dir from config, ignore passed dir_path
        target_dir = get_src_dir()
        
        logger.info(f"Starting incremental resource leak analysis: {target_dir}")
        
        # Collect all C++ files
        all_src_files = list_source_files(target_dir)
        
        # Get previously checked files from persistent storage
        checked_files = self.tracker.get_checked_files(target_dir)
        
        # Filter out files that haven't been checked (relative paths)
        remaining_files = [f for f in all_src_files if f not in checked_files]
        
        logger.info(f"Total source files: {len(all_src_files)}")
        logger.info(f"Previously checked files: {len(checked_files)}")
        logger.info(f"Remaining files to analyze: {len(remaining_files)}")
        
        if not remaining_files:
            logger.info(f"All files in directory {target_dir} have already been checked.")
            return {
                "analysis_method": "incremental_resource_analysis",
                "status": "all_files_already_checked",
                "directory": target_dir,
                "files_analyzed": 0,
                "total_files": len(all_src_files),
                "checked_files": len(checked_files),
                "remaining_files": 0,
                "resource_leaks": [],
                "recommendations": ["All files have been analyzed in previous sessions"],
                "session_stats": self.tracker.get_analysis_stats(target_dir)
            }
        
        if len(all_src_files) == 0:
            logger.info(f"No source files found in directory: {target_dir}")
            return {
                "analysis_method": "incremental_resource_analysis",
                "status": "no_src_files_found",
                "directory": target_dir,
                "files_analyzed": 0,
                "resource_leaks": [],
                "recommendations": ["No C++ files found in the specified directory"]
            }
        
        # Only analyze remaining files (not checked yet)
        full_paths = [os.path.join(target_dir, f) for f in remaining_files]
        
        # Analyze each file
        all_resource_ops = {}
        all_includes = {}
        all_cross_file_calls = {}
        
        logger.info(f"Analyzing {len(remaining_files)} remaining files for resource leaks...")
        
        for i, file_path in enumerate(full_paths, 1):
            logger.info(f"Analyzing file {i}/{len(full_paths)}: {os.path.basename(file_path)}")
            analysis = self.parser.parse_file(file_path)
            all_resource_ops[file_path] = analysis["resource_operations"]
            all_includes[file_path] = analysis["includes"]
            all_cross_file_calls[file_path] = analysis["cross_file_calls"]
        
        # Build resource flow map
        resource_flows = self._build_resource_flow_map(all_resource_ops)
        
        # Create dynamic groups for related files
        resource_groups = self._create_dynamic_groups(resource_flows, all_includes, all_cross_file_calls, all_resource_ops)
        
        # Detect resource leaks
        detected_leaks = self._detect_resource_leaks(resource_groups, resource_flows)

        # AI context for complex cases
        ai_context = self._prepare_ai_context_for_complex_cases(detected_leaks, resource_groups)
        
        # Summary
        summary = {
            "total_files_in_directory": len(all_src_files),
            "previously_checked_files": len(checked_files),
            "newly_analyzed_files": len(remaining_files),
            "resource_operations_found": sum(len(ops) for ops in all_resource_ops.values()),
            "cross_file_flows": len([f for f in resource_flows.values() if f.is_cross_file()]),
            "potential_leaks": len(detected_leaks),
            "dynamic_groups": len(resource_groups),
            "analysis_completeness": "incremental_analysis"
        }

        logger.info(f"Resource analysis summary: {summary}")
        logger.info(f"[RESOURCE_DEBUG] len(remaining_files) = {len(remaining_files)}")
        logger.info(f"[RESOURCE_DEBUG] remaining_files = {remaining_files}")
        logger.info(f"[RESOURCE_DEBUG] len(all_src_files) = {len(all_src_files)}")
        logger.info(f"[RESOURCE_DEBUG] all_src_files = {all_src_files}")
        logger.info(f"[RESOURCE_DEBUG] len(checked_files) = {len(checked_files)}")
        logger.info(f"[RESOURCE_DEBUG] checked_files = {checked_files}")
        logger.info(f"[RESOURCE_DEBUG] target_dir = {target_dir}")

        return {
            "analysis_method": "incremental_resource_analysis_with_dynamic_grouping",
            "directory": target_dir,
            "files_analyzed": len(remaining_files),
            "remaining_files": remaining_files,  # Add this for tool handler
            "resource_flows": {k: self._serialize_resource_flow(v) for k, v in resource_flows.items()},
            "detected_leaks": detected_leaks,
            "dynamic_groups": resource_groups,
            "ai_context_for_complex_cases": ai_context,
            "summary": summary,
            "recommendations": self._generate_recommendations(detected_leaks, resource_flows),
            "session_stats": self.tracker.get_analysis_stats(target_dir)
        }
    
    def analyze_directory(self, dir_path: str = None) -> List[Dict]:
        """
        Simple directory analysis - always uses src_dir from config like check_leaks
        
        Args:
            dir_path: IGNORED - always uses src_dir from config
            
        Returns:
            List[Dict]: List of resource leak findings
        """
        # Always use src_dir from config, ignore passed dir_path
        target_dir = get_src_dir()
        analysis = self.analyze_codebase(target_dir)
        logger.info(f"Resource leak analysis completed for directory: {target_dir}")
        return analysis.get("detected_leaks", [])
    
    def _build_resource_flow_map(self, all_resource_ops: Dict) -> Dict[str, ResourceFlow]:
        """Build map of resource flows across files"""
        resource_flows = {}
        
        # Collect all resource operations by variable name and type
        for file_path, operations in all_resource_ops.items():
            for op in operations:
                flow_key = f"{op.variable}_{op.resource_type}"
                
                if flow_key not in resource_flows:
                    resource_flows[flow_key] = ResourceFlow(op.variable, op.resource_type)
                
                flow = resource_flows[flow_key]
                
                if op.operation_type == 'open':
                    flow.add_open_operation(op)
                elif op.operation_type == 'close':
                    flow.add_close_operation(op)
        
        return resource_flows
    
    def _create_dynamic_groups(self, resource_flows: Dict[str, ResourceFlow], 
                              all_includes: Dict, all_cross_file_calls: Dict, all_resource_ops: Dict) -> List[Dict]:
        """Create dynamic groups of files with related resource operations"""
        groups = []
        processed_files = set()
        
        # Group 1: Files with cross-file resource flows
        for flow_key, flow in resource_flows.items():
            if flow.is_cross_file() and len(flow.files_involved) > 1:
                group_files = list(flow.files_involved)
                
                # Extend group with include relationships
                extended_files = set(group_files)
                for file_path in group_files:
                    for included in all_includes.get(file_path, []):
                        for other_file in all_includes.keys():
                            if included in os.path.basename(other_file):
                                extended_files.add(other_file)
                
                if extended_files not in [set(g['files']) for g in groups]:
                    groups.append({
                        'type': 'cross_file_resource_flow',
                        'variable': flow.variable,
                        'resource_type': flow.resource_type,
                        'files': list(extended_files),
                        'reason': f'Cross-file resource flow for {flow.resource_type} {flow.variable}'
                    })
                    processed_files.update(extended_files)
        
        # Group 2: Files with resource operations not yet grouped
        remaining_files = []
        for file_path, operations in all_resource_ops.items():
            if file_path not in processed_files and len(operations) > 0:
                remaining_files.append(file_path)
        
        # Batch remaining files
        batch_size = 5
        for i in range(0, len(remaining_files), batch_size):
            batch = remaining_files[i:i+batch_size]
            groups.append({
                'type': 'resource_hotspot_batch',
                'files': batch,
                'reason': f'Batch {i//batch_size + 1} of files with resource operations'
            })
        
        return groups
    
    def _detect_resource_leaks(self, resource_groups: List[Dict], 
                             resource_flows: Dict[str, ResourceFlow]) -> List[Dict]:
        """Detect resource leaks in groups"""
        detected_leaks = []
        
        for flow_key, flow in resource_flows.items():
            if flow.has_potential_leak():
                leak_info = {
                    'variable': flow.variable,
                    'resource_type': flow.resource_type,
                    'severity': self._get_severity(flow.resource_type, flow.is_cross_file()),
                    'type': 'cross_file_leak' if flow.is_cross_file() else 'single_file_leak',
                    'files_involved': list(flow.files_involved),
                    'open_operations': len(flow.open_operations),
                    'close_operations': len(flow.close_operations),
                    'open_details': [
                        {
                            'file': op.file_path,
                            'line': op.line_num,
                            'scope': op.scope,
                            'details': op.details
                        } for op in flow.open_operations
                    ],
                    'close_details': [
                        {
                            'file': op.file_path,
                            'line': op.line_num,
                            'scope': op.scope,
                            'details': op.details
                        } for op in flow.close_operations
                    ],
                    'recommendation': self._get_recommendation(flow.resource_type)
                }
                leak_lines = []
                leak_lines.extend([op['line'] for op in leak_info['open_details']])
                leak_lines.extend([op['line'] for op in leak_info['close_details']])
                leak_info['leak_lines'] = leak_lines
                detected_leaks.append(leak_info)
        
        return detected_leaks
    
    def _get_severity(self, resource_type: str, is_cross_file: bool) -> str:
        """Get severity level for resource type"""
        base_severity = {
            'socket': 'critical',
            'file_descriptor': 'high',
            'memory_mapping': 'high',
            'shared_memory': 'high',
            'semaphore': 'high',
            'message_queue': 'medium',
            'file_stream': 'medium',
            'directory_handle': 'medium',
            'pipe': 'medium'
        }
        
        severity = base_severity.get(resource_type, 'low')
        
        # Escalate severity for cross-file leaks
        if is_cross_file and severity != 'critical':
            severity_order = ['low', 'medium', 'high', 'critical']
            current_index = severity_order.index(severity)
            if current_index < len(severity_order) - 1:
                severity = severity_order[current_index + 1]
        
        return severity
    
    def _get_recommendation(self, resource_type: str) -> str:
        """Get fix recommendation for resource type"""
        recommendations = {
            'file_descriptor': 'Add close() call before function return or use RAII wrapper',
            'file_stream': 'Add fclose() call before function return or use std::ifstream/ofstream',
            'socket': 'Add close() call to prevent socket leak or use RAII socket wrapper',
            'memory_mapping': 'Add munmap() call to release mapping or use RAII wrapper',
            'directory_handle': 'Add closedir() call to close directory',
            'shared_memory': 'Add shmdt() and shmctl(IPC_RMID) calls to cleanup shared memory',
            'semaphore': 'Add semctl(IPC_RMID) call to remove semaphore',
            'message_queue': 'Add msgctl(IPC_RMID) call to remove message queue',
            'pipe': 'Add close() calls for both pipe ends'
        }
        return recommendations.get(resource_type, 'Ensure proper resource cleanup')
    
    def _prepare_ai_context_for_complex_cases(self, detected_leaks: List[Dict], 
                                            resource_groups: List[Dict]) -> Dict:
        """Prepare AI context for complex resource leak cases"""
        complex_cases = []
        
        for leak in detected_leaks:
            if leak['severity'] in ['critical', 'high'] or len(leak['files_involved']) > 2:
                file_contents = {}
                for file_path in leak['files_involved']:
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                            if len(content) > 1500:
                                content = content[:1500] + "\n\n// ... [TRUNCATED] ..."
                            file_contents[os.path.basename(file_path)] = content
                    except Exception as e:
                        file_contents[os.path.basename(file_path)] = f"// Error reading: {e}"
                
                complex_cases.append({
                    'leak_info': leak,
                    'file_contents': file_contents,
                    'analysis_focus': [
                        f"Cross-file {leak['resource_type']} flow for variable '{leak['variable']}'",
                        "RAII compliance for Linux resources",
                        "Resource ownership transfer mechanisms",
                        "Cleanup in error paths and exceptions"
                    ]
                })
        
        return {
            'complex_cases': complex_cases,
            'ai_analysis_needed': len(complex_cases) > 0,
            'analysis_focus': [
                "Linux resource lifecycle management",
                "Cross-file resource ownership verification",
                "Exception safety in resource handling",
                "IPC resource cleanup patterns"
            ]
        }
    
    def _serialize_resource_flow(self, flow: ResourceFlow) -> Dict:
        """Serialize ResourceFlow object to dict"""
        return {
            'variable': flow.variable,
            'resource_type': flow.resource_type,
            'is_cross_file': flow.is_cross_file(),
            'has_potential_leak': flow.has_potential_leak(),
            'files_involved': list(flow.files_involved),
            'open_count': len(flow.open_operations),
            'close_count': len(flow.close_operations)
        }
    
    def _generate_recommendations(self, detected_leaks: List[Dict], 
                                resource_flows: Dict[str, ResourceFlow]) -> List[str]:
        """Generate actionable recommendations"""
        recommendations = []
        
        if not detected_leaks:
            recommendations.append("✅ No obvious resource leaks detected in static analysis")
        else:
            recommendations.append(f"⚠️  {len(detected_leaks)} potential resource leaks detected")
            
            critical_leaks = [l for l in detected_leaks if l['severity'] == 'critical']
            if critical_leaks:
                recommendations.append(f"🔴 {len(critical_leaks)} critical resource leaks require immediate attention")
                
            cross_file_leaks = [l for l in detected_leaks if l['type'] == 'cross_file_leak']
            if cross_file_leaks:
                recommendations.append(f"🔴 {len(cross_file_leaks)} cross-file resource leaks detected")
                recommendations.append("Implement RAII pattern for automatic resource cleanup")
                
        # Pattern-based recommendations
        resource_types = set(flow.resource_type for flow in resource_flows.values())
        
        if 'socket' in resource_types:
            recommendations.append("Consider using RAII socket wrappers for automatic cleanup")
        if 'shared_memory' in resource_types or 'semaphore' in resource_types:
            recommendations.append("Implement proper IPC resource cleanup in error paths")
        if any(flow.is_cross_file() for flow in resource_flows.values()):
            recommendations.append("Establish clear resource ownership policies for cross-file transfers")
            
        recommendations.append("Run dynamic analysis tools (Valgrind/strace) for runtime verification")
        
        return recommendations

# Factory function for compatibility
def analyze_resources(dir_path: str = None) -> Dict:
    """
    Main entry point for full codebase resource leak analysis
    Always uses src_dir from config like check_leaks
    
    Args:
        dir_path: IGNORED - always uses src_dir from config
        
    Returns:
        Dict: Comprehensive analysis results
    """
    analyzer = ResourceAnalyzer()
    return analyzer.analyze_codebase()
