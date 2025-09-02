import pytest
import time
from datetime import datetime
from typing import Dict, Any, Optional

from rpaworkflow.node import (
    WorkflowNode, 
    NodeStatus, 
    NodeException,
    MergeWorkflowNode,
    DataStorageNode
)
from rpaworkflow.context import WorkflowContext, create_workflow_context
from rpaworkflow.exception import NodeError


# 创建测试用的节点类
class TestNode(WorkflowNode[WorkflowContext]):
    """用于测试的节点实现"""
    
    def __init__(self, name="测试节点", should_fail=False, should_raise=False, 
                 output_key=None, **kwargs):
        super().__init__(name=name, output_key=output_key, **kwargs)
        self.should_fail = should_fail
        self.should_raise = should_raise
        self.execute_called = False
    
    def execute(self, context: WorkflowContext) -> None:
        self.execute_called = True
        
        # 模拟执行时间
        time.sleep(0.01)
        
        # 根据配置决定是否失败
        if self.should_fail:
            if self.should_raise:
                raise ValueError("测试异常")
            else:
                self.status = NodeStatus.FAILED
                return
        
        # 如果设置了output_key，存储测试数据
        if self.output_key:
            self.set_output(context, f"测试数据-{self.name}")


class TestDataNode(DataStorageNode[WorkflowContext]):
    """用于测试的数据存储节点"""
    
    def __init__(self, name="测试数据节点", output_key="test_data", data=None, **kwargs):
        super().__init__(name=name, output_key=output_key, **kwargs)
        self.data = data or {"key": "value"}
    
    def execute(self, context: WorkflowContext) -> None:
        self.store_data(context, self.data)


# 测试用例
def test_node_initialization():
    """测试节点初始化"""
    node = TestNode(
        name="测试节点",
        description="测试描述",
        output_key="test_output",
        max_retries=2,
        timeout=10.0,
        required_context_keys=["required_key"]
    )
    
    assert node.name == "测试节点"
    assert node.description == "测试描述"
    assert node.output_key == "test_output"
    assert node.max_retries == 2
    assert node.timeout == 10.0
    assert node.required_context_keys == ["required_key"]
    assert node.status == NodeStatus.PENDING
    assert node.retry_count == 0
    assert node.start_time is None
    assert node.end_time is None
    assert node.last_error is None


def test_node_execution_success():
    """测试节点成功执行"""
    node = TestNode(output_key="test_output")
    context = create_workflow_context(
        workflow_id="test-id",
        workflow_name="测试工作流",
        execution_id="exec-id"
    )
    
    # 执行节点
    status = node.run(context)
    
    # 验证结果
    assert status == NodeStatus.SUCCESS
    assert node.execute_called is True
    assert node.status == NodeStatus.SUCCESS
    assert node.start_time is not None
    assert node.end_time is not None
    assert node.end_time >= node.start_time
    assert context.get("test_output") == "测试数据-测试节点"


def test_node_execution_failure():
    """测试节点执行失败"""
    node = TestNode(should_fail=True, should_raise=True)
    context = create_workflow_context(
        workflow_id="test-id",
        workflow_name="测试工作流",
        execution_id="exec-id"
    )
    
    # 执行节点
    status = node.run(context)
    
    # 验证结果
    assert status == NodeStatus.FAILED
    assert node.execute_called is True
    assert node.status == NodeStatus.FAILED
    assert node.start_time is not None
    assert node.end_time is not None
    assert node.last_error == "测试异常"
    assert node.exception_info is not None
    assert node.exception_info.node_name == "测试节点"
    assert node.exception_info.error_message == "测试异常"
    assert node.exception_info.error_type == "ValueError"


def test_node_retry_mechanism():
    """测试节点重试机制"""
    # 创建一个会失败但配置了重试的节点
    retry_count = 0
    
    class RetryTestNode(WorkflowNode[WorkflowContext]):
        def execute(self, context: WorkflowContext) -> None:
            nonlocal retry_count
            retry_count += 1
            if retry_count <= 2:  # 前两次失败，第三次成功
                raise ValueError(f"测试异常 {retry_count}")
    
    node = RetryTestNode(name="重试测试节点", max_retries=3)
    
    # 设置异常处理器，总是返回True表示可以重试
    def exception_handler(exception_info: NodeException, ctx: WorkflowContext) -> bool:
        return True
    
    node.set_exception_handler(exception_handler)
    
    context = create_workflow_context(
        workflow_id="test-id",
        workflow_name="测试工作流",
        execution_id="exec-id"
    )
    
    # 执行节点
    status = node.run(context)
    
    # 验证结果
    assert status == NodeStatus.SUCCESS
    assert retry_count == 3  # 应该尝试了3次
    assert node.retry_count == 2  # 重试计数应该是2


def test_merge_workflow_node_and():
    """测试AND合并节点"""
    node1 = TestNode(name="节点1", output_key="output1")
    node2 = TestNode(name="节点2", output_key="output2")
    
    # 创建AND合并节点
    merge_node = MergeWorkflowNode(
        name="AND合并节点",
        merge_type="and",
        nodes=[node1, node2]
    )
    
    context = create_workflow_context(
        workflow_id="test-id",
        workflow_name="测试工作流",
        execution_id="exec-id"
    )
    
    # 执行合并节点
    status = merge_node.run(context)
    
    # 验证结果
    assert status == NodeStatus.SUCCESS
    assert context.get("output1") == "测试数据-节点1"
    assert context.get("output2") == "测试数据-节点2"


