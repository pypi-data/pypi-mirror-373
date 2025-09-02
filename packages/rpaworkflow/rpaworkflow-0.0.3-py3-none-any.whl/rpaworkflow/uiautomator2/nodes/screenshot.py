#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
截图节点
"""
import os
import time
from typing import Optional
from loguru import logger

from rpaworkflow.uiautomator2.nodes.base import U2BaseNode
from rpaworkflow.uiautomator2.workflow_context import CONTEXT
from rpaworkflow.node import DataStorageNode


class ScreenshotNode(U2BaseNode, DataStorageNode):
    """截图节点

    用于截取屏幕截图并存储路径到指定键
    """

    def __init__(self,
                 name: str = "截图操作",
                 description: str = "截取屏幕截图",
                 output_key: str = "screenshot_path",
                 save_path: Optional[str] = None,
                 device_id: Optional[str] = None,
                 **kwargs):
        super().__init__(name, description, device_id=device_id, output_key=output_key, **kwargs)
        self.save_path = save_path

    def take_screenshot(self, context: CONTEXT, save_path: Optional[str] = None) -> str:
        """截取屏幕截图

        Args:
            context: 上下文
            save_path: 保存路径，如果不指定则自动生成

        Returns:
            str: 截图文件路径
        """
        device = self.get_device(context)

        if save_path is None:
            timestamp = int(time.time())
            save_path = f"screenshots/screenshot_{timestamp}.png"

        # 确保目录存在
        os.makedirs(os.path.dirname(save_path), exist_ok=True)

        # 截图
        device.screenshot(save_path)
        logger.debug(f"截图已保存: {save_path}")

        return save_path

    def execute(self, context: CONTEXT) -> None:
        """执行截图操作

        Args:
            context: 工作流上下文
        """
        # 从上下文或构造函数获取参数
        save_path = self.save_path

        screenshot_path = self.take_screenshot(context, save_path)
        self.logger.info(f"截图已保存: {screenshot_path}")

        # 存储截图路径到指定键
        self.store_data(context, screenshot_path)
