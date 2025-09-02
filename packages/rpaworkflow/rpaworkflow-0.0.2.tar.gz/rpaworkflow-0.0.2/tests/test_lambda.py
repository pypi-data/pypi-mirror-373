import pytest
from typing import Dict, Any, Optional

from rpaworkflow.nodes.lambda_ import LambdaActionNode, LambdaDataStorageNode
from rpaworkflow.node import NodeStatus
from rpaworkflow.context import WorkflowContext, create_workflow_context
from rpaworkflow.exception import NodeError


def test_lambda_action_node_initialization():
    """测试Lambda动作节点初始化"""
    # 创建Lambda函数
    def test_lambda(context):
        return "测试成功"
    
    # 创建Lambda动作节点
    lambda_node = LambdaActionNode(
        name="Lambda动作节点",
        description="测试Lambda动作节点",
        lambda_func=test_lambda
    )
    
    # 验证初始化
    assert lambda_node.name == "Lambda动作节点"
    assert lambda_node.description == "测试Lambda动作节点"
    assert lambda_node.lambda_func == test_lambda


def test_lambda_action_node_execution():
    """测试Lambda动作节点执行"""
    # 创建一个会修改上下文的Lambda函数
    def test_lambda(context):
        context["lambda_executed"] = True
        return "测试成功"
    
    # 创建Lambda动作节点
    lambda_node = LambdaActionNode(
        name="Lambda动作节点",
        lambda_func=test_lambda
    )
    
    # 创建上下文
    context = create_workflow_context(
        workflow_id="test-id",
        workflow_name="测试工作流",
        execution_id="exec-id"
    )
    
    # 执行Lambda动作节点
    status = lambda_node.run(context)
    
    # 验证结果
    assert status == NodeStatus.SUCCESS
    assert context.get("lambda_executed") is True


def test_lambda_action_node_execution_failure():
    """测试Lambda动作节点执行失败"""
    # 创建一个会抛出异常的Lambda函数
    def failing_lambda(context):
        raise ValueError("Lambda测试异常")
    
    # 创建Lambda动作节点
    lambda_node = LambdaActionNode(
        name="失败Lambda节点",
        lambda_func=failing_lambda
    )
    
    # 创建上下文
    context = create_workflow_context(
        workflow_id="test-id",
        workflow_name="测试工作流",
        execution_id="exec-id"
    )
    
    # 执行Lambda动作节点
    status = lambda_node.run(context)
    
    # 验证结果
    assert status == NodeStatus.FAILED
    assert lambda_node.last_error is not None
    assert "Lambda测试异常" in lambda_node.last_error


def test_lambda_action_node_without_lambda_func():
    """测试没有设置Lambda函数的Lambda动作节点"""
    # 创建没有设置Lambda函数的节点
    lambda_node = LambdaActionNode(
        name="无函数Lambda节点"
    )
    
    # 创建上下文
    context = create_workflow_context(
        workflow_id="test-id",
        workflow_name="测试工作流",
        execution_id="exec-id"
    )
    
    # 执行Lambda动作节点
    status = lambda_node.run(context)
    
    # 验证结果
    assert status == NodeStatus.FAILED
    assert lambda_node.last_error is not None
    assert "Lambda函数不能为空" in lambda_node.last_error


def test_lambda_data_storage_node_initialization():
    """测试Lambda数据存储节点初始化"""
    # 创建Lambda函数
    def test_lambda(context):
        return "测试数据"
    
    # 创建Lambda数据存储节点
    lambda_node = LambdaDataStorageNode(
        name="Lambda存储节点",
        description="测试Lambda存储节点",
        lambda_func=test_lambda,
        output_key="lambda_result"
    )
    
    # 验证初始化
    assert lambda_node.name == "Lambda存储节点"
    assert lambda_node.description == "测试Lambda存储节点"
    assert lambda_node.lambda_func == test_lambda
    assert lambda_node.output_key == "lambda_result"


def test_lambda_data_storage_node_execution():
    """测试Lambda数据存储节点执行"""
    # 创建返回数据的Lambda函数
    def test_lambda(context):
        return "测试数据结果"
    
    # 创建Lambda数据存储节点
    lambda_node = LambdaDataStorageNode(
        name="Lambda存储节点",
        lambda_func=test_lambda,
        output_key="lambda_result"
    )
    
    # 创建上下文
    context = create_workflow_context(
        workflow_id="test-id",
        workflow_name="测试工作流",
        execution_id="exec-id"
    )
    
    # 执行Lambda数据存储节点
    status = lambda_node.run(context)
    
    # 验证结果
    assert status == NodeStatus.SUCCESS
    assert context.get("lambda_result") == "测试数据结果"


def test_lambda_data_storage_node_execution_failure():
    """测试Lambda数据存储节点执行失败"""
    # 创建一个会抛出异常的Lambda函数
    def failing_lambda(context):
        raise ValueError("Lambda存储测试异常")
    
    # 创建Lambda数据存储节点
    lambda_node = LambdaDataStorageNode(
        name="失败Lambda存储节点",
        lambda_func=failing_lambda,
        output_key="lambda_result"
    )
    
    # 创建上下文
    context = create_workflow_context(
        workflow_id="test-id",
        workflow_name="测试工作流",
        execution_id="exec-id"
    )
    
    # 执行Lambda数据存储节点
    status = lambda_node.run(context)
    
    # 验证结果
    assert status == NodeStatus.FAILED
    assert lambda_node.last_error is not None
    assert "Lambda存储测试异常" in lambda_node.last_error
    assert "lambda_result" not in context


def test_lambda_data_storage_node_without_lambda_func():
    """测试没有设置Lambda函数的Lambda数据存储节点"""
    # 创建没有设置Lambda函数的节点
    lambda_node = LambdaDataStorageNode(
        name="无函数Lambda存储节点",
        output_key="lambda_result"
    )
    
    # 创建上下文
    context = create_workflow_context(
        workflow_id="test-id",
        workflow_name="测试工作流",
        execution_id="exec-id"
    )
    
    # 执行Lambda数据存储节点
    status = lambda_node.run(context)
    
    # 验证结果
    assert status == NodeStatus.FAILED
    assert lambda_node.last_error is not None
    assert "Lambda函数不能为空" in lambda_node.last_error