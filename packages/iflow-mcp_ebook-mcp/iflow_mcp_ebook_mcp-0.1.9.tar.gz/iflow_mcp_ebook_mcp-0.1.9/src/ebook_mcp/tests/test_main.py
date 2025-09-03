import pytest
import os
import tempfile
from unittest.mock import Mock, patch, MagicMock
from typing import List, Dict, Union, Tuple

# Mock external dependencies before importing main
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

# Mock mcp.server.fastmcp
try:
    import mcp.server.fastmcp
except ImportError:
    sys.modules['mcp.server.fastmcp'] = Mock()
    sys.modules['mcp'] = Mock()
    sys.modules['mcp.server'] = Mock()

# Import the functions to test
from ebook_mcp.main import (
    get_all_epub_files,
    get_epub_metadata,
    get_epub_toc,
    get_all_pdf_files,
    get_pdf_metadata,
    get_pdf_toc,
    get_pdf_page_text,
    get_pdf_page_markdown,
    get_pdf_chapter_content
)


class TestEpubFunctions:
    """Test EPUB related functions"""
    
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
    
    @patch('ebook_mcp.main.epub_helper.get_meta')
    def test_get_epub_metadata_success(self, mock_get_meta):
        """Test get_epub_metadata successful case"""
        mock_metadata = {
            'title': 'Test Book',
            'author': 'Test Author',
            'language': 'en'
        }
        mock_get_meta.return_value = mock_metadata
        
        result = get_epub_metadata("/path/to/test.epub")
        assert result == mock_metadata
        mock_get_meta.assert_called_once_with("/path/to/test.epub")
    
    @patch('ebook_mcp.main.epub_helper.get_meta')
    def test_get_epub_metadata_file_not_found(self, mock_get_meta):
        """Test get_epub_metadata with file not found"""
        mock_get_meta.side_effect = FileNotFoundError("File not found")
        
        with pytest.raises(FileNotFoundError):
            get_epub_metadata("/path/to/nonexistent.epub")
    
    @patch('ebook_mcp.main.epub_helper.get_meta')
    def test_get_epub_metadata_parsing_error(self, mock_get_meta):
        """Test get_epub_metadata with parsing error"""
        mock_get_meta.side_effect = Exception("Parsing error")
        
        with pytest.raises(Exception):
            get_epub_metadata("/path/to/corrupted.epub")
    
    @patch('ebook_mcp.main.epub_helper.get_toc')
    def test_get_epub_toc_success(self, mock_get_toc):
        """Test get_epub_toc successful case"""
        mock_toc = [
            ("Chapter 1", "chapter1.xhtml"),
            ("Chapter 2", "chapter2.xhtml")
        ]
        mock_get_toc.return_value = mock_toc
        
        result = get_epub_toc("/path/to/test.epub")
        assert result == mock_toc
        mock_get_toc.assert_called_once_with("/path/to/test.epub")
    
    @patch('ebook_mcp.main.epub_helper.get_toc')
    def test_get_epub_toc_file_not_found(self, mock_get_toc):
        """Test get_epub_toc with file not found"""
        mock_get_toc.side_effect = FileNotFoundError("File not found")
        
        with pytest.raises(FileNotFoundError):
            get_epub_toc("/path/to/nonexistent.epub")


