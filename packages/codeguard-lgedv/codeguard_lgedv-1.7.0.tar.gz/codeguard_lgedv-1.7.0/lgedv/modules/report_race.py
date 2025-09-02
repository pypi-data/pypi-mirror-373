import re
import sys

def extract_races(md_text):
    # Lọc các block RACE CONDITION - tìm từ ## 🚨 đến ---
    race_pattern = r'## 🚨 (RACE CONDITION #\d+: [^\n]+)(.*?)(?=^## 🚨 |^---|\Z)'
    matches = re.findall(race_pattern, md_text, flags=re.DOTALL | re.MULTILINE)
    results = []
    for title, block in matches:
        # Type - lấy từ **Type:**
        m = re.search(r'\*\*Type:\*\*\s*([^\n]+)', block)
        race_type = m.group(1).strip() if m else ''
        
        # Severity - lấy từ **Severity:**
        m = re.search(r'\*\*Severity:\*\*\s*([^\n]+)', block)
        severity = m.group(1).strip() if m else ''
        
        # Files Involved - lấy từ **Files Involved:**
        m = re.search(r'\*\*Files Involved:\*\*\s*([^\n]+)', block)
        files_involved = m.group(1).strip() if m else ''
        
        # Function Name - lấy từ **Function Name:** nếu có, nếu không thì lấy từ **Location:**
        m = re.search(r'\*\*Function Name:\*\*\s*([^\n]+)', block)
        function_name = m.group(1).strip() if m else ''
        if not function_name:
            m = re.search(r'\*\*Location:\*\*\s*([^\n]+)', block)
            function_name = m.group(1).strip() if m else ''
        
        # Problem - lấy từ sau **Problem Description:** đến trước **Current Code:**
        m = re.search(r'\*\*Problem Description:\*\*\s*(.*?)(?=\*\*Current Code:|\*\*Fix Recommendation:|$)', block, re.DOTALL)
        problem = m.group(1).strip() if m else ''
        
        # Current Code - lấy từ sau **Current Code:** đến trước **Fix Recommendation:**
        m = re.search(r'\*\*Current Code[^\*]*\*\*\s*(.*?)(?=\*\*Fix Recommendation:|$)', block, re.DOTALL)
        current_code_text = m.group(1).strip() if m else ''
        
        # Trích xuất code từ current_code_text (lấy nội dung trong ```cpp...```)
        code_match = re.search(r'```cpp\n?(.*?)```', current_code_text, re.DOTALL)
        current_code = code_match.group(1).strip() if code_match else ''
        
        # Fix Recommendation - lấy từ sau **Fix Recommendation:** đến trước ---
        m = re.search(r'\*\*Fix Recommendation:\*\*\s*(.*?)(?=^---|\Z)', block, re.DOTALL | re.MULTILINE)
        fix_text = m.group(1).strip() if m else ''
        
        # Trích xuất code từ fix_text (lấy nội dung trong ```cpp...```)
        fix_code_match = re.search(r'```cpp\n?(.*?)```', fix_text, re.DOTALL)
        fix_recommendation = fix_code_match.group(1).strip() if fix_code_match else ''
        
        results.append({
            'Issue': title.strip(),
            'Type': race_type,
            'Severity': severity,
            'Files Involved': files_involved,
            'Function Name': function_name,
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

def write_html_table(races, output_path):
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write('<!DOCTYPE html>\n<html><head><meta charset="utf-8"><title>Race Condition Report</title>\n')
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
        .function-col { max-width: 200px; min-width: 120px; overflow-x: auto; word-break: break-word; }
        .problem-col { max-width: 340px; min-width: 140px; overflow-x: auto; word-break: break-word; }
        .fix-col { max-width: 400px; min-width: 200px; overflow-x: auto; word-break: break-word; }
        </style>
        ''')
        f.write('</head><body>\n')
        f.write('<table>\n')
        f.write('<tr><th>Issue</th><th>Type</th><th>Severity</th><th>Files Involved</th><th>Function/Location</th><th>Problem</th><th>Current Code</th><th>Fix Recommendation</th></tr>\n')
        for v in races:
            f.write('<tr>')
            f.write(f'<td class="issue-col">{v["Issue"]}</td>')
            f.write(f'<td class="type-col">{v["Type"]}</td>')
            f.write(f'<td class="severity-col">{v["Severity"]}</td>')
            f.write(f'<td class="files-col">{v["Files Involved"]}</td>')
            f.write(f'<td class="function-col">{v["Function Name"]}</td>')
            f.write(f'<td class="problem-col">{v["Problem"]}</td>')
            f.write(f'<td class="code-col">{render_code_with_lines(v["Current Code"])}</td>')
            f.write(f'<td class="fix-col">{render_code_with_lines(v["Fix Recommendation"])}</td>')
            f.write('</tr>\n')
        f.write('</table>\n')
        f.write('</body></html>\n')

def write_consolidated_html_table(all_races, output_path, source_files):
    """Viết HTML table tổng hợp race conditions từ nhiều file .md"""
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write('<!DOCTYPE html>\n<html><head><meta charset="utf-8"><title>Consolidated Race Condition Report</title>\n')
        f.write('<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/styles/github.min.css">\n')
        f.write('<script src="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/highlight.min.js"></script>\n')
        f.write('<script src="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/languages/cpp.min.js"></script>\n')
        f.write('<script>hljs.highlightAll();</script>\n')
        f.write('''<style>
        table{border-collapse:collapse; width: 100%;}
        th,td{border:1px solid #888;padding:6px;vertical-align:top;}
        pre{margin:0;}
        .source-file-header{background-color:#fff3cd; font-weight:bold; text-align:center;}
        .code-col { max-width: 480px; min-width: 180px; }
        .code-col > div { max-width: 480px; overflow-x: auto; }
        .issue-col { max-width: 320px; min-width: 120px; overflow-x: auto; word-break: break-word; }
        .type-col { max-width: 150px; min-width: 100px; overflow-x: auto; word-break: break-word; }
        .severity-col { max-width: 100px; min-width: 80px; overflow-x: auto; word-break: break-word; }
        .files-col { max-width: 200px; min-width: 120px; overflow-x: auto; word-break: break-word; }
        .function-col { max-width: 200px; min-width: 120px; overflow-x: auto; word-break: break-word; }
        .problem-col { max-width: 340px; min-width: 140px; overflow-x: auto; word-break: break-word; }
        .source-col { max-width: 150px; min-width: 100px; overflow-x: auto; word-break: break-word; }
        </style>\n''')
        f.write('</head><body>\n')
        f.write(f'<h1>Consolidated Race Condition Report</h1>\n')
        f.write(f'<p>Processed {len(source_files)} files: {", ".join(source_files)}</p>\n')
        f.write(f'<p>Total race conditions: {len(all_races)}</p>\n')
        f.write('<table>\n')
        f.write('<tr><th>Source File</th><th>Issue</th><th>Type</th><th>Severity</th><th>Files Involved</th><th>Function/Location</th><th>Problem</th><th>Current Code</th><th>Fix Recommendation</th></tr>\n')
        
        # Group by source file
        races_by_file = {}
        for race in all_races:
            source = race.get('source_file', 'unknown')
            if source not in races_by_file:
                races_by_file[source] = []
            races_by_file[source].append(race)
        
        for source_file, races in races_by_file.items():
            # Header row for each file
            f.write(f'<tr class="source-file-header"><td colspan="9">File: {source_file} ({len(races)} race conditions)</td></tr>\n')
            for race in races:
                f.write('<tr>')
                f.write(f'<td class="source-col">{source_file}</td>')
                f.write(f'<td class="issue-col">{race["Issue"]}</td>')
                f.write(f'<td class="type-col">{race["Type"]}</td>')
                f.write(f'<td class="severity-col">{race["Severity"]}</td>')
                f.write(f'<td class="files-col">{race["Files Involved"]}</td>')
                f.write(f'<td class="function-col">{race["Function Name"]}</td>')
                f.write(f'<td class="problem-col">{race["Problem"]}</td>')
                f.write(f'<td class="code-col">{render_code_with_lines(race["Current Code"])}</td>')
                f.write(f'<td class="code-col">{render_code_with_lines(race["Fix Recommendation"])}</td>')
                f.write('</tr>\n')
        f.write('</table>\n</body></html>\n')
        

def print_usage():
    print("Usage: python report_race.py <input.md> [-o <output_file>]")
    sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) == 2:
        input_path = sys.argv[1]
        output_path = "output_race.html"
    elif len(sys.argv) == 4 and sys.argv[2] == "-o":
        input_path = sys.argv[1]
        output_path = sys.argv[3]
    else:
        print_usage()
    with open(input_path, 'r', encoding='utf-8') as f:
        md_text = f.read()
    races = extract_races(md_text)
    write_html_table(races, output_path)
