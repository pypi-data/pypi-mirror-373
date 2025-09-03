import io
import logging
from typing import Dict, Union, Optional, List, BinaryIO, Any, Tuple

import pandas as pd
import numpy as np
import openpyxl
from openpyxl.styles import numbers
import markitdown
from markitdown import StreamInfo
from markitdown.converters import HtmlConverter

logger = logging.getLogger(__name__)


def _normalize_column_names(df: pd.DataFrame) -> pd.DataFrame:
    """Normalize column names by renaming 'Unnamed: X' columns to 'ColX'

    Args:
        df: DataFrame with columns to normalize

    Returns:
        DataFrame with normalized column names
    """
    # Use dictionary comprehension for more efficient column renaming
    rename_dict = {
        col: f"Col{col.split(':')[1].strip()}"
        for col in df.columns
        if isinstance(col, str) and col.startswith("Unnamed: ") and ":" in col
    }

    # Rename columns if any matches were found
    if rename_dict:
        return df.rename(columns=rename_dict)
    return df


def _clean_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """Clean a DataFrame by removing empty rows and columns

    Args:
        df: DataFrame to clean

    Returns:
        Cleaned DataFrame with empty rows and columns removed
    """
    # Create mask for empty strings (after stripping whitespace)
    empty_str_mask_cols = df.astype(str).apply(lambda x: x.str.strip() == '')

    # Drop columns where all values are empty (either NaN or empty string)
    df_clean = df.loc[:, ~(empty_str_mask_cols.all())]

    # Drop rows where all values are empty (either NaN or empty string)
    empty_str_mask_rows = df_clean.astype(str).apply(lambda x: x.str.strip() == '', axis=1)
    df_clean = df_clean.loc[~(empty_str_mask_rows.all(axis=1))]

    return df_clean


def _get_visible_sheets(binary_content: BinaryIO) -> Optional[List[str]]:
    """Get a list of visible sheet names from an Excel file
    
    Args:
        binary_content: File-like object containing Excel data
        
    Returns:
        List of visible sheet names or None if an error occurs
    """
    try:
        # Load the workbook with openpyxl to check sheet visibility
        wb = openpyxl.load_workbook(binary_content, read_only=True)
        # Get only visible sheets
        visible_sheet_names = [sheet.title for sheet in wb.worksheets 
                              if sheet.sheet_state == 'visible']
        # Reset file pointer for pandas to read
        binary_content.seek(0)
        logger.debug(f"Found {len(visible_sheet_names)} visible sheets: {visible_sheet_names}")
        return visible_sheet_names
    except Exception as e:
        logger.warning(f"Failed to check sheet visibility: {str(e)}. Processing all sheets.")
        return None


def _replace_nan_with_empty(df: pd.DataFrame) -> pd.DataFrame:
    """
    Replace NaN values with empty strings in the DataFrame.

    Args:
        df: DataFrame to process

    Returns:
        DataFrame with NaN values replaced by empty strings
    """
    try:
        # Replace NaN values with empty strings without creating an unnecessary copy
        return df.fillna("")
    except Exception as e:
        logger.warning(f"Failed to replace NaN values: {str(e)}. Using original DataFrame.")
        return df

class XlsxProcessor:
    """
    Processes XLSX files by loading them into pandas DataFrames and converting to various formats.
    Provides functionality to filter out empty rows and columns, handle sheet visibility,
    and convert to markdown format.
    """

    def __init__(self, sheet_names: Optional[List[str]] = None, visible_only: bool = True):
        """
        Initialize the XLSX processor.

        Args:
            sheet_names: Optional list of specific sheet names to process
            visible_only: If True, only visible sheets will be processed
        """
        self.sheet_names = sheet_names
        self.visible_only = visible_only
        self._html_converter = HtmlConverter()
        logger.info("Initialized XlsxProcessor")
    
    def load(
        self,
        file_content: bytes | BinaryIO,
        clean_data: bool = True
    ) -> Dict[str, pd.DataFrame]:
        """Load an Excel file and return a dictionary of DataFrames for each sheet
    
        Args:
            file_content: The Excel file content as bytes or file-like object
            clean_data: If True, clean the data by removing empty rows and columns
    
        Returns:
            Dictionary of DataFrames for each sheet
        """
        try:
            # Create a file-like object from bytes content if needed
            if isinstance(file_content, bytes):
                binary_content = io.BytesIO(file_content)
            else:
                # Make a copy of the file-like object to avoid modifying the original
                binary_content = io.BytesIO(file_content.read())
                file_content.seek(0)  # Reset the original file pointer
    
            # If visible_only is True, we need to check sheet visibility using openpyxl
            visible_sheet_names = None
            if self.visible_only:
                visible_sheet_names = _get_visible_sheets(binary_content)
    
            # If sheet_names is provided, use it to filter the visible sheets
            sheets_to_load = self.sheet_names
            if self.visible_only and visible_sheet_names:
                if self.sheet_names:
                    # Filter sheet_names to only include visible sheets
                    sheets_to_load = [name for name in self.sheet_names if name in visible_sheet_names]
                else:
                    sheets_to_load = visible_sheet_names
    
            # Read sheets as dict of DataFrames
            sheets = pd.read_excel(
                binary_content,
                engine="openpyxl",
                sheet_name=sheets_to_load,  # None means all sheets, or list of visible sheets
                keep_default_na=True,  # Changed to True to properly detect NaN values
                na_filter=True,        # Changed to True to properly detect NaN values
            )
    
            # Process all sheets in a single pass with all transformations
            processed_sheets = {}
            for sheet_name, df in sheets.items():
                # Apply transformations in a pipeline to avoid multiple iterations
                # 1. Replace NaN values with empty strings
                # 2. Normalize column names
                # 3. Clean data if requested
                df = _normalize_column_names(_replace_nan_with_empty(df))
    
                if clean_data:
                    df = _clean_dataframe(df)
    
                processed_sheets[sheet_name] = df
    
            return processed_sheets
        except Exception as e:
            logger.error(f"Failed to load Excel file: {str(e)}")
            raise e
    
    def convert(
        self,
        sheets: Dict[str, pd.DataFrame],
        **kwargs: Any
    ) -> str:
        """
        Convert Excel sheets to markdown format.
        
        Args:
            sheets: Dictionary of sheet names to DataFrames
            **kwargs: Additional options to pass to the HTML converter
            
        Returns:
            Markdown string representation of the Excel sheets
        """
        logger.debug(f"Converting {len(sheets)} sheets to markdown: {sheets.keys()}")
        
        md_content = ""
        for sheet_name, df in sheets.items():
            md_content += f"## {sheet_name}\n"
            html_content = df.to_html(index=False)
            md_content += (
                self._html_converter.convert_string(
                    html_content, **kwargs
                ).markdown.strip()
                + "\n\n"
            )
        
        return md_content.strip()