# DOCX MCP 处理器

一个功能强大的Word文档处理工具，基于MCP (Model Context Protocol) 协议，支持完整的文档操作、图片编辑和表格处理。

## 🌟 主要特性

### 📄 文档操作
- ✅ 创建、打开、保存Word文档
- ✅ 支持文档另存为和副本创建
- ✅ 完整的段落和标题操作
- ✅ 页面设置和分页控制

### 📋 表格功能
- ✅ 创建和编辑表格
- ✅ **支持在指定位置插入行** (如在第1、2行之间插入)
- ✅ **支持在指定位置插入列**
- ✅ 单元格合并和编辑
- ✅ 删除行和列

### 🖼️ 图片处理
- ✅ **图片插入和删除**
- ✅ **图片大小调整**
- ✅ **图片位置控制**
- ✅ 支持多种图片格式

### 🎨 格式化
- ✅ 字体样式（加粗、斜体、下划线）
- ✅ 字体大小和颜色
- ✅ 段落对齐方式
- ✅ 自定义样式

### 🔍 搜索与替换
- ✅ 全文搜索
- ✅ 查找和替换
- ✅ 按标题替换章节内容

### ☁️ 云存储支持
- ✅ 阿里云OSS集成
- ✅ 网络文件下载
- ✅ 文件上传和管理

## 🚀 快速开始

### 安装

```bash
pip install docx-mcp
```

### 基本使用

#### 1. 作为MCP服务器运行

```bash
# 启动MCP服务器
docx-mcp

# 或者使用交互模式
docx-interactive
```

#### 2. 作为Python库使用

```python
from core.enhanced_docx_processor import EnhancedDocxProcessor

# 创建处理器实例
processor = EnhancedDocxProcessor()

# 打开文档
processor.open_document("document.docx")

# 在第1、2行之间插入新行
processor.add_table_row(
    table_index=0, 
    data=["新行内容", "数据1", "数据2"], 
    row_index=1  # 在第1行和第2行之间插入
)

# 调整图片大小
processor.resize_image(image_index=0, width="5cm", height="3cm")

# 保存文档
processor.save_document()
```

## 📋 主要功能

### 表格操作示例

```python
# 在指定位置插入行
processor.add_table_row(table_index=0, row_index=1, data=["新行数据"])

# 在指定位置插入列  
processor.add_table_column(table_index=0, column_index=1, data=["新列数据"])

# 编辑单元格
processor.edit_table_cell(table_index=0, row_index=0, col_index=0, text="新内容")

# 合并单元格
processor.merge_table_cells(table_index=0, start_row=0, start_col=0, end_row=1, end_col=1)
```

### 图片处理示例

```python
# 添加图片
processor.add_image("image.jpg", width="10cm", height="8cm", alignment="center")

# 调整图片大小
processor.resize_image(image_index=0, width="5cm", maintain_aspect_ratio=True)

# 删除图片
processor.delete_image(image_index=0)

# 列出所有图片
processor.list_images()
```

### 文档格式化示例

```python
# 添加格式化段落
processor.add_paragraph(
    text="重要内容", 
    bold=True, 
    italic=True, 
    font_size=16, 
    color="#FF0000"
)

# 添加标题
processor.add_heading("章节标题", level=2)

# 设置页边距
processor.set_page_margins(top=2.5, bottom=2.5, left=2.0, right=2.0)
```

## 🔧 MCP集成

本工具完全兼容MCP协议，可以作为AI工具链的一部分使用：

1. **启动MCP服务器**: `docx-mcp`
2. **在AI环境中使用**: 通过MCP协议调用所有功能
3. **交互式模式**: `docx-interactive` 进入命令行交互模式

## 📦 依赖要求

- Python 3.8+
- python-docx >= 1.1.0
- mcp >= 1.0.0
- fastmcp >= 0.5.0
- Pillow >= 10.0.0
- pydantic >= 2.5.0

## 🤝 贡献

欢迎提交Issue和Pull Request！

## 📄 许可证

MIT License

## 📞 支持

- GitHub: [https://github.com/rockcj/Docx_MCP_cj](https://github.com/rockcj/Docx_MCP_cj)
- Issues: [https://github.com/rockcj/Docx_MCP_cj/issues](https://github.com/rockcj/Docx_MCP_cj/issues)

---

**🎯 特别适用于**: 文档自动化、AI文档处理、批量文档操作、Word文档模板生成等场景。