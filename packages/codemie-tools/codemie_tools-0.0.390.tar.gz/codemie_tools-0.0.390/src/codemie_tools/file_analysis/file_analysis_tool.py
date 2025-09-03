import io
import logging
from typing import Type, Optional

from langchain_core.language_models import BaseChatModel
from markitdown import MarkItDown, PRIORITY_SPECIFIC_FILE_FORMAT
from pydantic import BaseModel, Field

from codemie_tools.base.codemie_tool import CodeMieTool
from codemie_tools.base.constants import SOURCE_DOCUMENT_KEY, SOURCE_FIELD_KEY, FILE_CONTENT_FIELD_KEY
from codemie_tools.base.file_object import FileObject
from codemie_tools.file_analysis.tool_vars import FILE_ANALYSIS_TOOL

logger = logging.getLogger(__name__)

class FileAnalysisToolInput(BaseModel):
    query: str = Field(default="", description="""User initial request should be passed as a string.""")

class FileAnalysisTool(CodeMieTool):
    """ Tool for working with and analyzing file contents. """
    args_schema: Optional[Type[BaseModel]] = FileAnalysisToolInput
    name: str = FILE_ANALYSIS_TOOL.name
    label: str = FILE_ANALYSIS_TOOL.label
    description: str = FILE_ANALYSIS_TOOL.description
    files: list[FileObject] = Field(exclude=True)
    chat_model: Optional[BaseChatModel] = Field(default=None, exclude=True)
    tokens_size_limit: int = 100_000

    @staticmethod
    def _fallback_decode_text_file(file_object: FileObject, original_exception: Exception = None) -> str:
        """
        Private fallback method to decode text files when markitdown fails
        :param file_object: The FileObject to process
        :param original_exception: The original exception from markitdown (if any)
    
        :return: file content as string or error message
        """
        if file_object.is_text_based():
            try:
                return file_object.string_content()
            except Exception as inner_e:
                return f"Failed to decode file: {str(inner_e)}"
    
        error_msg = "File type not supported for direct decoding"
        if original_exception:
            error_msg += f". Original error: {str(original_exception)}"
        return error_msg
    
    def _process_single_file(self, file_object: FileObject) -> str:
        """Process a single file and return its content as markdown text"""
        try:
            llm_model=(
                getattr(self.chat_model, "model_name", None)
                or getattr(self.chat_model, "model", None)
                if self.chat_model else None
            ),
            md = MarkItDown(
                enable_builtins=True,
                llm_client=self.chat_model.client if self.chat_model and hasattr(self.chat_model, "client") else None,
                llm_model=llm_model,
            )
            # Create a file-like object from bytes content
            binary_content = io.BytesIO(file_object.bytes_content())
            result = md.convert(binary_content)
            return result.text_content
        except FileNotFoundError as e:
            # Handle the case when a file is not found
            return f"File not found: {str(e)}"
        except Exception as e:
            # Fallback to direct decoding for text files if markitdown fails
            return self._fallback_decode_text_file(file_object, original_exception=e)
    
    def execute(self, query: str=""):
        if not self.files:
            raise ValueError(f"{self.name} requires at least one file to process.")
    
        # Process multiple files with LLM-friendly separators
        result = []
        for file_object in self.files:
            file_content = self._process_single_file(file_object)
            # Add file header with metadata
            result.append(f"\n{SOURCE_DOCUMENT_KEY}\n")
            result.append(f"{SOURCE_FIELD_KEY} {file_object.name}\n")
            result.append(f"{FILE_CONTENT_FIELD_KEY} \n{file_content}\n")
    
        return "\n".join(result)
