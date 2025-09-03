import pytest
import os
import tempfile
from unittest.mock import Mock, patch, MagicMock

# Mock external dependencies
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

# Mock PyMuPDF
try:
    import fitz
except ImportError:
    fitz = Mock()

from ebook_mcp.tools.pdf_helper import (
    get_all_pdf_files,
    get_meta,
    get_toc,
    extract_page_text,
    extract_page_markdown,
    extract_chapter_by_title
)


class TestPdfHelper:
    """Test PDF helper functions"""
    
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
    
    @patch('ebook_mcp.tools.pdf_helper.fitz.open')
    def test_get_meta_success(self, mock_fitz_open):
        """Test get_meta successful case"""
        # Mock PyMuPDF document with metadata
        mock_doc = Mock()
        mock_doc.metadata = {
            'title': 'Test PDF',
            'author': 'Test Author',
            'subject': 'Test Subject',
            'creator': 'Test Creator',
            'producer': 'Test Producer',
            'creationDate': '2023-01-01',
            'modDate': '2023-01-02',
            'keywords': 'test, pdf',
            'format': 'PDF'
        }
        mock_doc.page_count = 3
        mock_doc.version_major = 1
        mock_doc.version_minor = 7
        mock_doc.is_encrypted = False
        
        # Mock first page for dimensions
        mock_page = Mock()
        mock_rect = Mock()
        mock_rect.width = 595.0
        mock_rect.height = 842.0
        mock_page.rect = mock_rect
        mock_doc.__getitem__ = Mock(return_value=mock_page)
        
        mock_fitz_open.return_value = mock_doc
        
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as f:
            f.write(b"mock pdf content")
            pdf_path = f.name
        
        try:
            with patch('os.path.getsize', return_value=1024):
                result = get_meta(pdf_path)
                expected_fields = {
                    'title', 'author', 'subject', 'creator', 'producer',
                    'creation_date', 'modification_date', 'keywords', 'format',
                    'pages', 'file_size', 'pdf_version', 'is_encrypted',
                    'page_width', 'page_height'
                }
                assert all(field in result for field in expected_fields)
                assert result['title'] == 'Test PDF'
                assert result['author'] == 'Test Author'
                assert result['pages'] == 3
        finally:
            os.unlink(pdf_path)
    
    @patch('ebook_mcp.tools.pdf_helper.fitz.open')
    def test_get_meta_no_metadata(self, mock_fitz_open):
        """Test get_meta with no metadata"""
        # Mock PyMuPDF document without metadata
        mock_doc = Mock()
        mock_doc.metadata = {}
        mock_doc.page_count = 2
        mock_doc.version_major = 1
        mock_doc.version_minor = 4
        mock_doc.is_encrypted = False
        
        # Mock first page for dimensions
        mock_page = Mock()
        mock_rect = Mock()
        mock_rect.width = 595.0
        mock_rect.height = 842.0
        mock_page.rect = mock_rect
        mock_doc.__getitem__ = Mock(return_value=mock_page)
        
        mock_fitz_open.return_value = mock_doc
        
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as f:
            f.write(b"mock pdf content")
            pdf_path = f.name
        
        try:
            with patch('os.path.getsize', return_value=512):
                result = get_meta(pdf_path)
                assert result['pages'] == 2
                assert result['file_size'] == 512
                assert result['is_encrypted'] == False
                assert 'title' not in result
                assert 'author' not in result
        finally:
            os.unlink(pdf_path)
    
    def test_get_meta_file_not_found(self):
        """Test get_meta with non-existent file"""
        with pytest.raises(FileNotFoundError):
            get_meta("/non/existent/file.pdf")
    
    @patch('ebook_mcp.tools.pdf_helper.fitz.open')
    def test_get_meta_parsing_error(self, mock_fitz_open):
        """Test get_meta with parsing error"""
        mock_fitz_open.side_effect = Exception("PDF parsing error")
        
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as f:
            f.write(b"mock pdf content")
            pdf_path = f.name
        
        try:
            with pytest.raises(Exception, match="Failed to parse PDF file"):
                get_meta(pdf_path)
        finally:
            os.unlink(pdf_path)
    
    @patch('ebook_mcp.tools.pdf_helper.fitz.open')
    def test_get_toc_success(self, mock_fitz_open):
        """Test get_toc successful case"""
        # Mock PyMuPDF document with TOC
        mock_doc = Mock()
        mock_doc.get_toc.return_value = [
            (1, "Chapter 1", 1),
            (2, "Section 1.1", 2),
            (1, "Chapter 2", 5)
        ]
        mock_fitz_open.return_value = mock_doc
        
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as f:
            f.write(b"mock pdf content")
            pdf_path = f.name
        
        try:
            result = get_toc(pdf_path)
            expected = [
                ("Chapter 1", 1),
                ("Section 1.1", 2),
                ("Chapter 2", 5)
            ]
            assert result == expected
        finally:
            os.unlink(pdf_path)
    
    @patch('ebook_mcp.tools.pdf_helper.fitz.open')
    def test_get_toc_empty(self, mock_fitz_open):
        """Test get_toc with empty TOC"""
        # Mock PyMuPDF document with empty TOC
        mock_doc = Mock()
        mock_doc.get_toc.return_value = []
        mock_fitz_open.return_value = mock_doc
        
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as f:
            f.write(b"mock pdf content")
            pdf_path = f.name
        
        try:
            result = get_toc(pdf_path)
            assert result == []
        finally:
            os.unlink(pdf_path)
    
    def test_get_toc_file_not_found(self):
        """Test get_toc with non-existent file"""
        with pytest.raises(FileNotFoundError):
            get_toc("/non/existent/file.pdf")
    
    @patch('ebook_mcp.tools.pdf_helper.fitz.open')
    def test_get_toc_parsing_error(self, mock_fitz_open):
        """Test get_toc with parsing error"""
        mock_fitz_open.side_effect = Exception("PDF parsing error")
        
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as f:
            f.write(b"mock pdf content")
            pdf_path = f.name
        
        try:
            with pytest.raises(Exception, match="Failed to parse PDF file"):
                get_toc(pdf_path)
        finally:
            os.unlink(pdf_path)
    
    @patch('ebook_mcp.tools.pdf_helper.fitz.open')
    def test_extract_page_text_success(self, mock_fitz_open):
        """Test extract_page_text successful case"""
        # Mock PyMuPDF document and page
        mock_doc = Mock()
        mock_page = Mock()
        mock_page.get_text.return_value = "This is page content"
        mock_doc.__getitem__ = Mock(return_value=mock_page)
        mock_fitz_open.return_value = mock_doc
        
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as f:
            f.write(b"mock pdf content")
            pdf_path = f.name
        
        try:
            result = extract_page_text(pdf_path, 1)
            assert result == "This is page content"
        finally:
            os.unlink(pdf_path)
    
    @patch('ebook_mcp.tools.pdf_helper.fitz.open')
    def test_extract_page_text_page_not_found(self, mock_fitz_open):
        """Test extract_page_text with page not found"""
        # Mock PyMuPDF document with IndexError
        mock_doc = Mock()
        mock_doc.__getitem__ = Mock(side_effect=IndexError("Page not found"))
        mock_fitz_open.return_value = mock_doc
        
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as f:
            f.write(b"mock pdf content")
            pdf_path = f.name
        
        try:
            with pytest.raises(Exception, match="Failed to extract page text"):
                extract_page_text(pdf_path, 999)
        finally:
            os.unlink(pdf_path)
    
    @patch('ebook_mcp.tools.pdf_helper.fitz.open')
    def test_extract_page_markdown_success(self, mock_fitz_open):
        """Test extract_page_markdown successful case"""
        # Mock PyMuPDF document and page
        mock_doc = Mock()
        mock_page = Mock()
        mock_page.get_text.return_value = {
            "blocks": [
                {
                    "lines": [
                        {
                            "spans": [
                                {"text": "Header", "size": 16, "flags": 0},
                                {"text": "Bold text", "size": 12, "flags": 8},
                                {"text": "Italic text", "size": 12, "flags": 2}
                            ]
                        }
                    ]
                }
            ]
        }
        mock_doc.__getitem__ = Mock(return_value=mock_page)
        mock_fitz_open.return_value = mock_doc
        
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as f:
            f.write(b"mock pdf content")
            pdf_path = f.name
        
        try:
            result = extract_page_markdown(pdf_path, 1)
            assert "## Header" in result
            assert "**Bold text**" in result
            assert "*Italic text*" in result
        finally:
            os.unlink(pdf_path)
    
    @patch('ebook_mcp.tools.pdf_helper.fitz.open')
    def test_extract_page_markdown_with_formatting(self, mock_fitz_open):
        """Test extract_page_markdown with formatting"""
        # Mock PyMuPDF document and page with formatted text
        mock_doc = Mock()
        mock_page = Mock()
        mock_page.get_text.return_value = {
            "blocks": [
                {
                    "lines": [
                        {
                            "spans": [
                                {"text": "Large Title", "size": 18, "flags": 0},
                                {"text": "Normal text", "size": 12, "flags": 0}
                            ]
                        }
                    ]
                }
            ]
        }
        mock_doc.__getitem__ = Mock(return_value=mock_page)
        mock_fitz_open.return_value = mock_doc
        
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as f:
            f.write(b"mock pdf content")
            pdf_path = f.name
        
        try:
            result = extract_page_markdown(pdf_path, 1)
            assert "## Large Title" in result
            assert "Normal text" in result
        finally:
            os.unlink(pdf_path)
    
    @patch('ebook_mcp.tools.pdf_helper.fitz.open')
    def test_extract_chapter_by_title_success(self, mock_fitz_open):
        """Test extract_chapter_by_title successful case"""
        # Mock PyMuPDF document with TOC and pages
        mock_doc = Mock()
        mock_doc.get_toc.return_value = [
            (1, "Chapter 1", 1),
            (1, "Chapter 2", 3),
            (1, "Chapter 3", 5)
        ]
        mock_doc.page_count = 7
        
        # Mock pages
        mock_page1 = Mock()
        mock_page1.get_text.return_value = "Chapter 1 content"
        mock_page2 = Mock()
        mock_page2.get_text.return_value = "Chapter 2 content"
        
        mock_doc.__getitem__ = Mock(side_effect=lambda x: mock_page1 if x == 0 else mock_page2)
        
        mock_fitz_open.return_value = mock_doc
        
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as f:
            f.write(b"mock pdf content")
            pdf_path = f.name
        
        try:
            content, pages = extract_chapter_by_title(pdf_path, "Chapter 1")
            assert "Chapter 1 content" in content
            assert "Chapter 2 content" in content
            assert pages == [1, 2]
        finally:
            os.unlink(pdf_path)
    
    @patch('ebook_mcp.tools.pdf_helper.fitz.open')
    def test_extract_chapter_by_title_chapter_not_found(self, mock_fitz_open):
        """Test extract_chapter_by_title with chapter not found"""
        # Mock PyMuPDF document with TOC
        mock_doc = Mock()
        mock_doc.get_toc.return_value = [
            (1, "Chapter 1", 1),
            (1, "Chapter 2", 3)
        ]
        mock_fitz_open.return_value = mock_doc
        
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as f:
            f.write(b"mock pdf content")
            pdf_path = f.name
        
        try:
            with pytest.raises(Exception, match="Failed to extract chapter"):
                extract_chapter_by_title(pdf_path, "Non-existent Chapter")
        finally:
            os.unlink(pdf_path)
    
    @patch('ebook_mcp.tools.pdf_helper.fitz.open')
    def test_extract_chapter_by_title_single_page(self, mock_fitz_open):
        """Test extract_chapter_by_title with single page chapter"""
        # Mock PyMuPDF document with TOC
        mock_doc = Mock()
        mock_doc.get_toc.return_value = [
            (1, "Chapter 1", 1),
            (1, "Chapter 2", 2)
        ]
        mock_doc.page_count = 3
        
        # Mock page
        mock_page = Mock()
        mock_page.get_text.return_value = "Chapter 1 content"
        mock_doc.__getitem__ = Mock(return_value=mock_page)
        
        mock_fitz_open.return_value = mock_doc
        
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as f:
            f.write(b"mock pdf content")
            pdf_path = f.name
        
        try:
            content, pages = extract_chapter_by_title(pdf_path, "Chapter 1")
            assert "Chapter 1 content" in content
            assert pages == [1]
        finally:
            os.unlink(pdf_path)
