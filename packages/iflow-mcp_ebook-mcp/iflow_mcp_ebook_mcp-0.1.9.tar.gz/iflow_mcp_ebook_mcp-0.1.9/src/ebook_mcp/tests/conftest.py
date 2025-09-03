import pytest
import tempfile
import os
from unittest.mock import Mock


@pytest.fixture
def temp_dir():
    """Create a temporary directory for testing"""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield temp_dir


@pytest.fixture
def mock_epub_book():
    """Create a mock EPUB book for testing"""
    mock_book = Mock()
    mock_book.get_metadata.return_value = {
        'title': [('Test Book', {})],
        'creator': [('Test Author', {})],
        'language': [('en', {})],
        'identifier': [('test-id', {})],
        'date': [('2023-01-01', {})],
        'publisher': [('Test Publisher', {})],
        'description': [('Test description', {})]
    }
    return mock_book


@pytest.fixture
def mock_pdf_reader():
    """Create a mock PDF reader for testing"""
    mock_reader = Mock()
    mock_reader.metadata = {
        '/Title': 'Test PDF',
        '/Author': 'Test Author',
        '/Subject': 'Test Subject',
        '/Creator': 'Test Creator',
        '/Producer': 'Test Producer',
        '/CreationDate': '2023-01-01',
        '/ModDate': '2023-01-02'
    }
    mock_reader.pages = [Mock(), Mock(), Mock()]  # 3 pages
    return mock_reader


@pytest.fixture
def mock_pdf_document():
    """Create a mock PDF document for testing"""
    mock_doc = Mock()
    mock_doc.get_toc.return_value = [
        (1, "Chapter 1", 1),
        (1, "Chapter 2", 5),
        (2, "Subchapter 2.1", 7)
    ]
    return mock_doc


@pytest.fixture
def sample_epub_files():
    """Create sample EPUB file names for testing"""
    return ["book1.epub", "book2.epub", "document.txt"]


@pytest.fixture
def sample_pdf_files():
    """Create sample PDF file names for testing"""
    return ["document1.pdf", "document2.pdf", "text.txt"]


@pytest.fixture
def temp_epub_file():
    """Create a temporary EPUB file for testing"""
    with tempfile.NamedTemporaryFile(suffix='.epub', delete=False) as f:
        f.write(b"mock epub content")
        epub_path = f.name
    
    yield epub_path
    
    # Cleanup
    if os.path.exists(epub_path):
        os.unlink(epub_path)


@pytest.fixture
def temp_pdf_file():
    """Create a temporary PDF file for testing"""
    with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as f:
        f.write(b"mock pdf content")
        pdf_path = f.name
    
    yield pdf_path
    
    # Cleanup
    if os.path.exists(pdf_path):
        os.unlink(pdf_path) 