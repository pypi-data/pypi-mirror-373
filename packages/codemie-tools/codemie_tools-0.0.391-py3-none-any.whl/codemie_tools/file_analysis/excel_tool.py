import io
import logging
from typing import Type, Optional, List, Dict, Union, Any

import pandas as pd
from langchain_core.language_models import BaseChatModel
from markitdown import MarkItDown, PRIORITY_SPECIFIC_FILE_FORMAT
from pydantic import BaseModel, Field

from codemie_tools.base.codemie_tool import CodeMieTool
from codemie_tools.base.constants import SOURCE_DOCUMENT_KEY, SOURCE_FIELD_KEY, FILE_CONTENT_FIELD_KEY
from codemie_tools.base.file_object import FileObject
from codemie_tools.file_analysis.markitdown_xlsx_converter import XlsxConverter
from codemie_tools.file_analysis.xlsx_processor import XlsxProcessor
from codemie_tools.file_analysis.tool_vars import EXCEL_TOOL

logger = logging.getLogger(__name__)

class ExcelToolInput(BaseModel):
    query: str = Field(default="", description="""User initial request should be passed as a string.""")
    sheet_names: List[str] = Field(default_factory=list, description="""Sheet names of Excel file to analyze. If empty, all sheets will be processed.""")
    sheet_index: Optional[int] = Field(default=None, description="""Index of the sheet to analyze (0-based). If provided, overrides sheet_names.""")
    get_sheet_names: bool = Field(default=False, description="""If True, returns only the names of all sheets in the Excel file.""")
    get_stats: bool = Field(default=False, description="""If True, returns statistics about the Excel file (sheet count, row counts, column counts).""")
    visible_only: bool = Field(default=True, description="""If True, only visible sheets will be processed. Hidden and very hidden sheets will be ignored.""")

