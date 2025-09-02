"""
AI-Powered Memory Leak Analyzer v2 - Full Analysis with Dynamic Grouping
Học hỏi từ race_analyzer để phân tích tất cả files và detect cross-file memory leaks
"""
import os
import re
from typing import Dict, List, Optional, Set, Tuple
from lgedv.modules.config import get_src_dir, setup_logging
from lgedv.modules.file_utils import list_source_files
from lgedv.modules.persistent_storage import PersistentTracker

logger = setup_logging()

class MemoryOperation:
    """Represent một memory operation (allocation/deallocation)"""
    def __init__(self, file_path: str, line_num: int, operation_type: str, 
                 variable: str, details: str = ""):
        self.file_path = file_path
        self.line_num = line_num
        self.operation_type = operation_type  # 'alloc', 'dealloc', 'return', 'param'
        self.variable = variable
        self.details = details
        self.scope = "unknown"
        
class MemoryFlow:
    """Represent memory flow across files"""
    def __init__(self, variable: str):
        self.variable = variable
        self.allocations = []  # List of MemoryOperation
        self.deallocations = []  # List of MemoryOperation
        self.cross_file_transfers = []  # List of cross-file movements
        self.files_involved = set()
        
    def add_allocation(self, operation: MemoryOperation):
        self.allocations.append(operation)
        self.files_involved.add(operation.file_path)
        
    def add_deallocation(self, operation: MemoryOperation):
        self.deallocations.append(operation)
        self.files_involved.add(operation.file_path)
        
    def is_cross_file(self) -> bool:
        return len(self.files_involved) > 1
        
    def has_potential_leak(self) -> bool:
        # return len(self.allocations) > len(self.deallocations)
        return len(self.allocations) > 0 or  len(self.deallocations) > 0

