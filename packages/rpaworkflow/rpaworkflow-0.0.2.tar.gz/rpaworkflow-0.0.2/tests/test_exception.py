import pytest
from typing import Dict, Any, Optional

from rpaworkflow.exception import NodeError


# 测试用例
def test_node_error_initialization():
    """测试 NodeError 异常初始化"""
    # 创建 NodeError 异常
    error = NodeError("测试错误消息")
    
    # 验证初始化
    assert str(error) == "测试错误消息"
    assert isinstance(error, RuntimeError)


def test_node_error_with_node_name():
    """测试 NodeError 异常带有节点名称"""
    # 创建 NodeError 异常，带有节点名称
    error = NodeError("测试错误消息", node_name="测试节点")
    
    # 验证初始化
    assert str(error) == "[测试节点] 测试错误消息"


def test_node_error_inheritance():
    """测试 NodeError 异常继承关系"""
    # 创建 NodeError 异常
    error = NodeError("测试错误消息")
    
    # 验证继承关系
    assert isinstance(error, RuntimeError)
    assert isinstance(error, Exception)


def test_node_error_catching():
    """测试捕获 NodeError 异常"""
    # 创建一个会抛出 NodeError 的函数
    def raise_node_error():
        raise NodeError("测试错误消息", node_name="测试节点")
    
    # 尝试捕获异常
    try:
        raise_node_error()
        assert False, "应该抛出异常"
    except NodeError as e:
        assert str(e) == "[测试节点] 测试错误消息"
    except Exception:
        assert False, "应该捕获 NodeError 异常"


def test_node_error_as_exception():
    """测试将 NodeError 作为一般异常捕获"""
    # 创建一个会抛出 NodeError 的函数
    def raise_node_error():
        raise NodeError("测试错误消息")
    
    # 尝试捕获异常
    try:
        raise_node_error()
        assert False, "应该抛出异常"
    except Exception as e:
        assert isinstance(e, NodeError)
        assert str(e) == "测试错误消息"