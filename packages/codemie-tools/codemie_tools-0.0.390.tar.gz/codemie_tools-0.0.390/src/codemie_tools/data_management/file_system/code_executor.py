import asyncio
import base64
import logging
import os
import shutil
import sys
import uuid
from pathlib import Path
from typing import Any

import aiohttp
from codeboxapi.box import LocalBox
from codeboxapi.schema import CodeBoxStatus

logger = logging.getLogger(__name__)

class CodeExecutor:
    """
    The CodeExecutor class abstracts communication with code interpreters and runtimes.
    It currently supports executing Python code, with potential to expand for other languages in the future.
    """
    file_repository: Any = None

    def __init__(self, file_repository: Any):
        """
        Initializes the CodeExecutor instance.
        """
        self.file_repository = file_repository

    def execute_python(self, code: str, user_id: str):
        return self._execute_code(code=code, user_id=user_id, language='python')

    def _execute_code(self, code: str, user_id: str, language):
        """
        Executes code in the specified language.

        Parameters:
        - code (str): The code snippet to be executed.
        - language (str): The programming language of the code.

        Returns:
        The result of the code execution if the language is supported.

        Raises:
        - UnsupportedLanguageException: If the specified language is not supported.
        """
        if language.lower() == 'python':
            return asyncio.run(self._run_in_sandbox(code, user_id))
        else:
            raise UnsupportedLanguageException(f'{language} language is not supported. Only Python is supported.')

    async def _run_in_sandbox(self, code: str, user_id: str):
        async with CodemieBox() as codebox:
            output = await codebox.arun(code)

            if output.type == 'image/png':
                if self.file_repository:
                    stored_file = self.file_repository.write_file(
                        name=f"{uuid.uuid4()}.png",
                        mime_type=output.type,
                        content=base64.b64decode(output.content),
                        owner=user_id)
                    return f"This 'sandbox:/v1/files/{stored_file.to_encoded_url()}' is image URL. You MUST not transform it. Return as it is"
                else:
                    return f"This 'sandbox:/v1/files/{output.content}' is image URL. You MUST not transform it. Return as it is"
            else:
                return output


class UnsupportedLanguageException(Exception):
    """
    Custom exception class for handling unsupported languages in CodeExecutor.

    Attributes:
    - message (str): Explanation of the error.
    """
    pass


class CodemieBox(LocalBox):
    parent_temp_dir: str

    def __init__(self, parent_temp_dir: str = "."):
        super().__init__()
        self.parent_temp_dir = parent_temp_dir

    def _get_temp_dir(self):
        return f"{self.parent_temp_dir}/.codemiebox/{self.session_id}"

    async def astart(self) -> CodeBoxStatus:
        self.session_id = uuid.uuid4()
        code_temp_dir = self._get_temp_dir()
        logger.debug(f"Starting CodemieBox. Creating temp dir {code_temp_dir}")
        os.makedirs(code_temp_dir, exist_ok=True)

        await self._acheck_port()
        out = asyncio.subprocess.PIPE
        self._check_installed()
        python = Path(sys.executable).absolute()

        self.jupyter = await asyncio.create_subprocess_exec(
            python,
            "-m",
            "jupyter",
            "kernelgateway",
            "--KernelGatewayApp.ip='0.0.0.0'",
            f"--KernelGatewayApp.port={self.port}",
            stdout=out,
            stderr=out,
            cwd=code_temp_dir,
        )
        self._jupyter_pids.append(self.jupyter.pid)

        while True:
            try:
                response = await self.aiohttp_session.get(self.kernel_url)
                if response.status == 200:
                    break
            except aiohttp.ClientConnectorError:
                pass
            except aiohttp.ServerDisconnectedError:
                pass
            await asyncio.sleep(1)
        await self._aconnect()
        return CodeBoxStatus(status="started")

    async def astop(self) -> CodeBoxStatus:
        result = await super().astop()
        code_temp_dir = self._get_temp_dir()
        logger.debug(f"Stopping CodemieBox. Destroying temp dir {code_temp_dir}")
        shutil.rmtree(code_temp_dir)
        return result
