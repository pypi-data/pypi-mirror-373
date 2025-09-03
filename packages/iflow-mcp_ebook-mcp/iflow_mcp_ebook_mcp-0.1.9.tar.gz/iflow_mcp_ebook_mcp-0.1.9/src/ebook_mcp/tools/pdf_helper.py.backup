from PyPDF2 import PdfReader
from typing import List, Tuple, Dict, Union
import os
import logging
from io import StringIO
import fitz  # PyMuPDF
import re

# Initialize logger
logger = logging.getLogger(__name__)

def get_all_pdf_files(path: str) -> List[str]:
    """
    Get all PDF files in the specified path
    """
    return [f for f in os.listdir(path) if f.endswith('.pdf')]

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
            logger.error(f"File not found: {pdf_path}")
            raise FileNotFoundError(f"PDF file not found: {pdf_path}")
            
        # Read PDF file using PyMuPDF
        logger.debug(f"Starting to read PDF file: {pdf_path}")
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
        
        logger.debug(f"Successfully retrieved metadata with fields: {list(meta.keys())}")
        return meta

    except FileNotFoundError:
        raise FileNotFoundError(f"PDF file not found: {pdf_path}")
    except Exception as e:
        logger.error(f"Failed to parse PDF file: {str(e)}")
        raise Exception("Failed to parse PDF file")

def get_meta_pypdf2(pdf_path: str) -> Dict[str, Union[str, List[str]]]:
    """
    Get metadata from a PDF file using PyPDF2 (legacy method)
    
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
            logger.error(f"File not found: {pdf_path}")
            raise FileNotFoundError(f"PDF file not found: {pdf_path}")
            
        # Read PDF file using PyPDF2
        logger.debug(f"Starting to read PDF file with PyPDF2: {pdf_path}")
        reader = PdfReader(pdf_path)
        meta = {}

        # Extract metadata from PDF
        if reader.metadata:
            # Standard metadata fields
            standard_fields = {
                'title': '/Title',
                'author': '/Author',
                'subject': '/Subject',
                'creator': '/Creator',
                'producer': '/Producer',
                'creation_date': '/CreationDate',
                'modification_date': '/ModDate'
            }

            for field, pdf_field in standard_fields.items():
                if pdf_field in reader.metadata:
                    meta[field] = reader.metadata[pdf_field]

        # Add additional information
        meta['pages'] = len(reader.pages)
        
        logger.debug(f"Successfully retrieved metadata with PyPDF2, fields: {list(meta.keys())}")
        return meta

    except FileNotFoundError:
        raise FileNotFoundError(f"PDF file not found: {pdf_path}")
    except Exception as e:
        logger.error(f"Failed to parse PDF file with PyPDF2: {str(e)}")
        raise Exception("Failed to parse PDF file")

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
            logger.error(f"File not found: {pdf_path}")
            raise FileNotFoundError(f"PDF file not found: {pdf_path}")
            
        # Read PDF file using PyMuPDF for better TOC support
        logger.debug(f"Starting to read PDF file: {pdf_path}")
        doc = fitz.open(pdf_path)
        toc = []
        
        # Get TOC from document
        outline = doc.get_toc()
        for item in outline:
            level, title, page = item
            toc.append((title, page))
        
        doc.close()
        logger.debug(f"Successfully retrieved TOC with {len(toc)} entries")
        return toc

    except FileNotFoundError:
        raise FileNotFoundError(f"PDF file not found: {pdf_path}")
    except Exception as e:
        logger.error(f"Failed to parse PDF file: {str(e)}")
        raise Exception("Failed to parse PDF file")

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
        logger.error(f"Failed to extract page text: {str(e)}")
        raise Exception("Failed to extract page text")

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
        logger.error(f"Failed to extract page markdown: {str(e)}")
        raise Exception("Failed to extract page markdown")

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
            raise ValueError(f"Chapter '{chapter_title}' not found in TOC")
            
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
        logger.error(f"Failed to extract chapter: {str(e)}")
        raise Exception("Failed to extract chapter") 