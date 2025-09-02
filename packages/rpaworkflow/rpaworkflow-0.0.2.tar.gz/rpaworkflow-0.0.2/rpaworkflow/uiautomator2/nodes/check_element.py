#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
检查元素节点
"""

from typing import Dict, Any, Optional

from rpaworkflow.uiautomator2.nodes.base import U2BaseNode
from rpaworkflow.uiautomator2.workflow_context import CONTEXT
from rpaworkflow.node import DataStorageNode


class CheckElementNode(U2BaseNode, DataStorageNode):
    """检查元素节点

    用于检查UI元素是否存在
    将检查结果存储到上下文中
    """

    def __init__(self,
                 name: str = "检查元素",
                 description: str = "检查元素存在性",
                 store_to_key: str = "element_check_result",
                 selector: Optional[Dict[str, Any]] = None,
                 expected_exists: bool = True,
                 timeout: int = 5,
                 **kwargs):
        super().__init__(name, description, output_key=store_to_key, **kwargs)
        self.selector = selector
        self.expected_exists = expected_exists
        self.timeout = timeout

    def execute(self, context: CONTEXT) -> None:
        """执行元素检查

        Args:
            context: 工作流上下文
        """
        # 从上下文或构造函数获取参数
        selector = self.selector
        expected_exists = self.expected_exists
        timeout = self.timeout

        if not selector:
            raise ValueError("必须指定selector")

        # 检查元素是否存在
        if expected_exists:
            exists = self.find_element(context, **selector).wait(timeout=timeout)
        else:
            exists = not self.find_element(context, **selector).exists

        if exists == expected_exists:
            self.logger.info(f"元素检查通过: {selector}, 期望存在: {expected_exists}")
        else:
            raise Exception(f"元素检查失败: {selector}, 期望存在: {expected_exists}, 实际: {exists}")

        # 存储检查结果
        self.store_data(context, exists)
