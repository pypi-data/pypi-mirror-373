"""
Data models and structures for race condition analysis
Chứa các dataclass và structures để phân tích race condition
"""
from dataclasses import dataclass
from typing import Dict, List, Set, Tuple

@dataclass
class SharedResource:
    """Thông tin về shared resource"""
    name: str
    type: str  # 'global', 'static', 'singleton', 'shared_ptr'
    file_path: str
    line_number: int
    scope: str
    access_pattern: List[str]  # 'read', 'write', 'modify'

@dataclass 
class ThreadUsage:
    """Thông tin về việc sử dụng thread"""
    thread_type: str  # 'std::thread', 'pthread', 'async'
    file_path: str
    line_number: int
    target_function: str
    shared_resources_accessed: List[str]

@dataclass
class RaceCondition:
    """Thông tin về race condition được phát hiện"""
    severity: str  # 'critical', 'high', 'medium', 'low'
    type: str  # 'data_race', 'deadlock', 'missing_sync'
    description: str
    files_involved: List[str]
    resources_involved: List[str]
    line_numbers: List[int]
    fix_recommendation: str

@dataclass
class AnalysisResult:
    """Kết quả phân tích toàn bộ codebase"""
    # shared_resources: Dict[str, List[dict]]
    thread_usage: Dict[str, List[dict]]
    # potential_race_conditions: List[RaceCondition]
    summary: Dict[str, any]
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization"""
        return {
            # "shared_resources": self.shared_resources,
            "thread_usage": self.thread_usage,
            # "potential_race_conditions": [
            #     {
            #         "severity": rc.severity,
            #         "type": rc.type,
            #         "description": rc.description,
            #         "files_involved": rc.files_involved,
            #         "resources_involved": rc.resources_involved,
            #         "line_numbers": rc.line_numbers,
            #         "fix_recommendation": rc.fix_recommendation
            #     } for rc in self.potential_race_conditions
            # ],
            "summary": self.summary
        }

@dataclass
class MemoryAllocation:
    """Thông tin về việc cấp phát bộ nhớ"""
    allocation_type: str  # 'new', 'malloc', 'calloc', 'new[]', 'smart_ptr'
    file_path: str
    line_number: int
    variable_name: str
    pointer_type: str
    scope: str  # 'function', 'class', 'global'
    is_array: bool
    has_corresponding_deallocation: bool

@dataclass
class MemoryDeallocation:
    """Thông tin về việc giải phóng bộ nhớ"""
    deallocation_tymissing_deletepe: str  # 'delete', 'free', 'delete[]'
    file_path: str
    line_number: int
    variable_name: str
    scope: str

@dataclass
class MemoryLeak:
    """Thông tin về memory leak được phát hiện"""
    severity: str  # 'critical', 'high', 'medium', 'low'
    type: str  # 'missing_delete', 'double_delete', 'mismatched_alloc_dealloc', 'resource_leak'
    description: str
    allocation_info: MemoryAllocation
    files_involved: List[str]
    line_numbers: List[int]
    fix_recommendation: str

@dataclass
class MemoryAnalysisResult:
    """Kết quả phân tích memory leak toàn bộ codebase"""
    allocations: Dict[str, List[MemoryAllocation]]
    deallocations: Dict[str, List[MemoryDeallocation]]
    potential_leaks: List[MemoryLeak]
    summary: Dict[str, any]
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization"""
        return {
            "allocations": {
                file: [
                    {
                        "allocation_type": alloc.allocation_type,
                        "file_path": alloc.file_path,
                        "line_number": alloc.line_number,
                        "variable_name": alloc.variable_name,
                        "pointer_type": alloc.pointer_type,
                        "scope": alloc.scope,
                        "is_array": alloc.is_array,
                        "has_corresponding_deallocation": alloc.has_corresponding_deallocation
                    } for alloc in allocations
                ] for file, allocations in self.allocations.items()
            },
            "deallocations": {
                file: [
                    {
                        "deallocation_type": dealloc.deallocation_type,
                        "file_path": dealloc.file_path,
                        "line_number": dealloc.line_number,
                        "variable_name": dealloc.variable_name,
                        "scope": dealloc.scope
                    } for dealloc in deallocations
                ] for file, deallocations in self.deallocations.items()
            },
            "potential_leaks": [
                {
                    "severity": leak.severity,
                    "type": leak.type,
                    "description": leak.description,
                    "allocation_info": {
                        "allocation_type": leak.allocation_info.allocation_type,
                        "file_path": leak.allocation_info.file_path,
                        "line_number": leak.allocation_info.line_number,
                        "variable_name": leak.allocation_info.variable_name,
                        "pointer_type": leak.allocation_info.pointer_type,
                        "scope": leak.allocation_info.scope,
                        "is_array": leak.allocation_info.is_array
                    },
                    "files_involved": leak.files_involved,
                    "line_numbers": leak.line_numbers,
                    "fix_recommendation": leak.fix_recommendation
                } for leak in self.potential_leaks
            ],
            "summary": self.summary
        }
