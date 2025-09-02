# -*- coding: utf-8 -*-
"""
通用节点包

这个包提供了通用的工作流节点，不依赖于特定的自动化框架，
可以在任何工作流中使用。
"""

from .wait_time import WaitTimeNode
from .lambda_ import LambdaActionNode, LambdaDataStorageNode
from .condition import ConditionNode
from .empty import EmptyNode
from .error import ErrorNode, ErrorStorageNode
from .loop import LoopNode

__all__ = [
    'WaitTimeNode',
    'LambdaActionNode',
    'LambdaDataStorageNode',
    'ConditionNode',
    'EmptyNode',
    'ErrorNode',
    'ErrorStorageNode',
    'LoopNode',
]

# 版本信息
__version__ = '0.0.0' # 使用动态版本
__author__ = 'dragons96'
