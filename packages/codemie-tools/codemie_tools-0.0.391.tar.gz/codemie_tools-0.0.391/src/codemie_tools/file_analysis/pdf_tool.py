import logging
from enum import Enum
from typing import Optional, Type, Any, List, Union, Dict

from langchain_core.language_models import BaseChatModel
from pydantic import BaseModel, Field

from codemie_tools.base.codemie_tool import CodeMieTool
from codemie_tools.base.file_object import FileObject
from codemie_tools.file_analysis.pdf_processor import PdfProcessor
from codemie_tools.file_analysis.tool_vars import PDF_TOOL

# Configure logger
logger = logging.getLogger(__name__)


class QueryType(str, Enum):
    TEXT = "Text"
    TEXT_WITH_METADATA = "Text_with_Metadata"
    TEXT_WITH_OCR = "Text_with_Image"  # Kept the name for backward compatibility, now uses LLM
    TOTAL_PAGES = "Total_Pages"


class PDFToolInput(BaseModel):
    """
    Defines the schema for the arguments required by PDFTool.
    """
    pages: list[int] = Field(
        default_factory=list,
        description=(
            "List of page numbers of a PDF document to process. "
            "Must be empty to process all pages in a single request. "
            "Page numbers are 1-based."
        ),
    )
    query: QueryType = Field(
        ...,
        description=(
            "'Text' if the tool must return the text representation of the PDF pages. "
            "'Text_with_Metadata' if the tool must return the text representation of the "
            "PDF pages with metadata. "
            "'Text_with_Image' if the tool must extract text from PDF that contain images within it"
            "'Total_Pages' if the tool must return the total number of pages in the PDF "
            "document."
        ),
    )


class PDFTool(CodeMieTool):
    """
    A tool for processing PDF documents, such as extracting the text from specific pages.
    Also supports text extraction from images within PDFs using LLM-based image recognition.
    Supports multiple PDFs as input.
    """

    # The Pydantic model that describes the shape of arguments this tool takes.
    args_schema: Type[BaseModel] = PDFToolInput

    name: str = PDF_TOOL.name
    label: str = PDF_TOOL.label
    description: str = PDF_TOOL.description

    pdf_processor: Optional[PdfProcessor] = None
    files: Optional[list[FileObject]]= None

    # Chat model used for image text extraction
    chat_model: Optional[BaseChatModel] = Field(default=None, exclude=True)

    def __init__(self, files: list[FileObject], **kwargs: Any) -> None:
        """
        Initialize the PDFTool with PDF files.

        Args:
            files: List of FileObject instances containing PDF content
            **kwargs: Additional keyword arguments to pass along to the super class.
                      Expects chat_model for image text extraction.
        """
        super().__init__(**kwargs)
        if not files:
            raise ValueError(f"{self.name} requires at least one file to process.")
        self.files = files
        self.pdf_processor = PdfProcessor(chat_model=self.chat_model)

    def execute(self, pages: List[int], query: QueryType) -> Union[str, Dict[str, Any]]:
        """
        Process the PDF documents based on the provided query and pages.

        Args:
            pages (List[int]): A list of 1-based page numbers to process.
                               If empty, the entire document is processed.
            query (str): The query or action to perform:
                - "Total_Pages" to return the total number of pages.
                - "Text" to return the text representation of the PDF.
                - "Text_with_Metadata" to return the text along with metadata.
                - "Text_with_OCR" to extract text from PDF and images using LLM.

        Returns:
            str | dict: A string representation of the requested data or a dictionary with structured results.
        """
        logger.info(f"Processing {len(self.files)} PDF files with query type: {query}")

        if query == QueryType.TOTAL_PAGES:
            return self.pdf_processor.get_total_pages_from_files(self.files)

        elif query == QueryType.TEXT_WITH_OCR:
            return self.pdf_processor.process_pdf_files(self.files, pages)

        elif query.lower().startswith("text"):
            # Pass page_chunks parameter based on query type
            page_chunks = (query == QueryType.TEXT_WITH_METADATA)
            return self.pdf_processor.extract_text_as_markdown_from_files(
                files=self.files,
                pages=pages,
                page_chunks=page_chunks
            )

        else:
            error_msg = (f"Unknown query '{query}'. Expected one of ['Total_Pages', 'Text', "
                        f"'Text_with_Metadata', 'Text_with_OCR'].")
            logger.error(error_msg)
            raise ValueError(error_msg)