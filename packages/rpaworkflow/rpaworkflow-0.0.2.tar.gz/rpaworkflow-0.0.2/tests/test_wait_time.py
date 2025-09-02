import pytest
import time
from typing import Dict, Any, Optional

from rpaworkflow.nodes.wait_time import WaitTimeNode
from rpaworkflow.node import NodeStatus
from rpaworkflow.context import WorkflowContext, create_workflow_context
from rpaworkflow.exception import NodeError


def test_wait_time_node_initialization():
    """测试等待时间节点初始化"""
    # 创建固定时间等待节点
    wait_node = WaitTimeNode(
        name="等待节点",
        description="测试等待节点",
        min_time=1.0
    )
    
    # 验证初始化
    assert wait_node.name == "等待节点"
    assert wait_node.description == "测试等待节点"
    assert wait_node.min_time == 1.0
    assert wait_node.max_time is None


def test_wait_time_node_with_random_range():
    """测试带有随机范围的等待时间节点初始化"""
    # 创建带随机范围的等待节点
    wait_node = WaitTimeNode(
        name="随机等待节点",
        description="测试随机等待节点",
        min_time=0.5,
        max_time=1.5
    )
    
    # 验证初始化
    assert wait_node.name == "随机等待节点"
    assert wait_node.description == "测试随机等待节点"
    assert wait_node.min_time == 0.5
    assert wait_node.max_time == 1.5


def test_wait_time_node_execution():
    """测试等待时间节点执行"""
    # 创建等待节点，设置较短的等待时间以加快测试
    wait_time = 0.1  # 100毫秒
    wait_node = WaitTimeNode(
        name="等待节点",
        min_time=wait_time
    )
    
    # 创建上下文
    context = create_workflow_context(
        workflow_id="test-id",
        workflow_name="测试工作流",
        execution_id="exec-id"
    )
    
    # 记录开始时间
    start_time = time.time()
    
    # 执行等待节点
    status = wait_node.run(context)
    
    # 记录结束时间
    end_time = time.time()
    elapsed_time = end_time - start_time
    
    # 验证结果
    assert status == NodeStatus.SUCCESS
    assert elapsed_time >= wait_time  # 确保至少等待了指定的时间


def test_wait_time_node_with_random_execution():
    """测试带有随机范围的等待时间节点执行"""
    # 创建带随机范围的等待节点，设置较短的等待时间以加快测试
    min_time = 0.05  # 50毫秒
    max_time = 0.15  # 150毫秒
    wait_node = WaitTimeNode(
        name="随机等待节点",
        min_time=min_time,
        max_time=max_time
    )
    
    # 创建上下文
    context = create_workflow_context(
        workflow_id="test-id",
        workflow_name="测试工作流",
        execution_id="exec-id"
    )
    
    # 记录开始时间
    start_time = time.time()
    
    # 执行等待节点
    status = wait_node.run(context)
    
    # 记录结束时间
    end_time = time.time()
    elapsed_time = end_time - start_time
    
    # 验证结果
    assert status == NodeStatus.SUCCESS
    # 确保至少等待了最小时间
    assert elapsed_time >= min_time
    # 确保不会等待超过最大时间太多（考虑到执行开销）
    assert elapsed_time <= (max_time + 0.1)  # 添加0.1秒容差


def test_wait_time_node_with_negative_time():
    """测试等待时间为负值的情况"""
    # 创建等待时间为负值的节点
    wait_node = WaitTimeNode(
        name="负值等待节点",
        min_time=-1.0
    )
    
    # 创建上下文
    context = create_workflow_context(
        workflow_id="test-id",
        workflow_name="测试工作流",
        execution_id="exec-id"
    )
    
    # 执行等待节点
    status = wait_node.run(context)
    
    # 验证结果
    assert status == NodeStatus.FAILED
    assert wait_node.last_error is not None
    assert "等待时间不能为负数" in wait_node.last_error


def test_wait_time_node_with_negative_max_time():
    """测试最大等待时间小于最小等待时间的情况"""
    # 创建最大等待时间小于最小等待时间的节点
    wait_node = WaitTimeNode(
        name="无效时间范围节点",
        min_time=1.0,
        max_time=0.5
    )
    
    # 创建上下文
    context = create_workflow_context(
        workflow_id="test-id",
        workflow_name="测试工作流",
        execution_id="exec-id"
    )
    
    # 执行等待节点
    status = wait_node.run(context)
    
    # 验证结果
    assert status == NodeStatus.FAILED
    assert wait_node.last_error is not None
    assert "最大等待时间必须大于或等于最小等待时间" in wait_node.last_error