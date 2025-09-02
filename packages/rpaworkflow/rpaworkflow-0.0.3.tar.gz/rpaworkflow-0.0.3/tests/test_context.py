import pytest
from datetime import datetime
from typing import Dict, Any

from rpaworkflow.context import (
    WorkflowContext, 
    create_workflow_context, 
    get_context_value,
    NodeExecutionInfo,
    WorkflowExecutionInfo
)


def test_create_workflow_context():
    """测试创建工作流上下文"""
    # 基本参数测试
    workflow_id = "test-workflow-id"
    workflow_name = "测试工作流"
    execution_id = "test-execution-id"
    
    context = create_workflow_context(
        workflow_id=workflow_id,
        workflow_name=workflow_name,
        execution_id=execution_id
    )
    
    assert context["workflow_id"] == workflow_id
    assert context["workflow_name"] == workflow_name
    assert context["execution_id"] == execution_id
    assert isinstance(context["start_time"], datetime)
    
    # 测试额外参数
    extra_data = {"key1": "value1", "key2": 123}
    context = create_workflow_context(
        workflow_id=workflow_id,
        workflow_name=workflow_name,
        execution_id=execution_id,
        **extra_data
    )
    
    assert context["key1"] == "value1"
    assert context["key2"] == 123


def test_get_context_value():
    """测试安全获取上下文值"""
    context: Dict[str, Any] = {
        "existing_key": "value",
        "zero_value": 0,
        "false_value": False,
        "none_value": None
    }
    
    # 测试存在的键
    assert get_context_value(context, "existing_key") == "value"
    
    # 测试不存在的键，使用默认值
    assert get_context_value(context, "non_existing_key", "default") == "default"
    
    # 测试不存在的键，不提供默认值
    assert get_context_value(context, "non_existing_key") is None
    
    # 测试特殊值
    assert get_context_value(context, "zero_value") == 0
    assert get_context_value(context, "false_value") is False
    assert get_context_value(context, "none_value") is None


def test_typed_dict_structures():
    """测试TypedDict结构"""
    # 测试NodeExecutionInfo
    node_info: NodeExecutionInfo = {
        "node_name": "测试节点",
        "start_time": datetime.now(),
        "end_time": datetime.now(),
        "status": "success",
        "error": None,
        "execution_time": 1.5,
        "retry_count": 0
    }
    
    assert node_info["node_name"] == "测试节点"
    assert isinstance(node_info["start_time"], datetime)
    assert node_info["status"] == "success"
    
    # 测试WorkflowExecutionInfo
    workflow_info: WorkflowExecutionInfo = {
        "workflow_id": "test-id",
        "execution_id": "exec-id",
        "start_time": datetime.now(),
        "end_time": datetime.now(),
        "status": "success",
        "total_nodes": 5,
        "completed_nodes": 5,
        "failed_nodes": 0,
        "node_executions": [node_info]
    }
    
    assert workflow_info["workflow_id"] == "test-id"
    assert workflow_info["total_nodes"] == 5
    assert len(workflow_info["node_executions"]) == 1