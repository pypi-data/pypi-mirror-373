import pytest
from typing import Dict, Any, Optional

from rpaworkflow.nodes.empty import EmptyNode
from rpaworkflow.node import NodeStatus
from rpaworkflow.context import WorkflowContext, create_workflow_context


def test_empty_node_initialization():
    """测试空节点初始化"""
    # 创建空节点
    empty_node = EmptyNode(
        name="测试空节点",
        description="测试空节点描述"
    )
    
    # 验证初始化
    assert empty_node.name == "测试空节点"
    assert empty_node.description == "测试空节点描述"


def test_empty_node_execution():
    """测试空节点执行"""
    # 创建空节点
    empty_node = EmptyNode()
    
    # 创建上下文
    context = create_workflow_context(
        workflow_id="test-id",
        workflow_name="测试工作流",
        execution_id="exec-id"
    )
    
    # 执行空节点
    status = empty_node.run(context)
    
    # 验证结果
    assert status == NodeStatus.SUCCESS
    assert empty_node.status == NodeStatus.SUCCESS


def test_empty_node_with_additional_parameters():
    """测试带有额外参数的空节点"""
    # 创建带有额外参数的空节点
    empty_node = EmptyNode(
        name="自定义空节点",
        description="自定义描述",
        max_retries=3,
        timeout=10.0
    )
    
    # 验证初始化
    assert empty_node.name == "自定义空节点"
    assert empty_node.description == "自定义描述"
    assert empty_node.max_retries == 3
    assert empty_node.timeout == 10.0
    
    # 创建上下文
    context = create_workflow_context(
        workflow_id="test-id",
        workflow_name="测试工作流",
        execution_id="exec-id"
    )
    
    # 执行空节点
    status = empty_node.run(context)
    
    # 验证结果
    assert status == NodeStatus.SUCCESS