class CppMemoryParser:
    """Parser để phân tích memory operations trong C++ code"""
    
    def __init__(self):
        self.patterns = {
            # Memory allocations - fixed patterns
            'new_alloc': r'(\w+)\s*=\s*new\s+(?!\w+\[)([^;{}\n]+)',  # new but not new[]
            'new_array': r'(\w+)\s*=\s*new\s+\w+\[',  # new[] arrays (simplified)
            'malloc_alloc': r'(\w+)\s*=\s*(?:malloc|calloc|realloc)\s*\(',
            'smart_ptr': r'(?:std::)?(?:unique_ptr|shared_ptr|make_unique|make_shared)',
            
            # Memory deallocations - fixed patterns  
            'delete_op': r'delete\s+(?!\[\])(\w+)',  # delete but not delete[]
            'delete_array': r'delete\[\]\s*(\w+)',  # delete[] arrays
            'free_op': r'free\s*\(\s*(\w+)\s*\)',
            
            # Function signatures that return pointers
            'return_ptr': r'^\s*([^=]*\*[^=]*)\s+(\w+)\s*\([^)]*\)',
            'function_call': r'(\w+)\s*\([^)]*\)',
            
            # Cross-file indicators
            'extern_decl': r'extern\s+([^;]+);',
            'include_header': r'#include\s*[<"]([^>"]+)[>"]',
            
            # Class/struct definitions
            'class_def': r'^\s*(?:class|struct)\s+(\w+)',
            'destructor': r'~(\w+)\s*\(',
            'constructor': r'^\s*(\w+)\s*\([^)]*\)\s*(?::|{)',
        }
    
    def parse_file(self, file_path: str) -> Dict:
        """Parse một file để tìm memory operations"""
        result = {
            "memory_operations": [],
            "function_definitions": [],
            "class_definitions": [],
            "includes": [],
            "cross_file_calls": []
        }
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                lines = content.split('\n')
            
            # Track context
            current_function = None
            current_class = None
            brace_level = 0
            
            for i, line in enumerate(lines, 1):
                stripped_line = line.strip()
                
                # Skip comments and empty lines
                if not stripped_line or stripped_line.startswith('//') or stripped_line.startswith('/*'):
                    continue
                
                # Track braces for scope
                brace_level += stripped_line.count('{') - stripped_line.count('}')
                
                # Parse different patterns
                self._parse_line(stripped_line, i, file_path, result, current_function, current_class)
                
                # Update context
                if match := re.search(self.patterns['class_def'], stripped_line):
                    current_class = match.group(1)
                elif match := re.search(self.patterns['return_ptr'], stripped_line):
                    current_function = match.group(2)
                elif brace_level == 0:
                    current_function = None
                    current_class = None
        
        except Exception as e:
            logger.error(f"Error parsing {file_path}: {e}")
        
        return result
    
    def _parse_line(self, line: str, line_num: int, file_path: str, result: Dict,
                   current_function: str, current_class: str):
        """Parse một dòng code để tìm memory operations"""
        
        # Memory allocations
        if match := re.search(self.patterns['new_array'], line):
            # Check new[] first để tránh conflict với new
            var_name = match.group(1)
            operation = MemoryOperation(
                file_path=file_path,
                line_num=line_num,
                operation_type='alloc',
                variable=var_name,
                details="new[] array"
            )
            operation.scope = f"{current_class}::{current_function}" if current_class and current_function else current_function or "global"
            result["memory_operations"].append(operation)
        
        elif match := re.search(self.patterns['new_alloc'], line):
            var_name, alloc_type = match.groups()
            operation = MemoryOperation(
                file_path=file_path,
                line_num=line_num,
                operation_type='alloc',
                variable=var_name,
                details=f"new {alloc_type.strip()}"
            )
            operation.scope = f"{current_class}::{current_function}" if current_class and current_function else current_function or "global"
            result["memory_operations"].append(operation)
        
        elif re.search(self.patterns['malloc_alloc'], line):
            if match := re.search(r'(\w+)\s*=', line):
                var_name = match.group(1)
                operation = MemoryOperation(
                    file_path=file_path,
                    line_num=line_num,
                    operation_type='alloc',
                    variable=var_name,
                    details="malloc family"
                )
                operation.scope = f"{current_class}::{current_function}" if current_class and current_function else current_function or "global"
                result["memory_operations"].append(operation)
        
        # Memory deallocations
        elif match := re.search(self.patterns['delete_array'], line):
            # Check delete[] first để tránh conflict với delete
            var_name = match.group(1)
            operation = MemoryOperation(
                file_path=file_path,
                line_num=line_num,
                operation_type='dealloc',
                variable=var_name,
                details="delete[]"
            )
            operation.scope = f"{current_class}::{current_function}" if current_class and current_function else current_function or "global"
            result["memory_operations"].append(operation)
        
        elif match := re.search(self.patterns['delete_op'], line):
            var_name = match.group(1)
            operation = MemoryOperation(
                file_path=file_path,
                line_num=line_num,
                operation_type='dealloc',
                variable=var_name,
                details="delete"
            )
            operation.scope = f"{current_class}::{current_function}" if current_class and current_function else current_function or "global"
            result["memory_operations"].append(operation)
        
        elif match := re.search(self.patterns['free_op'], line):
            var_name = match.group(1)
            operation = MemoryOperation(
                file_path=file_path,
                line_num=line_num,
                operation_type='dealloc',
                variable=var_name,
                details="free"
            )
            operation.scope = f"{current_class}::{current_function}" if current_class and current_function else current_function or "global"
            result["memory_operations"].append(operation)
        
        # Function calls (potential cross-file operations)
        elif match := re.search(self.patterns['function_call'], line):
            func_name = match.group(1)
            # Skip standard library functions
            if not func_name.startswith('std::') and func_name not in ['printf', 'scanf', 'strlen', 'strcpy']:
                result["cross_file_calls"].append({
                    'line': line_num,
                    'function': func_name,
                    'context': line[:100]
                })
        
        # Includes
        elif match := re.search(self.patterns['include_header'], line):
            header = match.group(1)
            result["includes"].append(header)

