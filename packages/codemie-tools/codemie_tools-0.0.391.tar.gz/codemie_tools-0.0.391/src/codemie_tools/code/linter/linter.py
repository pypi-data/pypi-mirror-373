from abc import ABC, abstractmethod
from typing import Tuple, Dict


class Linter(ABC):
    """
    Abstract base class for a code linter.
    """

    @abstractmethod
    def lint_code_diff(self, old_content: str, new_content: str) -> Tuple[bool, str]:
        """
        Lint the given code content.

        :param old_content: The original content of the code.
        :param new_content: The new content of the code to be linted.
        :return: A tuple where the first element is a boolean indicating if the linting passed,
                 and the second element is a string with the linting result or error message.
        """
        pass

    @staticmethod
    def get_changed_lines(old_content: str, new_content: str) -> Dict[int, str]:
        old_lines = old_content.splitlines()
        new_lines = new_content.splitlines()

        max_lines = max(len(old_lines), len(new_lines))

        changed_lines = {
            i + 1: new_lines[i] if i < len(new_lines) else ""
            for i in range(max_lines)
            if (i < len(old_lines) and old_lines[i] != new_lines[i]) or (i >= len(old_lines))
        }

        return changed_lines
