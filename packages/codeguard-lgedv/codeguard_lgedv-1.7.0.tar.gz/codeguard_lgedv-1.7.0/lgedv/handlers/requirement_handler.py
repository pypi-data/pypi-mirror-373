import os
import json

def extract_requirements_from_md(md_path):
    """Trích xuất requirements từ file markdown"""
    requirements = []
    
    with open(md_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Tìm bảng Use-case checklist
    lines = content.split('\n')
    in_table = False
    
    for line in lines:
        # Bắt đầu bảng
        if '| TT | Tên Use-case' in line:
            in_table = True
            continue
        
        # Kết thúc bảng
        if in_table and line.strip() == '':
            break
            
        # Xử lý dòng trong bảng
        if in_table and line.startswith('|'):
            # Bỏ qua dòng separator
            if '---' in line:
                continue
                
            parts = [part.strip() for part in line.split('|')[1:-1]]  # Bỏ phần tử đầu và cuối rỗng
            
            if len(parts) >= 8:  # Đảm bảo có đủ cột
                tt = parts[0] if parts[0] != 'NaN' else ''
                usecase = parts[1] if parts[1] != 'NaN' else ''
                actor = parts[2] if parts[2] != 'NaN' else ''
                transaction = parts[3] if parts[3] != 'NaN' else ''
                priority = parts[4] if parts[4] != 'NaN' else ''
                assignee = parts[5] if parts[5] != 'NaN' else ''
                deadline = parts[6] if parts[6] != 'NaN' else ''
                status = parts[7] if parts[7] != 'NaN' else ''
                
                if usecase or transaction:  # Chỉ lấy dòng có thông tin
                    requirements.append({
                        'id': tt,
                        'usecase': usecase,
                        'actor': actor,
                        'transaction': transaction,
                        'priority': priority,
                        'assignee': assignee,
                        'deadline': deadline,
                        'status': status
                    })
    
    return requirements

def handle_requirement_analysis(dir_path: str):
    """Tool call: Phân tích requirement từ các file .md trong thư mục chỉ định."""
    try:
        if not os.path.exists(dir_path):
            return {"error": f"Thư mục không tồn tại: {dir_path}"}
        
        md_files = [f for f in os.listdir(dir_path) if f.endswith('.md')]
        
        if not md_files:
            return {"error": "Không tìm thấy file .md nào trong thư mục"}
        
        result = {}
        total_requirements = 0
        
        for md_file in md_files:
            file_path = os.path.join(dir_path, md_file)
            try:
                requirements = extract_requirements_from_md(file_path)
                result[md_file] = {
                    'total_requirements': len(requirements),
                    'requirements': requirements
                }
                total_requirements += len(requirements)
            except Exception as e:
                result[md_file] = {"error": str(e)}
        
        # Tạo summary
        summary = {
            'summary': {
                'total_files_analyzed': len(md_files),
                'total_requirements': total_requirements,
                'directory': dir_path
            },
            'files': result
        }
        
        return summary
        
    except Exception as e:
        return {"error": f"Lỗi khi phân tích requirement: {str(e)}"}