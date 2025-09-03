import os
import pytest
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

try:
    from ebook_mcp.azw import find_azw_files, get_metadata, get_toc, get_chapter_text
    AZW_AVAILABLE = True
except ImportError:
    # Skip tests if azw module is not available
    AZW_AVAILABLE = False

@pytest.mark.skipif(not AZW_AVAILABLE, reason="AZW module not available")
def test_find_azw_files(tmp_path):
    # Create test directory structure
    test_dir = tmp_path / "test_azw"
    test_dir.mkdir()

    # Create test files
    (test_dir / "book1.azw").touch()
    (test_dir / "book2.azw3").touch()
    (test_dir / "book3.txt").touch()
    
    # Create subdirectory with more files
    sub_dir = test_dir / "subdir"
    sub_dir.mkdir()
    (sub_dir / "book4.azw").touch()

    # Test file finding
    azw_files = find_azw_files(str(test_dir))
    assert len(azw_files) == 3

    # Clean up test files
    # (handled automatically by pytest)

@pytest.mark.skipif(not AZW_AVAILABLE, reason="AZW module not available")
def test_get_metadata(test_azw_path):
    """Test metadata extraction

    Args:
        test_azw_path: Path to test AZW file (should be provided when running tests)
    """
    metadata = get_metadata(test_azw_path)
    
    # Verify basic metadata fields exist
    assert "title" in metadata
    assert "author" in metadata
    assert "publisher" in metadata
    assert "publication_date" in metadata
    assert "language" in metadata
    assert "isbn" in metadata

@pytest.mark.skipif(not AZW_AVAILABLE, reason="AZW module not available")
def test_get_toc(test_azw_path):
    """Test table of contents extraction

    Args:
        test_azw_path: Path to test AZW file (should be provided when running tests)
    """
    toc = get_toc(test_azw_path)
    
    # Verify TOC structure
    assert isinstance(toc, list)
    for entry in toc:
        assert isinstance(entry, tuple)
        assert len(entry) == 2
        assert isinstance(entry[0], str)  # title
        assert isinstance(entry[1], str)  # chapter_id

@pytest.mark.skipif(not AZW_AVAILABLE, reason="AZW module not available")
def test_get_chapter_text(test_azw_path):
    """Test chapter text extraction

    Args:
        test_azw_path: Path to test AZW file (should be provided when running tests)
    """
    toc = get_toc(test_azw_path)
    if not toc:
        pytest.skip("No TOC available in test file")
    
    chapter_id = toc[0][1]
    text = get_chapter_text(test_azw_path, chapter_id)
    
    assert isinstance(text, str)
    assert len(text) > 0 