import re
from pydantic import ValidationError

from codemie_tools.base.codemie_tool import logger


def humanize_error(error: Exception) -> str:
    """
    If an error is a Pyndatic ValidationError, return a human-readable string
    Otherwise, return the string representation of the error.
    """
    if not isinstance(error, ValidationError):
        return str(error)
      
    try:
      return ", ".join([
        f"{_format_pydantic_validation_loc(item['loc'])}: {item['msg'].lower()}"
        for item in error.errors()
      ]).capitalize()
    except Exception:
        logger.error("Error formatting Pydantic ValidationError", exc_info=True)
        return str(error)
    
def _format_pydantic_validation_loc(items): 
  """Humanize the location field of a Pydantic validation error"""
  return ".".join(str(loc) for loc in items)


def normalize_filename(filename: str) -> str:
    """
    Normalize a filename by replacing all special characters with underscores.
    Consecutive underscores are replaced with a single underscore.
    Periods are also replaced with underscores.

    Args:
        filename (str): The original filename

    Returns:
        str: Normalized filename with special characters replaced by underscores

    Examples:
        >>> normalize_filename('test (1).csv')
        'test_1_csv'
        >>> normalize_filename('file with..multiple...periods')
        'file_with_multiple_periods'
    """
    # Replace all special characters (non-alphanumeric) with underscores
    normalized = re.sub(r'\W', '_', filename)
    # Replace consecutive underscores with a single one
    normalized = re.sub(r'_+', '_', normalized)
    return normalized