#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
启动应用节点
"""

import time
from typing import Optional

from rpaworkflow.uiautomator2.nodes.base import U2BaseNode
from rpaworkflow.uiautomator2.workflow_context import CONTEXT
from rpaworkflow.node import DataStorageNode


class LaunchAppNode(U2BaseNode, DataStorageNode):
    """启动应用节点

    用于启动Android应用
    将应用信息存储到上下文中
    """

    def __init__(self,
                 name: str = "启动应用",
                 description: str = "启动Android应用",
                 store_to_key: str = "current_app",
                 package_name: Optional[str] = None,
                 activity: Optional[str] = None,
                 device_id: Optional[str] = None,
                 **kwargs):
        super().__init__(name, description, output_key=store_to_key, device_id=device_id, **kwargs)
        self.package_name = package_name
        self.activity = activity

    def execute(self, context: CONTEXT) -> None:
        """执行应用启动

        Args:
            context: 工作流上下文
        """
        package_name = self.package_name
        activity = self.activity

        if not package_name:
            raise ValueError("必须指定package_name")

        device = self.get_device(context)

        # 启动应用
        if activity:
            device.app_start(package_name, activity)
        else:
            device.app_start(package_name)

        # 等待应用启动
        time.sleep(3)

        # 检查应用是否启动成功
        current_app = device.app_current()
        if current_app['package'] == package_name:
            self.logger.info(f"应用启动成功: {package_name}")

            # 存储应用信息
            self.store_data(context, current_app)
        else:
            raise Exception(f"应用启动失败，当前应用: {current_app['package']}")
