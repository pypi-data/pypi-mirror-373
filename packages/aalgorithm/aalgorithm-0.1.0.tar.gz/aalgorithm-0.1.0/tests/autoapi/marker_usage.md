# 使用指南 https://github.com/datalab-to/marker

## 1. 文档转换（PDF/图片/PPTX/DOCX/XLSX/HTML/EPUB）

### 功能说明
将 PDF、图片、PPTX、DOCX、XLSX、HTML、EPUB 等文件快速、准确地转换为 Markdown、JSON、HTML 或 Chunks 格式。支持表格、图片、公式、代码块等内容的结构化提取和格式化。

已经在 marker 这个 conda 环境中安装了相关依赖。运行相关 CLI 需要先激活虚拟环境。
### 输入
- 文件路径，例如：`/path/to/file.pdf` 或 `/path/to/file.jpg`

### 预期输出
返回输出文件夹压缩后的zip文件路径

### 使用示例
```bash
marker_single /path/to/file.pdf --output_format markdown
```

