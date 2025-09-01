# 迁移指南

## 从1.x版本升级到2.0版本

### 🔄 自动迁移（推荐）

运行迁移脚本：
```bash
python merge_and_cleanup.py
```

### 🔧 手动迁移步骤

1. **备份现有项目**
   ```bash
   cp -r your_project your_project_backup
   ```

2. **更新依赖**
   ```bash
   pip install -r requirements.txt
   ```

3. **测试兼容性**
   ```bash
   # 测试原有功能
   python main.py
   
   # 测试增强功能
   python enhanced_main.py --interactive
   ```

4. **逐步迁移**
   - 原有MCP调用无需修改
   - 可选择性使用新功能
   - 参考增强版文档

### 📋 API兼容性

#### 完全兼容的功能
- 所有原有的MCP工具调用
- 文档结构提取
- 基础表格操作
- 文本搜索替换

#### 新增功能
- 图片处理：`add_image()`, `resize_image()`, `delete_image()`
- 字体管理：`set_paragraph_font()`, `set_text_range_font()`
- 状态管理：自动文档状态保存和恢复
- 交互模式：命令行交互界面

#### 增强功能
- 更好的错误处理和提示
- 详细的日志记录
- 批量操作支持
- 上下文管理

### 🐛 常见问题

#### Q: 原有代码是否需要修改？
A: 不需要。所有原有的MCP工具调用保持完全兼容。

#### Q: 如何使用新功能？
A: 参考 `README_Enhanced.md` 文档，或使用交互模式体验。

#### Q: 性能是否有影响？
A: 增强版采用了更优的架构，性能通常更好。

#### Q: 如何回退到旧版本？
A: 使用 `backup_old_files/` 目录中的备份文件即可回退。

### 📞 获取帮助

如果遇到问题：
1. 查看 `CHANGELOG.md` 了解详细更改
2. 运行 `python enhanced_main.py --help` 查看帮助
3. 使用交互模式测试功能
4. 提交Issue获取支持

---

**祝您升级顺利！** 🚀
