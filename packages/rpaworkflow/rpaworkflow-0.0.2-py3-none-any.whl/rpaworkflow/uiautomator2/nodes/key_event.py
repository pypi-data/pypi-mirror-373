#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
按键事件节点
"""

from typing import Optional

from rpaworkflow.uiautomator2.nodes.base import U2BaseNode
from rpaworkflow.uiautomator2.workflow_context import CONTEXT
from rpaworkflow.node import ActionNode


class KeyEventNode(U2BaseNode, ActionNode):
    """按键事件节点

    用于执行设备按键操作
    不返回数据，只执行按键动作
    """

    def __init__(self,
                 name: str = "按键操作",
                 description: str = "设备按键",
                 key: Optional[str] = None,
                 device_id: Optional[str] = None,
                 **kwargs):
        super().__init__(name, description, device_id=device_id, **kwargs)
        self.key = key

    def execute(self, context: CONTEXT) -> None:
        """执行按键操作

        Args:
            context: 工作流上下文
        """
        # 从上下文或构造函数获取参数
        key = self.key

        if not key:
            raise ValueError("必须指定按键")

        device = self.get_device(context)
        device.press(key)
        self.logger.info(f"按键操作完成: {key}")
