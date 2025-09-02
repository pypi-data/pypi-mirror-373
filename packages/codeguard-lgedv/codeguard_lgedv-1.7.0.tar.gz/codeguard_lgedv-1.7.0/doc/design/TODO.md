# Cai dat
brew install pandoc   # macOS
sudo apt install pandoc  # Ubuntu

## window
https://pandoc.org/installing.html => .msi file
cmd => pandoc --version

## convert
pandoc input.docx -o output.md
pandoc input.html -o output.md

### excel file
Mở file Excel, chọn "Save As" → chọn định dạng .csv.
pandoc input.csv -o output.md

Hoặc dùng tool chuyên biệt như csvtomd:
pip install csvtomd
csvtomd input.csv > output.md