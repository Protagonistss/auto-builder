"""构建命令执行服务"""

import asyncio
import logging
import time
from typing import Optional

from .shell_service import ShellService

logger = logging.getLogger(__name__)


class BuildService:
    """构建命令执行服务"""

    def __init__(self):
        self.shell_service = ShellService()

    async def execute_build(
        self,
        command: str,
        cwd: Optional[str] = None,
        timeout: int = 300
    ) -> dict:
        """
        执行构建命令

        Args:
            command: 构建命令
            cwd: 工作目录
            timeout: 超时时间（秒）

        Returns:
            dict: 包含执行结果的字典
        """
        start_time = time.time()

        try:
            # 执行命令
            stdout = await self.shell_service.run_command(
                command=command,
                cwd=cwd,
                timeout=timeout
            )

            execution_time = time.time() - start_time

            return {
                "success": True,
                "command": command,
                "exit_code": 0,
                "stdout": stdout,
                "stderr": "",
                "execution_time": execution_time,
                "message": "构建成功"
            }

        except RuntimeError as e:
            execution_time = time.time() - start_time
            error_msg = str(e)

            # 解析错误信息
            stderr = ""
            if "Stderr:" in error_msg:
                parts = error_msg.split("Stderr:")
                stderr = parts[1].split("\n")[0] if len(parts) > 1 else ""

            return {
                "success": False,
                "command": command,
                "exit_code": -1,
                "stdout": "",
                "stderr": stderr,
                "execution_time": execution_time,
                "message": f"构建失败: {error_msg}"
            }

        except asyncio.TimeoutError:
            execution_time = time.time() - start_time
            return {
                "success": False,
                "command": command,
                "exit_code": -1,
                "stdout": "",
                "stderr": f"命令执行超时（{timeout}秒）",
                "execution_time": execution_time,
                "message": f"构建超时（超过 {timeout} 秒）"
            }

        except Exception as e:
            execution_time = time.time() - start_time
            logger.error(f"构建执行异常: {str(e)}")
            return {
                "success": False,
                "command": command,
                "exit_code": -1,
                "stdout": "",
                "stderr": str(e),
                "execution_time": execution_time,
                "message": f"构建异常: {str(e)}"
            }