def test_merge_workflow_node_and_failure():
    """测试AND合并节点失败情况"""
    node1 = TestNode(name="节点1")
    node2 = TestNode(name="节点2", should_fail=True, should_raise=True)
    
    # 创建AND合并节点
    merge_node = MergeWorkflowNode(
        name="AND合并节点",
        merge_type="and",
        nodes=[node1, node2]
    )
    
    context = create_workflow_context(
        workflow_id="test-id",
        workflow_name="测试工作流",
        execution_id="exec-id"
    )
    
    # 执行合并节点
    status = merge_node.run(context)
    
    # 验证结果
    assert status == NodeStatus.FAILED
    assert node1.status == NodeStatus.SUCCESS
    assert node2.status == NodeStatus.FAILED


def test_merge_workflow_node_or():
    """测试OR合并节点"""
    node1 = TestNode(name="节点1", should_fail=True)
    node2 = TestNode(name="节点2", output_key="output2")
    
    # 创建OR合并节点
    merge_node = MergeWorkflowNode(
        name="OR合并节点",
        merge_type="or",
        nodes=[node1, node2]
    )
    
    context = create_workflow_context(
        workflow_id="test-id",
        workflow_name="测试工作流",
        execution_id="exec-id"
    )
    
    # 执行合并节点
    status = merge_node.run(context)
    
    # 验证结果
    assert status == NodeStatus.SUCCESS
    assert node1.status == NodeStatus.FAILED
    assert node2.status == NodeStatus.SUCCESS
    assert context.get("output2") == "测试数据-节点2"


def test_merge_workflow_node_or_all_failure():
    """测试OR合并节点全部失败情况"""
    node1 = TestNode(name="节点1", should_fail=True)
    node2 = TestNode(name="节点2", should_fail=True)
    
    # 创建OR合并节点
    merge_node = MergeWorkflowNode(
        name="OR合并节点",
        merge_type="or",
        nodes=[node1, node2]
    )
    
    context = create_workflow_context(
        workflow_id="test-id",
        workflow_name="测试工作流",
        execution_id="exec-id"
    )
    
    # 执行合并节点
    status = merge_node.run(context)
    
    # 验证结果
    assert status == NodeStatus.FAILED
    assert node1.status == NodeStatus.FAILED
    assert node2.status == NodeStatus.FAILED


def test_data_storage_node():
    """测试数据存储节点"""
    test_data = {"name": "测试", "value": 123}
    node = TestDataNode(output_key="stored_data", data=test_data)
    
    context = create_workflow_context(
        workflow_id="test-id",
        workflow_name="测试工作流",
        execution_id="exec-id"
    )
    
    # 执行节点
    status = node.run(context)
    
    # 验证结果
    assert status == NodeStatus.SUCCESS
    assert context.get("stored_data") == test_data


def test_node_exception_handling():
    """测试节点异常处理"""
    node = TestNode(should_fail=True, should_raise=True)
    
    # 设置异常处理器
    handled_exceptions = []
    
    def exception_handler(exception_info: NodeException, ctx: WorkflowContext) -> bool:
        handled_exceptions.append(exception_info)
        return False  # 不重试
    
    node.set_exception_handler(exception_handler)
    
    context = create_workflow_context(
        workflow_id="test-id",
        workflow_name="测试工作流",
        execution_id="exec-id"
    )
    
    # 执行节点
    status = node.run(context)
    
    # 验证结果
    assert status == NodeStatus.FAILED
    assert len(handled_exceptions) == 1
    assert handled_exceptions[0].node_name == "测试节点"
    assert handled_exceptions[0].error_message == "测试异常"


def test_node_operator_overloading():
    """测试节点运算符重载"""
    node1 = TestNode(name="节点1")
    node2 = TestNode(name="节点2")
    node3 = TestNode(name="节点3")
    
    # 测试AND运算符
    and_node = node1 & node2
    assert isinstance(and_node, MergeWorkflowNode)
    assert and_node.merge_type == "and"
    assert len(and_node.nodes) == 2
    assert and_node.nodes[0] == node1
    assert and_node.nodes[1] == node2
    
    # 测试OR运算符
    or_node = node1 | node2
    assert isinstance(or_node, MergeWorkflowNode)
    assert or_node.merge_type == "or"
    assert len(or_node.nodes) == 2
    assert or_node.nodes[0] == node1
    assert or_node.nodes[1] == node2
    
    # 测试链式AND运算
    chain_and = node1 & node2 & node3
    assert isinstance(chain_and, MergeWorkflowNode)
    assert chain_and.merge_type == "and"
    assert len(chain_and.nodes) == 3
    
    # 测试链式OR运算
    chain_or = node1 | node2 | node3
    assert isinstance(chain_or, MergeWorkflowNode)
    assert chain_or.merge_type == "or"
    assert len(chain_or.nodes) == 3