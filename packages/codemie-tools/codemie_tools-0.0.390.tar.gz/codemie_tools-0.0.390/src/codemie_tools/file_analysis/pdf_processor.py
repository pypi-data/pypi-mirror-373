import logging
from typing import Optional, List, Union

import fitz
import pymupdf4llm
from langchain_core.language_models import BaseChatModel
from pymupdf import Document, Page

from codemie_tools.base.constants import SOURCE_DOCUMENT_KEY, SOURCE_FIELD_KEY, FILE_CONTENT_FIELD_KEY
from codemie_tools.base.file_object import FileObject
from codemie_tools.utils.image_processor import ImageProcessor

# Configure logger
logger = logging.getLogger(__name__)

# Constants for error messages
ERROR_NO_PDF_LOADED = "No PDF document is loaded"
ERROR_NO_PDF_LOADED_DETAIL = "No PDF document is loaded. Please provide a valid PDF."


class PdfProcessor:
    """
    A utility class for processing PDFs and extracting text using OCR capabilities.
    Uses ImageProcessor for image-based text extraction and PyMuPDF for PDF processing.
    """

    def __init__(self, chat_model: Optional[BaseChatModel] = None):
        """
        Initialize the OCR processor.

        Args:
            chat_model: Optional LangChain chat model for image text extraction
        """
        self.image_processor = ImageProcessor(chat_model=chat_model) if chat_model else None

    @staticmethod
    def open_pdf_document(file_content: bytes) -> Document:
        """
        Opens a PDF document from file content.

        Args:
            file_content: PDF file content as bytes

        Returns:
            Document: PyMuPDF document object
        """
        try:
            return fitz.open(stream=file_content, filetype="pdf")
        except Exception as e:
            raise ValueError(f"Failed to open PDF document: {str(e)}")

    def process_pdf_files(self, files: List[FileObject], pages: List[int] = None) -> str:
        """
        Process multiple PDF files and extract text from both regular content and images.
    
        Args:
            files: List of PDF files to process
            pages: List of 1-based page numbers to process. If None, processes all pages.
    
        Returns:
            str: Combined extracted text from all PDF content and images
        """
        if not files:
            raise ValueError(ERROR_NO_PDF_LOADED_DETAIL)
    
        logger.info(f"Processing {len(files)} PDF files with LLM for image text recognition")
    
        # If there's only one file, process it directly
        if len(files) == 1:
            pdf_document = self.open_pdf_document(files[0].content)
            try:
                return self._process_pdf_document(pdf_document, pages)
            finally:
                pdf_document.close()
    
        # Process multiple files with LLM-friendly separators
        results = []
        for idx, file_object in enumerate(files):
            logger.info(f"Processing PDF {idx + 1}/{len(files)}: {file_object.name}")
    
            pdf_document = self.open_pdf_document(file_object.content)
            try:
                file_content = self._process_pdf_document(pdf_document, pages)
                results.append(f"\n{SOURCE_DOCUMENT_KEY}\n")
                results.append(f"{SOURCE_FIELD_KEY} {file_object.name}\n")
                results.append(f"{FILE_CONTENT_FIELD_KEY} \n{file_content}\n")
            finally:
                pdf_document.close()
    
        return "\n".join(results)

    def process_pdf(self, pdf_document: Document, pages: List[int] = None) -> str:
        """
        Process a PDF document and extract text from both regular content and images.

        Args:
            pdf_document: PDF document object
            pages: List of 1-based page numbers to process. If None, processes all pages.

        Returns:
            str: Combined extracted text from PDF content and images
        """
        if not pdf_document or getattr(pdf_document, 'is_closed', True):
            raise ValueError(ERROR_NO_PDF_LOADED_DETAIL)

        logger.info("Processing PDF with LLM for image text recognition")

        try:
            return self._process_pdf_document(pdf_document, pages)
        finally:
            pdf_document.close()

    def extract_text_as_markdown_from_files(self, files: List[FileObject], pages: List[int] = None, 
                                          page_chunks: bool = False) -> str:
        """
        Extract text from multiple PDF files and format it as markdown.
    
        Args:
            files: List of PDF files to process
            pages: List of 1-based page numbers to process. If None, processes all pages.
            page_chunks: Whether to include page metadata in the output.
    
        Returns:
            str: Markdown-formatted extracted text from all PDFs
        """
        if not files:
            raise ValueError(ERROR_NO_PDF_LOADED)
    
        logger.info(f"Extracting text from {len(files)} PDF files")
    
        # If there's only one file, process it directly
        if len(files) == 1:
            pdf_document = self.open_pdf_document(files[0].content)
            try:
                return self.extract_text_as_markdown(pdf_document, pages, page_chunks)
            finally:
                pdf_document.close()
    
        # Process multiple files with LLM-friendly separators
        results = []
    
        for idx, file_object in enumerate(files):
            logger.info(f"Processing PDF {idx + 1}/{len(files)}: {file_object.name}")
    
            pdf_document = self.open_pdf_document(file_object.content)
            try:
                file_content = self.extract_text_as_markdown(pdf_document, pages, page_chunks)
                results.append(f"\n{SOURCE_DOCUMENT_KEY}\n")
                results.append(f"{SOURCE_FIELD_KEY} {file_object.name}\n")
                results.append(f"{FILE_CONTENT_FIELD_KEY} \n{file_content}\n")
            finally:
                pdf_document.close()
    
        return "\n".join(results)

    @staticmethod
    def extract_text_as_markdown(pdf_document: Document, pages: List[int] = None,
                                 page_chunks: bool = False) -> str:
        """
        Extract text from a PDF document and format it as markdown.

        Args:
            pdf_document: PyMuPDF document object
            pages: List of 1-based page numbers to process. If None, processes all pages.
            page_chunks: Whether to include page metadata in the output.

        Returns:
            str: Markdown-formatted extracted text from the PDF
        """
        if not pdf_document:
            raise ValueError(ERROR_NO_PDF_LOADED_DETAIL)

        if getattr(pdf_document, 'is_closed', False):
            raise ValueError("document closed")

        logger.info(f"Extracting text from pages: {pages if pages else 'all'}")

        # Convert 1-based page indices to 0-based for PyMuPDF.
        zero_based_pages = [p - 1 for p in pages] if pages else None

        markdown = pymupdf4llm.to_markdown(
            doc=pdf_document,
            pages=zero_based_pages,
            page_chunks=page_chunks
        )
        logger.debug(f"Extracted {len(markdown)} characters of text")
        return markdown

    def get_total_pages_from_files(self, files: List[FileObject]) -> str:
        """
        Get the total number of pages across all provided PDF files.
    
        Args:
            files: List of PDF files
    
        Returns:
            str: Total number of pages as a string and breakdown by file
        """
        if not files:
            raise ValueError(ERROR_NO_PDF_LOADED)
    
        # If there's only one file, get pages directly
        if len(files) == 1:
            pdf_document = self.open_pdf_document(files[0].content)
            try:
                pages = pdf_document.page_count
                return f"Total pages: {pages}\n{files[0].name}: {pages} pages"
            finally:
                pdf_document.close()
    
        # For multiple files
        total_pages = 0
        file_pages = []
    
        for idx, file_obj in enumerate(files):
            pdf_document = self.open_pdf_document(file_obj.content)
            try:
                pages = pdf_document.page_count
                total_pages += pages
                file_pages.append(f"{file_obj.name}: {pages} pages")
            finally:
                pdf_document.close()
    
        results = ["### PDF PAGE COUNT SUMMARY ###\n", f"**Total pages across all files:** {total_pages}\n",
                   "**Breakdown by file:**\n", "\n".join(file_pages)]

        return "\n".join(results)

    @staticmethod
    def get_total_pages(pdf_document: Document) -> str:
        """
        Get the total number of pages in a PDF document.

        Args:
            pdf_document: PyMuPDF document object

        Returns:
            str: Total number of pages as a string
        """
        if not pdf_document or getattr(pdf_document, 'is_closed', True):
            logger.error(ERROR_NO_PDF_LOADED)
            raise ValueError(ERROR_NO_PDF_LOADED_DETAIL)

        logger.debug(f"Returning total page count: {pdf_document.page_count}")
        return str(pdf_document.page_count)

    def _process_pdf_document(self, pdf_document: Document, pages: List[int] = None) -> str:
        """
        Internal method to process a PDF document and extract text.

        Args:
            pdf_document: PyMuPDF document object
            pages: List of 1-based page numbers to process. If None, processes all pages.

        Returns:
            str: Combined extracted text from PDF content and images
        """
        # Convert 1-based page indices to 0-based for PyMuPDF
        zero_based_pages = [p - 1 for p in pages] if pages else list(range(pdf_document.page_count))

        all_text = []

        for page_num in zero_based_pages:
            logger.info(f"Processing page {page_num + 1}")
            page = pdf_document[page_num]

            # Extract text directly from PDF
            text = page.get_text() if hasattr(page, 'get_text') else page.getText()
            if text.strip():
                all_text.append(f"--- Page {page_num + 1} PDF Text ---\n{text}")

            # Process images if image processor is available
            if not self.image_processor:
                continue

            # Extract and process images
            image_text = self._process_page_images(pdf_document, page, page_num)
            if image_text:
                all_text.append(image_text)

        # Combine all extracted text
        result = "\n\n".join(all_text)
        logger.info(f"Processing complete, extracted {len(result)} characters in total")
        return result

    def _process_page_images(self, pdf_document: Document, page: Page, page_num: int) -> Optional[str]:
        """
        Process all images on a single PDF page.

        Args:
            pdf_document: PyMuPDF document object
            page: PyMuPDF page object
            page_num: Zero-based page number

        Returns:
            Optional[str]: Extracted text from images, if any
        """
        image_list = page.get_images(full=True)
        if not image_list:
            logger.debug(f"No images found on page {page_num + 1}")
            return None

        logger.info(f"Found {len(image_list)} images on page {page_num + 1}")
        page_image_texts = []

        for img_idx, img_info in enumerate(image_list):
            try:
                xref = img_info[0]
                base_image = pdf_document.extract_image(xref)
                image_bytes = base_image["image"]

                # Use the image processor to extract text
                image_text = self.image_processor.extract_text_from_image_bytes(image_bytes)

                if image_text.strip():
                    page_image_texts.append(
                        f"--- Page {page_num + 1} Image {img_idx + 1} Text ---\n{image_text}"
                    )
                    logger.debug(f"Extracted {len(image_text)} characters from image {img_idx}")
                else:
                    logger.debug(f"No text found in image {img_idx} on page {page_num + 1}")

            except Exception as e:
                logger.error(f"Error processing image {img_idx} on page {page_num + 1}: {str(e)}")

        return "\n\n".join(page_image_texts) if page_image_texts else None