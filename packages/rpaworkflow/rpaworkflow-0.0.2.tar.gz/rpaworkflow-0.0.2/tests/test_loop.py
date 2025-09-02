import pytest
from typing import Dict, Any, Optional

from rpaworkflow.nodes.loop import LoopNode
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
        self.execution_count = 0
    
    def execute(self, context: WorkflowContext) -> None:
        self.execute_called = True
        self.execution_count += 1
        
        # 根据配置决定是否失败
        if self.should_fail:
            raise ValueError("测试异常")
        
        # 如果设置了output_key，存储测试数据
        if self.output_key:
            current_value = context.get(self.output_key, 0)
            if isinstance(current_value, int):
                self.set_output(context, current_value + 1)
            else:
                self.set_output(context, f"测试数据-{self.name}-{self.execution_count}")


# 测试用例
def test_loop_node_initialization():
    """测试循环节点初始化"""
    # 创建循环条件函数
    def test_condition(context: WorkflowContext) -> bool:
        return context.get("counter", 0) < 3
    
    # 创建循环体节点
    loop_body = TestNode(name="循环体")
    
    # 创建循环节点
    loop_node = LoopNode(
        name="循环节点",
        description="测试循环节点",
        loop_condition=test_condition,
        loop_node=loop_body,
        max_loops=5
    )
    
    # 验证初始化
    assert loop_node.name == "循环节点"
    assert loop_node.description == "测试循环节点"
    assert loop_node.loop_condition == test_condition
    assert loop_node.loop_node == loop_body
    assert loop_node.max_loops == 5


def test_loop_node_execution():
    """测试循环节点执行"""
    # 创建循环条件函数
    def test_condition(context: WorkflowContext) -> bool:
        counter = context.get("counter", 0)
        return counter < 3
    
    # 创建循环体节点，每次执行增加计数器
    class CounterNode(WorkflowNode[WorkflowContext]):
        def execute(self, context: WorkflowContext) -> None:
            counter = context.get("counter", 0)
            counter += 1
            self.set_context_value(context, "counter", counter)
    
    loop_body = CounterNode(name="计数器节点")
    
    # 创建循环节点
    loop_node = LoopNode(
        name="循环节点",
        loop_condition=test_condition,
        loop_node=loop_body
    )
    
    # 创建上下文
    context = create_workflow_context(
        workflow_id="test-id",
        workflow_name="测试工作流",
        execution_id="exec-id",
        counter=0
    )
    
    # 执行循环节点
    status = loop_node.run(context)
    
    # 验证结果
    assert status == NodeStatus.SUCCESS
    assert context.get("counter") == 3  # 循环应该执行3次


def test_loop_node_with_output_accumulation():
    """测试循环节点输出累积"""
    # 创建循环条件函数
    def test_condition(context: WorkflowContext) -> bool:
        counter = context.get("counter", 0)
        return counter < 3
    
    # 创建循环体节点，累积输出
    loop_body = TestNode(name="累积节点", output_key="counter")
    
    # 创建循环节点
    loop_node = LoopNode(
        name="循环节点",
        loop_condition=test_condition,
        loop_node=loop_body
    )
    
    # 创建上下文
    context = create_workflow_context(
        workflow_id="test-id",
        workflow_name="测试工作流",
        execution_id="exec-id",
        counter=0
    )
    
    # 执行循环节点
    status = loop_node.run(context)
    
    # 验证结果
    assert status == NodeStatus.SUCCESS
    assert context.get("counter") == 3  # 循环应该执行3次，最终值为3


def test_loop_node_max_loops():
    """测试循环节点最大循环次数"""
    # 创建循环条件函数，总是返回True
    def test_condition(context: WorkflowContext) -> bool:
        return True
    
    # 创建循环体节点，每次执行增加计数器
    class CounterNode(WorkflowNode[WorkflowContext]):
        def execute(self, context: WorkflowContext) -> None:
            counter = context.get("counter", 0)
            counter += 1
            self.set_context_value(context, "counter", counter)
    
    loop_body = CounterNode(name="计数器节点")
    
    # 创建循环节点，设置最大循环次数为5
    loop_node = LoopNode(
        name="循环节点",
        loop_condition=test_condition,
        loop_node=loop_body,
        max_loops=5
    )
    
    # 创建上下文
    context = create_workflow_context(
        workflow_id="test-id",
        workflow_name="测试工作流",
        execution_id="exec-id",
        counter=0
    )
    
    # 执行循环节点
    status = loop_node.run(context)
    
    # 验证结果
    assert status == NodeStatus.SUCCESS
    assert context.get("counter") == 5  # 循环应该执行5次后停止


