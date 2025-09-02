#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
元素检查节点
"""
from typing import Optional, Any, List

from playwright.sync_api import expect

from rpaworkflow.node import DataStorageNode
from rpaworkflow.playwright.nodes.base import PlaywrightBaseNode
from rpaworkflow.playwright.workflow_context import CONTEXT


class ElementExistsNode(PlaywrightBaseNode, DataStorageNode):
    """元素存在检查节点

    用于检查元素是否存在
    """

    def __init__(self,
                 name: str = "检查元素存在",
                 description: str = "检查元素是否存在",
                 selector: Optional[str] = None,
                 by_role: Optional[str] = None,
                 by_text: Optional[str] = None,
                 by_label: Optional[str] = None,
                 by_placeholder: Optional[str] = None,
                 by_alt_text: Optional[str] = None,
                 by_title: Optional[str] = None,
                 by_test_id: Optional[str] = None,
                 timeout: float = 5.0,
                 **kwargs):
        super().__init__(name, description, output_key='element_exists', **kwargs)
        self.selector = selector
        self.by_role = by_role
        self.by_text = by_text
        self.by_label = by_label
        self.by_placeholder = by_placeholder
        self.by_alt_text = by_alt_text
        self.by_title = by_title
        self.by_test_id = by_test_id
        self.timeout = timeout

    def execute(self, context: CONTEXT) -> Any:
        """执行元素存在检查操作"""
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
            
            # 检查元素是否存在
            try:
                locator.wait_for(state="attached", timeout=self.timeout * 1000)
                exists = True
                self.logger.info("元素存在")
            except Exception:
                exists = False
                self.logger.info("元素不存在")
            
            # 更新上下文
            context['last_locator'] = locator
            context['last_element_exists'] = exists
            
            return exists
            
        except Exception as e:
            self.logger.error(f"检查元素存在失败: {e}")
            raise


class ElementVisibleNode(PlaywrightBaseNode, DataStorageNode):
    """元素可见检查节点

    用于检查元素是否可见
    """

    def __init__(self,
                 name: str = "检查元素可见",
                 description: str = "检查元素是否可见",
                 selector: Optional[str] = None,
                 by_role: Optional[str] = None,
                 by_text: Optional[str] = None,
                 by_label: Optional[str] = None,
                 timeout: float = 5.0,
                 **kwargs):
        super().__init__(name, description, output_key='element_visible', **kwargs)
        self.selector = selector
        self.by_role = by_role
        self.by_text = by_text
        self.by_label = by_label
        self.timeout = timeout

    def execute(self, context: CONTEXT) -> Any:
        """执行元素可见检查操作"""
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
            
            # 检查元素是否可见
            try:
                locator.wait_for(state="visible", timeout=self.timeout * 1000)
                visible = True
                self.logger.info("元素可见")
            except Exception:
                visible = False
                self.logger.info("元素不可见")
            
            # 更新上下文
            context['last_locator'] = locator
            context['last_element_visible'] = visible
            
            return visible
            
        except Exception as e:
            self.logger.error(f"检查元素可见失败: {e}")
            raise


class ElementEnabledNode(PlaywrightBaseNode, DataStorageNode):
    """元素启用检查节点

    用于检查元素是否启用
    """

    def __init__(self,
                 name: str = "检查元素启用",
                 description: str = "检查元素是否启用",
                 selector: Optional[str] = None,
                 by_role: Optional[str] = None,
                 by_text: Optional[str] = None,
                 by_label: Optional[str] = None,
                 **kwargs):
        super().__init__(name, description, output_key='element_enabled', **kwargs)
        self.selector = selector
        self.by_role = by_role
        self.by_text = by_text
        self.by_label = by_label

    def execute(self, context: CONTEXT) -> Any:
        """执行元素启用检查操作"""
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
            
            # 检查元素是否启用
            enabled = locator.is_enabled()
            
            # 更新上下文
            context['last_locator'] = locator
            context['last_element_enabled'] = enabled
            
            self.logger.info(f"元素启用状态: {enabled}")
            
            return enabled
            
        except Exception as e:
            self.logger.error(f"检查元素启用失败: {e}")
            raise


class ElementCheckedNode(PlaywrightBaseNode, DataStorageNode):
    """元素选中检查节点

    用于检查复选框或单选框是否选中
    """

    def __init__(self,
                 name: str = "检查元素选中",
                 description: str = "检查复选框或单选框是否选中",
                 selector: Optional[str] = None,
                 by_role: Optional[str] = None,
                 by_label: Optional[str] = None,
                 **kwargs):
        super().__init__(name, description, output_key='element_checked', **kwargs)
        self.selector = selector
        self.by_role = by_role
        self.by_label = by_label

    def execute(self, context: CONTEXT) -> Any:
        """执行元素选中检查操作"""
        try:
            # 获取元素定位器
            if self.selector:
                locator = self.locator(context, self.selector)
            elif self.by_role:
                locator = self.get_by_role(context, self.by_role)
            elif self.by_label:
                locator = self.get_by_label(context, self.by_label)
            else:
                raise ValueError("必须提供至少一种元素定位方式")
            
            # 检查元素是否选中
            checked = locator.is_checked()
            
            # 更新上下文
            context['last_locator'] = locator
            context['last_element_checked'] = checked
            
            self.logger.info(f"元素选中状态: {checked}")
            
            return checked
            
        except Exception as e:
            self.logger.error(f"检查元素选中失败: {e}")
            raise


class ElementTextContainsNode(PlaywrightBaseNode, DataStorageNode):
    """元素文本包含检查节点

    用于检查元素文本是否包含指定内容
    """

    def __init__(self,
                 name: str = "检查文本包含",
                 description: str = "检查元素文本是否包含指定内容",
                 selector: Optional[str] = None,
                 by_role: Optional[str] = None,
                 by_text: Optional[str] = None,
                 by_label: Optional[str] = None,
                 expected_text: str = "",
                 case_sensitive: bool = True,
                 **kwargs):
        super().__init__(name, description, output_key='text_contains', **kwargs)
        self.selector = selector
        self.by_role = by_role
        self.by_text = by_text
        self.by_label = by_label
        self.expected_text = expected_text
        self.case_sensitive = case_sensitive

    def execute(self, context: CONTEXT) -> Any:
        """执行元素文本包含检查操作"""
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
            
            # 获取元素文本
            actual_text = locator.text_content() or ""
            
            # 检查文本是否包含
            if self.case_sensitive:
                contains = self.expected_text in actual_text
            else:
                contains = self.expected_text.lower() in actual_text.lower()
            
            # 更新上下文
            context['last_locator'] = locator
            context['last_text'] = actual_text
            context['last_text_contains'] = contains
            
            self.logger.info(f"文本包含检查: {contains} (期望: '{self.expected_text}', 实际: '{actual_text[:50]}...')")
            
            return contains
            
        except Exception as e:
            self.logger.error(f"检查文本包含失败: {e}")
            raise


class ElementAttributeNode(PlaywrightBaseNode, DataStorageNode):
    """元素属性检查节点

    用于检查元素属性值
    """

    def __init__(self,
                 name: str = "检查元素属性",
                 description: str = "检查元素属性值",
                 selector: Optional[str] = None,
                 by_role: Optional[str] = None,
                 by_text: Optional[str] = None,
                 by_label: Optional[str] = None,
                 attribute_name: str = "",
                 expected_value: Optional[str] = None,
                 **kwargs):
        super().__init__(name, description, output_key='attribute_check', **kwargs)
        self.selector = selector
        self.by_role = by_role
        self.by_text = by_text
        self.by_label = by_label
        self.attribute_name = attribute_name
        self.expected_value = expected_value

    def execute(self, context: CONTEXT) -> Any:
        """执行元素属性检查操作"""
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
            actual_value = locator.get_attribute(self.attribute_name)
            
            # 检查属性值
            if self.expected_value is not None:
                matches = actual_value == self.expected_value
                result = {
                    "attribute_name": self.attribute_name,
                    "actual_value": actual_value,
                    "expected_value": self.expected_value,
                    "matches": matches
                }
                self.logger.info(f"属性检查: {self.attribute_name}={actual_value}, 匹配: {matches}")
            else:
                result = {
                    "attribute_name": self.attribute_name,
                    "actual_value": actual_value
                }
                self.logger.info(f"属性值: {self.attribute_name}={actual_value}")
            
            # 更新上下文
            context['last_locator'] = locator
            context['last_attribute_value'] = actual_value
            
            return result
            
        except Exception as e:
            self.logger.error(f"检查元素属性失败: {e}")
            raise


class AssertElementNode(PlaywrightBaseNode):
    """元素断言节点

    用于对元素进行断言检查
    """

    def __init__(self,
                 name: str = "元素断言",
                 description: str = "对元素进行断言检查",
                 selector: Optional[str] = None,
                 by_role: Optional[str] = None,
                 by_text: Optional[str] = None,
                 by_label: Optional[str] = None,
                 assertion_type: str = "visible",  # visible, hidden, enabled, disabled, checked, unchecked, text, value, count
                 expected_text: Optional[str] = None,
                 expected_value: Optional[str] = None,
                 expected_count: Optional[int] = None,
                 timeout: float = 5.0,
                 **kwargs):
        super().__init__(name, description, **kwargs)
        self.selector = selector
        self.by_role = by_role
        self.by_text = by_text
        self.by_label = by_label
        self.assertion_type = assertion_type.lower()
        self.expected_text = expected_text
        self.expected_value = expected_value
        self.expected_count = expected_count
        self.timeout = timeout

    def execute(self, context: CONTEXT) -> Any:
        """执行元素断言操作"""
        try:
            timeout_ms = self.timeout * 1000
            
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
            
            # 执行断言
            if self.assertion_type == "visible":
                expect(locator).to_be_visible(timeout=timeout_ms)
                result = "元素可见断言通过"
                
            elif self.assertion_type == "hidden":
                expect(locator).to_be_hidden(timeout=timeout_ms)
                result = "元素隐藏断言通过"
                
            elif self.assertion_type == "enabled":
                expect(locator).to_be_enabled(timeout=timeout_ms)
                result = "元素启用断言通过"
                
            elif self.assertion_type == "disabled":
                expect(locator).to_be_disabled(timeout=timeout_ms)
                result = "元素禁用断言通过"
                
            elif self.assertion_type == "checked":
                expect(locator).to_be_checked(timeout=timeout_ms)
                result = "元素选中断言通过"
                
            elif self.assertion_type == "unchecked":
                expect(locator).not_to_be_checked(timeout=timeout_ms)
                result = "元素未选中断言通过"
                
            elif self.assertion_type == "text":
                if not self.expected_text:
                    raise ValueError("文本断言需要提供expected_text参数")
                expect(locator).to_contain_text(self.expected_text, timeout=timeout_ms)
                result = f"文本断言通过: {self.expected_text}"
                
            elif self.assertion_type == "value":
                if not self.expected_value:
                    raise ValueError("值断言需要提供expected_value参数")
                expect(locator).to_have_value(self.expected_value, timeout=timeout_ms)
                result = f"值断言通过: {self.expected_value}"
                
            elif self.assertion_type == "count":
                if self.expected_count is None:
                    raise ValueError("数量断言需要提供expected_count参数")
                expect(locator).to_have_count(self.expected_count, timeout=timeout_ms)
                result = f"数量断言通过: {self.expected_count}"
                
            else:
                raise ValueError(f"不支持的断言类型: {self.assertion_type}")
            
            # 更新上下文
            context['last_locator'] = locator
            
            self.logger.info(result)
            
            return result
            
        except Exception as e:
            self.logger.error(f"元素断言失败: {e}")
            raise