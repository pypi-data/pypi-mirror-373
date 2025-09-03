from typing import List, Tuple, Dict, Union
import os
from io import StringIO
import fitz  # PyMuPDF
import re
from .logger_config import get_logger, log_operation

# Custom exception class for PDF processing errors
class PdfProcessingError(Exception):
    """Custom exception for PDF processing errors with detailed context"""
    def __init__(self, message: str, file_path: str, operation: str, original_error: Exception = None):
        self.message = message
        self.file_path = file_path
        self.operation = operation
        self.original_error = original_error
        super().__init__(f"{message} (file: {file_path}, operation: {operation})")

# Initialize structured logger
logger = get_logger(__name__)

def get_all_pdf_files(path: str) -> List[str]:
    """
    Get all PDF files in the specified path
    """
    return [f for f in os.listdir(path) if f.endswith('.pdf')]

@log_operation("pdf_metadata_extraction")
def get_meta(pdf_path: str) -> Dict[str, Union[str, List[str]]]:
    """
    Get metadata from a PDF file using PyMuPDF
    
    Args:
        pdf_path (str): Absolute path to the PDF file
        
    Returns:
        Dict[str, Union[str, List[str]]]: Dictionary containing metadata
            
    Raises:
        FileNotFoundError: If the file does not exist
        Exception: If the file is not a valid PDF or parsing fails
    """
    try:
        if not os.path.exists(pdf_path):
            logger.error(
                "PDF file not found",
                file_path=pdf_path,
                operation="metadata_extraction"
            )
            raise FileNotFoundError(f"PDF file not found: {pdf_path}")
            
        # Read PDF file using PyMuPDF
        logger.debug(
            "Starting PDF metadata extraction",
            file_path=pdf_path,
            operation="metadata_extraction"
        )
        doc = fitz.open(pdf_path)
        meta = {}

        # Extract metadata from PDF using PyMuPDF
        metadata = doc.metadata
        
        # Standard metadata fields mapping
        standard_fields = {
            'title': 'title',
            'author': 'author', 
            'subject': 'subject',
            'creator': 'creator',
            'producer': 'producer',
            'creation_date': 'creationDate',
            'modification_date': 'modDate',
            'keywords': 'keywords',
            'format': 'format'
        }

        # Extract standard metadata fields
        for field, pdf_field in standard_fields.items():
            if pdf_field in metadata and metadata[pdf_field]:
                meta[field] = metadata[pdf_field]

        # Add additional information
        meta['pages'] = doc.page_count
        meta['file_size'] = os.path.getsize(pdf_path)
        
        # Get PDF version and encryption info
        try:
            # Try to get version info - different PyMuPDF versions have different APIs
            if hasattr(doc, 'version_major') and hasattr(doc, 'version_minor'):
                meta['pdf_version'] = f"{doc.version_major}.{doc.version_minor}"
            elif hasattr(doc, 'version'):
                meta['pdf_version'] = str(doc.version)
            else:
                meta['pdf_version'] = "Unknown"
        except:
            meta['pdf_version'] = "Unknown"
        
        meta['is_encrypted'] = doc.is_encrypted
        
        # Get page dimensions (first page)
        if doc.page_count > 0:
            try:
                first_page = doc[0]
                rect = first_page.rect
                meta['page_width'] = rect.width
                meta['page_height'] = rect.height
            except:
                # If we can't get page dimensions, skip it
                pass
        
        doc.close()
        
        logger.info(
            "PDF metadata extraction completed",
            file_path=pdf_path,
            operation="metadata_extraction",
            page_count=meta.get('pages', 0),
            file_size=meta.get('file_size', 0),
            metadata_fields=list(meta.keys())
        )
        return meta

    except FileNotFoundError:
        raise FileNotFoundError(f"PDF file not found: {pdf_path}")
    except Exception as e:
        logger.error(
            "Failed to parse PDF file",
            file_path=pdf_path,
            operation="metadata_extraction",
            error_type=type(e).__name__,
            error_details=str(e)
        )
        raise PdfProcessingError("Failed to parse PDF file", pdf_path, "metadata_extraction", e)

