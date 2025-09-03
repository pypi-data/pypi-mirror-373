# Ebook-MCP 单元测试指南

本指南说明如何运行 ebook-mcp 项目的服务器部分单元测试。

## 测试文件结构

```
src/ebook_mcp/tests/
├── conftest.py              # pytest 配置和共享 fixtures
├── test_main.py             # main.py 的单元测试
├── test_epub_helper.py      # epub_helper.py 的单元测试
├── test_pdf_helper.py       # pdf_helper.py 的单元测试
├── test_azw.py              # 现有的 AZW 测试
└── run_tests.py             # 测试运行脚本
```

## 测试覆盖范围

### main.py 测试
- EPUB 相关工具函数测试
  - `get_all_epub_files`
  - `get_epub_metadata`
  - `get_epub_toc`
  - `get_epub_chapter_markdown`
- PDF 相关工具函数测试
  - `get_all_pdf_files`
  - `get_pdf_metadata`
  - `get_pdf_toc`
  - `get_pdf_page_text`
  - `get_pdf_page_markdown`
  - `get_pdf_chapter_content`
- 错误处理测试
  - 文件不存在
  - 解析错误
  - 异常处理

### epub_helper.py 测试
- 文件操作测试
- EPUB 解析测试
- 目录结构处理测试
- HTML 清理和转换测试
- 章节提取测试

### pdf_helper.py 测试
- PDF 文件操作测试
- 元数据提取测试
- 目录提取测试
- 页面文本提取测试
- 章节内容提取测试

## 运行测试

### 方法 1: 使用测试运行脚本

```bash
# 运行所有测试
python src/ebook_mcp/tests/run_tests.py

# 列出所有测试文件
python src/ebook_mcp/tests/run_tests.py list

# 运行特定测试文件
python src/ebook_mcp/tests/run_tests.py run test_main.py
```

### 方法 2: 使用 pytest 直接运行

```bash
# 运行所有测试
pytest src/ebook_mcp/tests/ -v

# 运行特定测试文件
pytest src/ebook_mcp/tests/test_main.py -v

# 运行特定测试类
pytest src/ebook_mcp/tests/test_main.py::TestEpubFunctions -v

# 运行特定测试方法
pytest src/ebook_mcp/tests/test_main.py::TestEpubFunctions::test_get_all_epub_files_empty_directory -v
```

### 方法 3: 从项目根目录运行

```bash
# 从项目根目录运行所有测试
python -m pytest src/ebook_mcp/tests/ -v

# 运行特定测试
python -m pytest src/ebook_mcp/tests/test_main.py -v
```

### 方法 4: 使用 uv 运行（如果使用 uv 管理依赖）

```bash
# 运行所有测试
uv run pytest src/ebook_mcp/tests/ -v

# 运行特定测试
uv run pytest src/ebook_mcp/tests/test_main.py -v
```

### 方法 5: 运行基本测试（不需要外部依赖）

```bash
# 运行基本测试（推荐用于快速验证）
pytest src/ebook_mcp/tests/test_basic.py -v

# 或者
python -m pytest src/ebook_mcp/tests/test_basic.py -v
```

## 测试环境要求

### 基本依赖
确保已安装以下依赖：

```bash
# 如果使用 pip
pip install pytest
pip install pytest-cov  # 可选：用于代码覆盖率

# 如果使用 uv
uv add --dev pytest
uv add --dev pytest-cov  # 可选：用于代码覆盖率
```

### 完整依赖（用于完整测试）
如果要运行所有测试（包括需要外部库的测试），需要安装项目依赖：

```bash
# 安装项目依赖
pip install -e .

# 或者使用 uv
uv sync --dev
```

### 依赖说明
- **基本测试** (`test_basic.py`): 不需要外部依赖，可以立即运行 ✅
- **主要功能测试** (`test_main.py`, `test_epub_helper.py`, `test_pdf_helper.py`): 需要项目依赖 ⚠️
- **AZW 测试** (`test_azw.py`): 需要 AZW 模块（如果可用）⏭️

