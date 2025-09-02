import pytest
from typing import Dict, Any, Optional

from rpaworkflow.func.op import and_, or_
from rpaworkflow.node import NodeStatus, WorkflowNode, MergeWorkflowNode
from rpaworkflow.context import WorkflowContext, create_workflow_context
from rpaworkflow.exception import NodeError


# 创建测试用的节点类
class TestNode(WorkflowNode[WorkflowContext]):
    """用于测试的节点实现"""
    
    def __init__(self, name="测试节点", should_fail=False, **kwargs):
        super().__init__(name=name, **kwargs)
        self.should_fail = should_fail
        self.execute_called = False
    
    def execute(self, context: WorkflowContext) -> None:
        self.execute_called = True
        
        # 根据配置决定是否失败
        if self.should_fail:
            raise ValueError("测试异常")


def test_or_function():
    """测试or_函数"""
    # 创建测试节点
    node1 = TestNode(name="节点1")
    node2 = TestNode(name="节点2")
    node3 = TestNode(name="节点3")
    
    # 使用or_函数创建合并节点
    merge_node = or_(node1, node2, node3)
    
    # 验证结果
    assert isinstance(merge_node, MergeWorkflowNode)
    assert merge_node.name == "节点1 | 节点2 | 节点3"
    assert merge_node.merge_type == "or"
    assert len(merge_node.nodes) == 3
    assert merge_node.nodes[0] == node1
    assert merge_node.nodes[1] == node2
    assert merge_node.nodes[2] == node3


def test_and_function():
    """测试and_函数"""
    # 创建测试节点
    node1 = TestNode(name="节点1")
    node2 = TestNode(name="节点2")
    node3 = TestNode(name="节点3")
    
    # 使用and_函数创建合并节点
    merge_node = and_(node1, node2, node3)
    
    # 验证结果
    assert isinstance(merge_node, MergeWorkflowNode)
    assert merge_node.name == "节点1 & 节点2 & 节点3"
    assert merge_node.merge_type == "and"
    assert len(merge_node.nodes) == 3
    assert merge_node.nodes[0] == node1
    assert merge_node.nodes[1] == node2
    assert merge_node.nodes[2] == node3


def test_or_function_execution():
    """测试or_函数创建的节点执行"""
    # 创建测试节点，第一个会成功，其他会失败
    node1 = TestNode(name="成功节点")
    node2 = TestNode(name="失败节点1", should_fail=True)
    node3 = TestNode(name="失败节点2", should_fail=True)
    
    # 使用or_函数创建合并节点
    merge_node = or_(node1, node2, node3)
    
    # 创建上下文
    context = create_workflow_context(
        workflow_id="test-id",
        workflow_name="测试工作流",
        execution_id="exec-id"
    )
    
    # 执行合并节点
    status = merge_node.run(context)
    
    # 验证结果
    assert status == NodeStatus.SUCCESS  # 只要有一个成功，整体就成功
    assert node1.execute_called is True
    # 由于第一个节点成功，后面的节点不会被执行
    assert node2.execute_called is False
    assert node3.execute_called is False
    assert node1.status == NodeStatus.SUCCESS


def test_and_function_execution():
    """测试and_函数创建的节点执行"""
    # 创建测试节点，都会成功
    node1 = TestNode(name="成功节点1")
    node2 = TestNode(name="成功节点2")
    node3 = TestNode(name="成功节点3")
    
    # 使用and_函数创建合并节点
    merge_node = and_(node1, node2, node3)
    
    # 创建上下文
    context = create_workflow_context(
        workflow_id="test-id",
        workflow_name="测试工作流",
        execution_id="exec-id"
    )
    
    # 执行合并节点
    status = merge_node.run(context)
    
    # 验证结果
    assert status == NodeStatus.SUCCESS  # 所有节点都成功，整体才成功
    assert node1.execute_called is True
    assert node2.execute_called is True
    assert node3.execute_called is True
    assert node1.status == NodeStatus.SUCCESS
    assert node2.status == NodeStatus.SUCCESS
    assert node3.status == NodeStatus.SUCCESS


def test_and_function_execution_failure():
    """测试and_函数创建的节点执行失败"""
    # 创建测试节点，有一个会失败
    node1 = TestNode(name="成功节点1")
    node2 = TestNode(name="失败节点", should_fail=True)
    node3 = TestNode(name="成功节点2")
    
    # 使用and_函数创建合并节点
    merge_node = and_(node1, node2, node3)
    
    # 创建上下文
    context = create_workflow_context(
        workflow_id="test-id",
        workflow_name="测试工作流",
        execution_id="exec-id"
    )
    
    # 执行合并节点
    status = merge_node.run(context)
    
    # 验证结果
    assert status == NodeStatus.FAILED
    assert node1.execute_called is True
    assert node2.execute_called is True
    # 由于第二个节点失败，第三个节点不会被执行
    assert node3.execute_called is False
    assert node1.status == NodeStatus.SUCCESS
    assert node2.status == NodeStatus.FAILED
    # 验证错误信息
    assert merge_node.last_error is not None
    assert "失败节点" in merge_node.last_error


def test_or_function_all_failure():
    """测试or_函数创建的节点全部执行失败"""
    # 创建测试节点，全部会失败
    node1 = TestNode(name="失败节点1", should_fail=True)
    node2 = TestNode(name="失败节点2", should_fail=True)
    node3 = TestNode(name="失败节点3", should_fail=True)
    
    # 使用or_函数创建合并节点
    merge_node = or_(node1, node2, node3)
    
    # 创建上下文
    context = create_workflow_context(
        workflow_id="test-id",
        workflow_name="测试工作流",
        execution_id="exec-id"
    )
    
    # 执行合并节点
    status = merge_node.run(context)
    
    # 验证结果
    assert status == NodeStatus.FAILED
    assert node1.execute_called is True
    assert node2.execute_called is True
    assert node3.execute_called is True
    assert node1.status == NodeStatus.FAILED
    assert node2.status == NodeStatus.FAILED
    assert node3.status == NodeStatus.FAILED
    # 验证错误信息
    assert merge_node.last_error is not None
    assert "所有分支均失败" in merge_node.last_error