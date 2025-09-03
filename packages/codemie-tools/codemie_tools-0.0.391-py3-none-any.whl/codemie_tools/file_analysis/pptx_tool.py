from enum import Enum
from typing import Optional, Type, Any, Union, Dict, List

from langchain_core.language_models import BaseChatModel
from pydantic import BaseModel, Field

from codemie_tools.base.codemie_tool import CodeMieTool
from codemie_tools.base.file_object import FileObject
from codemie_tools.file_analysis.pptx_processor import PptxProcessor
from codemie_tools.file_analysis.tool_vars import PPTX_TOOL


class QueryType(str, Enum):
    TEXT = "Text"
    TEXT_WITH_METADATA = "Text_with_Metadata" 
    TOTAL_SLIDES = "Total_Slides"


class PPTXToolInput(BaseModel):
    """
    Defines the schema for the arguments required by PPTXTool.
    """
    slides: list[int] = Field(
        description=(
            "List of slide numbers of a PPTX document to process. "
            "Must be empty to process all slides in a single request. "
            "Slide numbers are 1-based."
        ),
    )
    query: QueryType = Field(
        ..., 
        description=(
            "'Text' if the tool must return the Markdown representation of the PPTX slides. "
            "'Text_with_Metadata' if the tool must return the JSON representation of the "
            "PPTX slides with metadata. Preferred if detailed information is needed. "
            "'Total_Slides' if the tool must return the total number of slides in the PPTX "
            "document."
        ),
    )


class PPTXTool(CodeMieTool):
    args_schema: Type[BaseModel] = PPTXToolInput

    name: str = PPTX_TOOL.name
    label: str = PPTX_TOOL.label
    description: str = PPTX_TOOL.description

    pptx_processor: Optional[PptxProcessor] = None
    files: Optional[List[FileObject]] = None
    chat_model: Optional[BaseChatModel] = Field(default=None, exclude=True)

    def __init__(self, files: List[FileObject], **kwargs: Any) -> None:
        """
        Initialize the PPTXTool with PPTX files.

        Args:
            files: List of FileObject instances containing PPTX content
            **kwargs: Additional keyword arguments to pass along to the super class.
                      Expects chat_model for image text extraction.
        """
        super().__init__(**kwargs)
        if not files:
            raise ValueError(f"{self.name} requires at least one file to process.")
        self.files = files
        self.pptx_processor = PptxProcessor(chat_model=self.chat_model)

    def execute(self, slides: List[int], query: QueryType) -> Union[str, Dict[str, Any]]:
        """
        Process the PPTX documents based on the provided query and slides.

        Args:
            slides (List[int]): A list of 1-based slide numbers to process.
                               If empty, the entire document is processed.
            query (str): The query or action to perform:
                - "Total_Slides" to return the total number of slides.
                - "Text" to return the text representation of the PPTX as markdown.
                - "Text_with_Metadata" to return the PPTX data as structured JSON.

        Returns:
            str | dict: A string representation of the requested data or a dictionary with structured results.
        """
        if not self.files:
            raise ValueError("No PPTX document is loaded. Please provide a valid PPTX.")

        if query == QueryType.TOTAL_SLIDES:
            return self.pptx_processor.get_total_slides_from_files(self.files)
        elif query == QueryType.TEXT:
            return self.pptx_processor.process_pptx_files(self.files, slides)
        elif query == QueryType.TEXT_WITH_METADATA:
            # For metadata, we need to get the structured dictionary data
            pptx_document = self.pptx_processor.open_pptx_document(self.files[0].content)
            return self.pptx_processor.extract_text_as_json(pptx_document, slides)