import re
import sys

def extract_violations(md_text):
    # Lọc các block RESOURCE LEAK - tìm từ ## 🚨 đến ---
    # Bỏ qua dòng format mẫu có [number] và [Brief Description]
    leak_pattern = r'## 🚨 (RESOURCE LEAK #\d+: [^\n]+)(.*?)(?=^## 🚨 |^---|\Z)'
    matches = re.findall(leak_pattern, md_text, flags=re.DOTALL | re.MULTILINE)
    results = []
    for title, block in matches:
        # Type - lấy từ **Type:**
        m = re.search(r'\*\*Type:\*\*\s*([^\n]+)', block)
        resource_type = m.group(1).strip() if m else ''
        
        # Severity - lấy từ **Severity:**
        m = re.search(r'\*\*Severity:\*\*\s*([^\n]+)', block)
        severity = m.group(1).strip() if m else ''
        
        # Files Involved - lấy từ **Files Involved:**
        m = re.search(r'\*\*Files Involved:\*\*\s*([^\n]+)', block)
        files_involved = m.group(1).strip() if m else ''
        
        # Location - lấy từ **Location:**
        m = re.search(r'\*\*Location:\*\*\s*([^\n]+)', block)
        location = m.group(1).strip() if m else ''
        
        # Problem - lấy toàn bộ từ **Problem:** đến **Current Code:**
        m = re.search(r'\*\*Problem:\*\*\s*(.*?)(?=\*\*Current Code|\*\*Fix Recommendation|$)', block, re.DOTALL)
        problem = m.group(1).strip() if m else ''
        
        # Current Code - lấy từ **Current Code:** đến ```
        m = re.search(r'\*\*Current Code[^\*]*\*\*\s*```cpp\n?(.*?)```', block, re.DOTALL)
        current_code = m.group(1).strip() if m else ''
        
        # Fix Recommendation - ưu tiên lấy block cuối cùng (Modern C++ Best Practice)
        fix_blocks = re.findall(r'```cpp\n?(.*?)```', block, re.DOTALL)
        fix_recommendation = ''
        if fix_blocks:
            # Ưu tiên lấy block cuối cùng nếu có nhiều block
            if len(fix_blocks) > 1:
                fix_recommendation = fix_blocks[-1]  # Block cuối cùng (Modern C++ Best Practice)
            else:
                # Nếu chỉ có 1 block, kiểm tra xem có khác Current Code không
                if fix_blocks[0].strip() != current_code.strip():
                    fix_recommendation = fix_blocks[0]
                else:
                    fix_recommendation = fix_blocks[0]  # Vẫn lấy nếu giống
        
        results.append({
            'Issue': title.strip(),
            'Type': resource_type,
            'Severity': severity,
            'Files Involved': files_involved,
            'Location': location,
            'Problem': problem,
            'Current Code': current_code,
            'Fix Recommendation': fix_recommendation
        })
    return results

def render_code_with_lines(code, lang="cpp"):
    lines = code.splitlines() if code else []
    if not lines:
        return '<pre><code class="language-cpp"></code></pre>'
    line_numbers = ''.join(f'<span class="line-number" style="display:block;">{i+1}</span>' for i in range(len(lines)))
    code_html = '\n'.join(lines)
    return f'''
    <div style="display:flex;">
      <div style="background:#f6f8fa;color:#888;padding:6px 8px 6px 6px;font-family:monospace;font-size:13px;line-height:1.5;text-align:right;user-select:none;border-right:1px solid #e1e4e8;">
        {line_numbers}
      </div>
      <pre style="margin:0;flex:1;"><code class="language-{lang}">{code_html}</code></pre>
    </div>
    '''

def is_placeholder(v):
    return (
        v["Issue"].strip().startswith("[#]:") or
        v["Type"].strip().startswith("[resource type]") or
        v["Severity"].strip().startswith("[Critical") or
        v["Files Involved"].strip().startswith("[list of files]") or
        v["Location"].strip().startswith("[function name") or
        v["Current Code"].strip() == "[show problematic code]" or
        v["Fix Recommendation"].strip() == "[suggested code or approach]" or
        v["Problem"].strip() == "[explanation]"
    )

