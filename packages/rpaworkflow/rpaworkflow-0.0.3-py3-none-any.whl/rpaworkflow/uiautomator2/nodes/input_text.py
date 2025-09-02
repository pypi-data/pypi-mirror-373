#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
输入文本节点
"""

import time
from typing import Dict, Any, Optional

from rpaworkflow.uiautomator2.nodes.base import U2BaseNode
from rpaworkflow.uiautomator2.workflow_context import CONTEXT
from rpaworkflow.node import ActionNode


class InputTextNode(U2BaseNode, ActionNode):
    """输入文本节点

    用于在指定输入框中输入文本
    不返回数据，只执行输入操作
    """

    def __init__(self,
                 name: str = "输入文本",
                 description: str = "输入文本到指定元素",
                 text: Optional[str] = None,
                 selector: Optional[Dict[str, Any]] = None,
                 clear_first: bool = True,
                 wait_timeout: int = 10,
                 device_id: Optional[str] = None,
                 **kwargs):
        super().__init__(name, description, device_id=device_id, **kwargs)
        self.text = text
        self.selector = selector
        self.clear_first = clear_first
        self.wait_timeout = wait_timeout

    def execute(self, context: CONTEXT) -> None:
        """执行输入文本操作

        Args:
            context: 工作流上下文
        """
        # 从上下文或构造函数获取参数
        text = self.text
        selector = self.selector
        clear_first = self.clear_first
        wait_timeout = self.wait_timeout

        if not text:
            raise ValueError("必须提供text参数")
        if not selector:
            raise ValueError("必须提供selector参数")

        # 等待输入框出现
        if not self.wait_for_element(context, selector, wait_timeout):
            raise Exception(f"输入框未找到: {selector}")

        # 获取输入框
        input_element = self.find_element(context, **selector)

        # 点击输入框
        input_element.click()
        time.sleep(0.5)

        # 清空输入框
        if clear_first:
            input_element.clear_text()

        # 输入文本
        input_element.send_keys(text)
        self.logger.info(f"文本输入成功: {text}")
