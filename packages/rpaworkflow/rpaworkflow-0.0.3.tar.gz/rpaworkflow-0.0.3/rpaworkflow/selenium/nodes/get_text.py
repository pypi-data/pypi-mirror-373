#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
获取文本节点
"""

from typing import Optional

from rpaworkflow.node import DataStorageNode
from rpaworkflow.selenium.nodes.base import SeleniumBaseNode
from rpaworkflow.selenium.workflow_context import CONTEXT


class GetTextNode(SeleniumBaseNode, DataStorageNode):
    """获取文本节点

    用于获取指定元素的文本内容
    将文本内容存储到上下文中
    """

    def __init__(self,
                 name: str = "获取文本",
                 description: str = "获取指定元素的文本内容",
                 by: str = None,
                 value: str = None,
                 attribute: Optional[str] = None,
                 multiple: bool = False,
                 wait_timeout: int = 10,
                 **kwargs):
        super().__init__(name, description, output_key='last_text', **kwargs)
        self.by = by
        self.value = value
        self.attribute = attribute
        self.multiple = multiple
        self.wait_timeout = wait_timeout

    def execute(self, context: CONTEXT) -> None:
        """执行获取文本操作

        Args:
            context: 工作流上下文
        """
        # 从上下文或构造函数获取参数
        by = self.by
        value = self.value
        attribute = self.attribute
        multiple = self.multiple
        wait_timeout = self.wait_timeout

        if not (by and value):
            raise ValueError("必须指定by和value")

        if multiple:
            # 获取多个元素的文本
            elements = self.find_elements(context, by, value, wait_timeout)
            
            if not elements:
                raise ValueError(f"未找到元素: {by}={value}")
            
            texts = []
            for element in elements:
                if attribute:
                    text = element.get_attribute(attribute)
                else:
                    text = element.text
                texts.append(text)
            
            # 存储元素列表到上下文
            context['last_elements'] = elements
            
            # 存储文本列表到上下文
            self.store_data(context, texts)
            
            self.logger.info(f"获取到 {len(texts)} 个元素的文本")
            
        else:
            # 获取单个元素的文本
            element = self.wait_for_element_visible(context, by, value, wait_timeout)
            
            # 存储元素到上下文
            context['last_element'] = element
            
            # 获取文本或属性值
            if attribute:
                text = element.get_attribute(attribute)
                context['last_attribute'] = text
                self.logger.info(f"获取元素属性 {attribute}: {text}")
            else:
                text = element.text
                self.logger.info(f"获取元素文本: {text}")
            
            # 存储文本到上下文
            self.store_data(context, text)