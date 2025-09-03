import pytest
import tempfile
import os
from unittest.mock import Mock, patch, MagicMock

# Add project root to path
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

# Skip tests if dependencies are not available
try:
    from ebooklib import epub
    from bs4 import BeautifulSoup
    import html2text
    DEPENDENCIES_AVAILABLE = True
except ImportError:
    DEPENDENCIES_AVAILABLE = False

if DEPENDENCIES_AVAILABLE:
    from ebook_mcp.tools.epub_helper import (
        extract_chapter_html,
        extract_chapter_markdown,
        clean_html,
        convert_html_to_markdown
    )


class TestExtractChapterHtml:
    """Test the improved version of extract_chapter_html function"""
    
    @pytest.mark.skipif(not DEPENDENCIES_AVAILABLE, reason="Dependencies not available")
    def test_simple_chapter_extraction(self):
        """Test simple chapter extraction without subchapters"""
        # Mock EPUB book
        mock_book = Mock()
        
        # Mock TOC structure
        mock_chapter1 = Mock()
        mock_chapter1.title = "Chapter 1"
        mock_chapter1.href = "chapter1.xhtml"
        
        mock_chapter2 = Mock()
        mock_chapter2.title = "Chapter 2"
        mock_chapter2.href = "chapter2.xhtml"
        
        mock_book.toc = [mock_chapter1, mock_chapter2]
        
        # Mock HTML content
        html_content = """
        <html>
            <body>
                <h1 id="chapter1">Chapter 1</h1>
                <p>Chapter 1 content</p>
                
                <h1 id="chapter2">Chapter 2</h1>
                <p>Chapter 2 content</p>
            </body>
        </html>
        """
        
        # Mock book.get_item_with_href
        mock_item = Mock()
        mock_item.get_content.return_value = html_content.encode('utf-8')
        mock_book.get_item_with_href.return_value = mock_item
        
        # Test extracting Chapter 1 - use the chapter ID that exists in TOC
        result = extract_chapter_markdown(mock_book, "chapter1.xhtml")
        
        # Should include Chapter 1 content but not Chapter 2
        assert "Chapter 1 content" in result
        assert "Chapter 2 content" not in result
    
    @pytest.mark.skipif(not DEPENDENCIES_AVAILABLE, reason="Dependencies not available")
    def test_chapter_with_subchapters_bug_case(self):
        """Test the specific bug case: chapter with subchapters causing premature truncation"""
        # Mock EPUB book
        mock_book = Mock()
        
        # Mock TOC structure with subchapters (the problematic case)
        mock_chapter1 = Mock()
        mock_chapter1.title = "Chapter 1"
        mock_chapter1.href = "chapter1.xhtml"
        
        mock_subchapter1_3 = Mock()
        mock_subchapter1_3.title = "1.3 Append-only"
        mock_subchapter1_3.href = "chapter1.xhtml#section1_3"
        
        mock_subchapter1_4 = Mock()
        mock_subchapter1_4.title = "1.4 Another Section"
        mock_subchapter1_4.href = "chapter1.xhtml#section1_4"
        
        mock_chapter2 = Mock()
        mock_chapter2.title = "Chapter 2"
        mock_chapter2.href = "chapter2.xhtml"
        
        # Set up nested TOC
        mock_book.toc = [
            (mock_chapter1, [mock_subchapter1_3, mock_subchapter1_4]),
            mock_chapter2
        ]
        
        # Mock HTML content that matches the bug report
        html_content = """
        <html>
            <body>
                <h1 id="chapter1">Chapter 1</h1>
                <p>Chapter 1 introduction</p>
                
                <h2 id="section1_3">1.3 Append-only</h2>
                <h3 id="subsection">Safe incremental updates with logs</h3>
                <p>One way to do incremental updates is to just append the updates to a file. 
                This is called a "log" because it's append-only. It's safer than in-place updates 
                because no data is overwritten; you can always recover the old data after a crash.</p>
                
                <h2 id="section1_4">1.4 Another Section</h2>
                <p>Another section content</p>
                
                <h1 id="chapter2">Chapter 2</h1>
                <p>Chapter 2 content</p>
            </body>
        </html>
        """
        
        # Mock book.get_item_with_href
        mock_item = Mock()
        mock_item.get_content.return_value = html_content.encode('utf-8')
        mock_book.get_item_with_href.return_value = mock_item
        
        # Test extracting section1_3 (the problematic case)
        result = extract_chapter_html(mock_book, "chapter1.xhtml#section1_3")
        
        # Should include the full section content
        assert "1.3 Append-only" in result
        assert "Safe incremental updates with logs" in result
        assert "One way to do incremental updates" in result
        assert "This is called a \"log\" because it's append-only" in result
        
        # Should NOT include content from other sections
        assert "1.4 Another Section" not in result
        assert "Another section content" not in result
        assert "Chapter 2 content" not in result
    
    @pytest.mark.skipif(not DEPENDENCIES_AVAILABLE, reason="Dependencies not available")
    def test_comparison_with_original_function(self):
        """Compare the improved function with the original function"""
        # Mock EPUB book
        mock_book = Mock()
        
        # Mock TOC structure
        mock_chapter1 = Mock()
        mock_chapter1.title = "Chapter 1"
        mock_chapter1.href = "chapter1.xhtml"
        
        mock_subchapter1_3 = Mock()
        mock_subchapter1_3.title = "1.3 Append-only"
        mock_subchapter1_3.href = "chapter1.xhtml#section1_3"
        
        mock_subchapter1_4 = Mock()
        mock_subchapter1_4.title = "1.4 Another Section"
        mock_subchapter1_4.href = "chapter1.xhtml#section1_4"
        
        mock_book.toc = [
            (mock_chapter1, [mock_subchapter1_3, mock_subchapter1_4])
        ]
        
        # Mock HTML content
        html_content = """
        <html>
            <body>
                <h2 id="section1_3">1.3 Append-only</h2>
                <p>Section 1.3 content</p>
                
                <h2 id="section1_4">1.4 Another Section</h2>
                <p>Section 1.4 content</p>
            </body>
        </html>
        """
        
        # Mock book.get_item_with_href
        mock_item = Mock()
        mock_item.get_content.return_value = html_content.encode('utf-8')
        mock_book.get_item_with_href.return_value = mock_item
        
        # Test with improved function (should work - return full content)
        improved_result = extract_chapter_html(mock_book, "chapter1.xhtml#section1_3")
        
        # The improved function should return the full content
        assert "Section 1.3 content" in improved_result
        assert "Section 1.4 content" not in improved_result
    
    @pytest.mark.skipif(not DEPENDENCIES_AVAILABLE, reason="Dependencies not available")
    def test_markdown_conversion(self):
        """Test the fixed markdown conversion function"""
        # Mock EPUB book
        mock_book = Mock()
        
        # Mock TOC structure
        mock_chapter1 = Mock()
        mock_chapter1.title = "Chapter 1"
        mock_chapter1.href = "chapter1.xhtml"
        
        mock_subchapter1_3 = Mock()
        mock_subchapter1_3.title = "1.3 Append-only"
        mock_subchapter1_3.href = "chapter1.xhtml#section1_3"
        
        mock_book.toc = [
            (mock_chapter1, [mock_subchapter1_3])
        ]
        
        # Mock HTML content
        html_content = """
        <html>
            <body>
                <h2 id="section1_3">1.3 Append-only</h2>
                <p>This is <strong>bold</strong> content.</p>
            </body>
        </html>
        """
        
        # Mock book.get_item_with_href
        mock_item = Mock()
        mock_item.get_content.return_value = html_content.encode('utf-8')
        mock_book.get_item_with_href.return_value = mock_item
        
        # Test markdown conversion
        result = extract_chapter_markdown(mock_book, "chapter1.xhtml#section1_3")
        
        # Should convert to markdown format
        assert "1.3 Append-only" in result
        assert "bold" in result
    
    @pytest.mark.skipif(not DEPENDENCIES_AVAILABLE, reason="Dependencies not available")
    def test_edge_cases(self):
        """Test edge cases and error conditions"""
        # Mock EPUB book
        mock_book = Mock()
        mock_book.toc = []
        
        # Test with non-existent chapter
        from ebook_mcp.tools.epub_helper import EpubProcessingError
        with pytest.raises(EpubProcessingError, match="not found in TOC"):
            extract_chapter_html(mock_book, "nonexistent.xhtml")
        
        # Test with non-existent anchor
        mock_chapter1 = Mock()
        mock_chapter1.title = "Chapter 1"
        mock_chapter1.href = "chapter1.xhtml"
        mock_book.toc = [mock_chapter1]
        
        mock_item = Mock()
        mock_item.get_content.return_value = "<html><body><h1>Test</h1></body></html>".encode('utf-8')
        mock_book.get_item_with_href.return_value = mock_item
        
        with pytest.raises(EpubProcessingError, match="not found in"):
            extract_chapter_html(mock_book, "chapter1.xhtml#nonexistent")
    
    @pytest.mark.skipif(not DEPENDENCIES_AVAILABLE, reason="Dependencies not available")
    def test_last_chapter_extraction(self):
        """Test extracting the last chapter (no next chapter)"""
        # Mock EPUB book
        mock_book = Mock()
        
        # Mock TOC structure
        mock_chapter1 = Mock()
        mock_chapter1.title = "Chapter 1"
        mock_chapter1.href = "chapter1.xhtml"
        
        mock_chapter2 = Mock()
        mock_chapter2.title = "Chapter 2"
        mock_chapter2.href = "chapter2.xhtml"
        
        mock_book.toc = [mock_chapter1, mock_chapter2]
        
        # Mock HTML content
        html_content = """
        <html>
            <body>
                <h1 id="chapter2">Chapter 2</h1>
                <p>Chapter 2 content</p>
                <p>More content</p>
            </body>
        </html>
        """
        
        # Mock book.get_item_with_href
        mock_item = Mock()
        mock_item.get_content.return_value = html_content.encode('utf-8')
        mock_book.get_item_with_href.return_value = mock_item
        
        # Test extracting the last chapter
        result = extract_chapter_html(mock_book, "chapter2.xhtml")
        
        # Should include all content (no next chapter to truncate at)
        assert "Chapter 2 content" in result
        assert "More content" in result
    
    @pytest.mark.skipif(not DEPENDENCIES_AVAILABLE, reason="Dependencies not available")
    def test_complex_nested_toc(self):
        """Test with complex nested TOC structure"""
        # Mock EPUB book
        mock_book = Mock()
        
        # Mock complex TOC structure
        mock_chapter1 = Mock()
        mock_chapter1.title = "Chapter 1"
        mock_chapter1.href = "chapter1.xhtml"
        
        mock_subchapter1_1 = Mock()
        mock_subchapter1_1.title = "1.1 Introduction"
        mock_subchapter1_1.href = "chapter1.xhtml#intro"
        
        mock_subchapter1_2 = Mock()
        mock_subchapter1_2.title = "1.2 Background"
        mock_subchapter1_2.href = "chapter1.xhtml#background"
        
        mock_subchapter1_3 = Mock()
        mock_subchapter1_3.title = "1.3 Append-only"
        mock_subchapter1_3.href = "chapter1.xhtml#section1_3"
        
        mock_chapter2 = Mock()
        mock_chapter2.title = "Chapter 2"
        mock_chapter2.href = "chapter2.xhtml"
        
        # Set up nested TOC
        mock_book.toc = [
            (mock_chapter1, [mock_subchapter1_1, mock_subchapter1_2, mock_subchapter1_3]),
            mock_chapter2
        ]
        
        # Mock HTML content
        html_content = """
        <html>
            <body>
                <h1 id="chapter1">Chapter 1</h1>
                
                <h2 id="intro">1.1 Introduction</h2>
                <p>Introduction content</p>
                
                <h2 id="background">1.2 Background</h2>
                <p>Background content</p>
                
                <h2 id="section1_3">1.3 Append-only</h2>
                <p>Section 1.3 content</p>
                <p>More content in section 1.3</p>
                
                <h1 id="chapter2">Chapter 2</h1>
                <p>Chapter 2 content</p>
            </body>
        </html>
        """
        
        # Mock book.get_item_with_href
        mock_item = Mock()
        mock_item.get_content.return_value = html_content.encode('utf-8')
        mock_book.get_item_with_href.return_value = mock_item
        
        # Test extracting section1_3
        result = extract_chapter_html(mock_book, "chapter1.xhtml#section1_3")
        
        # Should include section 1.3 content
        assert "1.3 Append-only" in result
        assert "Section 1.3 content" in result
        assert "More content in section 1.3" in result
        
        # Should NOT include content from other sections
        assert "1.1 Introduction" not in result
        assert "Introduction content" not in result
        assert "1.2 Background" not in result
        assert "Background content" not in result
        assert "Chapter 2 content" not in result 