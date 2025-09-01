#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
增强版MCP DOCX处理服务
整合了server.py的优秀设计和新增的功能模块
提供完整的Word文档处理能力
"""

import os
import tempfile
import logging
import traceback
from contextlib import asynccontextmanager
from typing import AsyncIterator, Dict, Any, Optional, List

from fastmcp import FastMCP
from core.enhanced_docx_processor import EnhancedDocxProcessor

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(os.path.join(tempfile.gettempdir(), "enhanced_docx_mcp_server.log")),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("EnhancedDocxMCPServer")

# 创建全局处理器实例
processor = EnhancedDocxProcessor()

# 创建MCP服务器
mcp = FastMCP("EnhancedDocxProcessor")

# ==================== 文档生命周期管理工具 ====================

@mcp.tool()
def create_document(file_path: str) -> str:
    """
    创建新的Word文档
    
    Parameters:
    - file_path: 文档保存路径
    """
    try:
        return processor.create_document(file_path)
    except Exception as e:
        error_msg = f"创建文档失败: {str(e)}"
        logger.error(error_msg)
        return error_msg

@mcp.tool()
def open_document(file_path: str) -> str:
    """
    打开现有Word文档
    
    Parameters:
    - file_path: 要打开的文档路径
    """
    try:
        return processor.open_document(file_path)
    except Exception as e:
        error_msg = f"打开文档失败: {str(e)}"
        logger.error(error_msg)
        return error_msg

@mcp.tool()
def save_document() -> str:
    """
    保存当前打开的Word文档到原文件
    """
    try:
        return processor.save_document()
    except Exception as e:
        error_msg = f"保存文档失败: {str(e)}"
        logger.error(error_msg)
        return error_msg

@mcp.tool()
def save_as_document(new_file_path: str) -> str:
    """
    将当前文档另存为新文件
    
    Parameters:
    - new_file_path: 新文件保存路径
    """
    try:
        return processor.save_as_document(new_file_path)
    except Exception as e:
        error_msg = f"另存文档失败: {str(e)}"
        logger.error(error_msg)
        return error_msg

@mcp.tool()
def close_document() -> str:
    """
    关闭当前文档
    """
    try:
        return processor.close_document()
    except Exception as e:
        error_msg = f"关闭文档失败: {str(e)}"
        logger.error(error_msg)
        return error_msg

@mcp.tool()
def get_document_info() -> str:
    """
    获取当前文档信息，包括段落数、表格数、节数等
    """
    try:
        return processor.get_document_info()
    except Exception as e:
        error_msg = f"获取文档信息失败: {str(e)}"
        logger.error(error_msg)
        return error_msg

# ==================== 内容编辑工具 ====================

@mcp.tool()
def add_paragraph(
    text: str,
    bold: bool = False,
    italic: bool = False,
    underline: bool = False,
    font_size: Optional[int] = None,
    font_name: Optional[str] = None,
    color: Optional[str] = None,
    alignment: Optional[str] = None,
    style: Optional[str] = None
) -> str:
    """
    向文档添加段落
    
    Parameters:
    - text: 段落文本内容
    - bold: 是否加粗
    - italic: 是否斜体
    - underline: 是否下划线
    - font_size: 字体大小（磅）
    - font_name: 字体名称
    - color: 文字颜色（十六进制格式，如#FF0000）
    - alignment: 对齐方式（left/center/right/justify）
    - style: 段落样式名称
    """
    try:
        return processor.add_paragraph(
            text, bold, italic, underline, font_size, font_name, color, alignment, style
        )
    except Exception as e:
        error_msg = f"添加段落失败: {str(e)}"
        logger.error(error_msg)
        return error_msg

@mcp.tool()
def add_heading(text: str, level: int) -> str:
    """
    向文档添加标题
    
    Parameters:
    - text: 标题文本
    - level: 标题级别（1-9）
    """
    try:
        return processor.add_heading(text, level)
    except Exception as e:
        error_msg = f"添加标题失败: {str(e)}"
        logger.error(error_msg)
        return error_msg

@mcp.tool()
def add_page_break() -> str:
    """
    添加分页符
    """
    try:
        return processor.add_page_break()
    except Exception as e:
        error_msg = f"添加分页符失败: {str(e)}"
        logger.error(error_msg)
        return error_msg

@mcp.tool()
def delete_paragraph(paragraph_index: int) -> str:
    """
    删除指定段落
    
    Parameters:
    - paragraph_index: 要删除的段落索引
    """
    try:
        return processor.delete_paragraph(paragraph_index)
    except Exception as e:
        error_msg = f"删除段落失败: {str(e)}"
        logger.error(error_msg)
        return error_msg

# ==================== 表格操作工具 ====================

@mcp.tool()
def add_table(rows: int, cols: int, data: Optional[List[List[str]]] = None) -> str:
    """
    向文档添加表格
    
    Parameters:
    - rows: 行数
    - cols: 列数
    - data: 表格数据，二维数组
    """
    try:
        return processor.add_table(rows, cols, data)
    except Exception as e:
        error_msg = f"添加表格失败: {str(e)}"
        logger.error(error_msg)
        return error_msg

@mcp.tool()
def add_table_row(table_index: int, data: Optional[List[str]] = None, row_index: Optional[int] = None) -> str:
    """
    向表格添加行
    
    Parameters:
    - table_index: 表格索引
    - data: 行数据列表
    - row_index: 插入位置，None表示在末尾添加，0表示在开头插入，1表示在第1行和第2行之间插入
    """
    try:
        return processor.add_table_row(table_index, data, row_index)
    except Exception as e:
        error_msg = f"添加表格行失败: {str(e)}"
        logger.error(error_msg)
        return error_msg

@mcp.tool()
def delete_table_row(table_index: int, row_index: int) -> str:
    """
    删除表格行
    
    Parameters:
    - table_index: 表格索引
    - row_index: 要删除的行索引
    """
    try:
        return processor.delete_table_row(table_index, row_index)
    except Exception as e:
        error_msg = f"删除表格行失败: {str(e)}"
        logger.error(error_msg)
        return error_msg

@mcp.tool()
def edit_table_cell(table_index: int, row_index: int, col_index: int, text: str) -> str:
    """
    编辑表格单元格内容
    
    Parameters:
    - table_index: 表格索引
    - row_index: 行索引
    - col_index: 列索引
    - text: 新的单元格文本
    """
    try:
        return processor.edit_table_cell(table_index, row_index, col_index, text)
    except Exception as e:
        error_msg = f"编辑单元格失败: {str(e)}"
        logger.error(error_msg)
        return error_msg

@mcp.tool()
def merge_table_cells(
    table_index: int,
    start_row: int,
    start_col: int,
    end_row: int,
    end_col: int
) -> str:
    """
    合并表格单元格
    
    Parameters:
    - table_index: 表格索引
    - start_row: 起始行索引
    - start_col: 起始列索引
    - end_row: 结束行索引
    - end_col: 结束列索引
    """
    try:
        return processor.merge_table_cells(table_index, start_row, start_col, end_row, end_col)
    except Exception as e:
        error_msg = f"合并单元格失败: {str(e)}"
        logger.error(error_msg)
        return error_msg

# ==================== 文本搜索和替换工具 ====================

@mcp.tool()
def search_text(keyword: str) -> str:
    """
    在文档中搜索文本
    
    Parameters:
    - keyword: 要搜索的关键词
    """
    try:
        return processor.search_text(keyword)
    except Exception as e:
        error_msg = f"搜索文本失败: {str(e)}"
        logger.error(error_msg)
        return error_msg

@mcp.tool()
def find_and_replace(find_text: str, replace_text: str) -> str:
    """
    查找并替换文本
    
    Parameters:
    - find_text: 要查找的文本
    - replace_text: 替换为的文本
    """
    try:
        return processor.find_and_replace(find_text, replace_text)
    except Exception as e:
        error_msg = f"查找替换失败: {str(e)}"
        logger.error(error_msg)
        return error_msg

# ==================== 图片处理工具 ====================

@mcp.tool()
def add_image(
    image_path: str,
    width: Optional[str] = None,
    height: Optional[str] = None,
    alignment: str = "left",
    paragraph_index: Optional[int] = None
) -> str:
    """
    向文档添加图片
    
    Parameters:
    - image_path: 图片文件路径
    - width: 图片宽度（支持"5cm", "2in"等格式）
    - height: 图片高度
    - alignment: 对齐方式（left/center/right）
    - paragraph_index: 插入位置，None表示文档末尾
    """
    try:
        return processor.add_image(image_path, width, height, alignment, paragraph_index)
    except Exception as e:
        error_msg = f"添加图片失败: {str(e)}"
        logger.error(error_msg)
        return error_msg

@mcp.tool()
def resize_image(
    image_index: int,
    width: Optional[str] = None,
    height: Optional[str] = None,
    maintain_aspect_ratio: bool = True
) -> str:
    """
    调整图片大小
    
    Parameters:
    - image_index: 图片索引（按文档中出现顺序）
    - width: 新宽度
    - height: 新高度
    - maintain_aspect_ratio: 是否保持宽高比
    """
    try:
        return processor.resize_image(image_index, width, height, maintain_aspect_ratio)
    except Exception as e:
        error_msg = f"调整图片大小失败: {str(e)}"
        logger.error(error_msg)
        return error_msg

@mcp.tool()
def delete_image(image_index: int) -> str:
    """
    删除图片
    
    Parameters:
    - image_index: 要删除的图片索引
    """
    try:
        return processor.delete_image(image_index)
    except Exception as e:
        error_msg = f"删除图片失败: {str(e)}"
        logger.error(error_msg)
        return error_msg

@mcp.tool()
def list_images() -> str:
    """
    列出文档中的所有图片信息
    """
    try:
        return processor.list_images()
    except Exception as e:
        error_msg = f"列出图片失败: {str(e)}"
        logger.error(error_msg)
        return error_msg

# ==================== 字体和格式化工具 ====================

@mcp.tool()
def set_paragraph_font(
    paragraph_index: int,
    font_name: Optional[str] = None,
    font_size: Optional[int] = None,
    bold: Optional[bool] = None,
    italic: Optional[bool] = None,
    underline: Optional[bool] = None,
    color: Optional[str] = None,
    alignment: Optional[str] = None
) -> str:
    """
    设置段落字体样式
    
    Parameters:
    - paragraph_index: 段落索引
    - font_name: 字体名称
    - font_size: 字体大小（磅）
    - bold: 是否加粗
    - italic: 是否斜体
    - underline: 是否下划线
    - color: 字体颜色（十六进制，如#FF0000）
    - alignment: 对齐方式（left/center/right/justify）
    """
    try:
        return processor.set_paragraph_font(
            paragraph_index, font_name, font_size, bold, italic, underline, color, alignment
        )
    except Exception as e:
        error_msg = f"设置段落字体失败: {str(e)}"
        logger.error(error_msg)
        return error_msg

@mcp.tool()
def set_text_range_font(
    paragraph_index: int,
    start_pos: int,
    end_pos: int,
    font_name: Optional[str] = None,
    font_size: Optional[int] = None,
    bold: Optional[bool] = None,
    italic: Optional[bool] = None,
    underline: Optional[bool] = None,
    color: Optional[str] = None
) -> str:
    """
    设置文本范围的字体样式
    
    Parameters:
    - paragraph_index: 段落索引
    - start_pos: 开始位置
    - end_pos: 结束位置
    - font_name: 字体名称
    - font_size: 字体大小
    - bold: 是否加粗
    - italic: 是否斜体
    - underline: 是否下划线
    - color: 字体颜色
    """
    try:
        return processor.set_text_range_font(
            paragraph_index, start_pos, end_pos, font_name, font_size, bold, italic, underline, color
        )
    except Exception as e:
        error_msg = f"设置文本范围字体失败: {str(e)}"
        logger.error(error_msg)
        return error_msg

@mcp.tool()
def get_font_info(paragraph_index: int) -> str:
    """
    获取段落的字体信息
    
    Parameters:
    - paragraph_index: 段落索引
    """
    try:
        return processor.get_font_info(paragraph_index)
    except Exception as e:
        error_msg = f"获取字体信息失败: {str(e)}"
        logger.error(error_msg)
        return error_msg

# ==================== 页面设置工具 ====================

@mcp.tool()
def set_page_margins(
    top: Optional[float] = None,
    bottom: Optional[float] = None,
    left: Optional[float] = None,
    right: Optional[float] = None
) -> str:
    """
    设置页边距
    
    Parameters:
    - top: 上边距（厘米）
    - bottom: 下边距（厘米）
    - left: 左边距（厘米）
    - right: 右边距（厘米）
    """
    try:
        return processor.set_page_margins(top, bottom, left, right)
    except Exception as e:
        error_msg = f"设置页边距失败: {str(e)}"
        logger.error(error_msg)
        return error_msg

# ==================== 表格列操作工具 ====================

@mcp.tool()
def add_table_column(table_index: int, column_index: int = None, data: list = None) -> str:
    """
    向表格添加列
    
    Parameters:
    - table_index: 表格索引
    - column_index: 插入位置索引，None=右侧添加，0=左侧插入，正整数=指定位置
    - data: 新列数据列表，按行顺序填充，如["标题", "数据1", "数据2"]，None=空单元格
    """
    try:
        return processor.add_table_column(table_index, column_index, data)
    except Exception as e:
        error_msg = f"添加表格列失败: {str(e)}"
        logger.error(error_msg)
        return error_msg

@mcp.tool()
def delete_table_column(table_index: int, column_index: int) -> str:
    """
    删除表格列
    
    Parameters:
    - table_index: 表格索引
    - column_index: 要删除的列索引（从0开始），0=第一列
    """
    try:
        return processor.delete_table_column(table_index, column_index)
    except Exception as e:
        error_msg = f"删除表格列失败: {str(e)}"
        logger.error(error_msg)
        return error_msg

# ==================== OSS云存储工具 ====================

@mcp.tool()
def upload_current_document_to_oss(custom_filename: str = None) -> str:
    """
    上传当前文档到OSS云存储
    
    Parameters:
    - custom_filename: 自定义文件名，None则自动生成
    """
    try:
        result = processor.upload_current_document_to_oss(custom_filename)
        if "error" in result:
            return result["error"]
        return f"上传成功！下载链接: {result.get('download_url', '')}"
    except Exception as e:
        error_msg = f"上传当前文档到OSS失败: {str(e)}"
        logger.error(error_msg)
        return error_msg

@mcp.tool()
def upload_file_to_oss(file_path: str, custom_filename: str = None) -> str:
    """
    上传指定文件到OSS云存储
    
    Parameters:
    - file_path: 要上传的文件路径
    - custom_filename: 自定义文件名，None则自动生成
    """
    try:
        result = processor.upload_file_to_oss(file_path, custom_filename)
        if "error" in result:
            return result["error"]
        return f"上传成功！文件: {result.get('filename', '')}, 下载链接: {result.get('download_url', '')}"
    except Exception as e:
        error_msg = f"上传文件到OSS失败: {str(e)}"
        logger.error(error_msg)
        return error_msg

@mcp.tool()
def download_file_from_oss(filename: str, local_path: str = None) -> str:
    """
    从OSS云存储下载文件
    
    Parameters:
    - filename: OSS上的文件名
    - local_path: 本地保存路径，None则保存到临时目录
    """
    try:
        result = processor.download_file_from_oss(filename, local_path)
        if "error" in result:
            return result["error"]
        return f"下载成功！文件保存到: {result.get('local_path', '')}"
    except Exception as e:
        error_msg = f"从OSS下载文件失败: {str(e)}"
        logger.error(error_msg)
        return error_msg

@mcp.tool()
def download_file_from_url(url: str, local_path: str = None) -> str:
    """
    从网络URL下载文件
    
    Parameters:
    - url: 文件的网络URL
    - local_path: 本地保存路径，None则保存到临时目录
    """
    try:
        result = processor.download_file_from_url(url, local_path)
        if "error" in result:
            return result["error"]
        return f"下载成功！文件保存到: {result.get('local_path', '')}"
    except Exception as e:
        error_msg = f"从URL下载文件失败: {str(e)}"
        logger.error(error_msg)
        return error_msg

@mcp.tool()
def open_document_from_url(url: str) -> str:
    """
    从网络URL下载并打开文档
    
    Parameters:
    - url: 文档的网络URL
    """
    try:
        return processor.open_document_from_url(url)
    except Exception as e:
        error_msg = f"从URL打开文档失败: {str(e)}"
        logger.error(error_msg)
        return error_msg

@mcp.tool()
def list_oss_files(prefix: str = "", max_keys: int = 100) -> str:
    """
    列出OSS中的文件
    
    Parameters:
    - prefix: 文件名前缀过滤
    - max_keys: 最大返回数量
    """
    try:
        result = processor.list_oss_files(prefix, max_keys)
        if "error" in result:
            return result["error"]
        
        files_info = []
        for file_info in result.get("files", []):
            files_info.append(f"文件: {file_info['filename']}, 大小: {file_info['size']} bytes, 修改时间: {file_info['last_modified']}")
        
        return f"找到 {result.get('count', 0)} 个文件:\n" + "\n".join(files_info)
    except Exception as e:
        error_msg = f"列出OSS文件失败: {str(e)}"
        logger.error(error_msg)
        return error_msg

@mcp.tool()
def delete_oss_file(filename: str) -> str:
    """
    删除OSS中的文件
    
    Parameters:
    - filename: 要删除的文件名
    """
    try:
        result = processor.delete_oss_file(filename)
        if "error" in result:
            return result["error"]
        return result.get("message", "删除成功")
    except Exception as e:
        error_msg = f"删除OSS文件失败: {str(e)}"
        logger.error(error_msg)
        return error_msg

# ==================== 高级功能工具 ====================

@mcp.tool()
def create_document_copy(suffix: str = "-副本") -> str:
    """
    创建当前文档的副本
    
    Parameters:
    - suffix: 文件名后缀，默认为"-副本"
    """
    try:
        if not processor.state_manager.has_current_document():
            return "没有打开的文档"
        
        current_path = processor.state_manager.get_current_file_path()
        if not current_path:
            return "当前文档未保存，无法创建副本"
        
        # 解析文件路径
        file_dir = os.path.dirname(current_path)
        file_name = os.path.basename(current_path)
        file_name_without_ext, file_ext = os.path.splitext(file_name)
        
        # 创建新文件名
        new_file_name = f"{file_name_without_ext}{suffix}{file_ext}"
        new_file_path = os.path.join(file_dir, new_file_name)
        
        # 保存为新文件
        document = processor.state_manager.get_current_document()
        document.save(new_file_path)
        
        return f"文档副本创建成功: {new_file_path}"
    except Exception as e:
        error_msg = f"创建文档副本失败: {str(e)}"
        logger.error(error_msg)
        return error_msg

@mcp.tool()
def batch_format_paragraphs(
    start_index: int,
    end_index: int,
    font_name: Optional[str] = None,
    font_size: Optional[int] = None,
    bold: Optional[bool] = None,
    italic: Optional[bool] = None,
    color: Optional[str] = None,
    alignment: Optional[str] = None
) -> str:
    """
    批量格式化段落范围
    
    Parameters:
    - start_index: 起始段落索引
    - end_index: 结束段落索引
    - font_name: 字体名称
    - font_size: 字体大小
    - bold: 是否加粗
    - italic: 是否斜体
    - color: 字体颜色
    - alignment: 对齐方式
    """
    try:
        document = processor.state_manager.get_current_document()
        if not document:
            return "没有打开的文档"
        
        if start_index < 0 or end_index >= len(document.paragraphs) or start_index > end_index:
            return f"段落索引范围无效: {start_index}-{end_index}"
        
        success_count = 0
        for i in range(start_index, end_index + 1):
            try:
                processor.set_paragraph_font(
                    i, font_name, font_size, bold, italic, None, color, alignment
                )
                success_count += 1
            except Exception as e:
                logger.warning(f"Format paragraph {i} failed: {e}")
        
        return f"批量格式化完成，成功处理 {success_count} 个段落"
    except Exception as e:
        error_msg = f"批量格式化失败: {str(e)}"
        logger.error(error_msg)
        return error_msg

if __name__ == "__main__":
    # 启动MCP服务器
    mcp.run()