class MemoryAnalyzer:
    """
    Memory Leak Analyzer với full analysis và dynamic grouping
    Học hỏi từ race_analyzer để phân tích toàn bộ codebase
    """
    
    def __init__(self):
        self.parser = CppMemoryParser()
        self.tracker = PersistentTracker(analysis_type="memory_analysis")
        
    def analyze_codebase(self, dir_path: str = None) -> Dict:
        """
        Phân tích memory leak trong toàn bộ codebase với dynamic grouping
        
        Args:
            dir_path: Thư mục cần phân tích
            
        Returns:
            Dict: Kết quả phân tích chi tiết
        """
        if dir_path is None:
            dir_path = get_src_dir()
        
        logger.info(f"Starting full codebase memory leak analysis: {dir_path}")
        
        # Thu thập tất cả file C++
        all_src_files = list_source_files(dir_path)
        
        # Lấy danh sách file đã check từ persistent storage
        checked_files = self.tracker.get_checked_files(dir_path)
        
        # Lọc ra các file chưa check (relative paths)
        remaining_files = [f for f in all_src_files if f not in checked_files]
        
        logger.info(f"Total source files: {len(all_src_files)}")
        logger.info(f"Previously checked files: {len(checked_files)}")
        logger.info(f"Remaining files to analyze: {len(remaining_files)}")
        
        # Nếu không còn file nào để phân tích, trả về kết quả tóm tắt
        if not remaining_files:
            # return {
            #     "analysis_method": "incremental_analysis",
            #     "status": "all_files_already_checked",
            #     "directory": dir_path,
            #     "total_files": len(all_src_files),
            #     "checked_files": len(checked_files),
            #     "remaining_files": 0,
            #     "memory_leaks": [],
            #     "recommendations": ["All files have been analyzed in previous sessions"],
            #     "session_stats": self.tracker.get_analysis_stats(dir_path)
            # }
            summary = {
            "total_files_in_directory": len(all_src_files),
            "previously_checked_files": len(checked_files),
            "newly_analyzed_files": len(remaining_files),          
            "analysis_completeness": "incremental_analysis"
            }
        
            return {
                "analysis_method": "incremental_analysis_with_dynamic_grouping",
                "directory": dir_path,           
                "remaining_files": remaining_files,  # Add this for tool handler                
                "summary": summary
            }
        
        if len(all_src_files) == 0:
            return {
                "analysis_method": "incremental_analysis",
                "status": "no_src_files_found",
                "directory": dir_path,
                "files_analyzed": 0,
                "memory_leaks": [],
                "recommendations": ["No C++ files found in the specified directory"]
            }
        
        # Chỉ phân tích các file chưa check
        full_paths = [os.path.join(dir_path, f) for f in remaining_files]
        
        # Phân tích từng file
        all_memory_ops = {}
        all_includes = {}
        all_cross_file_calls = {}
        
        logger.info(f"Analyzing {len(remaining_files)} remaining files...")
        
        for i, file_path in enumerate(full_paths, 1):
            logger.info(f"Analyzing file {i}/{len(full_paths)}: {os.path.basename(file_path)}")
            analysis = self.parser.parse_file(file_path)   
            # get relative path for memory operations         
            rel_path = os.path.relpath(file_path, dir_path)
            all_memory_ops[rel_path] = analysis["memory_operations"]
            # logger.info(f"[taikt-DEBUG] {file_path}: {len(analysis['memory_operations'])} memory ops")
            all_includes[file_path] = analysis["includes"]
            all_cross_file_calls[file_path] = analysis["cross_file_calls"]
        
        # Xây dựng memory flow map
        memory_flows = self._build_memory_flow_map(all_memory_ops)
        
        # Dynamic grouping: group files có liên quan memory-wise
        memory_groups = self._create_dynamic_groups(memory_flows, all_includes, all_cross_file_calls, all_memory_ops)
        
        # Detect memory leaks trong từng group
        detected_leaks = self._detect_memory_leaks(memory_groups, memory_flows)
        
        # AI-assisted analysis cho complex cases
        ai_context = self._prepare_ai_context_for_complex_cases(detected_leaks, memory_groups)
        
        

        # Summary
        summary = {
            "total_files_in_directory": len(all_src_files),
            "previously_checked_files": len(checked_files),
            "newly_analyzed_files": len(remaining_files),
            "memory_operations_found": sum(len(ops) for ops in all_memory_ops.values()),
            "cross_file_flows": len([f for f in memory_flows.values() if f.is_cross_file()]),
            "potential_leaks": len(detected_leaks),
            "dynamic_groups": len(memory_groups),
            "analysis_completeness": "incremental_analysis"
        }
        
        return {
            "analysis_method": "incremental_analysis_with_dynamic_grouping",
            "directory": dir_path,
            "files_analyzed": len(remaining_files),
            "remaining_files": remaining_files,  # Add this for tool handler
            "memory_flows": {k: self._serialize_memory_flow(v) for k, v in memory_flows.items()},
            "detected_leaks": detected_leaks,
            "dynamic_groups": memory_groups,
            "ai_context_for_complex_cases": ai_context,
            "summary": summary,
            "recommendations": self._generate_recommendations(detected_leaks, memory_flows),
            "session_stats": self.tracker.get_analysis_stats(dir_path),
            "all_memory_ops": all_memory_ops
        }
    
    def _build_memory_flow_map(self, all_memory_ops: Dict) -> Dict[str, MemoryFlow]:
        """Xây dựng map của memory flows across files"""
        memory_flows = {}
        
        # Collect all memory operations by variable name
        for file_path, operations in all_memory_ops.items():
            for op in operations:
                var_name = op.variable
                
                if var_name not in memory_flows:
                    memory_flows[var_name] = MemoryFlow(var_name)
                
                flow = memory_flows[var_name]
                
                if op.operation_type == 'alloc':
                    flow.add_allocation(op)
                elif op.operation_type == 'dealloc':
                    flow.add_deallocation(op)
        
        return memory_flows
    
    def _create_dynamic_groups(self, memory_flows: Dict[str, MemoryFlow], 
                              all_includes: Dict, all_cross_file_calls: Dict, all_memory_ops: Dict) -> List[Dict]:
        """Tạo dynamic groups của files có liên quan memory-wise"""
        groups = []
        processed_files = set()
        
        # Group 1: Files có cross-file memory flows
        for var_name, flow in memory_flows.items():
            if flow.is_cross_file() and len(flow.files_involved) > 1:
                group_files = list(flow.files_involved)
                
                # Extend group với files có include relationships
                extended_files = set(group_files)
                for file_path in group_files:
                    for included in all_includes.get(file_path, []):
                        # Tìm file tương ứng với header
                        for other_file in all_includes.keys():
                            if included in os.path.basename(other_file):
                                extended_files.add(other_file)
                
                if extended_files not in [set(g['files']) for g in groups]:
                    groups.append({
                        'type': 'cross_file_memory_flow',
                        'variable': var_name,
                        'files': list(extended_files),
                        'reason': f'Cross-file memory flow for variable {var_name}'
                    })
                    processed_files.update(extended_files)
        
        # Group 2: Files chưa được group nhưng có memory operations
        remaining_files = []
        for file_path, operations in all_memory_ops.items():
            if file_path not in processed_files and len(operations) > 0:
                remaining_files.append(file_path)
        
        # Batch remaining files
        batch_size = 5
        for i in range(0, len(remaining_files), batch_size):
            batch = remaining_files[i:i+batch_size]
            groups.append({
                'type': 'memory_hotspot_batch',
                'files': batch,
                'reason': f'Batch {i//batch_size + 1} of files with memory operations'
            })
        
        return groups
    
    def _detect_memory_leaks(self, memory_groups: List[Dict], 
                           memory_flows: Dict[str, MemoryFlow]) -> List[Dict]:
        """Detect memory leaks trong các groups"""
        detected_leaks = []
        
        for flow_name, flow in memory_flows.items():
            if flow.has_potential_leak():
                allocation_details = [
                {
                    'file': op.file_path,
                    'line': op.line_num,
                    'scope': op.scope,
                    'details': op.details
                } for op in flow.allocations
                ]
                deallocation_details = [
                    {
                        'file': op.file_path,
                        'line': op.line_num,
                        'scope': op.scope,
                        'details': op.details
                    } for op in flow.deallocations
                ]
                # Tổng hợp tất cả các dòng có thao tác cấp phát/giải phóng bộ nhớ
                allocation_lines = [op['line'] for op in allocation_details]
                deallocation_lines = [op['line'] for op in deallocation_details]
                leak_lines = sorted(set(allocation_lines + deallocation_lines))

                leak_info = {
                    'variable': flow_name,
                    'severity': 'high' if flow.is_cross_file() else 'medium',
                    'type': 'cross_file_leak' if flow.is_cross_file() else 'single_file_leak',
                    'files_involved': list(flow.files_involved),
                    'allocations': len(flow.allocations),
                    'deallocations': len(flow.deallocations),
                    'allocation_details': allocation_details,
                    'deallocation_details': deallocation_details,
                    'leak_lines': leak_lines
                }
                detected_leaks.append(leak_info)
        
        return detected_leaks
    
    def _prepare_ai_context_for_complex_cases(self, detected_leaks: List[Dict], 
                                            memory_groups: List[Dict]) -> Dict:
        """Chuẩn bị context cho AI analysis các cases phức tạp"""
        complex_cases = []
        
        for leak in detected_leaks:
            if leak['severity'] == 'high' or len(leak['files_involved']) > 2:
                # Chỉ include code snippets cho complex cases
                file_contents = {}
                for file_path in leak['files_involved']:
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                            # Truncate for AI context
                            if len(content) > 1500:
                                content = content[:1500] + "\n\n// ... [TRUNCATED] ..."
                            file_contents[os.path.basename(file_path)] = content
                    except Exception as e:
                        file_contents[os.path.basename(file_path)] = f"// Error reading: {e}"
                
                complex_cases.append({
                    'leak_info': leak,
                    'file_contents': file_contents,
                    'analysis_focus': [
                        f"Cross-file memory flow for variable '{leak['variable']}'",
                        "RAII compliance and exception safety",
                        "Ownership transfer mechanisms",
                        "Resource cleanup in error paths"
                    ]
                })
        
        return {
            'complex_cases': complex_cases,
            'ai_analysis_needed': len(complex_cases) > 0,
            'analysis_focus': [
                "Cross-file memory ownership verification",
                "Exception safety in multi-file scenarios", 
                "Factory pattern memory responsibilities",
                "Resource lifecycle management"
            ]
        }
    
    def _serialize_memory_flow(self, flow: MemoryFlow) -> Dict:
        """Serialize MemoryFlow object to dict"""
        return {
            'variable': flow.variable,
            'is_cross_file': flow.is_cross_file(),
            'has_potential_leak': flow.has_potential_leak(),
            'files_involved': list(flow.files_involved),
            'allocation_count': len(flow.allocations),
            'deallocation_count': len(flow.deallocations)
        }
    
    def _generate_recommendations(self, detected_leaks: List[Dict], 
                                memory_flows: Dict[str, MemoryFlow]) -> List[str]:
        """Generate actionable recommendations"""
        recommendations = []
        
        if not detected_leaks:
            recommendations.append("✅ No obvious memory leaks detected in static analysis")
        else:
            recommendations.append(f"⚠️  {len(detected_leaks)} potential memory leaks detected")
            
            cross_file_leaks = [l for l in detected_leaks if l['type'] == 'cross_file_leak']
            if cross_file_leaks:
                recommendations.append(f"🔴 {len(cross_file_leaks)} cross-file memory leaks require immediate attention")
                recommendations.append("Consider implementing RAII pattern with smart pointers")
                
        # Pattern-based recommendations
        if any(flow.is_cross_file() for flow in memory_flows.values()):
            recommendations.append("Implement clear ownership policies for cross-file memory transfers")
            recommendations.append("Use smart pointers (unique_ptr/shared_ptr) for automatic cleanup")
            
        recommendations.append("Run dynamic analysis tools (Valgrind/AddressSanitizer) for runtime verification")
        
        return recommendations

# Factory function
def analyze_leaks(dir_path: str = None) -> Dict:
    """
    Main entry point cho full codebase memory leak analysis với dynamic grouping
    
    Args:
        dir_path: Thư mục cần phân tích
        
    Returns:
        Dict: Kết quả phân tích toàn diện
    """
    analyzer = MemoryAnalyzer()
    return analyzer.analyze_codebase(dir_path)
