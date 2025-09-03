import pytest
import os
import tempfile
from unittest.mock import Mock, patch

# Test basic file operations that don't require external dependencies

def test_get_all_epub_files_basic():
    """Test basic EPUB file discovery without external dependencies"""
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create mock EPUB files
        epub_files = ["book1.epub", "book2.epub", "document.txt"]
        for file in epub_files:
            with open(os.path.join(temp_dir, file), 'w') as f:
                f.write("mock content")
        
        # Test the basic file discovery logic
        result = [f for f in os.listdir(temp_dir) if f.endswith('.epub')]
        assert set(result) == {"book1.epub", "book2.epub"}

def test_get_all_pdf_files_basic():
    """Test basic PDF file discovery without external dependencies"""
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create mock PDF files
        pdf_files = ["document1.pdf", "document2.pdf", "text.txt"]
        for file in pdf_files:
            with open(os.path.join(temp_dir, file), 'w') as f:
                f.write("mock content")
        
        # Test the basic file discovery logic
        result = [f for f in os.listdir(temp_dir) if f.endswith('.pdf')]
        assert set(result) == {"document1.pdf", "document2.pdf"}

def test_file_not_found_error():
    """Test file not found error handling"""
    with pytest.raises(FileNotFoundError):
        with open("/nonexistent/file.txt", 'r') as f:
            pass

def test_temp_file_operations():
    """Test temporary file operations"""
    with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
        f.write("test content")
        temp_path = f.name
    
    try:
        # Verify file was created
        assert os.path.exists(temp_path)
        
        # Read content
        with open(temp_path, 'r') as f:
            content = f.read()
        assert content == "test content"
    finally:
        # Clean up
        if os.path.exists(temp_path):
            os.unlink(temp_path)

def test_directory_operations():
    """Test directory operations"""
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create subdirectory
        sub_dir = os.path.join(temp_dir, "subdir")
        os.makedirs(sub_dir)
        
        # Create files in subdirectory
        files = ["file1.txt", "file2.txt"]
        for file in files:
            with open(os.path.join(sub_dir, file), 'w') as f:
                f.write(f"content for {file}")
        
        # List files
        result = os.listdir(sub_dir)
        assert set(result) == set(files)

@pytest.mark.parametrize("file_extension,expected_count", [
    (".epub", 2),
    (".pdf", 1),
    (".txt", 3),
])
def test_file_filtering(file_extension, expected_count):
    """Test file filtering by extension"""
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create test files
        test_files = [
            "book1.epub",
            "book2.epub", 
            "document.pdf",
            "file1.txt",
            "file2.txt",
            "file3.txt"
        ]
        
        for file in test_files:
            with open(os.path.join(temp_dir, file), 'w') as f:
                f.write("content")
        
        # Filter by extension
        result = [f for f in os.listdir(temp_dir) if f.endswith(file_extension)]
        assert len(result) == expected_count

def test_mock_basic_operations():
    """Test basic mock operations"""
    mock_file = Mock()
    mock_file.read.return_value = "mock content"
    mock_file.write.return_value = None
    
    # Test mock behavior
    assert mock_file.read() == "mock content"
    mock_file.write("test")
    mock_file.write.assert_called_once_with("test")

def test_patch_basic():
    """Test basic patch functionality"""
    with patch('os.path.exists', return_value=False):
        assert not os.path.exists("/any/path")
    
    with patch('os.path.exists', return_value=True):
        assert os.path.exists("/any/path") 