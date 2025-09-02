#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
点击节点
"""
import random
from typing import Dict, Any, Optional, Tuple

from rpaworkflow.uiautomator2.nodes.base import U2BaseNode
from rpaworkflow.uiautomator2.workflow_context import CONTEXT
from rpaworkflow.node import ActionNode


class ClickNode(U2BaseNode, ActionNode):
    """点击节点

    用于点击指定元素或坐标
    不返回数据，只执行点击操作
    """

    def __init__(self,
                 name: str = "点击操作",
                 description: str = "点击指定元素或坐标",
                 selector: Optional[Dict[str, Any]] = None,
                 coordinates: Optional[Tuple[int, int]] = None,
                 random_click: bool = False,
                 wait_timeout: int = 10,
                 device_id: Optional[str] = None,
                 **kwargs):
        super().__init__(name, description, device_id=device_id, **kwargs)
        self.selector = selector
        self.coordinates = coordinates
        self.wait_timeout = wait_timeout
        self.random_click = random_click

    def execute(self, context: CONTEXT) -> None:
        """执行点击操作

        Args:
            context: 工作流上下文
        """
        # 从上下文或构造函数获取参数
        selector = self.selector
        coordinates = self.coordinates
        wait_timeout = self.wait_timeout

        if not selector and not coordinates:
            raise ValueError("必须指定selector或coordinates中的一个")

        device = self.get_device(context)

        if selector:
            # 等待元素出现
            if not self.wait_for_element(context, selector, wait_timeout):
                raise Exception(f"元素未找到: {selector}")

            # 点击元素
            element = self.find_element(context, **selector)
            # 随机点击
            if self.random_click:
                # 随机点击坐标
                bounds = element.info['bounds']
                left, top, right, bottom = bounds['left'], bounds['top'], bounds['right'], bounds['bottom']
                x, y = random.randint(left + 5, right - 5), random.randint(top + 5, bottom - 5)
                device.click(x, y)
            else:
                element.click()
            self.logger.info(f"点击元素成功: {selector}")

        elif coordinates:
            # 点击坐标
            x, y = coordinates
            device.click(x, y)
            self.logger.info(f"点击坐标成功: ({x}, {y})")