def write_html_table(violations, output_path):
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write('<!DOCTYPE html>\n<html><head><meta charset="utf-8"><title>Resource Leak Report</title>\n')
        f.write('<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/styles/github.min.css">\n')
        f.write('<script src="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/highlight.min.js"></script>\n')
        f.write('<script src="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/languages/cpp.min.js"></script>\n')
        f.write('<script>hljs.highlightAll();</script>\n')
        f.write('''
        <style>
        table{border-collapse:collapse;}
        th,td{border:1px solid #888;padding:6px;vertical-align:top;}
        pre{margin:0;}
        .code-col { max-width: 480px; min-width: 180px; }
        .code-col > div { max-width: 480px; overflow-x: auto; }
        .issue-col { max-width: 320px; min-width: 120px; overflow-x: auto; word-break: break-word; }
        .type-col { max-width: 150px; min-width: 100px; overflow-x: auto; word-break: break-word; }
        .severity-col { max-width: 100px; min-width: 80px; overflow-x: auto; word-break: break-word; }
        .files-col { max-width: 200px; min-width: 120px; overflow-x: auto; word-break: break-word; }
        .location-col { max-width: 200px; min-width: 120px; overflow-x: auto; word-break: break-word; }
        .problem-col { max-width: 340px; min-width: 140px; overflow-x: auto; word-break: break-word; }
        .fix-col { max-width: 400px; min-width: 200px; overflow-x: auto; word-break: break-word; }
        </style>
        ''')
        f.write('</head><body>\n')
        f.write('<table>\n')
        f.write('<tr><th>Issue</th><th>Type</th><th>Severity</th><th>Files Involved</th><th>Location</th><th>Problem</th><th>Current Code</th><th>Fix Recommendation</th></tr>\n')
        for v in violations:
            f.write('<tr>')
            f.write(f'<td class="issue-col">{v["Issue"]}</td>')
            f.write(f'<td class="type-col">{v["Type"]}</td>')
            f.write(f'<td class="severity-col">{v["Severity"]}</td>')
            f.write(f'<td class="files-col">{v["Files Involved"]}</td>')
            f.write(f'<td class="location-col">{v["Location"]}</td>')
            f.write(f'<td class="problem-col">{v["Problem"]}</td>')
            f.write(f'<td class="code-col">{render_code_with_lines(v["Current Code"])}</td>')
            f.write(f'<td class="fix-col">{render_code_with_lines(v["Fix Recommendation"])}</td>')
            f.write('</tr>\n')
        f.write('</table>\n')
        f.write('</body></html>\n')

def write_consolidated_html_table(all_leaks, output_path, source_files):
    """Viết HTML table tổng hợp resource leaks từ nhiều file .md"""
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write('<!DOCTYPE html>\n<html><head><meta charset="utf-8"><title>Consolidated Resource Leak Report</title>\n')
        f.write('<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/styles/github.min.css">\n')
        f.write('<script src="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/highlight.min.js"></script>\n')
        f.write('<script src="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/languages/cpp.min.js"></script>\n')
        f.write('<script>hljs.highlightAll();</script>\n')
        f.write('''<style>
        table{border-collapse:collapse; width: 100%;}
        th,td{border:1px solid #888;padding:6px;vertical-align:top;}
        pre{margin:0;}
        .source-file-header{background-color:#d4edda; font-weight:bold; text-align:center;}
        .code-col { max-width: 480px; min-width: 180px; }
        .code-col > div { max-width: 480px; overflow-x: auto; }
        .issue-col { max-width: 320px; min-width: 120px; overflow-x: auto; word-break: break-word; }
        .type-col { max-width: 150px; min-width: 100px; overflow-x: auto; word-break: break-word; }
        .severity-col { max-width: 100px; min-width: 80px; overflow-x: auto; word-break: break-word; }
        .files-col { max-width: 200px; min-width: 120px; overflow-x: auto; word-break: break-word; }
        .location-col { max-width: 200px; min-width: 120px; overflow-x: auto; word-break: break-word; }
        .problem-col { max-width: 340px; min-width: 140px; overflow-x: auto; word-break: break-word; }
        .source-col { max-width: 150px; min-width: 100px; overflow-x: auto; word-break: break-word; }
        </style>''')
        f.write('</head><body>\n')
        f.write(f'<h1>Consolidated Resource Leak Report</h1>\n')
        f.write(f'<p>Processed {len(source_files)} files: {", ".join(source_files)}</p>\n')
        f.write(f'<p>Total resource leaks: {len(all_leaks)}</p>\n')
        f.write('<table>\n')
        f.write('<tr><th>Source File</th><th>Issue</th><th>Type</th><th>Severity</th><th>Files Involved</th><th>Location</th><th>Problem</th><th>Current Code</th><th>Fix Recommendation</th></tr>\n')
        
        # Group by source file
        leaks_by_file = {}
        for leak in all_leaks:
            source = leak.get('source_file', 'unknown')
            if source not in leaks_by_file:
                leaks_by_file[source] = []
            leaks_by_file[source].append(leak)
        
        for source_file, leaks in leaks_by_file.items():
            # Header row for each file
            f.write(f'<tr class="source-file-header"><td colspan="9">File: {source_file} ({len(leaks)} resource leaks)</td></tr>\n')
            for leak in leaks:
                f.write('<tr>')
                f.write(f'<td class="source-col">{source_file}</td>')
                f.write(f'<td class="issue-col">{leak["Issue"]}</td>')
                f.write(f'<td class="type-col">{leak["Type"]}</td>')
                f.write(f'<td class="severity-col">{leak["Severity"]}</td>')
                f.write(f'<td class="files-col">{leak["Files Involved"]}</td>')
                f.write(f'<td class="location-col">{leak["Location"]}</td>')
                f.write(f'<td class="problem-col">{leak["Problem"]}</td>')
                f.write(f'<td class="code-col">{render_code_with_lines(leak["Current Code"])}</td>')
                f.write(f'<td class="code-col">{render_code_with_lines(leak["Fix Recommendation"])}</td>')
                f.write('</tr>\n')
        
        f.write('</table>\n')
        f.write('</body></html>\n')

def print_usage():
    print("Usage: python report_resource.py <input.md> [-o <output_file>]")
    sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) == 2:
        input_path = sys.argv[1]
        output_path = "output_resource.html"
    elif len(sys.argv) == 4 and sys.argv[2] == "-o":
        input_path = sys.argv[1]
        output_path = sys.argv[3]
    else:
        print_usage()
    with open(input_path, 'r', encoding='utf-8') as f:
        md_text = f.read()
    violations = extract_violations(md_text)
    write_html_table(violations, output_path)
