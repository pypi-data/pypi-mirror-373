#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
工作流上下文定义
"""

from datetime import datetime
from typing import TypedDict, Any, Dict, Optional, List, TypeVar, Type


class WorkflowContext(TypedDict, total=False):
    """工作流上下文类型定义

    使用TypedDict提供类型提示，同时保持字典的灵活性
    total=False表示所有字段都是可选的
    """

    # === 基础信息 ===
    workflow_id: str  # 工作流ID
    workflow_name: str  # 工作流名称
    execution_id: str  # 执行ID
    start_time: datetime  # 开始时间
    current_node: str  # 当前执行的节点名称
    error: Exception # error节点异常对象
    loop_counts: dict # 循环次数统计


CONTEXT = TypeVar('CONTEXT', bound=WorkflowContext)


class NodeExecutionInfo(TypedDict):
    """节点执行信息"""
    node_name: str
    start_time: datetime
    end_time: Optional[datetime]
    status: str
    error: Optional[str]
    execution_time: Optional[float]
    retry_count: int


class WorkflowExecutionInfo(TypedDict):
    """工作流执行信息"""
    workflow_id: str
    execution_id: str
    start_time: datetime
    end_time: Optional[datetime]
    status: str
    total_nodes: int
    completed_nodes: int
    failed_nodes: int
    node_executions: List[NodeExecutionInfo]


def create_workflow_context(
    workflow_id: str,
    workflow_name: str,
    execution_id: str,
    ctx_cls: Type[CONTEXT] = WorkflowContext,
    **kwargs
) -> WorkflowContext:
    """创建工作流上下文

    Args:
        ctx_cls: 上下文类型
        workflow_id: 工作流ID
        workflow_name: 工作流名称
        execution_id: 执行ID
        **kwargs: 其他初始化参数

    Returns:
        WorkflowContext: 初始化的工作流上下文
    """
    context: CONTEXT = ctx_cls(**{
        'workflow_id': workflow_id,
        'workflow_name': workflow_name,
        'execution_id': execution_id,
        'start_time': datetime.now(),
    })

    # 添加额外的初始化参数
    context.update(kwargs)

    return context


def get_context_value(context: WorkflowContext, key: str, default: Any = None) -> Any:
    """安全获取上下文值

    Args:
        context: 工作流上下文
        key: 键名
        default: 默认值

    Returns:
        Any: 上下文值
    """
    return context.get(key, default)  # type: ignore


def set_context_value(context: WorkflowContext, key: str, value: Any) -> None:
    """设置上下文值

    Args:
        context: 工作流上下文
        key: 键名
        value: 值
    """
    context[key] = value  # type: ignore


def update_context(context: WorkflowContext, updates: Dict[str, Any]) -> None:
    """批量更新上下文

    Args:
        context: 工作流上下文
        updates: 更新的键值对
    """
    context.update(updates)
