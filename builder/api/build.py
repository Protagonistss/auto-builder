"""构建命令执行 API"""

import json
import time
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from ..models.task import BuildCommandRequest, BuildCommandResponse
from ..services.shell_service import ShellService
from ..config import settings

router = APIRouter()
shell_service = ShellService()


@router.post(
    "/execute",
    response_model=BuildCommandResponse,
    summary="执行构建命令",
    description="异步执行 Maven/npm/Gradle 等构建命令并返回结果（非流式）"
)
async def execute_build(request: BuildCommandRequest):
    """
    执行构建命令（非流式）

    支持的构建类型：
    - **maven**: Maven 命令（如 'mvn clean install'）
    - **npm**: npm 命令（如 'npm run build'）
    - **gradle**: Gradle 命令（如 'gradle build'）
    - **custom**: 自定义命令

    参数：
    - **command**: 构建命令字符串
    - **cwd**: 工作目录（可选，默认为项目根目录）
    - **timeout**: 超时时间（秒），默认 300 秒
    - **command_type**: 命令类型标识
    """
    # 安全验证：防止命令注入
    _validate_command(request.command)

    # 设置默认工作目录
    cwd = request.cwd or settings.project_root

    # 执行构建（收集所有输出）
    start_time = time.time()
    output_lines = []

    try:
        async for line in shell_service.run_command_stream(
            command=request.command,
            cwd=cwd,
            timeout=request.timeout
        ):
            output_lines.append(line)

        execution_time = time.time() - start_time

        return BuildCommandResponse(
            success=True,
            command=request.command,
            exit_code=0,
            stdout='\n'.join(output_lines),
            stderr="",
            execution_time=execution_time,
            message="构建成功"
        )

    except Exception as e:
        execution_time = time.time() - start_time
        return BuildCommandResponse(
            success=False,
            command=request.command,
            exit_code=-1,
            stdout="",
            stderr=str(e),
            execution_time=execution_time,
            message=f"构建失败: {str(e)}"
        )


@router.post(
    "/execute/stream",
    summary="流式执行构建命令",
    description="流式执行 Maven/npm/Gradle 等构建命令，通过 SSE 实时返回输出"
)
async def execute_build_stream(request: BuildCommandRequest):
    """
    流式执行构建命令（SSE）

    返回 Server-Sent Events 格式的流式数据：
    - data: {"type": "log", "line": "输出行"}
    - data: {"type": "complete", "success": true/false, "message": "..."}

    参数：
    - **command**: 构建命令字符串
    - **cwd**: 工作目录（可选，默认为项目根目录）
    - **timeout**: 超时时间（秒），默认 300 秒
    - **command_type**: 命令类型标识
    """
    # 安全验证：防止命令注入
    _validate_command(request.command)

    # 设置默认工作目录
    cwd = request.cwd or settings.project_root

    async def event_generator():
        """SSE 事件生成器"""
        try:
            async for line in shell_service.run_command_stream(
                command=request.command,
                cwd=cwd,
                timeout=request.timeout
            ):
                # 发送日志行
                yield f"data: {json.dumps({'type': 'log', 'line': line}, ensure_ascii=False)}\n\n"

            # 发送完成事件
            yield f"data: {json.dumps({'type': 'complete', 'success': True, 'message': '构建成功'}, ensure_ascii=False)}\n\n"

        except Exception as e:
            # 发送错误事件
            yield f"data: {json.dumps({'type': 'complete', 'success': False, 'message': str(e)}, ensure_ascii=False)}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )


def _validate_command(command: str) -> None:
    """
    验证命令安全性，防止命令注入

    Args:
        command: 命令字符串

    Raises:
        HTTPException: 命令不安全时抛出
    """
    # 危险字符黑名单
    dangerous_chars = ['|', '&', ';', '$', '`', '(', ')', '<', '>']

    for char in dangerous_chars:
        if char in command:
            raise HTTPException(
                status_code=400,
                detail=f"命令包含非法字符: {char}，可能存在命令注入风险"
            )
