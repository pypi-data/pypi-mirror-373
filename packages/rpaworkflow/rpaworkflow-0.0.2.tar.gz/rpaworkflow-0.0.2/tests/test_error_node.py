import pytest
from typing import Dict, Any, Optional

from rpaworkflow.nodes.error import ErrorNode, ErrorStorageNode
from rpaworkflow.node import NodeStatus, NodeException
from rpaworkflow.context import WorkflowContext, create_workflow_context
from rpaworkflow.exception import NodeError


def test_error_node_initialization_with_error_message():
    """测试使用错误消息初始化ErrorNode"""
    # 创建错误节点，使用字符串错误消息
    error_node = ErrorNode(
        name="错误节点",
        description="测试错误节点",
        error="测试错误消息"
    )
    
    # 验证初始化
    assert error_node.name == "错误节点"
    assert error_node.description == "测试错误节点"
    assert error_node.error == "测试错误消息"


def test_error_node_initialization_with_exception():
    """测试使用异常对象初始化ErrorNode"""
    # 创建异常对象
    test_exception = ValueError("测试异常")
    
    # 创建错误节点，使用异常对象
    error_node = ErrorNode(
        name="异常节点",
        description="测试异常节点",
        error=test_exception
    )
    
    # 验证初始化
    assert error_node.name == "异常节点"
    assert error_node.description == "测试异常节点"
    assert error_node.error == test_exception


def test_error_node_execution_with_error_message():
    """测试使用错误消息的ErrorNode执行"""
    # 创建错误节点，使用字符串错误消息
    error_node = ErrorNode(
        name="错误节点",
        error="测试错误消息"
    )
    
    # 创建上下文
    context = create_workflow_context(
        workflow_id="test-id",
        workflow_name="测试工作流",
        execution_id="exec-id"
    )
    
    # 执行错误节点，应该失败并记录错误
    status = error_node.run(context)
    
    # 验证结果
    assert status == NodeStatus.FAILED
    assert error_node.last_error is not None
    assert "测试错误消息" in error_node.last_error


def test_error_node_execution_with_exception():
    """测试使用异常对象的ErrorNode执行"""
    # 创建异常对象
    test_exception = ValueError("测试异常")
    
    # 创建错误节点，使用异常对象
    error_node = ErrorNode(
        name="异常节点",
        error=test_exception
    )
    
    # 创建上下文
    context = create_workflow_context(
        workflow_id="test-id",
        workflow_name="测试工作流",
        execution_id="exec-id"
    )
    
    # 执行错误节点，应该失败并记录错误
    status = error_node.run(context)
    
    # 验证结果
    assert status == NodeStatus.FAILED
    assert error_node.last_error is not None
    assert "测试异常" in error_node.last_error


def test_error_node_without_error():
    """测试没有设置错误的ErrorNode"""
    # 创建错误节点，不设置错误
    error_node = ErrorNode(
        name="无错误节点"
    )
    
    # 创建上下文
    context = create_workflow_context(
        workflow_id="test-id",
        workflow_name="测试工作流",
        execution_id="exec-id"
    )
    
    # 执行错误节点，应该失败并记录错误
    status = error_node.run(context)
    
    # 验证结果
    assert status == NodeStatus.FAILED
    assert error_node.last_error is not None
    assert "错误节点错误信息不能为空" in error_node.last_error


def test_error_storage_node_initialization_with_error_message():
    """测试使用错误消息初始化ErrorStorageNode"""
    # 创建错误存储节点，使用字符串错误消息
    error_node = ErrorStorageNode(
        name="错误存储节点",
        description="测试错误存储节点",
        output_key="stored_error",
        error="测试错误消息"
    )
    
    # 验证初始化
    assert error_node.name == "错误存储节点"
    assert error_node.description == "测试错误存储节点"
    assert error_node.output_key == "stored_error"
    assert error_node.error == "测试错误消息"


def test_error_storage_node_initialization_with_exception():
    """测试使用异常对象初始化ErrorStorageNode"""
    # 创建异常对象
    test_exception = ValueError("测试异常")
    
    # 创建错误存储节点，使用异常对象
    error_node = ErrorStorageNode(
        name="异常存储节点",
        description="测试异常存储节点",
        output_key="stored_exception",
        error=test_exception
    )
    
    # 验证初始化
    assert error_node.name == "异常存储节点"
    assert error_node.description == "测试异常存储节点"
    assert error_node.output_key == "stored_exception"
    assert error_node.error == test_exception


def test_error_storage_node_execution_with_error_message():
    """测试使用错误消息的ErrorStorageNode执行"""
    # 创建错误存储节点，使用字符串错误消息
    error_node = ErrorStorageNode(
        name="错误存储节点",
        output_key="stored_error",
        error="测试错误消息"
    )
    
    # 创建上下文
    context = create_workflow_context(
        workflow_id="test-id",
        workflow_name="测试工作流",
        execution_id="exec-id"
    )
    
    # 执行错误存储节点，应该失败并记录错误
    status = error_node.run(context)
    
    # 验证结果
    assert status == NodeStatus.FAILED
    assert error_node.last_error is not None
    assert "测试错误消息" in error_node.last_error
    assert "stored_error" in context
    assert isinstance(context["stored_error"], NodeError)
    assert "测试错误消息" in str(context["stored_error"])


def test_error_storage_node_execution_with_exception():
    """测试使用异常对象的ErrorStorageNode执行"""
    # 创建异常对象
    exception = ValueError("测试异常")
    
    # 创建错误存储节点，使用异常对象
    error_node = ErrorStorageNode(
        name="异常存储节点",
        output_key="stored_exception",
        error=exception
    )
    
    # 创建上下文
    context = create_workflow_context(
        workflow_id="test-id",
        workflow_name="测试工作流",
        execution_id="exec-id"
    )
    
    # 执行错误存储节点，应该失败并记录错误
    status = error_node.run(context)
    
    # 验证结果
    assert status == NodeStatus.FAILED
    assert error_node.last_error is not None
    assert "测试异常" in error_node.last_error
    assert "stored_exception" in context
    assert context["stored_exception"] is exception


def test_error_storage_node_without_error():
    """测试未设置错误的ErrorStorageNode"""
    # 创建错误存储节点，不设置错误
    error_node = ErrorStorageNode(
        name="错误存储节点",
        output_key="stored_error"
    )
    
    # 创建上下文
    context = create_workflow_context(
        workflow_id="test-id",
        workflow_name="测试工作流",
        execution_id="exec-id"
    )
    
    # 执行错误存储节点，应该失败并记录错误
    status = error_node.run(context)
    
    # 验证结果
    assert status == NodeStatus.FAILED
    assert error_node.last_error is not None
    assert "错误信息不能为空" in error_node.last_error