#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
等待节点
"""

import time
from typing import Dict, Any, Optional

from rpaworkflow.uiautomator2.nodes.base import U2BaseNode
from rpaworkflow.uiautomator2.workflow_context import CONTEXT
from rpaworkflow.node import ActionNode


class WaitNode(U2BaseNode, ActionNode):
    """等待节点

    用于等待时间、元素出现或元素消失
    不返回数据，只执行等待操作
    """

    def __init__(self,
                 name: str = "等待操作",
                 description: str = "等待指定条件",
                 wait_type: str = "time",
                 duration: float = 1.0,
                 selector: Optional[Dict[str, Any]] = None,
                 timeout: int = 10,
                 device_id: Optional[str] = None,
                 **kwargs):
        super().__init__(name, description, device_id=device_id, **kwargs)
        self.wait_type = wait_type.lower()
        self.duration = duration
        self.selector = selector
        self.timeout = timeout

    def execute(self, context: CONTEXT) -> None:
        """执行等待操作

        Args:
            context: 工作流上下文
        """
        # 从上下文或构造函数获取参数
        wait_type = self.wait_type
        duration = self.duration
        selector = self.selector
        timeout = self.timeout

        if wait_type not in ['time', 'element', 'element_gone']:
            raise ValueError("wait_type必须是: time, element, element_gone")

        if wait_type == "time":
            # 等待指定时间
            time.sleep(duration)
            self.logger.info(f"等待时间完成: {duration}秒")

        elif wait_type == "element":
            # 等待元素出现
            if not selector:
                raise ValueError("等待元素时必须指定selector")

            if self.wait_for_element(context, selector, timeout):
                self.logger.info(f"元素出现: {selector}")
            else:
                raise Exception(f"等待元素超时: {selector}")

        elif wait_type == "element_gone":
            # 等待元素消失
            if not selector:
                raise ValueError("等待元素消失时必须指定selector")

            start_time = time.time()

            while time.time() - start_time < timeout:
                if not self.find_element(context, **selector).exists:
                    self.logger.info(f"元素消失: {selector}")
                    return
                time.sleep(0.5)

            raise Exception(f"等待元素消失超时: {selector}")
