#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
增强版DOCX MCP服务主入口
提供两种运行模式：
1. MCP服务器模式（用于AI工具集成）
2. 独立服务模式（用于直接调用）
"""

import sys
import os
import argparse
import logging
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from core.enhanced_docx_processor import EnhancedDocxProcessor

def setup_logging(level=logging.INFO):
    """设置日志配置"""
    logging.basicConfig(
        level=level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )

def run_mcp_server():
    """运行MCP服务器"""
    try:
        from enhanced_server import mcp
        print("启动增强版DOCX MCP服务器...")
        print("服务器功能包括:")
        print("- 完整的文档生命周期管理")
        print("- 内容编辑和格式化")
        print("- 表格操作")
        print("- 图片处理")
        print("- 字体和样式管理")
        print("- 搜索和替换")
        print("- 状态持久化")
        print()
        mcp.run()
    except ImportError as e:
        print(f"MCP服务器启动失败，缺少依赖: {e}")
        print("请运行: pip install -r requirements_enhanced.txt")
        sys.exit(1)
    except Exception as e:
        print(f"MCP服务器启动失败: {e}")
        sys.exit(1)

def run_interactive_mode():
    """运行交互模式"""
    print("=== 增强版DOCX处理器 - 交互模式 ===")
    print("输入 'help' 查看可用命令，输入 'quit' 退出")
    print()
    
    processor = EnhancedDocxProcessor()
    
    while True:
        try:
            command = input("docx> ").strip()
            
            if not command:
                continue
                
            if command.lower() in ['quit', 'exit', 'q']:
                print("再见！")
                break
                
            if command.lower() in ['help', 'h']:
                show_help()
                continue
            
            # 解析命令
            parts = command.split()
            cmd = parts[0].lower()
            args = parts[1:] if len(parts) > 1 else []
            
            result = execute_command(processor, cmd, args)
            print(result)
            print()
            
        except KeyboardInterrupt:
            print("\n再见！")
            break
        except EOFError:
            print("\n输入结束，退出程序")
            break
        except Exception as e:
            print(f"错误: {e}")
            print()

def show_help():
    """显示帮助信息"""
    help_text = """
可用命令:

文档操作:
  create <path>           - 创建新文档
  open <path>             - 打开文档
  save                    - 保存文档
  saveas <path>           - 另存为
  close                   - 关闭文档
  info                    - 显示文档信息

内容编辑:
  addp <text>             - 添加段落
  addh <text> <level>     - 添加标题
  delp <index>            - 删除段落
  pagebreak               - 添加分页符

表格操作:
  addtable <rows> <cols>  - 添加表格
  addrow <table_index>    - 添加表格行
  delrow <table_index> <row_index> - 删除表格行
  editcell <table_index> <row> <col> <text> - 编辑单元格

图片操作:
  addimg <path>           - 添加图片
  listimg                 - 列出图片
  delimg <index>          - 删除图片

搜索替换:
  search <keyword>        - 搜索文本
  replace <find> <replace> - 替换文本

其他:
  help, h                 - 显示帮助
  quit, exit, q           - 退出程序
"""
    print(help_text)

def execute_command(processor, cmd, args):
    """执行命令"""
    try:
        if cmd == 'create':
            if not args:
                return "错误: 请指定文件路径"
            return processor.create_document(args[0])
            
        elif cmd == 'open':
            if not args:
                return "错误: 请指定文件路径"
            return processor.open_document(args[0])
            
        elif cmd == 'save':
            return processor.save_document()
            
        elif cmd == 'saveas':
            if not args:
                return "错误: 请指定新文件路径"
            return processor.save_as_document(args[0])
            
        elif cmd == 'close':
            return processor.close_document()
            
        elif cmd == 'info':
            return processor.get_document_info()
            
        elif cmd == 'addp':
            if not args:
                return "错误: 请指定段落文本"
            text = ' '.join(args)
            return processor.add_paragraph(text)
            
        elif cmd == 'addh':
            if len(args) < 2:
                return "错误: 请指定标题文本和级别"
            text = ' '.join(args[:-1])
            level = int(args[-1])
            return processor.add_heading(text, level)
            
        elif cmd == 'delp':
            if not args:
                return "错误: 请指定段落索引"
            index = int(args[0])
            return processor.delete_paragraph(index)
            
        elif cmd == 'pagebreak':
            return processor.add_page_break()
            
        elif cmd == 'addtable':
            if len(args) < 2:
                return "错误: 请指定行数和列数"
            rows, cols = int(args[0]), int(args[1])
            return processor.add_table(rows, cols)
            
        elif cmd == 'addrow':
            if not args:
                return "错误: 请指定表格索引"
            table_index = int(args[0])
            return processor.add_table_row(table_index)
            
        elif cmd == 'delrow':
            if len(args) < 2:
                return "错误: 请指定表格索引和行索引"
            table_index, row_index = int(args[0]), int(args[1])
            return processor.delete_table_row(table_index, row_index)
            
        elif cmd == 'editcell':
            if len(args) < 4:
                return "错误: 请指定表格索引、行索引、列索引和文本"
            table_index, row_index, col_index = int(args[0]), int(args[1]), int(args[2])
            text = ' '.join(args[3:])
            return processor.edit_table_cell(table_index, row_index, col_index, text)
            
        elif cmd == 'addimg':
            if not args:
                return "错误: 请指定图片路径"
            return processor.add_image(args[0])
            
        elif cmd == 'listimg':
            return processor.list_images()
            
        elif cmd == 'delimg':
            if not args:
                return "错误: 请指定图片索引"
            index = int(args[0])
            return processor.delete_image(index)
            
        elif cmd == 'search':
            if not args:
                return "错误: 请指定搜索关键词"
            keyword = ' '.join(args)
            return processor.search_text(keyword)
            
        elif cmd == 'replace':
            if len(args) < 2:
                return "错误: 请指定查找文本和替换文本"
            find_text = args[0]
            replace_text = ' '.join(args[1:])
            return processor.find_and_replace(find_text, replace_text)
            
        else:
            return f"未知命令: {cmd}，输入 'help' 查看可用命令"
            
    except ValueError as e:
        return f"参数错误: {e}"
    except Exception as e:
        return f"命令执行失败: {e}"

def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description="增强版DOCX MCP处理器",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
运行模式:
  默认: MCP服务器模式，用于AI工具集成
  --interactive: 交互式命令行模式
  --verbose: 启用详细日志输出
        """
    )
    
    parser.add_argument(
        "--interactive", "-i",
        action="store_true",
        help="运行交互式命令行模式"
    )
    
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="启用详细日志输出"
    )
    
    args = parser.parse_args()
    
    # 设置日志级别
    log_level = logging.DEBUG if args.verbose else logging.INFO
    setup_logging(log_level)
    
    if args.interactive:
        run_interactive_mode()
    else:
        run_mcp_server()

if __name__ == "__main__":
    main()