class TestPdfFunctions:
    """Test PDF related functions"""
    
    def test_get_all_pdf_files_empty_directory(self):
        """Test get_all_pdf_files with empty directory"""
        with tempfile.TemporaryDirectory() as temp_dir:
            result = get_all_pdf_files(temp_dir)
            assert result == []
    
    def test_get_all_pdf_files_with_pdf_files(self):
        """Test get_all_pdf_files with PDF files present"""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create mock PDF files
            pdf_files = ["document1.pdf", "document2.pdf", "text.txt"]
            for file in pdf_files:
                with open(os.path.join(temp_dir, file), 'w') as f:
                    f.write("mock content")
            
            result = get_all_pdf_files(temp_dir)
            assert set(result) == {"document1.pdf", "document2.pdf"}
    
    @patch('ebook_mcp.main.pdf_helper.get_meta')
    def test_get_pdf_metadata_success(self, mock_get_meta):
        """Test get_pdf_metadata successful case"""
        mock_metadata = {
            'title': 'Test PDF',
            'author': 'Test Author',
            'pages': 10
        }
        mock_get_meta.return_value = mock_metadata
        
        result = get_pdf_metadata("/path/to/test.pdf")
        assert result == mock_metadata
        mock_get_meta.assert_called_once_with("/path/to/test.pdf")
    
    @patch('ebook_mcp.main.pdf_helper.get_meta')
    def test_get_pdf_metadata_file_not_found(self, mock_get_meta):
        """Test get_pdf_metadata with file not found"""
        mock_get_meta.side_effect = FileNotFoundError("File not found")
        
        with pytest.raises(FileNotFoundError):
            get_pdf_metadata("/path/to/nonexistent.pdf")
    
    @patch('ebook_mcp.main.pdf_helper.get_meta')
    def test_get_pdf_metadata_parsing_error(self, mock_get_meta):
        """Test get_pdf_metadata with parsing error"""
        mock_get_meta.side_effect = Exception("Parsing error")
        
        with pytest.raises(Exception):
            get_pdf_metadata("/path/to/corrupted.pdf")
    
    @patch('ebook_mcp.main.pdf_helper.get_toc')
    def test_get_pdf_toc_success(self, mock_get_toc):
        """Test get_pdf_toc successful case"""
        mock_toc = [
            ("Chapter 1", 1),
            ("Chapter 2", 5)
        ]
        mock_get_toc.return_value = mock_toc
        
        result = get_pdf_toc("/path/to/test.pdf")
        assert result == mock_toc
        mock_get_toc.assert_called_once_with("/path/to/test.pdf")
    
    @patch('ebook_mcp.main.pdf_helper.get_toc')
    def test_get_pdf_toc_file_not_found(self, mock_get_toc):
        """Test get_pdf_toc with file not found"""
        mock_get_toc.side_effect = FileNotFoundError("File not found")
        
        with pytest.raises(FileNotFoundError):
            get_pdf_toc("/path/to/nonexistent.pdf")
    
    @patch('ebook_mcp.main.pdf_helper.extract_page_text')
    def test_get_pdf_page_text_success(self, mock_extract):
        """Test get_pdf_page_text successful case"""
        mock_extract.return_value = "This is page 1 content."
        
        result = get_pdf_page_text("/path/to/test.pdf", 1)
        assert result == "This is page 1 content."
        mock_extract.assert_called_once_with("/path/to/test.pdf", 1)
    
    @patch('ebook_mcp.main.pdf_helper.extract_page_text')
    def test_get_pdf_page_text_error(self, mock_extract):
        """Test get_pdf_page_text with error"""
        mock_extract.side_effect = Exception("Extraction error")
        
        with pytest.raises(Exception):
            get_pdf_page_text("/path/to/test.pdf", 1)
    
    @patch('ebook_mcp.main.pdf_helper.extract_page_markdown')
    def test_get_pdf_page_markdown_success(self, mock_extract):
        """Test get_pdf_page_markdown successful case"""
        mock_extract.return_value = "# Page 1\n\nThis is page 1 content."
        
        result = get_pdf_page_markdown("/path/to/test.pdf", 1)
        assert result == "# Page 1\n\nThis is page 1 content."
        mock_extract.assert_called_once_with("/path/to/test.pdf", 1)
    
    @patch('ebook_mcp.main.pdf_helper.extract_page_markdown')
    def test_get_pdf_page_markdown_error(self, mock_extract):
        """Test get_pdf_page_markdown with error"""
        mock_extract.side_effect = Exception("Extraction error")
        
        with pytest.raises(Exception):
            get_pdf_page_markdown("/path/to/test.pdf", 1)
    
    @patch('ebook_mcp.main.pdf_helper.extract_chapter_by_title')
    def test_get_pdf_chapter_content_success(self, mock_get_chapter):
        """Test get_pdf_chapter_content successful case"""
        mock_content = ("This is chapter content.", [1, 2, 3])
        mock_get_chapter.return_value = mock_content
        
        result = get_pdf_chapter_content("/path/to/test.pdf", "Chapter 1")
        assert result == mock_content
        mock_get_chapter.assert_called_once_with("/path/to/test.pdf", "Chapter 1")
    
    @patch('ebook_mcp.main.pdf_helper.extract_chapter_by_title')
    def test_get_pdf_chapter_content_error(self, mock_get_chapter):
        """Test get_pdf_chapter_content with error"""
        mock_get_chapter.side_effect = Exception("Chapter extraction error")
        
        with pytest.raises(Exception):
            get_pdf_chapter_content("/path/to/test.pdf", "Chapter 1")


