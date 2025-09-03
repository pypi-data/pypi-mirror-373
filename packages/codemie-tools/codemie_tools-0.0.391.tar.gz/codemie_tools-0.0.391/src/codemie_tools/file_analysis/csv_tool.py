import logging
from io import StringIO
from typing import Type, Optional, Dict, Any, Tuple, Union

import clevercsv
import pandas as pd
from pydantic import BaseModel, Field

from codemie_tools.base.codemie_tool import CodeMieTool
from codemie_tools.base.constants import SOURCE_DOCUMENT_KEY, SOURCE_FIELD_KEY, FILE_CONTENT_FIELD_KEY
from codemie_tools.base.file_object import FileObject
from codemie_tools.file_analysis.tool_vars import CSV_TOOL

logger = logging.getLogger(__name__)

def get_csv_delimiter(data: str, length_to_sniff: int) -> str:
    """ Get the delimiter of the CSV file. """
    dialect = clevercsv.Sniffer().sniff(data[:length_to_sniff])
    return dialect.delimiter


class Input(BaseModel):
    method_name: str = Field(
        description="Method to be called on the pandas dataframe object generated from the file"
    )
    method_args: dict = Field(
        description="Pandas dataframe arguments to be passed to the method",
        default={}
    )
    column: Optional[str] = Field(
        description="Column to be used for the operation",
        default=None
    )


class CSVTool(CodeMieTool):
    """ Tool for working with data from CSV files. """
    args_schema: Type[BaseModel] = Input
    name: str = CSV_TOOL.name
    label: str = CSV_TOOL.label
    description: str = CSV_TOOL.description
    files: list[FileObject] = Field(exclude=True)

    @staticmethod
    def _process_single_csv(
            file_object: FileObject,
            method_name: str,
            method_args: Dict[str, Any],
            column: Optional[str] = None) -> Tuple[str, Union[str, pd.DataFrame]]:
        """Process a single CSV file and return its processed content"""
        try:
            data = file_object.string_content()
            df = pd.read_csv(StringIO(data), sep=get_csv_delimiter(data, 128), on_bad_lines='skip')
            logger.debug(
                f"Processing CSV file '{file_object.name}'. "
                         f"MethodName: {method_name}, "
                         f"MethodArgs:{method_args}. "
                         f"Column: {column}. "
                         f"DataFrame: {df}")
            if column:
                if column not in df.columns:
                    return file_object.name, f"Error: Column '{column}' not found in file {file_object.name}"
                col = df[column]
                result = getattr(col, method_name)
            else:
                result = getattr(df, method_name)

            if len(method_args):
                result = result(**method_args)
            else:
                result = result()

            result = str(result)
            logger.debug(f"Processing CSV '{file_object.name}' completed. Result: {result}")
            return file_object.name, result
        except Exception as e:
            return file_object.name, f"Error processing {file_object.name}: {str(e)}"

    def execute(self, method_name: str, method_args=None, column: Optional[str] = None):
        if method_args is None:
            method_args = {}
        if not self.files:
            raise ValueError(f"{self.name} requires at least one file to process.")

        # Process multiple files with formatted output for each
        result = []
        for file_object in self.files:
            _, file_content = self._process_single_csv(file_object, method_name, method_args, column)
            result.append(f"\n{SOURCE_DOCUMENT_KEY}\n")
            result.append(f"{SOURCE_FIELD_KEY} {file_object.name}\n")
            result.append(f"{FILE_CONTENT_FIELD_KEY} \n{file_content}\n")

        return "\n\n".join(result)
