import pytest
from typing import Dict, Any, Optional

from rpaworkflow.nodes.error import ErrorNode, ErrorStorageNode
from rpaworkflow.node import NodeStatus, WorkflowNode, NodeException
from rpaworkflow.context import WorkflowContext, create_workflow_context
from rpaworkflow.exception import NodeError


# 创建测试用的节点类
class TestNode(WorkflowNode[WorkflowContext]):
    """用于测试的节点实现"""
    
    def __init__(self, name="测试节点", should_fail=False, error_message="测试异常", **kwargs):
        super().__init__(name=name, **kwargs)
        self.should_fail = should_fail
        self.error_message = error_message
        self.execute_called = False
    
    def execute(self, context: WorkflowContext) -> None:
        self.execute_called = True
        
        # 根据配置决定是否失败
        if self.should_fail:
            raise ValueError(self.error_message)


# 测试用例
def test_error_node_initialization():
    """测试错误节点初始化"""
    # 创建错误处理函数
    def error_handler(exception_info: NodeException, context: WorkflowContext) -> None:
        context["error_handled"] = True
        context["error_message"] = exception_info.error_message
    
    # 创建错误节点
    error_node = ErrorNode(
        name="错误节点",
        description="测试错误节点",
        error_handler=error_handler
    )
    
    # 验证初始化
    assert error_node.name == "错误节点"
    assert error_node.description == "测试错误节点"
    assert error_node.error_handler == error_handler


def test_error_node_execution():
    """测试错误节点执行"""
    # 创建错误处理函数
    def error_handler(exception_info: NodeException, context: WorkflowContext) -> None:
        context["error_handled"] = True
        context["error_message"] = exception_info.error_message
        context["error_node"] = exception_info.node_name
    
    # 创建错误节点
    error_node = ErrorNode(
        name="错误节点",
        error_handler=error_handler
    )
    
    # 创建上下文和异常信息
    context = create_workflow_context(
        workflow_id="test-id",
        workflow_name="测试工作流",
        execution_id="exec-id"
    )
    
    exception_info = NodeException(
        node_name="测试节点",
        error_message="测试异常",
        error_type="ValueError",
        traceback="测试追踪信息"
    )
    
    # 设置异常信息到上下文
    context["exception_info"] = exception_info
    
    # 执行错误节点
    status = error_node.run(context)
    
    # 验证结果
    assert status == NodeStatus.SUCCESS
    assert context.get("error_handled") is True
    assert context.get("error_message") == "测试异常"
    assert context.get("error_node") == "测试节点"


def test_error_node_without_exception_info():
    """测试错误节点在没有异常信息时的行为"""
    # 创建错误处理函数
    def error_handler(exception_info: NodeException, context: WorkflowContext) -> None:
        context["error_handled"] = True
    
    # 创建错误节点
    error_node = ErrorNode(
        name="错误节点",
        error_handler=error_handler
    )
    
    # 创建上下文，不设置异常信息
    context = create_workflow_context(
        workflow_id="test-id",
        workflow_name="测试工作流",
        execution_id="exec-id"
    )
    
    # 执行错误节点
    status = error_node.run(context)
    
    # 验证结果
    assert status == NodeStatus.SUCCESS
    assert "error_handled" not in context  # 没有异常信息，不应该调用处理函数


def test_error_node_without_handler():
    """测试错误节点在没有设置处理函数时的行为"""
    # 创建错误节点，不设置处理函数
    error_node = ErrorNode(name="错误节点")
    
    # 创建上下文和异常信息
    context = create_workflow_context(
        workflow_id="test-id",
        workflow_name="测试工作流",
        execution_id="exec-id"
    )
    
    exception_info = NodeException(
        node_name="测试节点",
        error_message="测试异常",
        error_type="ValueError",
        traceback="测试追踪信息"
    )
    
    # 设置异常信息到上下文
    context["exception_info"] = exception_info
    
    # 执行错误节点，应该抛出异常
    with pytest.raises(NodeError) as excinfo:
        error_node.run(context)
    
    # 验证异常信息
    assert "错误处理函数未设置" in str(excinfo.value)


def test_error_storage_node_initialization():
    """测试错误存储节点初始化"""
    # 创建错误存储节点
    error_storage_node = ErrorStorageNode(
        name="错误存储节点",
        description="测试错误存储节点",
        output_key="stored_error"
    )
    
    # 验证初始化
    assert error_storage_node.name == "错误存储节点"
    assert error_storage_node.description == "测试错误存储节点"
    assert error_storage_node.output_key == "stored_error"


def test_error_storage_node_execution():
    """测试错误存储节点执行"""
    # 创建错误存储节点
    error_storage_node = ErrorStorageNode(
        name="错误存储节点",
        output_key="stored_error"
    )
    
    # 创建上下文和异常信息
    context = create_workflow_context(
        workflow_id="test-id",
        workflow_name="测试工作流",
        execution_id="exec-id"
    )
    
    exception_info = NodeException(
        node_name="测试节点",
        error_message="测试异常",
        error_type="ValueError",
        traceback="测试追踪信息"
    )
    
    # 设置异常信息到上下文
    context["exception_info"] = exception_info
    
    # 执行错误存储节点
    status = error_storage_node.run(context)
    
    # 验证结果
    assert status == NodeStatus.SUCCESS
    assert context.get("stored_error") == exception_info


def test_error_storage_node_without_exception_info():
    """测试错误存储节点在没有异常信息时的行为"""
    # 创建错误存储节点
    error_storage_node = ErrorStorageNode(
        name="错误存储节点",
        output_key="stored_error"
    )
    
    # 创建上下文，不设置异常信息
    context = create_workflow_context(
        workflow_id="test-id",
        workflow_name="测试工作流",
        execution_id="exec-id"
    )
    
    # 执行错误存储节点
    status = error_storage_node.run(context)
    
    # 验证结果
    assert status == NodeStatus.SUCCESS
    assert context.get("stored_error") is None  # 没有异常信息，应该存储None


def test_error_node_integration():
    """测试错误节点与失败节点的集成"""
    # 创建一个会失败的节点
    failing_node = TestNode(
        name="失败节点",
        should_fail=True,
        error_message="集成测试异常"
    )
    
    # 创建错误处理函数
    handled_exceptions = []
    
    def error_handler(exception_info: NodeException, context: WorkflowContext) -> None:
        handled_exceptions.append(exception_info)
        context["error_handled"] = True
    
    # 创建错误节点
    error_node = ErrorNode(
        name="错误节点",
        error_handler=error_handler
    )
    
    # 创建上下文
    context = create_workflow_context(
        workflow_id="test-id",
        workflow_name="测试工作流",
        execution_id="exec-id"
    )
    
    # 执行失败节点
    failing_status = failing_node.run(context)
    
    # 验证失败节点结果
    assert failing_status == NodeStatus.FAILED
    assert failing_node.status == NodeStatus.FAILED
    assert "exception_info" in context
    
    # 执行错误节点
    error_status = error_node.run(context)
    
    # 验证错误节点结果
    assert error_status == NodeStatus.SUCCESS
    assert len(handled_exceptions) == 1
    assert handled_exceptions[0].node_name == "失败节点"
    assert handled_exceptions[0].error_message == "集成测试异常"
    assert handled_exceptions[0].error_type == "ValueError"
    assert context.get("error_handled") is True