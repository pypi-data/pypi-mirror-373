#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
点击节点
"""

from typing import Optional, Tuple

from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import TimeoutException
from rpaworkflow.node import ActionNode
from rpaworkflow.selenium.nodes.base import SeleniumBaseNode
from rpaworkflow.selenium.workflow_context import CONTEXT


class ClickNode(SeleniumBaseNode, ActionNode):
    """点击节点

    用于点击指定元素
    不返回数据，只执行点击操作
    """

    def __init__(self,
                 name: str = "点击操作",
                 description: str = "点击指定元素",
                 by: str = None,
                 value: str = None,
                 coordinates: Optional[Tuple[int, int]] = None,
                 wait_timeout: int = 10,
                 js_click: bool = False,
                 double_click: bool = False,
                 right_click: bool = False,
                 **kwargs):
        super().__init__(name, description, **kwargs)
        self.by = by
        self.value = value
        self.coordinates = coordinates
        self.wait_timeout = wait_timeout
        self.js_click = js_click
        self.double_click = double_click
        self.right_click = right_click

    def execute(self, context: CONTEXT) -> None:
        """执行点击操作

        Args:
            context: 工作流上下文
        """
        # 从上下文或构造函数获取参数
        by = self.by
        value = self.value
        coordinates = self.coordinates
        wait_timeout = self.wait_timeout
        js_click = self.js_click
        double_click = self.double_click
        right_click = self.right_click

        if not ((by and value) or coordinates):
            raise ValueError("必须指定by和value，或者coordinates")

        driver = self.get_driver(context)
        actions = ActionChains(driver)

        if by and value:
            # 等待元素可点击
            try:
                element = self.wait_for_element_clickable(context, by, value, wait_timeout)
            except TimeoutException as e:
                element = self.find_element(context, by, value)

            # 存储元素到上下文
            context['last_element'] = element

            # 执行点击
            if js_click:
                # 使用JavaScript点击
                driver.execute_script("arguments[0].click();", element)
            elif double_click:
                # 双击
                actions.double_click(element).perform()
            elif right_click:
                # 右键点击
                actions.context_click(element).perform()
            else:
                # 普通点击
                element.click()

            self.logger.info(f"点击元素: {by}={value}")

        elif coordinates:
            # 坐标点击
            x, y = coordinates
            actions.move_by_offset(x, y).click().perform()
            context['last_click_position'] = coordinates
            self.logger.info(f"点击坐标: ({x}, {y})")
