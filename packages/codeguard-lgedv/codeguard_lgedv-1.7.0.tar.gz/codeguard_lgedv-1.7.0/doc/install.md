# Build and upload package
## pypi
# https://pypi.org/manage/account/token/
# taikt_18_8
(user: taikt, Yeuem2025@, google authenticator)

## build server (linux)
cd /home/worker/src/codefun/deepl/mcp_server
(trong thu muc chua pyproject.toml)
python3 -m venv venv
source venv/bin/activate
pip install -e .

## build server (window)
cd C:\path\to\codefun\deepl\mcp_server
python -m venv venv
venv\Scripts\activate
pip install -e .


## package (linux)
rm -rf dist
pip install build twine (in venv environment)
python -m build
Kết quả: thư mục dist/ sẽ có file .whl và .tar.gz

## upload len PyPI (linux)
twine upload dist/*

# Install server for user (with pip)
## on Linux
sudo apt install python3 python3-venv python3-pip
python3 -m venv venv
source venv/bin/activate
pip install codeguard-lgedv

## on window
### 1. Cài đặt Python và pip
- Truy cập trang chủ Python: https://www.python.org/downloads/windows/
- Tải bản Python 3.9+ 
### 2. Tạo môi trường ảo (venv)
- Tạo thư mục dự án (ví dụ: `C:\mcp_test`)
  python -m venv venv
  venv\Scripts\activate

### 3. Cài đặt MCP server từ PyPI
  pip install codeguard-lgedv
  dir venv\Scripts\codeguard.exe

### 4. Cấu hình file mcp.json 
- create folder .vscode on current codebase
- create file mcp.json in .vscode folder
- Ví dụ nội dung:
  ```json
  {
    "servers": {
        "lgedv": {
            "command": "C:\\Users\\tai2.tran\\mcp_server\\venv\\Scripts\\codeguard.exe",
            "args": ["--transport", "stdio"],
            "env": {
            "src_dir": "E:\\src\\code_test\\mem_leak",
            "custom_path": "E:\\src\\codefun\\deepl\\mcp_server\\lgedv\\resources\\CustomRule.md" 
            }
        }
    }
  }
  ```
## How to use report
python report.py in.md -o out.md
python report_http.py inp.md -o out.html

## get code context
### e.g tiger framework
#get_src_context dir=/home/worker/src/tsu/nad/LGE/tiger-src/servicelayer/core/framework/utils

(right click on a code dir in vscode -> Copy Path)



