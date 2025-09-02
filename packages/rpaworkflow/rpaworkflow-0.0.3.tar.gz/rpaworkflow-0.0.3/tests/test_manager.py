import pytest
from typing import Dict, Any, Optional, List, Callable

from rpaworkflow.manager import WorkflowManager, WorkflowStatus, WorkflowResult
from rpaworkflow.node import NodeStatus, WorkflowNode, NodeException
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
def test_workflow_manager_initialization():
    """测试工作流管理器初始化"""
    # 创建工作流节点
    node1 = TestNode(name="节点1")
    node2 = TestNode(name="节点2")
    
    # 创建工作流管理器
    manager = WorkflowManager(
        workflow_id="test-workflow",
        workflow_name="测试工作流",
        nodes=[node1, node2]
    )
    
    # 验证初始化
    assert manager.workflow_id == "test-workflow"
    assert manager.workflow_name == "测试工作流"
    assert len(manager.nodes) == 2
    assert manager.nodes[0] == node1
    assert manager.nodes[1] == node2
    assert manager.status == WorkflowStatus.PENDING


def test_workflow_manager_execution_success():
    """测试工作流管理器成功执行"""
    # 创建工作流节点
    node1 = TestNode(name="节点1", output_key="output1")
    node2 = TestNode(name="节点2", output_key="output2")
    
    # 创建工作流管理器
    manager = WorkflowManager(
        workflow_id="test-workflow",
        workflow_name="测试工作流",
        nodes=[node1, node2]
    )
    
    # 执行工作流
    result = manager.execute()
    
    # 验证结果
    assert result.status == WorkflowStatus.SUCCESS
    assert node1.status == NodeStatus.SUCCESS
    assert node2.status == NodeStatus.SUCCESS
    assert result.context.get("output1") == "测试数据-节点1"
    assert result.context.get("output2") == "测试数据-节点2"
    assert manager.status == WorkflowStatus.SUCCESS


def test_workflow_manager_execution_failure():
    """测试工作流管理器执行失败"""
    # 创建工作流节点，第二个节点会失败
    node1 = TestNode(name="节点1", output_key="output1")
    node2 = TestNode(name="节点2", should_fail=True)
    node3 = TestNode(name="节点3", output_key="output3")
    
    # 创建工作流管理器
    manager = WorkflowManager(
        workflow_id="test-workflow",
        workflow_name="测试工作流",
        nodes=[node1, node2, node3]
    )
    
    # 执行工作流
    result = manager.execute()
    
    # 验证结果
    assert result.status == WorkflowStatus.FAILED
    assert node1.status == NodeStatus.SUCCESS
    assert node2.status == NodeStatus.FAILED
    assert node3.status == NodeStatus.PENDING  # 第三个节点不应该执行
    assert result.context.get("output1") == "测试数据-节点1"
    assert "output3" not in result.context
    assert manager.status == WorkflowStatus.FAILED
    assert result.error_node == node2


def test_workflow_manager_with_context():
    """测试工作流管理器使用预设上下文"""
    # 创建工作流节点
    node1 = TestNode(name="节点1", output_key="output1")
    
    # 创建工作流管理器
    manager = WorkflowManager(
        workflow_id="test-workflow",
        workflow_name="测试工作流",
        nodes=[node1]
    )
    
    # 创建预设上下文
    context = create_workflow_context(
        workflow_id="test-workflow",
        workflow_name="测试工作流",
        execution_id="test-execution",
        preset_value="预设值"
    )
    
    # 执行工作流，使用预设上下文
    result = manager.execute(context=context)
    
    # 验证结果
    assert result.status == WorkflowStatus.SUCCESS
    assert result.context.get("preset_value") == "预设值"
    assert result.context.get("output1") == "测试数据-节点1"


def test_workflow_manager_events():
    """测试工作流管理器事件回调"""
    # 创建工作流节点
    node1 = TestNode(name="节点1", output_key="output1")
    node2 = TestNode(name="节点2", output_key="output2")
    
    # 创建事件记录列表
    events = []
    
    # 创建事件回调函数
    def on_workflow_start(context: WorkflowContext) -> None:
        events.append("workflow_start")
    
    def on_workflow_end(context: WorkflowContext, status: WorkflowStatus) -> None:
        events.append(f"workflow_end_{status.name}")
    
    def on_node_start(node: WorkflowNode, context: WorkflowContext) -> None:
        events.append(f"node_start_{node.name}")
    
    def on_node_end(node: WorkflowNode, context: WorkflowContext, status: NodeStatus) -> None:
        events.append(f"node_end_{node.name}_{status.name}")
    
    # 创建工作流管理器
    manager = WorkflowManager(
        workflow_id="test-workflow",
        workflow_name="测试工作流",
        nodes=[node1, node2]
    )
    
    # 设置事件回调
    manager.set_on_workflow_start(on_workflow_start)
    manager.set_on_workflow_end(on_workflow_end)
    manager.set_on_node_start(on_node_start)
    manager.set_on_node_end(on_node_end)
    
    # 执行工作流
    result = manager.execute()
    
    # 验证事件顺序
    expected_events = [
        "workflow_start",
        "node_start_节点1",
        "node_end_节点1_SUCCESS",
        "node_start_节点2",
        "node_end_节点2_SUCCESS",
        "workflow_end_SUCCESS"
    ]
    
    assert events == expected_events


