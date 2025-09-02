#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
滚动节点（在可滚动容器中滚动）
"""

from typing import Dict, Any, Optional

from rpaworkflow.uiautomator2.nodes.base import U2BaseNode
from rpaworkflow.uiautomator2.workflow_context import CONTEXT
from rpaworkflow.node import ActionNode


class ScrollNode(U2BaseNode, ActionNode):
    """滚动节点（在可滚动容器中滚动）

    用于在屏幕或指定容器中执行滚动操作
    不返回数据，只执行滚动动作
    """

    def __init__(self,
                 name: str = "滚动操作",
                 description: str = "容器滚动",
                 selector: Optional[Dict[str, Any]] = None,
                 direction: str = "down",
                 steps: int = 3,
                 device_id: Optional[str] = None,
                 **kwargs):
        super().__init__(name, description, device_id=device_id, **kwargs)
        self.selector = selector
        self.direction = direction.lower()
        self.steps = steps

    def execute(self, context: CONTEXT) -> None:
        """执行滚动操作

        Args:
            context: 工作流上下文
        """
        # 从上下文或构造函数获取参数
        selector = self.selector
        direction = self.direction
        steps = self.steps

        if direction not in ['up', 'down', 'left', 'right']:
            raise ValueError("direction必须是: up, down, left, right")

        device = self.get_device(context)

        if selector:
            # 在指定容器中滚动
            if not self.wait_for_element(context, selector, 10):
                raise Exception(f"滚动容器未找到: {selector}")

            element = self.find_element(context, **selector)

            if direction == "up":
                element.scroll.up(steps=steps)
            elif direction == "down":
                element.scroll.down(steps=steps)
            elif direction == "left":
                element.scroll.left(steps=steps)
            elif direction == "right":
                element.scroll.right(steps=steps)

            self.logger.info(f"容器滚动完成: {direction}, 步数: {steps}")
        else:
            # 在整个屏幕中滚动
            if direction == "up":
                device.scroll.up(steps=steps)
            elif direction == "down":
                device.scroll.down(steps=steps)
            elif direction == "left":
                device.scroll.left(steps=steps)
            elif direction == "right":
                device.scroll.right(steps=steps)

            self.logger.info(f"屏幕滚动完成: {direction}, 步数: {steps}")
