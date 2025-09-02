#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
输入文本节点
"""

from selenium.webdriver.common.keys import Keys

from rpaworkflow.node import ActionNode
from rpaworkflow.selenium.nodes.base import SeleniumBaseNode
from rpaworkflow.selenium.workflow_context import CONTEXT


class InputTextNode(SeleniumBaseNode, ActionNode):
    """输入文本节点

    用于在指定元素中输入文本
    不返回数据，只执行输入操作
    """

    def __init__(self,
                 name: str = "输入文本",
                 description: str = "在指定元素中输入文本",
                 by: str = None,
                 value: str = None,
                 text: str = None,
                 clear_first: bool = True,
                 press_enter: bool = False,
                 wait_timeout: int = 10,
                 **kwargs):
        super().__init__(name, description, **kwargs)
        self.by = by
        self.value = value
        self.text = text
        self.clear_first = clear_first
        self.press_enter = press_enter
        self.wait_timeout = wait_timeout

    def execute(self, context: CONTEXT) -> None:
        """执行输入文本操作

        Args:
            context: 工作流上下文
        """
        # 从上下文或构造函数获取参数
        by = self.by
        value = self.value
        text = self.text
        clear_first = self.clear_first
        press_enter = self.press_enter
        wait_timeout = self.wait_timeout

        if not (by and value):
            raise ValueError("必须指定by和value")
        
        if not text:
            raise ValueError("必须指定要输入的文本")

        # 等待元素可见
        element = self.wait_for_element_visible(context, by, value, wait_timeout)
        
        # 存储元素到上下文
        context['last_element'] = element
        
        # 清空输入框
        if clear_first:
            element.clear()
        
        # 输入文本
        element.send_keys(text)
        
        # 按回车键
        if press_enter:
            element.send_keys(Keys.RETURN)
        
        # 存储输入的文本到上下文
        context['last_input_text'] = text
        
        self.logger.info(f"输入文本: {text} 到元素: {by}={value}")