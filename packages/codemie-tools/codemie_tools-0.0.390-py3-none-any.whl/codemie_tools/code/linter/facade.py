import logging
from typing import Tuple

from codemie_tools.code.linter.impl.python import PythonLinter

logger = logging.getLogger(__name__)


class LinterFacade:
    PYTHON_LINTER_ERROR_CODES: str = "E999,F821"

    def __init__(self):
        self.linters = {
            "python": PythonLinter(error_codes=self.PYTHON_LINTER_ERROR_CODES)
        }

    def lint_code(self, lang: str, old_content: str, content_candidate: str) -> Tuple[bool, str]:
        linter = self.linters.get(lang)
        if not linter:
            logger.info(f"Unsupported language: {lang}")
            return True, ""
        return linter.lint_code_diff(old_content, content_candidate)
