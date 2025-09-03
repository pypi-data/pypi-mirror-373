# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.1.7] - 2025-08-06

### 🔧 Refactored
- **Modernized Dependency Management**: Removed `requirements.txt`, fully using `pyproject.toml` for dependency management
  - Deleted `requirements.txt` file
  - Updated installation instructions in all README files
  - Unified use of modern Python package management standards
  - Simplified installation process: `uv pip install -e .` or `pip install -e .`

- **PDF Processing Optimization**: Removed `PyPDF2` dependency, fully using `PyMuPDF`
  - Removed `PyPDF2` imports and `get_meta_pypdf2` function from `pdf_helper.py`
  - Updated `pyproject.toml`, removed `PyPDF2` dependency
  - Deleted `test_pdf_metadata_comparison.py` test file
  - Updated related tests, removed `PyPDF2` related tests

  - Enhanced PDF metadata extraction functionality, providing richer metadata information

### 🌍 Added
- **Internationalization Support**: Added multilingual README documentation
  - Added German README (`README-DE.md`)
  - Added French README (`README-FR.md`)
  - Added Japanese README (`README-JP.md`)
  - Added Korean README (`README-KR.md`)
  - Added Kiro translation tool configuration (`.kiro/hooks/readme-translation-hook.kiro.hook`)

### 🔧 Technical Improvements
- **Dependency Management**: Compliant with modern Python project standards (PEP 518/621)
- **PDF Processing**: Improved performance and stability, reduced dependency conflicts
- **Test Coverage**: All tests passing (76 passed, 5 skipped)
- **Code Quality**: Simplified code structure, improved maintainability

### 📝 Documentation
- Updated installation instructions in all README files
- Added multilingual support documentation
- Updated MCP client example documentation
- Improved project documentation accessibility

### 🗑️ Removed
- `requirements.txt` file
- `PyPDF2` dependency and related code
- `test_pdf_metadata_comparison.py` test file
- Outdated installation instruction references

### 🔄 Backward Compatibility
- ✅ Maintained API compatibility, no need to modify existing code
- ✅ All MCP tools working normally
- ✅ Functional integrity guaranteed

### 📦 Installation Instructions
```bash
# Development environment
git clone <repository-url>
cd ebook-mcp
uv pip install -e .
# or
pip install -e .

# Run tests
./run_tests.sh
# or
pytest src/ebook_mcp/tests/
```

### 🎯 Impact Assessment
- **Positive Impact**:
  - Simplified dependency management
  - Improved PDF processing performance
  - Enhanced internationalization support
  - Reduced maintenance complexity
  - Compliant with modern Python project standards

- **Potential Impact**:
  - Users need to update installation methods
  - Removed specific PyPDF2 features (replaced by PyMuPDF)

### 🔄 Migration Guide
For existing users:
1. Delete `requirements.txt` file (if exists)
2. Reinstall using `uv pip install -e .`
3. Update CI/CD configuration (if using requirements.txt)

---

## [0.1.4] - 2025-08-05

### 🔧 Fixed
- Fixed subchapter truncation issue in EPUB chapter extraction
- Added `get_epub_chapter_markdown_fixed` tool
- Improved chapter boundary detection logic
- Updated related tests and documentation

### 📝 Documentation
- Added `HOW-TO-TEST.md` testing documentation
- Updated test runner scripts
- Improved error handling and logging

## [0.1.3] - 2025-08-04

### 🌟 Added
- Added comprehensive unit test suite
- Created test configuration files and runner scripts
- Added test documentation and examples

### 🔧 Improved
- Improved error handling mechanisms
- Optimized code structure and readability
- Enhanced test coverage

## [0.1.2] - 2025-08-03

### 🌟 Added
- Added PDF chapter content extraction functionality
- Support for extracting content by chapter title
- Added Markdown format output support

### 🔧 Improved
- Optimized PDF metadata extraction
- Improved error handling
- Updated API documentation

## [0.0.1] - 2025-08-02

### 🔧 Fixed
- Fixed compatibility issues in PDF processing
- Improved EPUB metadata extraction
- Optimized file path handling

### 📝 Documentation
- Updated installation instructions
- Added usage examples
- Improved API documentation

## [1.0.0] - 2025-08-01

### 🌟 Initial Release
- EPUB and PDF format support
- Basic file processing APIs
- MCP client examples - Claude, DeepSeek, OpenAI
- Support for running server from PyPI
- Basic metadata extraction functionality
- Table of contents extraction support
- Chapter content extraction functionality

---

## Version Notes

### Semantic Versioning
- **Major version**: Incompatible API changes
- **Minor version**: Backward-compatible functionality additions
- **Patch version**: Backward-compatible bug fixes

### Change Types
- **Added**: New features
- **Changed**: Changes to existing functionality
- **Deprecated**: Features that will be removed soon
- **Removed**: Removed features
- **Fixed**: Bug fixes
- **Security**: Security improvements 