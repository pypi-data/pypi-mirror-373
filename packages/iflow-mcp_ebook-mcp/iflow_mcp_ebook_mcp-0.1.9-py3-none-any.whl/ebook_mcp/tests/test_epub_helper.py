import pytest
import os
import tempfile
from unittest.mock import Mock, patch, MagicMock

# Mock external dependencies
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

# Mock ebooklib
try:
    from ebooklib import epub
except ImportError:
    epub = Mock()

# Mock BeautifulSoup
try:
    from bs4 import BeautifulSoup
except ImportError:
    BeautifulSoup = Mock()

from ebook_mcp.tools.epub_helper import (
    get_all_epub_files,
    get_meta,
    get_toc,
    read_epub,
    flatten_toc,
    extract_chapter_html,
    extract_chapter_plain_text,

    convert_html_to_markdown,
    clean_html
)


class TestEpubHelper:
    """Test EPUB helper functions"""
    
    def test_get_all_epub_files_empty_directory(self):
        """Test get_all_epub_files with empty directory"""
        with tempfile.TemporaryDirectory() as temp_dir:
            result = get_all_epub_files(temp_dir)
            assert result == []
    
    def test_get_all_epub_files_with_epub_files(self):
        """Test get_all_epub_files with EPUB files present"""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create mock EPUB files
            epub_files = ["book1.epub", "book2.epub", "document.txt"]
            for file in epub_files:
                with open(os.path.join(temp_dir, file), 'w') as f:
                    f.write("mock content")
            
            result = get_all_epub_files(temp_dir)
            assert set(result) == {"book1.epub", "book2.epub"}
    
    @patch('ebook_mcp.tools.epub_helper.epub.read_epub')
    def test_get_toc_success(self, mock_read_epub):
        """Test get_toc successful case"""
        # Mock EPUB book with TOC
        mock_book = Mock()
        mock_chapter1 = Mock()
        mock_chapter1.title = "Chapter 1"
        mock_chapter1.href = "chapter1.xhtml"
        mock_chapter2 = Mock()
        mock_chapter2.title = "Chapter 2"
        mock_chapter2.href = "chapter2.xhtml"
        
        mock_book.toc = [mock_chapter1, mock_chapter2]
        mock_read_epub.return_value = mock_book
        
        with tempfile.NamedTemporaryFile(suffix='.epub', delete=False) as f:
            f.write(b"mock epub content")
            epub_path = f.name
        
        try:
            result = get_toc(epub_path)
            expected = [
                ("Chapter 1", "chapter1.xhtml"),
                ("Chapter 2", "chapter2.xhtml")
            ]
            assert result == expected
        finally:
            os.unlink(epub_path)
    
    @patch('ebook_mcp.tools.epub_helper.epub.read_epub')
    def test_get_toc_nested_structure(self, mock_read_epub):
        """Test get_toc with nested TOC structure"""
        # Mock EPUB book with nested TOC
        mock_book = Mock()
        mock_chapter1 = Mock()
        mock_chapter1.title = "Chapter 1"
        mock_chapter1.href = "chapter1.xhtml"
        mock_subchapter1 = Mock()
        mock_subchapter1.title = "Subchapter 1.1"
        mock_subchapter1.href = "subchapter1.1.xhtml"
        
        mock_book.toc = [(mock_chapter1, [mock_subchapter1])]
        mock_read_epub.return_value = mock_book
        
        with tempfile.NamedTemporaryFile(suffix='.epub', delete=False) as f:
            f.write(b"mock epub content")
            epub_path = f.name
        
        try:
            result = get_toc(epub_path)
            expected = [
                ("Chapter 1", "chapter1.xhtml"),
                ("Subchapter 1.1", "subchapter1.1.xhtml")
            ]
            assert result == expected
        finally:
            os.unlink(epub_path)
    
    def test_get_toc_file_not_found(self):
        """Test get_toc with non-existent file"""
        with pytest.raises(FileNotFoundError):
            get_toc("/path/to/nonexistent.epub")
    
    @patch('ebook_mcp.tools.epub_helper.epub.read_epub')
    def test_get_toc_parsing_error(self, mock_read_epub):
        """Test get_toc with parsing error"""
        mock_read_epub.side_effect = Exception("EPUB parsing error")
        
        with tempfile.NamedTemporaryFile(suffix='.epub', delete=False) as f:
            f.write(b"mock epub content")
            epub_path = f.name
        
        try:
            with pytest.raises(Exception):
                get_toc(epub_path)
        finally:
            os.unlink(epub_path)
    
    @patch('ebook_mcp.tools.epub_helper.epub.read_epub')
    def test_get_meta_success(self, mock_read_epub):
        """Test get_meta successful case"""
        # Mock EPUB book with metadata
        mock_book = Mock()
        
        # 设置 get_metadata 方法返回正确的格式
        def mock_get_metadata(namespace, field):
            metadata_map = {
                'title': [('Test Book', {})],
                'creator': [('Test Author', {})],
                'language': [('en', {})],
                'identifier': [('test-id', {})],
                'date': [('2023-01-01', {})],
                'publisher': [('Test Publisher', {})],
                'description': [('Test description', {})]
            }
            return metadata_map.get(field, [])
        
        mock_book.get_metadata = mock_get_metadata
        mock_read_epub.return_value = mock_book
        
        with tempfile.NamedTemporaryFile(suffix='.epub', delete=False) as f:
            f.write(b"mock epub content")
            epub_path = f.name
        
        try:
            result = get_meta(epub_path)
            expected = {
                'title': 'Test Book',
                'creator': ['Test Author'],
                'language': 'en',
                'identifier': 'test-id',
                'date': '2023-01-01',
                'publisher': 'Test Publisher',
                'description': 'Test description'
            }
            assert result == expected
        finally:
            os.unlink(epub_path)
    
    def test_get_meta_file_not_found(self):
        """Test get_meta with non-existent file"""
        with pytest.raises(FileNotFoundError):
            get_meta("/path/to/nonexistent.epub")
    
    @patch('ebook_mcp.tools.epub_helper.epub.read_epub')
    def test_get_meta_parsing_error(self, mock_read_epub):
        """Test get_meta with parsing error"""
        mock_read_epub.side_effect = Exception("EPUB parsing error")
        
        with tempfile.NamedTemporaryFile(suffix='.epub', delete=False) as f:
            f.write(b"mock epub content")
            epub_path = f.name
        
        try:
            with pytest.raises(Exception):
                get_meta(epub_path)
        finally:
            os.unlink(epub_path)
    
    @patch('ebook_mcp.tools.epub_helper.epub.read_epub')
    def test_read_epub_success(self, mock_read_epub):
        """Test read_epub successful case"""
        mock_book = Mock()
        mock_read_epub.return_value = mock_book
        
        with tempfile.NamedTemporaryFile(suffix='.epub', delete=False) as f:
            f.write(b"mock epub content")
            epub_path = f.name
        
        try:
            result = read_epub(epub_path)
            assert result == mock_book
            mock_read_epub.assert_called_once_with(epub_path)
        finally:
            os.unlink(epub_path)
    
    def test_flatten_toc_simple(self):
        """Test flatten_toc with simple TOC structure"""
        mock_chapter1 = Mock()
        mock_chapter1.title = "Chapter 1"
        mock_chapter1.href = "chapter1.xhtml"
        mock_chapter2 = Mock()
        mock_chapter2.title = "Chapter 2"
        mock_chapter2.href = "chapter2.xhtml"
        
        toc = [mock_chapter1, mock_chapter2]
        mock_book = Mock()
        mock_book.toc = toc
        result = flatten_toc(mock_book)
        
        expected = ["chapter1.xhtml", "chapter2.xhtml"]
        assert result == expected
    
    def test_flatten_toc_nested(self):
        """Test flatten_toc with nested TOC structure"""
        mock_chapter1 = Mock()
        mock_chapter1.title = "Chapter 1"
        mock_chapter1.href = "chapter1.xhtml"
        mock_subchapter1 = Mock()
        mock_subchapter1.title = "Subchapter 1.1"
        mock_subchapter1.href = "subchapter1.1.xhtml"
        
        toc = [(mock_chapter1, [mock_subchapter1])]
        mock_book = Mock()
        mock_book.toc = toc
        result = flatten_toc(mock_book)
        
        expected = ["chapter1.xhtml", "subchapter1.1.xhtml"]
        assert result == expected
    
    def test_clean_html(self):
        """Test clean_html function"""
        html_content = """
        <html>
            <head><title>Test</title></head>
            <body>
                <h1>Title</h1>
                <p>Content</p>
                <!-- Comment -->
                <script>alert('test');</script>
            </body>
        </html>
        """
        
        result = clean_html(html_content)
        
        # Should remove comments and scripts
        assert "<!-- Comment -->" not in result
        assert "<script>" not in result
        assert "alert('test');" not in result
        # Should keep content
        assert "<h1>Title</h1>" in result
        assert "<p>Content</p>" in result
    
    def test_convert_html_to_markdown(self):
        """Test convert_html_to_markdown function"""
        html_content = "<h1>Title</h1><p>This is <strong>bold</strong> text.</p>"
        
        result = convert_html_to_markdown(html_content)
        
        # Should convert HTML to markdown
        assert "# Title" in result
        assert "**bold**" in result
    
    @patch('ebook_mcp.tools.epub_helper.extract_chapter_html')
    def test_extract_chapter_plain_text(self, mock_extract_html):
        """Test extract_chapter_plain_text function"""
        mock_extract_html.return_value = "<h1>Title</h1><p>Content</p>"
        
        mock_book = Mock()
        result = extract_chapter_plain_text(mock_book, "chapter1")
        
        mock_extract_html.assert_called_once_with(mock_book, "chapter1")
        # Should return plain text (HTML tags removed)
        assert "<h1>" not in result
        assert "<p>" not in result
        assert "Title" in result
        assert "Content" in result
    
 