class ExcelTool(CodeMieTool):
    """ Tool for working with and analyzing Excel file contents. """
    args_schema: Optional[Type[BaseModel]] = ExcelToolInput
    name: str = EXCEL_TOOL.name
    label: str = EXCEL_TOOL.label
    description: str = EXCEL_TOOL.description
    files: list[FileObject] = Field(exclude=True)
    chat_model: Optional[BaseChatModel] = Field(default=None, exclude=True)
    tokens_size_limit: int = 100_000

    def _load_excel_file(
            self,
            file_object: FileObject,
            clean_data: bool = True,
            visible_only: bool = True,
            sheet_names: List[str] = None
    ) -> Dict[str, pd.DataFrame]:
        """Load an Excel file and return a dictionary of DataFrames for each sheet
    
        Args:
            file_object: The FileObject containing the Excel file
            clean_data: If True, clean the data by removing empty rows and columns
            visible_only: If True, only visible sheets will be processed
            sheet_names: Optional list of specific sheet names to load
    
        Returns:
            Dictionary of DataFrames for each sheet
        """
        try:
            processor = XlsxProcessor(sheet_names=sheet_names, visible_only=visible_only)
            return processor.load(file_object.bytes_content(), clean_data=clean_data)
        except Exception as e:
            logger.error(f"Failed to load Excel file: {str(e)}")
            raise e
    
    def _get_sheet_names(self, file_object: FileObject, visible_only: bool = True) -> List[str]:
        """Get the names of all sheets in an Excel file
    
        Args:
            file_object: The FileObject containing the Excel file
            visible_only: If True, only visible sheets will be returned
    
        Returns:
            List of sheet names
        """
        try:
            sheets = self._load_excel_file(file_object, visible_only=visible_only)
            return list(sheets.keys())
        except Exception as e:
            logger.error(f"Failed to get sheet names: {str(e)}")
            return [f"Error getting sheet names: {str(e)}"]
    
    def _get_sheet_by_index(
            self, file_object: FileObject, index: int, visible_only: bool = True
    ) -> Union[pd.DataFrame, str]:
        """Get a specific sheet by its index (0-based)
    
        Args:
            file_object: The FileObject containing the Excel file
            index: The index of the sheet to get (0-based)
            visible_only: If True, only visible sheets will be considered
    
        Returns:
            DataFrame of the sheet and its name, or error message and None
        """
        try:
            sheets = self._load_excel_file(file_object, visible_only=visible_only)
            sheet_names = list(sheets.keys())
            if 0 <= index < len(sheet_names):
                sheet_name = sheet_names[index]
                return sheets[sheet_name], sheet_name
            else:
                return f"Invalid sheet index: {index}. Valid range: 0-{len(sheet_names)-1}", None
        except Exception as e:
            logger.error(f"Failed to get sheet by index: {str(e)}")
            return f"Error getting sheet by index: {str(e)}", None
    
    def _detect_column_data_type(self, column: pd.Series) -> str:
        """Detect the data type of a column
    
        Args:
            column: The pandas Series to analyze
    
        Returns:
            String representation of the data type
        """
        if pd.api.types.is_numeric_dtype(column):
            if pd.api.types.is_integer_dtype(column):
                return "integer"
            else:
                return "float"
        elif pd.api.types.is_datetime64_dtype(column):
            return "datetime"
        else:
            # Check if it's a boolean column (True/False values)
            unique_vals = set(column.astype(str).str.lower().unique())
            if unique_vals.issubset({'true', 'false', '', 'yes', 'no', 'y', 'n'}):
                return "boolean"
            else:
                return "string"
    
    def _get_column_sample_values(self, column: pd.Series, max_samples: int = 5, max_length: int = 50) -> List[str]:
        """Get sample values from a column
    
        Args:
            column: The pandas Series to get samples from
            max_samples: Maximum number of samples to return
            max_length: Maximum length of each sample string
    
        Returns:
            List of sample values as strings
        """
        unique_vals = column.astype(str).unique()
        # Limit samples and truncate long values
        return [str(val)[:max_length] + ('...' if len(str(val)) > max_length else '') 
                for val in unique_vals[:max_samples]]
    
    def _get_sheet_statistics(self, sheet_name: str, dataframe: pd.DataFrame) -> Dict[str, Any]:
        """Generate statistics for a single sheet
    
        Args:
            sheet_name: Name of the sheet
            dataframe: DataFrame containing the sheet data
    
        Returns:
            Dictionary of sheet statistics
        """
        data_types = {}
        sample_values = {}
    
        for col in dataframe.columns:
            data_types[col] = self._detect_column_data_type(dataframe[col])
            sample_values[col] = self._get_column_sample_values(dataframe[col])
    
        return {
            "columns": list(dataframe.columns),
            "data_types": data_types,
            "sample_values": sample_values
        }
    
    def _get_excel_stats(self, file_object: FileObject, visible_only: bool = True) -> Dict[str, Any]:
        """Get comprehensive statistics about an Excel file, with data cleaning to avoid pollution
    
        Args:
            file_object: The FileObject containing the Excel file
            visible_only: If True, only visible sheets will be included in stats
    
        Returns:
            Dictionary of statistics about the Excel file
        """
        try:
            # Load cleaned sheets for clean stats
            raw_sheets = self._load_excel_file(file_object, visible_only=visible_only)
    
            stats = {
                "file_name": file_object.name,
                "sheet_count": len(raw_sheets),
                "sheets": {}
            }
    
            # Process each sheet
            for sheet_name, raw_df in raw_sheets.items():
                stats["sheets"][sheet_name] = self._get_sheet_statistics(sheet_name, raw_df)
    
            return stats
        except Exception as e:
            logger.error(f"Failed to get Excel stats: {str(e)}")
            return {"error": f"Failed to get Excel stats: {str(e)}"}
    
    def _process_excel_file(
            self, file_object: FileObject, sheet_names: List[str] = None, visible_only: bool = True
    ) -> str:
        """Process an Excel file and return its content as markdown text
    
        Args:
            file_object: The FileObject containing the Excel file
            sheet_names: List of sheet names to process. If None, all sheets will be processed
            visible_only: If True, only visible sheets will be processed
    
        Returns:
            Markdown text representation of the Excel file
        """
        try:
            
            llm_model = (
                getattr(self.chat_model, "model_name", None)
                or getattr(self.chat_model, "model", None)
                if self.chat_model else None
            )
            md = MarkItDown(
                enable_builtins=True,
                llm_client=self.chat_model.client if self.chat_model and hasattr(self.chat_model, "client") else None,
                llm_model=llm_model,
            )
            md.register_converter(
                XlsxConverter(sheet_names=sheet_names, visible_only=visible_only),
                priority=PRIORITY_SPECIFIC_FILE_FORMAT
            )
            # Create a file-like object from bytes content
            binary_content = io.BytesIO(file_object.bytes_content())
            result = md.convert(binary_content)
            return result.text_content
        except FileNotFoundError as e:
            # Handle the case when a file is not found
            return f"File not found: {str(e)}"
        except Exception as e:
            # Return error message for Excel processing failures
            return f"Failed to process Excel file: {str(e)}"
    
    def _format_dataframe_as_markdown(self, df: pd.DataFrame, sheet_name: str = None) -> str:
        """Format a DataFrame as a markdown table"""
        header = f"## {sheet_name}\n" if sheet_name else ""
        return header + df.to_markdown(index=False)
    
    def _format_stats_as_markdown(self, stats: Dict[str, Any]) -> str:
        """Format Excel statistics as markdown with comprehensive details"""
        if "error" in stats:
            return f"Error: {stats['error']}"
    
        result = [f"# Excel File Statistics: {stats['file_name']}"]
        result.append(f"- **Total Sheets:** {stats['sheet_count']}")
    
        for sheet_name, sheet_stats in stats['sheets'].items():
            result.append(f"\n## Sheet: {sheet_name}")
    
            # Column information
            if "columns" in sheet_stats:
                result.append("\n### Columns:")
                col_table = ["| Column | Data Type | Sample Values |"]
                col_table.append("| ------ | --------- | ------------- |")
    
                for col in sheet_stats["columns"]:
                    data_type = sheet_stats.get("data_types", {}).get(col, "unknown")
                    samples = sheet_stats.get("sample_values", {}).get(col, [])
                    sample_str = ", ".join([f"`{s}`" for s in samples[:3]])
                    if len(samples) > 3:
                        sample_str += ", ..."
                    col_table.append(f"| {col} | {data_type} | {sample_str} |")
    
                result.extend(col_table)
    
        return "\n".join(result)
    
    def execute(self, query: str = "", sheet_names: List[str] = None, sheet_index: int = None, 
                get_sheet_names: bool = False, get_stats: bool = False, visible_only: bool = True):
        if not self.files:
            raise ValueError(f"{self.name} requires at least one Excel file to process.")
    
        # Process multiple Excel files with LLM-friendly separators
        result = []
    
        for file_object in self.files:
            # Handle special operations
            if get_sheet_names:
                # Get sheet names only
                sheet_list = self._get_sheet_names(file_object, visible_only=visible_only)
                content = f"## Sheets in {file_object.name}:\n- " + "\n- ".join(sheet_list)
            elif get_stats:
                # Get Excel statistics
                stats = self._get_excel_stats(file_object, visible_only=visible_only)
                content = self._format_stats_as_markdown(stats)
            elif sheet_index is not None:
                # Get specific sheet by index
                sheet_data, sheet_name = self._get_sheet_by_index(file_object, sheet_index, visible_only=visible_only)
                if isinstance(sheet_data, pd.DataFrame):
                    content = self._format_dataframe_as_markdown(sheet_data, sheet_name)
                else:
                    content = sheet_data  # This is an error message
            else:
                # Default: process Excel file with markitdown
                content = self._process_excel_file(file_object, sheet_names=sheet_names, visible_only=visible_only)
    
            # Add file header with metadata
            result.append(f"\n{SOURCE_DOCUMENT_KEY}\n")
            result.append(f"{SOURCE_FIELD_KEY} {file_object.name}\n")
            result.append(f"{FILE_CONTENT_FIELD_KEY} \n{content}\n")
    
        return "\n".join(result)