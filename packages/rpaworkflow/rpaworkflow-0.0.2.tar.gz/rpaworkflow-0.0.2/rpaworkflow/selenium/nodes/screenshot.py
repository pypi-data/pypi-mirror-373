#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
截图节点
"""

import os
import time
from typing import Optional

from rpaworkflow.selenium.nodes.base import SeleniumBaseNode
from rpaworkflow.selenium.workflow_context import CONTEXT
from rpaworkflow.node import DataStorageNode


class ScreenshotNode(SeleniumBaseNode, DataStorageNode):
    """截图节点

    用于截取当前页面或元素的截图
    将截图路径存储到上下文中
    """

    def __init__(self,
                 name: str = "截图操作",
                 description: str = "截取当前页面或元素的截图",
                 by: Optional[str] = None,
                 value: Optional[str] = None,
                 save_path: Optional[str] = None,
                 filename: Optional[str] = None,
                 **kwargs):
        super().__init__(name, description, output_key='last_screenshot', **kwargs)
        self.by = by
        self.value = value
        self.save_path = save_path
        self.filename = filename

    def execute(self, context: CONTEXT) -> None:
        """执行截图操作

        Args:
            context: 工作流上下文
        """
        # 从上下文或构造函数获取参数
        by = self.by
        value = self.value
        save_path = self.save_path or os.path.join(os.getcwd(), 'screenshots')
        filename = self.filename or f"screenshot_{int(time.time())}.png"

        # 确保保存路径存在
        os.makedirs(save_path, exist_ok=True)
        
        # 完整的文件路径
        file_path = os.path.join(save_path, filename)
        
        driver = self.get_driver(context)
        
        # 截取元素或整个页面的截图
        if by and value:
            try:
                # 查找元素
                element = self.find_element(context, by, value)
                # 截取元素截图
                element.screenshot(file_path)
                self.logger.info(f"元素截图已保存: {file_path}")
            except Exception as e:
                self.logger.error(f"元素截图失败: {str(e)}")
                # 如果元素截图失败，退回到整页截图
                driver.save_screenshot(file_path)
                self.logger.info(f"页面截图已保存: {file_path}")
        else:
            # 截取整个页面的截图
            driver.save_screenshot(file_path)
            self.logger.info(f"页面截图已保存: {file_path}")
        
        # 存储截图路径到上下文
        self.store_data(context, file_path)