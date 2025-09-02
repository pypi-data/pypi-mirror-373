#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
获取文本节点
"""

from typing import Dict, Any, Optional

from rpaworkflow.uiautomator2.nodes.base import U2BaseNode
from rpaworkflow.uiautomator2.workflow_context import CONTEXT
from rpaworkflow.node import DataStorageNode


class GetTextNode(U2BaseNode, DataStorageNode):
    """获取文本节点

    用于获取元素文本内容并存储到指定键
    """

    def __init__(self,
                 name: str = "获取文本",
                 description: str = "获取元素文本内容",
                 output_key: str = "text",
                 selector: Optional[Dict[str, Any]] = None,
                 wait_timeout: int = 10,
                 device_id: Optional[str] = None,
                 **kwargs):
        super().__init__(name, description, device_id=device_id, output_key=output_key, **kwargs)
        self.selector = selector
        self.wait_timeout = wait_timeout

    def execute(self, context: CONTEXT) -> None:
        """执行获取文本操作

        Args:
            context: 工作流上下文
        """
        # 从上下文或构造函数获取参数
        selector = self.selector
        wait_timeout = self.wait_timeout

        if not selector:
            raise ValueError("必须提供selector参数")

        # 等待元素出现
        if not self.wait_for_element(context, selector, wait_timeout):
            raise Exception(f"元素未找到: {selector}")

        # 获取文本
        element = self.find_element(context, **selector)
        text = element.get_text()
        self.logger.info(f"获取文本成功: {text}")

        # 存储文本到指定键
        self.store_data(context, text)

