#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
滑动节点
"""

import random
import time
from typing import Optional

from rpaworkflow.uiautomator2.nodes.base import U2BaseNode
from rpaworkflow.uiautomator2.workflow_context import CONTEXT
from rpaworkflow.node import ActionNode


class SwipeNode(U2BaseNode, ActionNode):
    """滑动节点

    用于在屏幕上执行滑动操作
    不返回数据，只执行滑动动作
    """

    def __init__(self,
                 name: str = "滑动操作",
                 description: str = "屏幕滑动",
                 direction: str = "up",
                 distance: float = 0.5,
                 duration: float = 0.5,
                 count: int = 1,
                 device_id: Optional[str] = None,
                 **kwargs):
        super().__init__(name, description, device_id=device_id, **kwargs)
        self.direction = direction.lower()
        self.distance = distance  # 滑动距离比例 (0-1)
        self.duration = duration  # 滑动持续时间
        self.count = count

    def execute(self, context: CONTEXT) -> None:
        """执行滑动操作

        Args:
            context: 工作流上下文
        """
        # 从上下文或构造函数获取参数
        direction = self.direction.lower()
        distance = self.distance
        duration = self.duration
        count = self.count

        if direction not in ['up', 'down', 'left', 'right']:
            raise ValueError("direction必须是: up, down, left, right")

        device = self.get_device(context)
        screen_width, screen_height = device.window_size()

        # 计算滑动起点和终点
        center_x = screen_width // 2
        center_y = screen_height // 2

        if direction == "up":
            start_y = int(screen_height * (0.5 + distance / 2))
            end_y = int(screen_height * (0.5 - distance / 2))
            start_point = (center_x, start_y)
            end_point = (center_x, end_y)
        elif direction == "down":
            start_y = int(screen_height * (0.5 - distance / 2))
            end_y = int(screen_height * (0.5 + distance / 2))
            start_point = (center_x, start_y)
            end_point = (center_x, end_y)
        elif direction == "left":
            start_x = int(screen_width * (0.5 + distance / 2))
            end_x = int(screen_width * (0.5 - distance / 2))
            start_point = (start_x, center_y)
            end_point = (end_x, center_y)
        elif direction == "right":
            start_x = int(screen_width * (0.5 - distance / 2))
            end_x = int(screen_width * (0.5 + distance / 2))
            start_point = (start_x, center_y)
            end_point = (end_x, center_y)
        else:
            raise ValueError("direction必须是: up, down, left, right")

        # 执行滑动
        for i in range(count):
            device.swipe(*start_point, *end_point, duration=duration)
            self.logger.debug(f"滑动 {i + 1}/{count}: {start_point} -> {end_point}")

            # 滑动间隔
            if i < count - 1:
                time.sleep(random.uniform(0.5, 1.5))

        self.logger.info(f"滑动完成: {direction} x{count}")
