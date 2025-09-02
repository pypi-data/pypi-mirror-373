#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
滚动节点
"""

from typing import Optional

from selenium.webdriver.common.action_chains import ActionChains

from rpaworkflow.node import ActionNode
from rpaworkflow.selenium.nodes.base import SeleniumBaseNode
from rpaworkflow.selenium.workflow_context import CONTEXT


class ScrollNode(SeleniumBaseNode, ActionNode):
    """滚动节点

    用于滚动页面或元素
    不返回数据，只执行滚动操作
    """

    def __init__(self,
                 name: str = "滚动操作",
                 description: str = "滚动页面或元素",
                 scroll_type: str = "page",  # page, element, to_element
                 by: Optional[str] = None,
                 value: Optional[str] = None,
                 direction: str = "down",  # up, down, left, right
                 distance: int = 300,
                 x_offset: int = 0,
                 y_offset: int = 0,
                 **kwargs):
        super().__init__(name, description, **kwargs)
        self.scroll_type = scroll_type
        self.by = by
        self.value = value
        self.direction = direction
        self.distance = distance
        self.x_offset = x_offset
        self.y_offset = y_offset

    def execute(self, context: CONTEXT) -> None:
        """执行滚动操作

        Args:
            context: 工作流上下文
        """
        # 从上下文或构造函数获取参数
        scroll_type = self.scroll_type
        by = self.by
        value = self.value
        direction = self.direction
        distance = self.distance
        x_offset = self.x_offset
        y_offset = self.y_offset

        driver = self.get_driver(context)
        
        if scroll_type == "page":
            # 滚动页面
            if direction == "down":
                driver.execute_script(f"window.scrollBy(0, {distance});")
            elif direction == "up":
                driver.execute_script(f"window.scrollBy(0, -{distance});")
            elif direction == "left":
                driver.execute_script(f"window.scrollBy(-{distance}, 0);")
            elif direction == "right":
                driver.execute_script(f"window.scrollBy({distance}, 0);")
            else:
                raise ValueError(f"不支持的滚动方向: {direction}")
            
            # 获取当前滚动位置
            scroll_x = driver.execute_script("return window.pageXOffset;")
            scroll_y = driver.execute_script("return window.pageYOffset;")
            context['last_scroll_position'] = (scroll_x, scroll_y)
            
            self.logger.info(f"页面滚动: {direction}, 距离: {distance}")
            
        elif scroll_type == "element":
            # 滚动元素
            if not (by and value):
                raise ValueError("滚动元素时必须指定by和value")
            
            element = self.find_element(context, by, value)
            
            # 使用ActionChains滚动元素
            actions = ActionChains(driver)
            actions.move_to_element(element)
            
            if direction == "down":
                actions.scroll_by_amount(0, distance)
            elif direction == "up":
                actions.scroll_by_amount(0, -distance)
            elif direction == "left":
                actions.scroll_by_amount(-distance, 0)
            elif direction == "right":
                actions.scroll_by_amount(distance, 0)
            else:
                raise ValueError(f"不支持的滚动方向: {direction}")
            
            actions.perform()
            
            # 存储元素到上下文
            context['last_element'] = element
            
            self.logger.info(f"元素滚动: {by}={value}, 方向: {direction}, 距离: {distance}")
            
        elif scroll_type == "to_element":
            # 滚动到指定元素
            if not (by and value):
                raise ValueError("滚动到元素时必须指定by和value")
            
            element = self.find_element(context, by, value)
            
            # 滚动到元素位置
            driver.execute_script("arguments[0].scrollIntoView(true);", element)
            
            # 如果有偏移量，再进行微调
            if x_offset != 0 or y_offset != 0:
                driver.execute_script(f"window.scrollBy({x_offset}, {y_offset});")
            
            # 存储元素到上下文
            context['last_element'] = element
            
            self.logger.info(f"滚动到元素: {by}={value}")
            
        else:
            raise ValueError(f"不支持的滚动类型: {scroll_type}")