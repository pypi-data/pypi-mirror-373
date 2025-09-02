import pytest
from typing import Dict, Any, Optional

from rpaworkflow.nodes.condition import ConditionNode
from rpaworkflow.node import NodeStatus, WorkflowNode
from rpaworkflow.context import WorkflowContext, create_workflow_context
from rpaworkflow.exception import NodeError


# 创建测试用的节点类
class TestNode(WorkflowNode[WorkflowContext]):
    """用于测试的节点实现"""
    
    def __init__(self, name="测试节点", should_fail=False, output_key=None, **kwargs):
        super().__init__(name=name, output_key=output_key, **kwargs)
        self.should_fail = should_fail
        self.execute_called = False
    
    def execute(self, context: WorkflowContext) -> None:
        self.execute_called = True
        
        # 根据配置决定是否失败
        if self.should_fail:
            raise ValueError("测试异常")
        
        # 如果设置了output_key，存储测试数据
        if self.output_key:
            self.set_output(context, f"测试数据-{self.name}")


# 测试用例
def test_condition_node_initialization():
    """测试条件节点初始化"""
    # 创建条件函数
    def test_condition(context: WorkflowContext) -> bool:
        return True
    
    # 创建分支节点
    true_node = TestNode(name="真分支")
    false_node = TestNode(name="假分支")
    
    # 创建条件节点
    condition_node = ConditionNode(
        name="条件节点",
        description="测试条件节点",
        condition=test_condition,
        true_node=true_node,
        false_node=false_node
    )
    
    # 验证初始化
    assert condition_node.name == "条件节点"
    assert condition_node.description == "测试条件节点"
    assert condition_node.condition == test_condition
    assert condition_node.true_node == true_node
    assert condition_node.false_node == false_node


def test_condition_node_true_branch():
    """测试条件节点真分支执行"""
    # 创建条件函数
    def test_condition(context: WorkflowContext) -> bool:
        return True
    
    # 创建分支节点
    true_node = TestNode(name="真分支", output_key="true_output")
    false_node = TestNode(name="假分支", output_key="false_output")
    
    # 创建条件节点
    condition_node = ConditionNode(
        name="条件节点",
        condition=test_condition,
        true_node=true_node,
        false_node=false_node
    )
    
    # 创建上下文
    context = create_workflow_context(
        workflow_id="test-id",
        workflow_name="测试工作流",
        execution_id="exec-id"
    )
    
    # 执行条件节点
    status = condition_node.run(context)
    
    # 验证结果
    assert status == NodeStatus.SUCCESS
    assert true_node.execute_called is True
    assert false_node.execute_called is False
    assert context.get("true_output") == "测试数据-真分支"
    assert "false_output" not in context


def test_condition_node_false_branch():
    """测试条件节点假分支执行"""
    # 创建条件函数
    def test_condition(context: WorkflowContext) -> bool:
        return False
    
    # 创建分支节点
    true_node = TestNode(name="真分支", output_key="true_output")
    false_node = TestNode(name="假分支", output_key="false_output")
    
    # 创建条件节点
    condition_node = ConditionNode(
        name="条件节点",
        condition=test_condition,
        true_node=true_node,
        false_node=false_node
    )
    
    # 创建上下文
    context = create_workflow_context(
        workflow_id="test-id",
        workflow_name="测试工作流",
        execution_id="exec-id"
    )
    
    # 执行条件节点
    status = condition_node.run(context)
    
    # 验证结果
    assert status == NodeStatus.SUCCESS
    assert true_node.execute_called is False
    assert false_node.execute_called is True
    assert "true_output" not in context
    assert context.get("false_output") == "测试数据-假分支"


def test_condition_node_without_condition():
    """测试条件节点没有设置条件函数"""
    # 创建分支节点
    true_node = TestNode(name="真分支")
    false_node = TestNode(name="假分支")
    
    # 创建条件节点
    condition_node = ConditionNode(
        name="条件节点",
        true_node=true_node,
        false_node=false_node
    )
    
    # 创建上下文
    context = create_workflow_context(
        workflow_id="test-id",
        workflow_name="测试工作流",
        execution_id="exec-id"
    )
    
    # 执行条件节点，应该失败
    status = condition_node.run(context)
    
    # 验证结果
    assert status == NodeStatus.FAILED
    assert condition_node.last_error is not None
    assert "未设置条件函数" in condition_node.last_error