def test_loop_node_without_condition():
    """测试循环节点没有设置循环条件"""
    # 创建循环体节点
    loop_body = TestNode(name="循环体")
    
    # 创建循环节点
    loop_node = LoopNode(
        name="循环节点",
        loop_node=loop_body
    )
    
    # 创建上下文
    context = create_workflow_context(
        workflow_id="test-id",
        workflow_name="测试工作流",
        execution_id="exec-id"
    )
    
    # 执行循环节点，应该抛出异常
    with pytest.raises(NodeError) as excinfo:
        loop_node.run(context)
    
    # 验证异常信息
    assert "循环条件未设置" in str(excinfo.value)


def test_loop_node_without_loop_body():
    """测试循环节点没有设置循环体"""
    # 创建循环条件函数
    def test_condition(context: WorkflowContext) -> bool:
        return True
    
    # 创建循环节点
    loop_node = LoopNode(
        name="循环节点",
        loop_condition=test_condition
    )
    
    # 创建上下文
    context = create_workflow_context(
        workflow_id="test-id",
        workflow_name="测试工作流",
        execution_id="exec-id"
    )
    
    # 执行循环节点，应该抛出异常
    with pytest.raises(NodeError) as excinfo:
        loop_node.run(context)
    
    # 验证异常信息
    assert "循环体未设置" in str(excinfo.value)


def test_loop_node_body_failure():
    """测试循环节点循环体执行失败"""
    # 创建循环条件函数
    def test_condition(context: WorkflowContext) -> bool:
        counter = context.get("counter", 0)
        return counter < 3
    
    # 创建循环体节点，第二次执行时失败
    class FailingNode(WorkflowNode[WorkflowContext]):
        def execute(self, context: WorkflowContext) -> None:
            counter = context.get("counter", 0)
            counter += 1
            self.set_context_value(context, "counter", counter)
            
            # 第二次执行时失败
            if counter == 2:
                raise ValueError("测试异常")
    
    loop_body = FailingNode(name="失败节点")
    
    # 创建循环节点
    loop_node = LoopNode(
        name="循环节点",
        loop_condition=test_condition,
        loop_node=loop_body
    )
    
    # 创建上下文
    context = create_workflow_context(
        workflow_id="test-id",
        workflow_name="测试工作流",
        execution_id="exec-id",
        counter=0
    )
    
    # 执行循环节点
    status = loop_node.run(context)
    
    # 验证结果
    assert status == NodeStatus.FAILED
    assert context.get("counter") == 2  # 循环应该执行到第2次就失败
    assert loop_body.status == NodeStatus.FAILED


def test_loop_node_with_break_condition():
    """测试循环节点带有中断条件"""
    # 创建上下文
    context = create_workflow_context(
        workflow_id="test-id",
        workflow_name="测试工作流",
        execution_id="exec-id",
        counter=0,
        should_break=False
    )
    
    # 创建循环条件函数，检查中断标志
    def test_condition(ctx: WorkflowContext) -> bool:
        if ctx.get("should_break", False):
            return False  # 如果设置了中断标志，停止循环
        return ctx.get("counter", 0) < 5  # 否则检查计数器
    
    # 创建循环体节点，增加计数器并在特定条件下设置中断标志
    class BreakableNode(WorkflowNode[WorkflowContext]):
        def execute(self, ctx: WorkflowContext) -> None:
            counter = ctx.get("counter", 0)
            counter += 1
            self.set_context_value(ctx, "counter", counter)
            
            # 当计数器达到3时，设置中断标志
            if counter >= 3:
                self.set_context_value(ctx, "should_break", True)
    
    loop_body = BreakableNode(name="可中断节点")
    
    # 创建循环节点
    loop_node = LoopNode(
        name="循环节点",
        loop_condition=test_condition,
        loop_node=loop_body
    )
    
    # 执行循环节点
    status = loop_node.run(context)
    
    # 验证结果
    assert status == NodeStatus.SUCCESS
    assert context.get("counter") == 3  # 循环应该在计数器达到3时中断
    assert context.get("should_break") is True