### 测试状态
- ✅ **基本测试**: 10个测试全部通过
- ⏭️ **AZW 测试**: 4个测试跳过（模块不可用）
- ⚠️ **主要功能测试**: 需要安装项目依赖后运行

## 测试输出示例

### 成功运行示例
```
Running ebook-mcp unit tests...
==================================================
test_main.py::TestEpubFunctions::test_get_all_epub_files_empty_directory PASSED
test_main.py::TestEpubFunctions::test_get_all_epub_files_with_epub_files PASSED
test_main.py::TestEpubFunctions::test_get_epub_metadata_success PASSED
...
test_pdf_helper.py::TestPdfHelper::test_get_all_pdf_files_empty_directory PASSED
test_pdf_helper.py::TestPdfHelper::test_get_all_pdf_files_with_pdf_files PASSED
...

==================================================
✅ All tests passed!
```

### 失败运行示例
```
test_main.py::TestEpubFunctions::test_get_epub_metadata_file_not_found FAILED
...
AssertionError: Expected FileNotFoundError to be raised, but no exception was raised.
```

## 测试策略

### 单元测试原则
1. **隔离性**: 每个测试都是独立的，不依赖其他测试
2. **可重复性**: 测试可以在任何环境下重复运行
3. **快速性**: 测试运行速度快
4. **完整性**: 覆盖正常情况和异常情况

### Mock 使用
- 使用 `unittest.mock` 来模拟外部依赖
- 模拟文件系统操作
- 模拟 EPUB 和 PDF 解析库

### 测试数据
- 使用临时文件和目录
- 使用模拟数据而不是真实文件
- 测试完成后自动清理

## 调试测试

### 查看详细输出
```bash
# 运行测试并显示详细输出
pytest src/ebook_mcp/tests/ -v -s

# 在失败时停止
pytest src/ebook_mcp/tests/ -x

# 显示本地变量
pytest src/ebook_mcp/tests/ --tb=long
```

### 运行特定测试
```bash
# 运行包含特定关键词的测试
pytest src/ebook_mcp/tests/ -k "epub" -v

# 运行特定类的测试
pytest src/ebook_mcp/tests/ -k "TestEpubFunctions" -v

# 运行特定方法的测试
pytest src/ebook_mcp/tests/ -k "test_get_epub_metadata" -v
```

## 添加新测试

### 为新功能添加测试
1. 在相应的测试文件中添加测试类或方法
2. 使用描述性的测试方法名
3. 包含正常情况和异常情况的测试
4. 使用适当的 mock 来隔离依赖

### 测试方法命名规范
- 使用 `test_` 前缀
- 描述测试的功能和场景
- 例如: `test_get_epub_metadata_success`, `test_get_epub_metadata_file_not_found`

### 测试文档
- 每个测试方法都应该有文档字符串
- 说明测试的目的和预期结果
- 对于复杂的测试，说明测试步骤

## 持续集成

这些测试可以集成到 CI/CD 流程中：

```yaml
# 示例 GitHub Actions 配置
- name: Run tests
  run: |
    python -m pytest src/ebook_mcp/tests/ -v --cov=src/ebook_mcp
```

## 故障排除

### 常见问题

1. **导入错误**: 确保 Python 路径正确设置
   ```bash
   # 从项目根目录运行
   cd /path/to/ebook-mcp
   python -m pytest src/ebook_mcp/tests/ -v
   ```

2. **Mock 问题**: 检查 mock 路径是否正确
   ```python
   # 确保 mock 路径与实际的导入路径一致
   @patch('ebook_mcp.main.epub_helper.get_meta')
   ```

3. **文件权限**: 确保有创建临时文件的权限
   ```bash
   # 检查当前目录权限
   ls -la
   ```

4. **依赖问题**: 确保所有测试依赖已安装
   ```bash
   # 安装开发依赖
   pip install -e .[dev]
   # 或使用 uv
   uv sync --dev
   ```

### 获取帮助

如果遇到问题，可以：

1. 查看测试输出中的错误信息
2. 使用 `-v` 参数获取详细输出
3. 使用 `--tb=long` 查看完整的错误堆栈
4. 检查测试文件中的 mock 设置 