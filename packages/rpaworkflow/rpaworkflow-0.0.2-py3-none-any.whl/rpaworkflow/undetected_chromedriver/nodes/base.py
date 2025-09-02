#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Undetected Chrome 基础节点类

提供 Undetected Chrome 的基础功能和浏览器驱动管理。
"""

from typing import Any, Generic, List

import undetected_chromedriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from rpaworkflow.node import WorkflowNode
from rpaworkflow.selenium.nodes.base import ElementLocator
from rpaworkflow.undetected_chromedriver.workflow_context import CONTEXT


class UndetectedChromeBaseNode(WorkflowNode[CONTEXT]):
    """Undetected Chrome 基础节点类

    提供 Undetected Chrome 的基础功能和浏览器驱动管理。
    继承自 WorkflowNode，复用 Selenium 的元素定位功能。
    """

    def __init__(self, name: str, description: str, **kwargs):
        super().__init__(name, description, **kwargs)

    def get_driver(self, context: CONTEXT) -> undetected_chromedriver.Chrome:
        """获取浏览器驱动

        Args:
            context: 工作流上下文

        Returns:
            WebDriver: 浏览器驱动
        """
        return context['driver']

    def find_element(self, context: CONTEXT, by: str, value: str, timeout: int = 0) -> WebElement:
        """查找单个元素

        Args:
            context: 工作流上下文
            by: 定位方式，可以是By.ID, By.XPATH等
            value: 定位值
            timeout: 等待超时时间，0表示不等待

        Returns:
            WebElement: 元素
        """
        driver = self.get_driver(context)
        return ElementLocator(driver)(by, value, multiple=False, timeout=timeout)

    def find_elements(self, context: CONTEXT, by: str, value: str, timeout: int = 0) -> List[WebElement]:
        """查找多个元素

        Args:
            context: 工作流上下文
            by: 定位方式，可以是By.ID, By.XPATH等
            value: 定位值
            timeout: 等待超时时间，0表示不等待

        Returns:
            List[WebElement]: 元素列表
        """
        driver = self.get_driver(context)
        return ElementLocator(driver)(by, value, multiple=True, timeout=timeout)

    def wait_for_element(self, context: CONTEXT, by: str, value: str, timeout: int = 10) -> WebElement:
        """等待元素出现

        Args:
            context: 工作流上下文
            by: 定位方式，可以是By.ID, By.XPATH等
            value: 定位值
            timeout: 等待超时时间

        Returns:
            WebElement: 元素
        """
        driver = self.get_driver(context)
        wait = WebDriverWait(driver, timeout)
        return wait.until(EC.presence_of_element_located((by, value)))

    def wait_for_element_visible(self, context: CONTEXT, by: str, value: str, timeout: int = 10) -> WebElement:
        """等待元素可见

        Args:
            context: 工作流上下文
            by: 定位方式，可以是By.ID, By.XPATH等
            value: 定位值
            timeout: 等待超时时间

        Returns:
            WebElement: 元素
        """
        driver = self.get_driver(context)
        wait = WebDriverWait(driver, timeout)
        return wait.until(EC.visibility_of_element_located((by, value)))

    def wait_for_element_clickable(self, context: CONTEXT, by: str, value: str, timeout: int = 10) -> WebElement:
        """等待元素可点击

        Args:
            context: 工作流上下文
            by: 定位方式，可以是By.ID, By.XPATH等
            value: 定位值
            timeout: 等待超时时间

        Returns:
            WebElement: 元素
        """
        driver = self.get_driver(context)
        wait = WebDriverWait(driver, timeout)
        return wait.until(EC.element_to_be_clickable((by, value)))

    def execute_script(self, context: CONTEXT, script: str, *args) -> Any:
        """执行JavaScript

        Args:
            context: 工作流上下文
            script: JavaScript代码
            args: 参数

        Returns:
            Any: 执行结果
        """
        driver = self.get_driver(context)
        return driver.execute_script(script, *args)

    def is_detection_evasion_enabled(self, context: CONTEXT) -> bool:
        """检查是否启用了反检测功能

        Args:
            context: 工作流上下文

        Returns:
            bool: 是否启用反检测
        """
        return context.get('detection_evasion_enabled', True)

    def get_stealth_status(self, context: CONTEXT) -> dict:
        """获取隐身模式状态

        Args:
            context: 工作流上下文

        Returns:
            dict: 隐身模式状态信息
        """
        return {
            'stealth_mode': context.get('stealth_mode', False),
            'webrtc_leak_prevention': context.get('webrtc_leak_prevention', False),
            'detection_evasion_enabled': context.get('detection_evasion_enabled', True),
            'user_agent': context.get('user_agent'),
            'viewport_size': context.get('viewport_size'),
        }

    def apply_stealth_settings(self, context: CONTEXT, driver) -> None:
        """应用隐身设置

        Args:
            context: 工作流上下文
            driver: 浏览器驱动
        """
        # 设置用户代理
        if context.get('user_agent'):
            driver.execute_cdp_cmd('Network.setUserAgentOverride', {
                'userAgent': context['user_agent']
            })

        # 设置视口大小
        if context.get('viewport_size'):
            width, height = context['viewport_size']
            driver.execute_cdp_cmd('Emulation.setDeviceMetricsOverride', {
                'width': width,
                'height': height,
                'deviceScaleFactor': 1,
                'mobile': False
            })

        # 设置时区
        if context.get('timezone'):
            driver.execute_cdp_cmd('Emulation.setTimezoneOverride', {
                'timezoneId': context['timezone']
            })

        # 设置地理位置
        if context.get('geolocation'):
            latitude, longitude = context['geolocation']
            driver.execute_cdp_cmd('Emulation.setGeolocationOverride', {
                'latitude': latitude,
                'longitude': longitude,
                'accuracy': 100
            })

        # 设置语言
        if context.get('language'):
            driver.execute_cdp_cmd('Emulation.setLocaleOverride', {
                'locale': context['language']
            })
