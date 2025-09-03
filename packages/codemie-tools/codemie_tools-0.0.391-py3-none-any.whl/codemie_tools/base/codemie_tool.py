import logging
import traceback
from abc import abstractmethod
from typing import Any, Optional, Union

from langchain_core.tools import BaseTool
from langchain_core.tools.base import ToolException

from codemie_tools.base.errors import TruncatedOutputError
from codemie_tools.base.utils import get_encoding, sanitize_string
from codemie_tools.base.models import ToolOutputFormat

logger = logging.getLogger(__name__)



class CodeMieTool(BaseTool):
    base_name: Optional[str] = None
    handle_tool_error: bool = True
    tokens_size_limit: int = 30_000
    throw_truncated_error: bool = False
    truncate_message: str = "Tool output is truncated, make more lightweight query."
    base_llm_model_name: str = "gpt-4.1-mini"
    output_format: ToolOutputFormat = ToolOutputFormat.TEXT

    def _parse_input(
        self, tool_input: Union[str, dict], tool_call_id: Optional[str]
    ) -> Union[str, dict[str, Any]]:
        """Override _parse_input to catch all exceptions and raise ToolException.
        
        Args:
            tool_input: The input to the tool.
            tool_call_id: The id of the tool call.
            
        Returns:
            The parsed input.
            
        Raises:
            ToolException: If any exception occurs during input parsing.
        """
        try:
            return super()._parse_input(tool_input, tool_call_id)
        except Exception as e:
            error_message = f"Error parsing tool input in {self.name}: {str(e)}"
            logger.error(error_message)
            raise ToolException(error_message) from e

    def _run(self, *args, **kwargs):
        try:
            result = self.execute(*args, **kwargs)
            output, _ = self._limit_output_content(result)
            return self._post_process_output_content(output,*args, **kwargs)
        except Exception as ex:
            stacktrace = sanitize_string(traceback.format_exc())
            error_message = (f"Error calling tool: {self.name} with: \n"
                             f"Arguments: {kwargs}. \n"
                             f"The root cause is: '{str(ex)}'")
            logger.error(f"{error_message}. Error stacktrace: {stacktrace}")
            raise ToolException(error_message) from ex

    @abstractmethod
    def execute(self, *args, **kwargs) -> Any:
        pass

    def calculate_tokens_count(self, output: Any) -> int:
        encoding = get_encoding(self.base_llm_model_name)

        tokens = encoding.encode(str(output))
        return len(tokens)

    def _limit_output_content(self, output: Any) -> Any:
        """
        Limit the size of the output based on token constraints.

        Args:
            output (Any): The content to be processed and potentially truncated.

        Returns:
            Tuple[Any, int]: The (possibly truncated) output and the token count.

        Raises:
            TruncatedOutputError: If the output exceeds the token size limit and throwing errors is enabled.
        """
        encoding = get_encoding(self.base_llm_model_name)

        tokens = encoding.encode(str(output))
        token_count = len(tokens)

        logger.info(f"{self.name}: Tokens size of potential response: {token_count}")

        if token_count <= self.tokens_size_limit:
            return output, token_count

        # Output exceeds token limit: calculate truncation details
        truncate_ratio = self.tokens_size_limit / token_count
        truncated_data = encoding.decode(tokens[:self.tokens_size_limit])
        truncated_output = (
            f"{self.truncate_message} "
            f"Ratio limit/used_tokens: {truncate_ratio}. Tool output: {truncated_data}"
        )
        error_message = (
            f"{self.name} output is too long: {token_count} tokens. "
            f"Ratio limit/used_tokens: {truncate_ratio} for output tokens {self.tokens_size_limit}"
        )

        logger.error(error_message)

        if self.throw_truncated_error:
            raise TruncatedOutputError(truncated_output)

        return truncated_output, token_count

    def _post_process_output_content(self, output: Any, *args, **kwargs) -> Any:
        return output