@log_operation("pdf_toc_extraction")
def get_toc(pdf_path: str) -> List[Tuple[str, int]]:
    """
    Get the Table of Contents (TOC) from a PDF file
    
    Args:
        pdf_path (str): Absolute path to the PDF file
        
    Returns:
        List[Tuple[str, int]]: List of TOC entries, each entry is a tuple of (title, page_number)
        
    Raises:
        FileNotFoundError: If the file does not exist
        Exception: If the file is not a valid PDF or parsing fails
    """
    try:
        if not os.path.exists(pdf_path):
            logger.error(
                "PDF file not found",
                file_path=pdf_path,
                operation="toc_extraction"
            )
            raise FileNotFoundError(f"PDF file not found: {pdf_path}")
            
        # Read PDF file using PyMuPDF for better TOC support
        logger.debug(
            "Starting PDF TOC extraction",
            file_path=pdf_path,
            operation="toc_extraction"
        )
        doc = fitz.open(pdf_path)
        toc = []
        
        # Get TOC from document
        outline = doc.get_toc()
        for item in outline:
            level, title, page = item
            toc.append((title, page))
        
        doc.close()
        logger.info(
            "PDF TOC extraction completed",
            file_path=pdf_path,
            operation="toc_extraction",
            chapter_count=len(toc)
        )
        return toc

    except FileNotFoundError:
        raise FileNotFoundError(f"PDF file not found: {pdf_path}")
    except Exception as e:
        logger.error(
            "Failed to parse PDF file",
            file_path=pdf_path,
            operation="toc_extraction",
            error_type=type(e).__name__,
            error_details=str(e)
        )
        raise PdfProcessingError("Failed to parse PDF file", pdf_path, "toc_extraction", e)

def extract_page_text(pdf_path: str, page_number: int) -> str:
    """
    Extract text content from a specific page in the PDF
    
    Args:
        pdf_path: Path to the PDF file
        page_number: Page number to extract (1-based index)
        
    Returns:
        str: Extracted text content
    """
    try:
        doc = fitz.open(pdf_path)
        # Convert to 0-based index
        page = doc[page_number - 1]
        text = page.get_text()
        doc.close()
        return text
    except Exception as e:
        logger.error(
            "Failed to extract page text",
            file_path=pdf_path,
            page_number=page_number,
            operation="page_text_extraction",
            error_type=type(e).__name__,
            error_details=str(e)
        )
        raise PdfProcessingError("Failed to extract page text", pdf_path, "page_text_extraction", e)

def extract_page_markdown(pdf_path: str, page_number: int) -> str:
    """
    Extract text content from a specific page and convert to markdown format
    
    Args:
        pdf_path: Path to the PDF file
        page_number: Page number to extract (1-based index)
        
    Returns:
        str: Markdown formatted text
    """
    try:
        doc = fitz.open(pdf_path)
        page = doc[page_number - 1]
        
        # Extract text with formatting information
        blocks = page.get_text("dict")["blocks"]
        markdown_text = StringIO()
        
        for block in blocks:
            if "lines" in block:
                for line in block["lines"]:
                    for span in line["spans"]:
                        text = span["text"]
                        size = span["size"]
                        flags = span["flags"]
                        
                        # Convert formatting to markdown
                        if size > 14:  # Assuming larger text is a header
                            text = f"## {text}"
                        if flags & 2**3:  # Bold text
                            text = f"**{text}**"
                        if flags & 2**1:  # Italic text
                            text = f"*{text}*"
                            
                        markdown_text.write(text + " ")
                    markdown_text.write("\n")
                markdown_text.write("\n")
        
        doc.close()
        return markdown_text.getvalue()
    except Exception as e:
        logger.error(
            "Failed to extract page markdown",
            file_path=pdf_path,
            page_number=page_number,
            operation="page_markdown_extraction",
            error_type=type(e).__name__,
            error_details=str(e)
        )
        raise PdfProcessingError("Failed to extract page markdown", pdf_path, "page_markdown_extraction", e)

def extract_chapter_by_title(pdf_path: str, chapter_title: str) -> Tuple[str, List[int]]:
    """
    Extract a chapter's content by its title from the TOC
    
    Args:
        pdf_path: Path to the PDF file
        chapter_title: Title of the chapter to extract
        
    Returns:
        Tuple[str, List[int]]: Tuple containing (chapter_content, page_numbers)
    """
    try:
        # Get TOC to find chapter location
        toc = get_toc(pdf_path)
        chapter_start_page = None
        chapter_end_page = None
        
        # Find the chapter in TOC
        for i, (title, page) in enumerate(toc):
            if title == chapter_title:
                chapter_start_page = page
                if i < len(toc) - 1:
                    chapter_end_page = toc[i + 1][1]
                break
        
        if chapter_start_page is None:
            raise PdfProcessingError(f"Chapter '{chapter_title}' not found in TOC", pdf_path, "chapter_lookup")
            
        # If it's the last chapter, read until the end of the document
        if chapter_end_page is None:
            doc = fitz.open(pdf_path)
            chapter_end_page = doc.page_count
            doc.close()
            
        # Extract content from all pages in the chapter
        content = []
        for page_num in range(chapter_start_page, chapter_end_page):
            content.append(extract_page_text(pdf_path, page_num))
            
        return ("\n".join(content), list(range(chapter_start_page, chapter_end_page)))
        
    except Exception as e:
        logger.error(
            "Failed to extract chapter",
            file_path=pdf_path,
            chapter_title=chapter_title,
            operation="chapter_extraction",
            error_type=type(e).__name__,
            error_details=str(e)
        )
        raise PdfProcessingError("Failed to extract chapter", pdf_path, "chapter_extraction", e)
