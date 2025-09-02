#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
连接设备节点
"""

from typing import Optional

import uiautomator2 as u2

from rpaworkflow.uiautomator2.nodes.base import U2BaseNode
from rpaworkflow.context import WorkflowContext
from rpaworkflow.node import DataStorageNode


class ConnectDeviceNode(U2BaseNode, DataStorageNode):
    """连接设备节点

    用于连接Android设备并获取设备信息
    将设备信息存储到上下文中
    """

    def __init__(self,
                 name: str = "连接设备",
                 description: str = "连接到Android设备",
                 device_id: Optional[str] = None,
                 **kwargs):
        super().__init__(name, description, output_key='device', device_id=device_id, **kwargs)

    def execute(self, context: WorkflowContext) -> None:
        """执行设备连接

        Args:
            context: 工作流上下文
        """
        if self.device_id:
            device = u2.connect(self.device_id)
        else:
            device = u2.connect()

        self.logger.info(f"设备连接成功: {device.serial}")

        # 存储设备信息到指定键
        self.store_data(context, device)

