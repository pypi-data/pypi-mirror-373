#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
文本获取节点
"""
from typing import Optional, Any, List, Dict

from rpaworkflow.node import DataStorageNode
from rpaworkflow.playwright.nodes.base import PlaywrightBaseNode
from rpaworkflow.playwright.workflow_context import CONTEXT


class GetTextNode(PlaywrightBaseNode, DataStorageNode):
    """获取文本节点

    用于获取元素的文本内容
    """

    def __init__(self,
                 name: str = "获取文本",
                 description: str = "获取元素的文本内容",
                 selector: Optional[str] = None,
                 by_role: Optional[str] = None,
                 by_text: Optional[str] = None,
                 by_label: Optional[str] = None,
                 by_placeholder: Optional[str] = None,
                 by_alt_text: Optional[str] = None,
                 by_title: Optional[str] = None,
                 by_test_id: Optional[str] = None,
                 text_type: str = "text_content",  # text_content, inner_text, inner_html
                 **kwargs):
        super().__init__(name, description, output_key='text', **kwargs)
        self.selector = selector
        self.by_role = by_role
        self.by_text = by_text
        self.by_label = by_label
        self.by_placeholder = by_placeholder
        self.by_alt_text = by_alt_text
        self.by_title = by_title
        self.by_test_id = by_test_id
        self.text_type = text_type.lower()

    def execute(self, context: CONTEXT) -> Any:
        """执行获取文本操作"""
        try:
            # 获取元素定位器
            if self.selector:
                locator = self.locator(context, self.selector)
            elif self.by_role:
                locator = self.get_by_role(context, self.by_role)
            elif self.by_text:
                locator = self.get_by_text(context, self.by_text)
            elif self.by_label:
                locator = self.get_by_label(context, self.by_label)
            elif self.by_placeholder:
                locator = self.get_by_placeholder(context, self.by_placeholder)
            elif self.by_alt_text:
                locator = self.get_by_alt_text(context, self.by_alt_text)
            elif self.by_title:
                locator = self.get_by_title(context, self.by_title)
            elif self.by_test_id:
                locator = self.get_by_test_id(context, self.by_test_id)
            else:
                raise ValueError("必须提供至少一种元素定位方式")
            
            # 获取文本内容
            if self.text_type == "text_content":
                text = locator.text_content()
            elif self.text_type == "inner_text":
                text = locator.inner_text()
            elif self.text_type == "inner_html":
                text = locator.inner_html()
            else:
                raise ValueError(f"不支持的文本类型: {self.text_type}")
            
            # 更新上下文
            context['last_locator'] = locator
            context['last_text'] = text
            
            self.logger.info(f"获取文本成功: {text[:100]}{'...' if len(text) > 100 else ''}")
            
            return text
            
        except Exception as e:
            self.logger.error(f"获取文本失败: {e}")
            raise


class GetAllTextNode(PlaywrightBaseNode, DataStorageNode):
    """获取所有文本节点

    用于获取多个元素的文本内容
    """

    def __init__(self,
                 name: str = "获取所有文本",
                 description: str = "获取多个元素的文本内容",
                 selector: str = "",
                 text_type: str = "text_content",  # text_content, inner_text, inner_html
                 **kwargs):
        super().__init__(name, description, output_key='texts', **kwargs)
        self.selector = selector
        self.text_type = text_type.lower()

    def execute(self, context: CONTEXT) -> Any:
        """执行获取所有文本操作"""
        try:
            # 获取所有匹配的元素
            locator = self.locator(context, self.selector)
            
            # 获取所有文本内容
            if self.text_type == "text_content":
                texts = locator.all_text_contents()
            elif self.text_type == "inner_text":
                texts = locator.all_inner_texts()
            else:
                # 对于inner_html，需要逐个获取
                elements = locator.all()
                texts = [element.inner_html() for element in elements]
            
            # 更新上下文
            context['last_locator'] = locator
            context['last_texts'] = texts
            
            self.logger.info(f"获取到 {len(texts)} 个文本")
            
            return texts
            
        except Exception as e:
            self.logger.error(f"获取所有文本失败: {e}")
            raise


class GetAttributeNode(PlaywrightBaseNode, DataStorageNode):
    """获取属性节点

    用于获取元素的属性值
    """

    def __init__(self,
                 name: str = "获取属性",
                 description: str = "获取元素的属性值",
                 selector: Optional[str] = None,
                 by_role: Optional[str] = None,
                 by_text: Optional[str] = None,
                 by_label: Optional[str] = None,
                 attribute_name: str = "",
                 **kwargs):
        super().__init__(name, description, output_key='attribute_value', **kwargs)
        self.selector = selector
        self.by_role = by_role
        self.by_text = by_text
        self.by_label = by_label
        self.attribute_name = attribute_name

    def execute(self, context: CONTEXT) -> Any:
        """执行获取属性操作"""
        try:
            # 获取元素定位器
            if self.selector:
                locator = self.locator(context, self.selector)
            elif self.by_role:
                locator = self.get_by_role(context, self.by_role)
            elif self.by_text:
                locator = self.get_by_text(context, self.by_text)
            elif self.by_label:
                locator = self.get_by_label(context, self.by_label)
            else:
                raise ValueError("必须提供至少一种元素定位方式")
            
            if not self.attribute_name:
                raise ValueError("必须提供属性名称")
            
            # 获取属性值
            attribute_value = locator.get_attribute(self.attribute_name)
            
            # 更新上下文
            context['last_locator'] = locator
            context['last_attribute_value'] = attribute_value
            
            self.logger.info(f"获取属性 {self.attribute_name}: {attribute_value}")
            
            return attribute_value
            
        except Exception as e:
            self.logger.error(f"获取属性失败: {e}")
            raise


class GetValueNode(PlaywrightBaseNode, DataStorageNode):
    """获取输入值节点

    用于获取输入框的值
    """

    def __init__(self,
                 name: str = "获取输入值",
                 description: str = "获取输入框的值",
                 selector: Optional[str] = None,
                 by_role: Optional[str] = None,
                 by_label: Optional[str] = None,
                 by_placeholder: Optional[str] = None,
                 **kwargs):
        super().__init__(name, description, output_key='input_value', **kwargs)
        self.selector = selector
        self.by_role = by_role
        self.by_label = by_label
        self.by_placeholder = by_placeholder

    def execute(self, context: CONTEXT) -> Any:
        """执行获取输入值操作"""
        try:
            # 获取元素定位器
            if self.selector:
                locator = self.locator(context, self.selector)
            elif self.by_role:
                locator = self.get_by_role(context, self.by_role)
            elif self.by_label:
                locator = self.get_by_label(context, self.by_label)
            elif self.by_placeholder:
                locator = self.get_by_placeholder(context, self.by_placeholder)
            else:
                raise ValueError("必须提供至少一种元素定位方式")
            
            # 获取输入值
            input_value = locator.input_value()
            
            # 更新上下文
            context['last_locator'] = locator
            context['last_input_value'] = input_value
            
            self.logger.info(f"获取输入值: {input_value}")
            
            return input_value
            
        except Exception as e:
            self.logger.error(f"获取输入值失败: {e}")
            raise


class GetPageInfoNode(PlaywrightBaseNode, DataStorageNode):
    """获取页面信息节点

    用于获取页面的基本信息
    """

    def __init__(self,
                 name: str = "获取页面信息",
                 description: str = "获取页面的基本信息",
                 info_type: str = "all",  # all, title, url, content
                 **kwargs):
        super().__init__(name, description, output_key='page_info', **kwargs)
        self.info_type = info_type.lower()

    def execute(self, context: CONTEXT) -> Any:
        """执行获取页面信息操作"""
        page = self.get_page(context)
        
        try:
            if self.info_type == "title":
                result = page.title()
                self.logger.info(f"获取页面标题: {result}")
                
            elif self.info_type == "url":
                result = page.url
                self.logger.info(f"获取页面URL: {result}")
                
            elif self.info_type == "content":
                result = page.content()
                self.logger.info(f"获取页面内容，长度: {len(result)}")
                
            elif self.info_type == "all":
                result = {
                    "title": page.title(),
                    "url": page.url,
                    "content": page.content(),
                    "viewport": page.viewport_size,
                }
                self.logger.info(f"获取页面完整信息: {result['title']} - {result['url']}")
                
            else:
                raise ValueError(f"不支持的信息类型: {self.info_type}")
            
            # 更新上下文
            if self.info_type == "title" or self.info_type == "all":
                context['page_title'] = result['title'] if isinstance(result, dict) else result
            if self.info_type == "url" or self.info_type == "all":
                context['current_url'] = result['url'] if isinstance(result, dict) else result
            
            return result
            
        except Exception as e:
            self.logger.error(f"获取页面信息失败: {e}")
            raise


class GetElementCountNode(PlaywrightBaseNode, DataStorageNode):
    """获取元素数量节点

    用于获取匹配选择器的元素数量
    """

    def __init__(self,
                 name: str = "获取元素数量",
                 description: str = "获取匹配选择器的元素数量",
                 selector: str = "",
                 **kwargs):
        super().__init__(name, description, output_key='element_count', **kwargs)
        self.selector = selector

    def execute(self, context: CONTEXT) -> Any:
        """执行获取元素数量操作"""
        try:
            # 获取元素定位器
            locator = self.locator(context, self.selector)
            
            # 获取元素数量
            count = locator.count()
            
            # 更新上下文
            context['last_locator'] = locator
            context['last_element_count'] = count
            
            self.logger.info(f"找到 {count} 个匹配的元素")
            
            return count
            
        except Exception as e:
            self.logger.error(f"获取元素数量失败: {e}")
            raise