class TestMainModule:
    """Test main module functionality"""
    
    def test_main_module_imports(self):
        """Test that main module can be imported without errors"""
        import ebook_mcp.main
        assert hasattr(ebook_mcp.main, 'mcp')
        assert hasattr(ebook_mcp.main, 'get_all_epub_files')
        assert hasattr(ebook_mcp.main, 'get_all_pdf_files')
    
    @pytest.mark.skip(reason="Requires actual MCP server environment")
    def test_cli_entry_function(self):
        """Test cli_entry function"""
        from ebook_mcp.main import cli_entry
        
        # Mock the FastMCP instance
        mock_mcp_instance = Mock()
        mock_mcp.return_value = mock_mcp_instance
        
        cli_entry()
        
        mock_mcp_instance.run.assert_called_once_with(transport='stdio') 


class TestDecorators:
    """Test the error handling decorators"""
    
    def test_handle_mcp_errors_file_not_found(self):
        """Test handle_mcp_errors decorator with FileNotFoundError"""
        from ebook_mcp.main import handle_mcp_errors
        
        @handle_mcp_errors
        def test_function():
            raise FileNotFoundError("Test file not found")
        
        with pytest.raises(FileNotFoundError, match="Test file not found"):
            test_function()
    
    def test_handle_mcp_errors_general_exception(self):
        """Test handle_mcp_errors decorator with general exception"""
        from ebook_mcp.main import handle_mcp_errors
        
        @handle_mcp_errors
        def test_function():
            raise ValueError("Test value error")
        
        with pytest.raises(Exception, match="Test value error"):
            test_function()
    
    def test_handle_pdf_errors(self):
        """Test handle_pdf_errors decorator"""
        from ebook_mcp.main import handle_pdf_errors
        
        @handle_pdf_errors
        def test_function():
            raise ValueError("Test PDF error")
        
        with pytest.raises(Exception, match="Test PDF error"):
            test_function()
    
    def test_decorator_preserves_return_value(self):
        """Test that decorators preserve return values"""
        from ebook_mcp.main import handle_mcp_errors
        
        @handle_mcp_errors
        def test_function():
            return "test result"
        
        result = test_function()
        assert result == "test result"
    
    def test_handle_mcp_errors_with_custom_exceptions(self):
        """Test handle_mcp_errors decorator with custom exceptions"""
        from ebook_mcp.main import handle_mcp_errors
        from ebook_mcp.tools.epub_helper import EpubProcessingError
        from ebook_mcp.tools.pdf_helper import PdfProcessingError
        
        @handle_mcp_errors
        def test_epub_function():
            raise EpubProcessingError("Test EPUB error", "/test.epub", "test_operation")
        
        @handle_mcp_errors
        def test_pdf_function():
            raise PdfProcessingError("Test PDF error", "/test.pdf", "test_operation")
        
        # Custom exceptions should be re-raised as-is
        with pytest.raises(EpubProcessingError, match="Test EPUB error"):
            test_epub_function()
        
        with pytest.raises(PdfProcessingError, match="Test PDF error"):
            test_pdf_function() 