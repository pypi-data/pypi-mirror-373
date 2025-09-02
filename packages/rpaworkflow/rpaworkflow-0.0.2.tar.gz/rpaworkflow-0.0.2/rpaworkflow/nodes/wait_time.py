#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
等待时间节点

提供等待指定时间的功能
"""

import time
import random
from typing import Optional
from ..node import ActionNode
from ..context import CONTEXT
from ..exception import NodeError


class WaitTimeNode(ActionNode):
    """
    等待时间节点

    用于在工作流中等待指定的时间
    不返回数据，只执行等待操作
    """

    def __init__(self,
                 name: str = "等待时间",
                 description: str = "等待指定时间",
                 min_time: Optional[float] = None,
                 max_time: Optional[float] = None,
                 **kwargs):
        super().__init__(name, description, **kwargs)
        self.min_time = min_time
        self.max_time = max_time

    def execute(self, context: CONTEXT) -> None:
        """
        执行等待操作

        Args:
            context: 工作流上下文
        """
        if self.max_time:
            # 随机等待
            min_time = self.min_time
            max_time = self.max_time

            if min_time is None or max_time is None:
                raise NodeError("随机等待模式需要提供 min_time 和 max_time 参数")

            if min_time < 0 or max_time < 0:
                raise NodeError("等待时间不能为负数")

            if min_time > max_time:
                raise NodeError("最大等待时间必须大于或等于最小等待时间")

            actual_wait_time = random.uniform(min_time, max_time)
        else:
            # 固定等待
            wait_time = self.min_time

            if wait_time is None:
                raise NodeError("固定等待模式需要提供 min_time 参数")

            if wait_time < 0:
                raise NodeError("等待时间不能为负数")

            actual_wait_time = wait_time

        self.logger.info(f"开始等待 {actual_wait_time:.2f} 秒")
        time.sleep(actual_wait_time)
        self.logger.info(f"等待 {actual_wait_time:.2f} 秒完成")
