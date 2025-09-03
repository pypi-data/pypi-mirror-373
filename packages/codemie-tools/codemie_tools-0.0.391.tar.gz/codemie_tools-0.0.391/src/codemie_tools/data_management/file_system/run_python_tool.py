import functools
import logging
from typing import Type, Optional
from pydantic import BaseModel, Field

from codemie_tools.base.codemie_tool import CodeMieTool
from codemie_tools.data_management.file_system.code_executor import CodeExecutor
from codemie_tools.data_management.file_system.tools_vars import PYTHON_RUN_CODE_TOOL

logger = logging.getLogger(__name__)

@functools.lru_cache(maxsize=None)
def warn_once() -> None:
    """Warn once about the dangers of PythonREPL."""
    logger.warning("Python REPL can execute arbitrary code. Use with caution.")


class PythonRunCodeInput(BaseModel):
    python_script: str = Field(
        description="""
        You must send the whole script every time and print your outputs. 
        Script should be pure python code that can be evaluated. It should be in python format NOT markdown. 
        The code should NOT be wrapped in backticks. 
        All python packages including requests, matplotlib, scipy, numpy, pandas, etc are available. 
        If you have any files outputted write them to current dir.
        If you need to generate plot always use matplotlib. Follow example below and never use plt.savefig():
        # Plot the data
        plt.figure(figsize=(12, 6))
        plt.plot(data["Date"], data["USD_to_EUR"], label="USD to EUR")
        plt.xlabel("Date")
        plt.ylabel("Exchange Rate (USD to EUR)")
        plt.title("USD to EUR Exchange Rate Over the Past Year (Fake Data)")
        plt.legend()
        plt.grid(True)
        plt.show()
        """.strip())


class PythonRunCodeTool(CodeMieTool):
    name: str = PYTHON_RUN_CODE_TOOL.name
    tokens_size_limit: int = 30000
    description: str = PYTHON_RUN_CODE_TOOL.description
    args_schema: Type[BaseModel] = PythonRunCodeInput
    code_executor: CodeExecutor
    user_id: Optional[str] = "test"

    def execute(self, python_script: str):
        logger.info(f"Python script: {python_script}")
        result = self.code_executor.execute_python(code=python_script, user_id=self.user_id)
        logger.info(f"Python script execution result: {result}")
        return result
