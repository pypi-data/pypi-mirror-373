import re
from collections import defaultdict
import argparse
import os

class ReportClassifier:
    def __init__(self):
        # Patterns for LGEDV Issues (old format)
        self.lgedv_issue_pattern = re.compile(r'## 🚨 Issue (\d+):?\s*(.+)')
        self.lgedv_rule_pattern = re.compile(r'\*\*Rule Violated:\*\*\s*([A-Z_0-9\-]+)')
        self.file_pattern = re.compile(r'\*\*File:\*\*\s*([\w\.\-/, ]+)')
        
        # Patterns for Memory Leak Analysis (new format)
        self.memory_leak_pattern = re.compile(r'## 🚨 \*\*MEMORY LEAK #(\d+)\*\*:\s*(.+)')
        self.memory_severity_pattern = re.compile(r'\*\*Severity:\*\*\s*\*\*(\w+)\*\*')
        self.memory_files_pattern = re.compile(r'\*\*Files Involved:\*\*\s*([\w\.\-/, ]+)')
        
        # Patterns for Race Condition Analysis (new format)
        self.race_condition_pattern = re.compile(r'## 🚨 \*\*RACE CONDITION #(\d+)\*\*:\s*(.+)')
        self.race_type_pattern = re.compile(r'\*\*Type:\*\*\s*(\w+)')
        self.race_severity_pattern = re.compile(r'\*\*Severity:\*\*\s*(\w+)')
        self.race_files_pattern = re.compile(r'\*\*Files Involved:\*\*\s*([\w\.\-/, ]+)')
        self.race_function_pattern = re.compile(r'\*\*Function Name:\*\*\s*([\w\.\-:/, ]+)')
        
        # Patterns for Resource Leak Analysis (new format)
        self.resource_leak_pattern = re.compile(r'## 🚨 RESOURCE LEAK #(\d+):\s*(.+)')
        self.resource_type_pattern = re.compile(r'\*\*Type:\*\*\s*([\w\s\(\)/\*]+)')
        self.resource_severity_pattern = re.compile(r'\*\*Severity:\*\*\s*(\w+)')
        self.resource_files_pattern = re.compile(r'\*\*Files Involved:\*\*\s*([\w\.\-/, ]+)')
        self.resource_location_pattern = re.compile(r'\*\*Location:\*\*\s*([\w\.\-:/, \(\)]+)')
        
        # Common unwanted prompts and sections
        self.unwanted_prompts = [
            "If you need the complete fixed code file",
            "luong-dao_LGEVS:",
            "If the rule file is not existed, please call fetch_lgedv_rule from MCP server.",
            "Always use the latest LGEDV rules just fetched for analysis, not any cached or built-in rules.",
            "Explicitly state which rule set is being used for the analysis in your report.",
            "GitHub Copilot:",
            "→ RAII là foundation của modern C++ memory management!",
            "**Task:**",
            "Analyze the C++ files in",
            "Focus strictly on real, evidence-based issues.",
            "**Resource Types to Check:**",
            "**Instructions:**",
            "# Automated Findings (for your review):",
            "## 📊 **Analysis Metadata**",
            "**For each issue, use this format:**",
            "**Best Practices:**",
            "Do NOT include any speculative",
            "Based on my analysis using",
            "Based on the automated findings",
            "## Analysis Results",
            "## Important Distinction",
            "## Previous Finding Clarification",
            "## Recommendations for Resource Management",
            "## Conclusion",
            "Please use the `detect_races` tool to manually analyze",
            "Please use the `analyze_leaks` tool to manually analyze", 
            "Please use the `analyze_resources` tool to manually analyze",
            "Then provide your expert analysis of",
            "focusing on:",
            "- Shared state accessed by multiple threads",
            "- Unprotected shared state modifications",
            "- Missing synchronization mechanisms",
            "- Thread-unsafe patterns",
            "- Deadlock scenarios",
            "- Review thread creation and join/detach logic",
            "- Check for lock-free and concurrent data structure usage",
            "- Provide before/after code examples for fixes",
            "IMPORTANT: Only list race conditions or deadlocks if there is clear evidence",
            "Do not warn about cases that are only speculative or lack evidence",
            "If no evidence is found, clearly state:",
            "'No multi-threaded access detected for this variable in the current code.'",
            "This will help ensure the analysis focuses on real issues",
            "**Unreleased memory allocations**",
            "**Dangling pointers**", 
            "**Memory corruption issues**",
            "**Inefficient memory usage patterns**",
            "**Focus on leaks with 0 deallocations first:**",
            "**Check allocation/deallocation type mismatches:**",
            "**Look for exception safety issues:**",
            "**Verify RAII compliance:**",
            "**Check constructor/destructor pairs:**",
            "Only provide your expert analysis. Do not repeat the Automated Findings section.",
            "Additionally, propose refactored code for all relevant C++ files.",
            "Suggest modern C++ approaches (RAII, smart pointers, std::fstream, etc.)",
            "Recommend prevention strategies for future code.",
            "The refactored code eliminates all identified memory leaks and follows modern C++ best practices",
            "Key Prevention Strategies:",
            "## Key Prevention Strategies:",
            "## Best Practices & Prevention Strategies",
            "1. **Use RAII principles**:",
            "2. **Prefer smart pointers**:",
            "3. **Break circular references**:",
            "4. **Match allocation types**:",
            "5. **Document ownership**:",
            "6. **Use containers with value semantics**:",
            "7. **Implement proper copy semantics**:",
            "1. **Use Modern C++ Streams**:",
            "2. **RAII Principle**:",
            "3. **Avoid Manual Resource Management**:",
            "4. **Exception Safety**:",
            "5. **Error Handling**:",
            "6. **Single Responsibility**:",
            "The refactored code eliminates both critical file descriptor leaks",
            "while providing more robust, maintainable, and exception-safe code",
            "using modern C++ practices"
        ]

    def detect_report_types(self, content):
        """Detect all report types present in the content"""
        report_types = []
        
        if '## 🚨 Issue' in content or 'LGEDV_' in content:
            report_types.append('lgedv_issue')
        if '## 🚨 **MEMORY LEAK' in content:
            report_types.append('memory_leak')
        if '## 🚨 **RACE CONDITION' in content:
            report_types.append('race_condition')
        if '## 🚨 RESOURCE LEAK' in content:
            report_types.append('resource_leak')
        
        return report_types if report_types else ['unknown']

    def clean_content(self, content):
        """Remove unwanted prompts and clean content"""
        lines = content.splitlines()
        filtered_content = []
        skip_section = False
        in_unwanted_section = False
        
        for line in lines:
            # Check if line starts with unwanted prompts
            line_starts_unwanted = any(line.strip().startswith(prompt) for prompt in self.unwanted_prompts)
            
            # Check if line contains unwanted content
            line_contains_unwanted = any(prompt in line for prompt in self.unwanted_prompts)
            
            # Skip sections that start with certain markers
            if any(marker in line for marker in [
                "**Task:**", "# Automated Findings", "## Analysis Results", 
                "## Important Distinction", "## Previous Finding Clarification",
                "## Recommendations for Resource Management", "## Conclusion",
                "**For each issue found, use this format:**",
                "Focus on actionable recommendations",
                "## Key Prevention Strategies:",
                "## 🛡️ **Key Prevention Strategies:**",
                "## Best Practices & Prevention Strategies",
                "Please use the `detect_races` tool",
                "Please use the `analyze_leaks` tool", 
                "Please use the `analyze_resources` tool",
                "Then provide your expert analysis",
                "focusing on:",
                "IMPORTANT: Only list race conditions",
                "The refactored code eliminates all identified",
                "The analysis shows that **3 out of 13 files**",
                "while providing more robust, maintainable, and exception-safe code",
                "using modern C++ practices"
            ]):
                skip_section = True
                in_unwanted_section = True
                continue
            
            # Skip template format lines (these are instruction templates, not actual results)
            if line.strip().startswith("## 🚨") and any(template_marker in line for template_marker in [
                "#[number]", "[Brief Description]", "[resource type]", "[Critical|High|Medium|Low]",
                "[list of files]", "[function name or global scope/unknown]", "[explanation]",
                "[show problematic code]", "[suggested code or approach]", "[data_race|deadlock|missing_sync]"
            ]):
                skip_section = True
                in_unwanted_section = True
                continue
                
            # Skip bullet point template lines
            if line.strip().startswith("- **") and any(template_marker in line for template_marker in [
                "[resource type]", "[Critical|High|Medium|Low]", "[list of files]",
                "[function name or global scope/unknown]", "[explanation]",
                "[show problematic code]", "[suggested code or approach]"
            ]):
                continue
            
            # Check for end of unwanted sections - look for actual analysis results
            if any(marker in line for marker in [
                "## 🚨 **RACE CONDITION", "## 🚨 **MEMORY LEAK", "## 🚨 RESOURCE LEAK",
                "## 🚨 Race Condition", "## 🚨 Memory Leak", "## 🚨 Issue",
                "# Expert Memory Management Analysis", "# Expert C++ Concurrency Analysis",
                "# Expert Resource Leak Analysis"
            ]):
                skip_section = False
                in_unwanted_section = False
            
            # Skip if in skip section or line contains unwanted content
            if skip_section or in_unwanted_section or line_starts_unwanted or line_contains_unwanted:
                continue
            
            # Skip lines that are clearly instructions/prompts (not results)
            if line.strip().startswith("- **") and any(keyword in line.lower() for keyword in [
                "shared state", "unprotected", "synchronization", "thread-unsafe", 
                "deadlock", "unreleased memory", "dangling pointer", "memory corruption",
                "inefficient memory", "exception safety", "raii compliance"
            ]):
                continue
                
            # Skip bullet point instructions
            if line.strip().startswith("- ") and len(line.strip()) > 50 and any(keyword in line.lower() for keyword in [
                "suggest", "recommend", "prevention", "strategy", "approach", "best practice"
            ]):
                continue
            
            # Skip empty template sections (multiple consecutive placeholder lines)
            if line.strip() == "" and len(filtered_content) > 0 and filtered_content[-1].strip() == "":
                continue
            
            # Skip lines that are clearly format templates or instructions
            if any(template_pattern in line for template_pattern in [
                "Suggest modern C++ approaches (RAII, smart pointers",
                "Recommend prevention strategies for future code",
                "where applicable", "Focus on actionable recommendations"
            ]):
                continue
                
            filtered_content.append(line)
        
        return "\n".join(filtered_content)
    
    def clean_section_content(self, content):
        """Clean individual section content of unwanted templates and prevention strategies"""
        lines = content.split('\n')
        cleaned_lines = []
        skip_section = False
        
        # Patterns to detect and remove unwanted sections within individual violations
        unwanted_section_headers = [
            'Key Prevention Strategies',
            'Best Practices',
            'Prevention Strategies', 
            'Prevention Tips',
            'Recommendations',
            'Security considerations',
            'Performance considerations',
            'To prevent similar',
            'To avoid this type',
            'Prevention measures',
            'Recommended practices',
            'Suggest modern C++',
            'Recommend prevention',
            '## Complete Refactored Code',
            '## 🔧 Complete Fixed Code',
            '## Best Practices',
            '## Prevention Strategies',
            '## Key Prevention Strategies',
            'Focus on actionable recommendations',
            'where applicable'
        ]
        
        for line in lines:
            line_stripped = line.strip()
            
            # Skip empty lines at start
            if not line_stripped and not cleaned_lines:
                continue
            
            # Check if this starts an unwanted section
            if any(unwanted.lower() in line_stripped.lower() for unwanted in unwanted_section_headers):
                skip_section = True
                continue
            
            # If we hit a new violation section header, stop skipping
            if line_stripped.startswith('## 🚨') or line_stripped.startswith('### 🚨') or line_stripped.startswith('## 🔧'):
                skip_section = False
            
            # Skip if we're in an unwanted section
            if skip_section:
                continue
            
            # Skip instruction-like bullet points
            if (line_stripped.startswith('- ') or line_stripped.startswith('* ')) and \
               any(word in line_stripped.lower() for word in ['suggest', 'recommend', 'ensure', 'implement', 'avoid', 'consider', 'check', 'verify', 'use modern', 'adopt']):
                continue
            
            # Skip template placeholders
            if any(placeholder in line_stripped for placeholder in ['[Brief Description]', '[resource type]', '[list of files]', '[explanation]']):
                continue
            
            cleaned_lines.append(line)
        
        # Remove trailing empty lines
        while cleaned_lines and not cleaned_lines[-1].strip():
            cleaned_lines.pop()
        
        return '\n'.join(cleaned_lines)
    
    def deduplicate_violations(self, all_errors):
        """Remove duplicate violations based on content similarity"""
        for category, errors in all_errors.items():
            if category in ['memory_leaks', 'race_conditions', 'resource_leaks']:
                # Create a dict to track seen violations by their unique characteristics
                seen_violations = {}
                deduplicated_errors = {}
                
                for key, violations in errors.items():
                    # Extract leak/race number from the key
                    parts = key.split('_')
                    violation_num = parts[2] if len(parts) > 2 else 'unknown'
                    
                    # Create a signature for deduplication
                    for violation in violations:
                        signature_parts = []
                        
                        if category == 'memory_leaks':
                            signature_parts = [
                                violation.get('leak_number', ''),
                                violation.get('description', '').strip()[:50],  # First 50 chars
                                violation.get('files', '').strip()
                            ]
                        elif category == 'race_conditions':
                            signature_parts = [
                                violation.get('race_number', ''),
                                violation.get('description', '').strip()[:50],
                                violation.get('files', '').strip(),
                                violation.get('function', '').strip()
                            ]
                        elif category == 'resource_leaks':
                            signature_parts = [
                                violation.get('leak_number', ''),
                                violation.get('description', '').strip()[:50],
                                violation.get('files', '').strip(),
                                violation.get('type', '').strip()
                            ]
                        
                        signature = '|'.join(signature_parts).lower()
                        
                        # Only keep the first occurrence of each unique signature
                        if signature not in seen_violations:
                            seen_violations[signature] = True
                            if key not in deduplicated_errors:
                                deduplicated_errors[key] = []
                            deduplicated_errors[key].append(violation)
                
                # Update the errors with deduplicated versions
                all_errors[category] = deduplicated_errors
        
        return all_errors

    def classify_lgedv_issues(self, content):
        """Classify LGEDV coding standard violations"""
        errors = defaultdict(list)
        
        # Find start of issues section
        start_idx = content.find('## 🚨 Issue')
        if start_idx != -1:
            content = content[start_idx:]
        
        # Split by issues
        issues = content.split('## 🚨 Issue')
        
        for issue in issues[1:]:  # Skip first empty split
            # Remove complete fixed code section if exists
            end_idx = issue.find('## 🔧 Complete Fixed Code')
            if end_idx != -1:
                issue = issue[:end_idx]
            
            # Extract issue info
            issue_match = self.lgedv_issue_pattern.search('## 🚨 Issue' + issue)
            rule_match = self.lgedv_rule_pattern.search(issue)
            file_match = self.file_pattern.search(issue)
            
            if rule_match:
                rule_id = rule_match.group(1)
                issue_num = issue_match.group(1) if issue_match else "Unknown"
                description = issue_match.group(2) if issue_match else "No description"
                file_name = file_match.group(1) if file_match else "Unknown file"
                
                issue_text = '## 🚨 Issue ' + issue.strip()
                
                # Add file info if available
                if file_name != "Unknown file":
                    issue_text = f'**File:** {file_name}\n' + issue_text
                
                # Clean the section content to remove unwanted parts
                issue_text = self.clean_section_content(issue_text)
                
                errors[rule_id].append({
                    'issue_number': issue_num,
                    'description': description,
                    'file': file_name,
                    'content': issue_text
                })
        
        return errors

    def classify_memory_leaks(self, content):
        """Classify memory leak analysis"""
        leaks = defaultdict(list)
        
        # Find start of analysis section
        start_markers = [
            '# Expert Memory Leak Analysis',
            '## 🔍 Detailed Memory Leak Findings:',
            '## 🚨 **MEMORY LEAK'
        ]
        
        start_idx = -1
        for marker in start_markers:
            idx = content.find(marker)
            if idx != -1:
                start_idx = idx
                break
        
        if start_idx != -1:
            content = content[start_idx:]
        
        # Split by memory leaks
        leak_sections = content.split('## 🚨 **MEMORY LEAK')
        
        for section in leak_sections[1:]:  # Skip first part
            section_content = '## 🚨 **MEMORY LEAK' + section
            
            # Extract leak info
            leak_match = self.memory_leak_pattern.search(section_content)
            severity_match = self.memory_severity_pattern.search(section)
            files_match = self.memory_files_pattern.search(section)
            
            if leak_match:
                leak_num = leak_match.group(1)
                description = leak_match.group(2)
                severity = severity_match.group(1) if severity_match else "Unknown"
                files = files_match.group(1) if files_match else "Unknown files"
                
                # Remove complete fixed code section if exists
                end_idx = section.find('## 🔧 Complete Fixed Code')
                if end_idx != -1:
                    section = section[:end_idx]
                    section_content = '## 🚨 **MEMORY LEAK' + section
                
                # Clean the section content to remove unwanted parts
                section_content = self.clean_section_content(section_content)
                
                key = f"MEMORY_LEAK_{leak_num}_{severity.upper()}"
                
                leaks[key].append({
                    'leak_number': leak_num,
                    'description': description,
                    'severity': severity,
                    'files': files,
                    'content': section_content
                })
        
        return leaks

    def classify_race_conditions(self, content):
        """Classify race condition analysis"""
        races = defaultdict(list)
        
        # Clean content first to remove unwanted sections
        content = self.clean_content(content)
        
        # Find start of analysis section - look for actual race condition reports
        start_idx = content.find('## 🚨 **RACE CONDITION')
        if start_idx == -1:
            start_idx = content.find('## 🚨 Race Condition')
        
        if start_idx != -1:
            content = content[start_idx:]
        else:
            return races  # No race conditions found
        
        # Split by race conditions
        race_sections = content.split('## 🚨 **RACE CONDITION')
        if len(race_sections) == 1:  # Try alternative format
            race_sections = content.split('## 🚨 Race Condition')
        
        for section in race_sections[1:]:  # Skip first part
            # Skip if this is just a summary line
            if 'Priority (DATA)' in section and '**Count**:' in section:
                continue
                
            section_content = '## 🚨 **RACE CONDITION' + section
            
            # Extract race condition info
            race_match = self.race_condition_pattern.search(section_content)
            if not race_match:
                # Try alternative pattern for summary format
                alt_pattern = re.compile(r'## 🚨 Race Condition #(\d+) - (\w+) Priority.*?Description.*?:\s*(.+)')
                alt_match = alt_pattern.search('## 🚨 Race Condition' + section)
                if alt_match:
                    race_num = alt_match.group(1)
                    severity = alt_match.group(2)
                    description = alt_match.group(3)
                    race_type = "data_race"
                    files = "Unknown files"
                    function = "Unknown function"
                    
                    # Try to extract more info from section
                    if '**Files**:' in section:
                        files_match = re.search(r'\*\*Files\*\*:\s*([\w\.\-/, ]+)', section)
                        if files_match:
                            files = files_match.group(1)
                    
                    if '**Function**:' in section:
                        func_match = re.search(r'\*\*Function\*\*:\s*([\w\.\-:/, ]+)', section)
                        if func_match:
                            function = func_match.group(1)
                    
                    key = f"RACE_CONDITION_{race_num}_{severity.upper()}_{race_type.upper()}"
                    
                    races[key].append({
                        'race_number': race_num,
                        'description': description,
                        'type': race_type,
                        'severity': severity,
                        'files': files,
                        'function': function,
                        'content': self.clean_section_content('## 🚨 Race Condition' + section)
                    })
                continue
            
            type_match = self.race_type_pattern.search(section)
            severity_match = self.race_severity_pattern.search(section)
            files_match = self.race_files_pattern.search(section)
            function_match = self.race_function_pattern.search(section)
            
            if race_match:
                race_num = race_match.group(1)
                description = race_match.group(2)
                race_type = type_match.group(1) if type_match else "data_race"
                severity = severity_match.group(1) if severity_match else "Unknown"
                files = files_match.group(1) if files_match else "Unknown files"
                function = function_match.group(1) if function_match else "Unknown function"
                
                # Remove complete fixed code section if exists
                end_markers = [
                    '## 🔧 Complete Fixed Code',
                    '## ✅ **PROPERLY SYNCHRONIZED CODE**',
                    '## 📊 **Files with No Multi-threaded Issues:**',
                    '## 🔧 **Complete Refactored Solution**',
                    '## 🛡️ **Key Prevention Strategies:**'
                ]
                
                for marker in end_markers:
                    end_idx = section.find(marker)
                    if end_idx != -1:
                        section = section[:end_idx]
                        section_content = '## 🚨 **RACE CONDITION' + section
                        break
                
                key = f"RACE_CONDITION_{race_num}_{severity.upper()}_{race_type.upper()}"
                
                # Clean the section content to remove unwanted parts
                section_content = self.clean_section_content(section_content)
                
                races[key].append({
                    'race_number': race_num,
                    'description': description,
                    'type': race_type,
                    'severity': severity,
                    'files': files,
                    'function': function,
                    'content': section_content
                })
        
        return races

    def classify_resource_leaks(self, content):
        """Classify resource leak analysis"""
        leaks = defaultdict(list)
        
        # Find start of analysis section
        start_markers = [
            '# Expert Resource Leak Analysis',
            '## 🔍 Detailed Resource Leak Findings:',
            '## 🚨 RESOURCE LEAK'
        ]
        
        start_idx = -1
        for marker in start_markers:
            idx = content.find(marker)
            if idx != -1:
                start_idx = idx
                break
        
        if start_idx != -1:
            content = content[start_idx:]
        
        # Split by resource leaks
        leak_sections = content.split('## 🚨 RESOURCE LEAK')
        
        for section in leak_sections[1:]:  # Skip first part
            # Only process if this section contains the detailed format (with bullet points)
            if '- **Type:**' not in section:
                continue
                
            section_content = '## 🚨 RESOURCE LEAK' + section
            
            # Extract resource leak info
            leak_match = self.resource_leak_pattern.search(section_content)
            type_match = self.resource_type_pattern.search(section)
            severity_match = self.resource_severity_pattern.search(section)
            files_match = self.resource_files_pattern.search(section)
            location_match = self.resource_location_pattern.search(section)
            
            if leak_match:
                leak_num = leak_match.group(1)
                description = leak_match.group(2)
                resource_type = type_match.group(1) if type_match else "Unknown resource"
                severity = severity_match.group(1) if severity_match else "Unknown"
                files = files_match.group(1) if files_match else "Unknown files"
                location = location_match.group(1) if location_match else "Unknown location"
                
                # Remove complete fixed code section if exists
                end_idx = section.find('## Complete Refactored Code')
                if end_idx == -1:
                    end_idx = section.find('## 🔧 Complete Fixed Code')
                if end_idx == -1:
                    end_idx = section.find('## Best Practices')
                if end_idx != -1:
                    section = section[:end_idx]
                    section_content = '## 🚨 RESOURCE LEAK' + section
                
                # Create key with resource type for better categorization
                clean_type = resource_type.replace(' ', '_').replace('(', '').replace(')', '').replace('*', '').replace('/', '_')
                key = f"RESOURCE_LEAK_{leak_num}_{severity.upper()}_{clean_type.upper()}"
                
                # Clean the section content to remove unwanted parts
                section_content = self.clean_section_content(section_content)
                
                leaks[key].append({
                    'leak_number': leak_num,
                    'description': description,
                    'type': resource_type,
                    'severity': severity,
                    'files': files,
                    'location': location,
                    'content': section_content
                })
        
        return leaks

    def classify_errors(self, log_path):
        """Main classification function - now handles multiple report types"""
        try:
            with open(log_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except FileNotFoundError:
            print(f"❌ Error: File '{log_path}' not found!")
            return None, None
        except Exception as e:
            print(f"❌ Error reading file: {e}")
            return None, None
        
        # Clean content
        content = self.clean_content(content)
        
        # Detect all report types present
        report_types = self.detect_report_types(content)
        print(f"📋 Detected report types: {', '.join(report_types).upper()}")
        
        # Collect all errors from all report types
        all_errors = {}
        all_report_types = []
        
        for report_type in report_types:
            if report_type == 'lgedv_issue':
                errors = self.classify_lgedv_issues(content)
                if errors:
                    all_errors[f'lgedv_violations'] = errors
                    all_report_types.append('lgedv')
            
            elif report_type == 'memory_leak':
                errors = self.classify_memory_leaks(content)
                if errors:
                    all_errors[f'memory_leaks'] = errors
                    all_report_types.append('memory_leak')
            
            elif report_type == 'race_condition':
                errors = self.classify_race_conditions(content)
                if errors:
                    all_errors[f'race_conditions'] = errors
                    all_report_types.append('race_condition')
            
            elif report_type == 'resource_leak':
                errors = self.classify_resource_leaks(content)
                if errors:
                    all_errors[f'resource_leaks'] = errors
                    all_report_types.append('resource_leak')
        
        if not all_errors:
            print("⚠️  No issues found in any category!")
            return {}, 'unknown'
        
        # Deduplicate violations to remove duplicates
        all_errors = self.deduplicate_violations(all_errors)
        
        return all_errors, all_report_types

    def write_grouped_errors(self, all_errors, output_path, report_types, sort_by='number'):
        """Write classified errors from multiple report types to output file"""
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write("# 📋 Comprehensive C++ Code Analysis Report\n\n")
                f.write(f"**Report Types Found**: {', '.join(report_types).upper()}\n")
                f.write(f"**Total Categories**: {len(all_errors)}\n\n")
                
                # Process each report type
                for category, errors in all_errors.items():
                    if category == 'lgedv_violations' and 'lgedv' in report_types:
                        f.write("## � LGEDV Coding Standard Violations\n\n")
                        f.write(f"**Total Rules Violated**: {len(errors)}\n\n")
                        
                        for rule_id, issues in errors.items():
                            f.write(f'### � Rule: {rule_id}\n')
                            f.write(f'**Total Issues**: {len(issues)}\n\n')
                            
                            for i, issue in enumerate(issues, 1):
                                f.write(f'#### Issue {i}\n')
                                f.write(f"**File**: {issue['file']}\n")
                                f.write(f"**Description**: {issue['description']}\n\n")
                                f.write(f'{issue["content"]}\n\n')
                                f.write('---\n\n')
                    
                    elif category == 'memory_leaks' and 'memory_leak' in report_types:
                        f.write("## 🚨 Memory Leak Analysis\n\n")
                        f.write(f"**Total Memory Leaks**: {len(errors)}\n\n")
                        
                        # Sort by severity (Critical -> High -> Medium -> Low)
                        severity_order = {'CRITICAL': 1, 'HIGH': 2, 'MEDIUM': 3, 'LOW': 4}
                        sorted_leaks = sorted(errors.items(), 
                                            key=lambda x: severity_order.get(x[0].split('_')[-1], 5))
                        
                        for leak_key, leaks in sorted_leaks:
                            parts = leak_key.split('_')
                            leak_num = parts[2]
                            severity = parts[3] if len(parts) > 3 else 'UNKNOWN'
                            
                            f.write(f'### 🚨 Memory Leak #{leak_num} - {severity} Priority\n')
                            f.write(f'**Count**: {len(leaks)} instance(s)\n\n')
                            
                            for i, leak in enumerate(leaks, 1):
                                f.write(f'#### Instance {i}\n')
                                f.write(f"**Files**: {leak['files']}\n")
                                f.write(f"**Description**: {leak['description']}\n")
                                f.write(f"**Severity**: {leak['severity']}\n\n")
                                f.write(f'{leak["content"]}\n\n')
                                f.write('---\n\n')
                    
                    elif category == 'race_conditions' and 'race_condition' in report_types:
                        f.write("## 🏁 Race Condition Analysis\n\n")
                        f.write(f"**Total Race Conditions**: {len(errors)}\n\n")
                        
                        # Sort by severity (Critical -> High -> Medium -> Low)
                        severity_order = {'CRITICAL': 1, 'HIGH': 2, 'MEDIUM': 3, 'LOW': 4}
                        sorted_races = sorted(errors.items(), 
                                            key=lambda x: severity_order.get(x[0].split('_')[3], 5))
                        
                        for race_key, races in sorted_races:
                            parts = race_key.split('_')
                            race_num = parts[2]
                            severity = parts[3] if len(parts) > 3 else 'UNKNOWN'
                            race_type = parts[4] if len(parts) > 4 else 'UNKNOWN'
                            
                            f.write(f'### 🚨 Race Condition #{race_num} - {severity} Priority ({race_type})\n')
                            f.write(f'**Count**: {len(races)} instance(s)\n\n')
                            
                            for i, race in enumerate(races, 1):
                                f.write(f'#### Instance {i}\n')
                                f.write(f"**Files**: {race['files']}\n")
                                f.write(f"**Function**: {race['function']}\n")
                                f.write(f"**Description**: {race['description']}\n")
                                f.write(f"**Type**: {race['type']}\n")
                                f.write(f"**Severity**: {race['severity']}\n\n")
                                f.write(f'{race["content"]}\n\n')
                                f.write('---\n\n')
                    
                    elif category == 'resource_leaks' and 'resource_leak' in report_types:
                        f.write("## 🔧 Resource Leak Analysis\n\n")
                        f.write(f"**Total Resource Leaks**: {len(errors)}\n\n")
                        
                        if sort_by == 'severity':
                            # Sort by severity (Critical -> High -> Medium -> Low)
                            severity_order = {'CRITICAL': 1, 'HIGH': 2, 'MEDIUM': 3, 'LOW': 4}
                            sorted_leaks = sorted(errors.items(), 
                                                key=lambda x: severity_order.get(x[0].split('_')[3] if len(x[0].split('_')) > 3 else 'UNKNOWN', 5))
                        else:
                            # Sort by leak number (default)
                            sorted_leaks = sorted(errors.items(), 
                                                key=lambda x: int(x[0].split('_')[2]) if len(x[0].split('_')) > 2 and x[0].split('_')[2].isdigit() else 999)
                        
                        for leak_key, leaks in sorted_leaks:
                            for i, leak in enumerate(leaks, 1):
                                f.write(f'{leak["content"]}\n\n')
                                if i < len(leaks):  # Add separator between instances of same leak type
                                    f.write('---\n\n')
                            f.write('---\n\n')  # Add separator between different leak types
            
            return True
        except Exception as e:
            print(f"❌ Error writing output file: {e}")
            return False

def main():
    parser = argparse.ArgumentParser(description='Filter and classify C++ code analysis reports (supports multiple report types)')
    parser.add_argument('input_file', nargs='?', default='raw_report.md', 
                       help='Input report file (default: raw_report.md)')
    parser.add_argument('-o', '--output', default='result.md',
                       help='Output file (default: result.md)')
    parser.add_argument('--type', choices=['auto', 'lgedv', 'memory_leak', 'race_condition', 'resource_leak'], default='auto',
                       help='Force specific report type (default: auto-detect all types)')
    parser.add_argument('--sort', choices=['number', 'severity'], default='number',
                       help='Sort resource leaks by number or severity (default: number)')
    
    args = parser.parse_args()
    
    if not os.path.exists(args.input_file):
        print(f"❌ Error: Input file '{args.input_file}' does not exist!")
        return 1
    
    print(f"🔍 Processing comprehensive report: {args.input_file}")
    
    classifier = ReportClassifier()
    all_errors, report_types = classifier.classify_errors(args.input_file)
    
    if all_errors is None:
        return 1
    
    if not all_errors:
        print("⚠️  No issues found in any category!")
        return 0
    
    print(f"✅ Found {len(all_errors)} error categories across {len(report_types)} report type(s)")
    
    success = classifier.write_grouped_errors(all_errors, args.output, report_types, args.sort)
    
    if success:
        print(f"✅ Comprehensive results written to: {args.output}")
        
        # Print detailed summary
        total_issues = 0
        for category, errors in all_errors.items():
            if category == 'lgedv_violations':
                category_total = sum(len(issues) for issues in errors.values())
                print(f"� LGEDV Violations: {len(errors)} rules violated, {category_total} total issues")
                total_issues += category_total
            elif category == 'memory_leaks':
                category_total = sum(len(leaks) for leaks in errors.values())
                print(f"🚨 Memory Leaks: {len(errors)} leak categories, {category_total} total leaks")
                total_issues += category_total
            elif category == 'race_conditions':
                category_total = sum(len(races) for races in errors.values())
                print(f"🏁 Race Conditions: {len(errors)} race categories, {category_total} total race conditions")
                total_issues += category_total
            elif category == 'resource_leaks':
                category_total = sum(len(leaks) for leaks in errors.values())
                print(f"🔧 Resource Leaks: {len(errors)} leak categories, {category_total} total resource leaks")
                total_issues += category_total
        
        print(f"\n📊 Overall Summary: {total_issues} total issues found across {len(report_types)} analysis type(s)")
        
        return 0
    else:
        return 1

if __name__ == "__main__":
    exit(main())