def test_workflow_manager_error_events():
    """测试工作流管理器错误事件回调"""
    # 创建工作流节点，第二个节点会失败
    node1 = TestNode(name="节点1", output_key="output1")
    node2 = TestNode(name="节点2", should_fail=True)
    
    # 创建事件记录列表
    events = []
    error_info = None
    
    # 创建事件回调函数
    def on_workflow_error(context: WorkflowContext, error_node: WorkflowNode, exception_info: NodeException) -> None:
        nonlocal error_info
        events.append(f"workflow_error_{error_node.name}")
        error_info = exception_info
    
    # 创建工作流管理器
    manager = WorkflowManager(
        workflow_id="test-workflow",
        workflow_name="测试工作流",
        nodes=[node1, node2]
    )
    
    # 设置事件回调
    manager.set_on_workflow_error(on_workflow_error)
    
    # 执行工作流
    result = manager.execute()
    
    # 验证错误事件
    assert events == ["workflow_error_节点2"]
    assert error_info is not None
    assert error_info.node_name == "节点2"
    assert error_info.error_message == "测试异常"
    assert error_info.error_type == "ValueError"


def test_workflow_manager_add_nodes():
    """测试工作流管理器添加节点"""
    # 创建工作流节点
    node1 = TestNode(name="节点1", output_key="output1")
    node2 = TestNode(name="节点2", output_key="output2")
    
    # 创建工作流管理器，初始只有一个节点
    manager = WorkflowManager(
        workflow_id="test-workflow",
        workflow_name="测试工作流",
        nodes=[node1]
    )
    
    # 添加第二个节点
    manager.add_node(node2)
    
    # 验证节点列表
    assert len(manager.nodes) == 2
    assert manager.nodes[0] == node1
    assert manager.nodes[1] == node2
    
    # 执行工作流
    result = manager.execute()
    
    # 验证结果
    assert result.status == WorkflowStatus.SUCCESS
    assert result.context.get("output1") == "测试数据-节点1"
    assert result.context.get("output2") == "测试数据-节点2"


def test_workflow_manager_execution_id():
    """测试工作流管理器执行ID"""
    # 创建工作流节点
    node = TestNode(name="节点1")
    
    # 创建工作流管理器
    manager = WorkflowManager(
        workflow_id="test-workflow",
        workflow_name="测试工作流",
        nodes=[node]
    )
    
    # 执行工作流
    result1 = manager.execute()
    result2 = manager.execute()
    
    # 验证执行ID不同
    assert result1.context.get("execution_id") is not None
    assert result2.context.get("execution_id") is not None
    assert result1.context.get("execution_id") != result2.context.get("execution_id")


def test_workflow_manager_custom_execution_id():
    """测试工作流管理器自定义执行ID"""
    # 创建工作流节点
    node = TestNode(name="节点1")
    
    # 创建工作流管理器
    manager = WorkflowManager(
        workflow_id="test-workflow",
        workflow_name="测试工作流",
        nodes=[node]
    )
    
    # 执行工作流，指定执行ID
    custom_id = "custom-execution-id"
    result = manager.execute(execution_id=custom_id)
    
    # 验证执行ID
    assert result.context.get("execution_id") == custom_id


def test_workflow_manager_error_handler():
    """测试工作流管理器错误处理器"""
    # 创建工作流节点，第二个节点会失败
    node1 = TestNode(name="节点1", output_key="output1")
    node2 = TestNode(name="节点2", should_fail=True)
    node3 = TestNode(name="节点3", output_key="output3")
    
    # 创建错误处理记录
    handled_errors = []
    
    # 创建错误处理函数，允许继续执行
    def error_handler(context: WorkflowContext, error_node: WorkflowNode, exception_info: NodeException) -> bool:
        handled_errors.append((error_node.name, exception_info.error_message))
        return True  # 允许继续执行
    
    # 创建工作流管理器
    manager = WorkflowManager(
        workflow_id="test-workflow",
        workflow_name="测试工作流",
        nodes=[node1, node2, node3]
    )
    
    # 设置错误处理器
    manager.set_error_handler(error_handler)
    
    # 执行工作流
    result = manager.execute()
    
    # 验证结果
    assert result.status == WorkflowStatus.PARTIAL_SUCCESS
    assert node1.status == NodeStatus.SUCCESS
    assert node2.status == NodeStatus.FAILED
    assert node3.status == NodeStatus.SUCCESS  # 第三个节点应该执行
    assert result.context.get("output1") == "测试数据-节点1"
    assert result.context.get("output3") == "测试数据-节点3"
    assert len(handled_errors) == 1
    assert handled_errors[0] == ("节点2", "测试异常")


def test_workflow_manager_multiple_executions():
    """测试工作流管理器多次执行"""
    # 创建一个会记录执行次数的节点
    execution_count = 0
    
    class CounterNode(WorkflowNode[WorkflowContext]):
        def execute(self, context: WorkflowContext) -> None:
            nonlocal execution_count
            execution_count += 1
            self.set_output(context, execution_count)
    
    node = CounterNode(name="计数器节点", output_key="count")
    
    # 创建工作流管理器
    manager = WorkflowManager(
        workflow_id="test-workflow",
        workflow_name="测试工作流",
        nodes=[node]
    )
    
    # 执行工作流多次
    result1 = manager.execute()
    result2 = manager.execute()
    result3 = manager.execute()
    
    # 验证结果
    assert result1.context.get("count") == 1
    assert result2.context.get("count") == 2
    assert result3.context.get("count") == 3
    assert execution_count == 3