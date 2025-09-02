#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Selenium 基础节点类

提供 Selenium 的基础功能和浏览器驱动管理。
"""
from typing import Any, Generic, List

from selenium.webdriver.remote.webdriver import WebDriver

from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from rpaworkflow.node import WorkflowNode
from rpaworkflow.selenium.workflow_context import CONTEXT


class ElementLocator:
    """元素定位类型"""

    def __init__(self, driver):
        self.driver = driver

    def __call__(self, by: str, value: str, multiple: bool = False, timeout: int = 0):
        """定位元素

        Args:
            by: 定位方式，可以是By.ID, By.XPATH等
            value: 定位值
            multiple: 是否查找多个元素
            timeout: 等待超时时间，0表示不等待

        Returns:
            WebElement或List[WebElement]
        """
        if timeout > 0:
            wait = WebDriverWait(self.driver, timeout)
            if multiple:
                return wait.until(EC.presence_of_all_elements_located((by, value)))
            else:
                return wait.until(EC.presence_of_element_located((by, value)))
        else:
            if multiple:
                return self.driver.find_elements(by, value)
            else:
                return self.driver.find_element(by, value)


class SeleniumBaseNode(WorkflowNode, Generic[CONTEXT]):
    """Selenium 基础节点类

    提供 Selenium 的基础功能和浏览器驱动管理。
    """

    def __init__(self, name: str, description: str, **kwargs):
        super().__init__(name, description, **kwargs)

    def get_driver(self, context: CONTEXT) -> WebDriver:
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