def test_condition_node_without_true_node():
    """测试条件节点没有设置真分支"""
    # 创建条件函数
    def test_condition(context: WorkflowContext) -> bool:
        return True
    
    # 创建假分支节点
    false_node = TestNode(name="假分支")
    
    # 创建条件节点
    condition_node = ConditionNode(
        name="条件节点",
        condition=test_condition,
        false_node=false_node
    )
    
    # 创建上下文
    context = create_workflow_context(
        workflow_id="test-id",
        workflow_name="测试工作流",
        execution_id="exec-id"
    )
    
    # 执行条件节点，应该失败
    status = condition_node.run(context)
    
    # 验证结果
    assert status == NodeStatus.FAILED
    assert condition_node.last_error is not None
    assert "未设置当前条件分支" in condition_node.last_error


def test_condition_node_without_false_node():
    """测试条件节点没有设置假分支"""
    # 创建条件函数
    def test_condition(context: WorkflowContext) -> bool:
        return False
    
    # 创建真分支节点
    true_node = TestNode(name="真分支")
    
    # 创建条件节点
    condition_node = ConditionNode(
        name="条件节点",
        condition=test_condition,
        true_node=true_node
    )
    
    # 创建上下文
    context = create_workflow_context(
        workflow_id="test-id",
        workflow_name="测试工作流",
        execution_id="exec-id"
    )
    
    # 执行条件节点，应该失败
    status = condition_node.run(context)
    
    # 验证结果
    assert status == NodeStatus.FAILED
    assert condition_node.last_error is not None
    assert "未设置当前条件分支" in condition_node.last_error


def test_condition_node_branch_failure():
    """测试条件节点分支执行失败"""
    # 创建条件函数
    def test_condition(context: WorkflowContext) -> bool:
        return True
    
    # 创建分支节点，真分支会失败
    true_node = TestNode(name="真分支", should_fail=True)
    false_node = TestNode(name="假分支")
    
    # 创建条件节点
    condition_node = ConditionNode(
        name="条件节点",
        condition=test_condition,
        true_node=true_node,
        false_node=false_node
    )
    
    # 创建上下文
    context = create_workflow_context(
        workflow_id="test-id",
        workflow_name="测试工作流",
        execution_id="exec-id"
    )
    
    # 执行条件节点
    status = condition_node.run(context)
    
    # 验证结果
    assert status == NodeStatus.FAILED
    assert true_node.execute_called is True
    assert false_node.execute_called is False
    assert true_node.status == NodeStatus.FAILED


def test_condition_node_with_context_value():
    """测试条件节点使用上下文值"""
    # 创建条件函数，检查上下文中的标志
    def test_condition(context: WorkflowContext) -> bool:
        return context.get("flag", False)
    
    # 创建分支节点
    true_node = TestNode(name="真分支", output_key="true_output")
    false_node = TestNode(name="假分支", output_key="false_output")
    
    # 创建条件节点
    condition_node = ConditionNode(
        name="条件节点",
        condition=test_condition,
        true_node=true_node,
        false_node=false_node
    )
    
    # 创建上下文，设置标志为True
    context = create_workflow_context(
        workflow_id="test-id",
        workflow_name="测试工作流",
        execution_id="exec-id",
        flag=True
    )
    
    # 执行条件节点
    status = condition_node.run(context)
    
    # 验证结果
    assert status == NodeStatus.SUCCESS
    assert true_node.execute_called is True
    assert false_node.execute_called is False
    
    # 重置节点状态
    true_node.status = NodeStatus.PENDING
    true_node.execute_called = False
    false_node.status = NodeStatus.PENDING
    false_node.execute_called = False
    
    # 创建新上下文，设置标志为False
    context = create_workflow_context(
        workflow_id="test-id",
        workflow_name="测试工作流",
        execution_id="exec-id",
        flag=False
    )
    
    # 再次执行条件节点
    status = condition_node.run(context)
    
    # 验证结果
    assert status == NodeStatus.SUCCESS
    assert true_node.execute_called is False
    assert false_node.execute_called is True