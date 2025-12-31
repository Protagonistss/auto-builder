from fastapi import APIRouter, HTTPException, UploadFile, File, BackgroundTasks
from typing import List

from ..models.conversation import (
    CreateConversationRequest,
    CreateConversationResponse,
    SendMessageRequest,
    ChatResponse,
    ConversationDetail,
    Conversation,
    FileUploadResponse,
    MessageTask,
    MessageTaskSubmitResponse,
)
from ..services.conversation_service import ConversationService

router = APIRouter(prefix="/conversations", tags=["对话管理"])
conversation_service = ConversationService()


@router.post(
    "/",
    response_model=CreateConversationResponse,
    summary="创建会话",
    description="创建一个新的对话会话"
)
async def create_conversation(request: CreateConversationRequest):
    """
    创建新会话

    - **title**: 会话标题（1-200字符）
    """
    conversation = conversation_service.create_conversation(request.title)

    return CreateConversationResponse(
        conversation_id=conversation.id,
        title=conversation.title
    )


@router.post(
    "/{conversation_id}/upload",
    response_model=FileUploadResponse,
    summary="上传文件",
    description="上传文件到会话，支持多文件上传"
)
async def upload_file(
    conversation_id: str,
    files: List[UploadFile] = File(..., description="要上传的文件")
):
    """
    上传文件到会话

    - **conversation_id**: 会话ID
    - **files**: 一个或多个文件
    - 支持的文件类型: JSON, TXT, PDF, 图片等
    - 文件大小限制: 10MB
    """
    # 验证会话存在
    conversation = conversation_service.get_conversation(conversation_id)
    if not conversation:
        raise HTTPException(status_code=404, detail="会话不存在")

    # 上传文件（返回第一个文件的结果）
    file_info = await conversation_service.upload_file(conversation_id, files[0])

    return FileUploadResponse(
        file_id=file_info.id,
        original_name=file_info.original_name,
        file_size=file_info.file_size
    )


@router.post(
    "/{conversation_id}/messages",
    response_model=MessageTaskSubmitResponse,
    summary="发送消息（异步）",
    description="发送消息，立即返回任务ID，后台异步处理"
)
async def send_message(
    conversation_id: str,
    request: SendMessageRequest,
    background_tasks: BackgroundTasks
):
    """
    发送消息到会话（异步处理）

    - **conversation_id**: 会话ID
    - **message**: 用户消息内容
    - **file_ids**: 关联的文件ID列表（可选）
    - 返回任务ID，需要轮询获取结果
    """
    task_id = conversation_service.submit_message_task(
        conversation_id=conversation_id,
        content=request.message,
        file_ids=request.file_ids,
        background_tasks=background_tasks
    )

    return MessageTaskSubmitResponse(task_id=task_id)


@router.get(
    "/tasks/{task_id}",
    response_model=MessageTask,
    summary="查询消息任务状态",
    description="查询消息任务的处理状态和结果"
)
async def get_message_task(
    task_id: str
):
    """
    查询消息任务

    - **task_id**: 任务ID
    - 返回任务状态和结果
    """
    task = conversation_service.get_message_task(task_id)

    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")

    return task


@router.get(
    "/{conversation_id}",
    response_model=ConversationDetail,
    summary="获取会话详情",
    description="获取会话及其所有消息和文件"
)
async def get_conversation(conversation_id: str):
    """
    获取会话详情

    - **conversation_id**: 会话ID
    - 返回会话信息、完整消息历史和文件列表
    """
    detail = conversation_service.get_conversation_detail(conversation_id)

    if not detail:
        raise HTTPException(status_code=404, detail="会话不存在")

    return detail


@router.get(
    "/",
    response_model=List[Conversation],
    summary="列出所有会话",
    description="获取当前所有会话列表"
)
async def list_conversations():
    """
    列出所有会话

    - 返回所有活跃会话的列表，按创建时间倒序
    """
    conversations = conversation_service.list_conversations()
    return conversations


@router.delete(
    "/{conversation_id}",
    summary="删除会话",
    description="删除会话及其所有消息和文件"
)
async def delete_conversation(conversation_id: str):
    """
    删除会话

    - **conversation_id**: 会话ID
    - 删除会话及其所有消息和文件（包括磁盘文件）
    """
    success = conversation_service.delete_conversation(conversation_id)

    if not success:
        raise HTTPException(status_code=404, detail="会话不存在")

    return {"message": "会话已删除"}
