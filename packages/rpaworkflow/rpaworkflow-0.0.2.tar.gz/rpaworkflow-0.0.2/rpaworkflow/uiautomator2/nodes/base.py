#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
U2 基础节点类

提供 uiautomator2 的基础功能和设备连接管理。
"""
import abc
from typing import Dict, Any, Optional, Union, Generic

import uiautomator2 as u2

from rpaworkflow.uiautomator2.workflow_context import CONTEXT
from rpaworkflow.node import WorkflowNode


class DeviceLocator:
    """设备定位类型"""

    def __init__(self, device: u2.Device):
        self.device = device

    def __call__(self, **kwargs):
        if 'xpath' in kwargs:
            locator = kwargs.pop('xpath')
            return self.device.xpath(locator)
        return self.device(**kwargs)


class U2BaseNode(WorkflowNode, Generic[CONTEXT]):
    """U2 基础节点类

    提供 uiautomator2 的基础功能和设备连接管理。
    """

    def __init__(self, name: str, description: str, device_id: Optional[str] = None, **kwargs):
        super().__init__(name, description, **kwargs)
        self.device_id = device_id

    def get_device(self, context: CONTEXT) -> u2.Device:
        return context['device']

    def find_element(self, context: CONTEXT, **kwargs) -> Union[u2.UiObject, u2.xpath.XPathSelector]:
        device = context['device']
        return DeviceLocator(device)(**kwargs)

    def wait_for_element(self, context: CONTEXT, selector: Dict[str, Any], timeout: int = 10) -> bool:
        """等待元素出现

        Args:
            context: 上下文对象
            selector: 元素选择器
            timeout: 超时时间（秒）

        Returns:
            bool: 是否找到元素
        """
        element = self.find_element(context, **selector)
        try:
            return element.wait(timeout=timeout)
        except Exception:
            return False
