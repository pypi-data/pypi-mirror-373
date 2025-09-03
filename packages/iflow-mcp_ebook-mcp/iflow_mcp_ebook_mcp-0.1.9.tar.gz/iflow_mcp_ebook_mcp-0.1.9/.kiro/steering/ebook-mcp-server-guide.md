---
inclusion: always
---

# Ebook MCP Server Development Guide

## Architecture
FastMCP-based server for EPUB/PDF processing with tools for metadata extraction, content parsing, and format conversion.

**Core Structure:**
- `src/ebook_mcp/main.py` - MCP server entry point with FastMCP app
- `src/ebook_mcp/tools/` - MCP tool implementations (epub_helper.py, pdf_helper.py, logger_config.py)
- Use `uv` package manager exclusively

## Code Conventions

**Python Standards:**
- Python 3.10+ with full type annotations
- PEP 8 compliance, English-only documentation
- Specific exception handling: `FileNotFoundError` over generic `Exception`
- Always log debug info before processing: `logger.debug(f"Calling {tool_name}: {params}")`

**MCP Tool Pattern (MANDATORY):**
```python
@mcp.tool()
def tool_name(param: str) -> ReturnType:
    """Brief description.
    
    Args:
        param: Description with format examples
        
    Returns:
        ReturnType: Description
        
    Raises:
        FileNotFoundError: When file doesn't exist
        Exception: For parsing/processing errors
    """
    logger.debug(f"Calling tool_name: {param}")
    try:
        # Implementation
        return result
    except FileNotFoundError as e:
        raise FileNotFoundError(str(e))
    except Exception as e:
        raise Exception(str(e))
```

## Processing Rules

**EPUB Processing:**
- Use `ebooklib` library exclusively
- **CRITICAL:** 
- Use `get_epub_chapter_markdown` (fixes truncation issues)
- Convert all content to Markdown format
- Handle missing TOC gracefully with fallback methods

**PDF Processing:**
- Use `PyMuPDF` (fitz) library exclusively
- Support both page-based and chapter-based extraction
- When TOC missing, fallback to page-by-page extraction
- Provide both plain text and Markdown output formats

**Error Handling Pattern:**
- File operations: Raise `FileNotFoundError` for missing files
- Format/parsing errors: Use specific exceptions with descriptive messages
- Wrap optional imports in try-except blocks
- Always preserve original error context in exception messages

## Available Tools Reference

**EPUB:** `get_all_epub_files`, `get_epub_metadata`, `get_epub_toc`, `get_epub_chapter_markdown_fixed`
**PDF:** `get_all_pdf_files`, `get_pdf_metadata`, `get_pdf_toc`, `get_pdf_page_text`, `get_pdf_page_markdown`, `get_pdf_chapter_content`

## Development Commands
```bash
# Test suite
uv run pytest [specific_test_file]

# Development server
uv run mcp dev src/ebook_mcp/main.py

# Debug with MCP inspector
npx @modelcontextprotocol/inspector uv --directory . run src/ebook_mcp/main.py
```

**Logging:** Files in `logs/ebook-mcp_server_YYYYMMDD_HHMMSS.log`, DEBUG level, console + file output

