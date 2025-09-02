#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DrissionPage 元素检查节点

提供元素存在性、可见性、状态等检查功能。
"""

from typing import Dict, Any, Optional

from DrissionPage._elements.chromium_element import ChromiumElement
from DrissionPage._elements.session_element import SessionElement

from .base import DrissionPageBaseNode
from ..workflow_context import CONTEXT


class CheckElementExistsNode(DrissionPageBaseNode):
    """检查元素存在节点
    
    检查指定元素是否存在于页面中。
    """
    
    def __init__(self, 
                 locator: str = None,
                 by_css: str = None,
                 by_xpath: str = None,
                 by_text: str = None,
                 by_tag: str = None,
                 by_attr: tuple = None,
                 timeout: float = 10.0,
                 **kwargs):
        """
        初始化检查元素存在节点
        
        Args:
            locator: 通用定位器
            by_css: CSS选择器
            by_xpath: XPath表达式
            by_text: 文本内容
            by_tag: 标签名
            by_attr: 属性元组
            timeout: 超时时间
        """
        super().__init__(
            name="检查元素存在",
            description=f"检查元素是否存在: {locator or by_css or by_xpath or by_text or by_tag or by_attr}",
            **kwargs
        )
        
        self.locator = locator
        self.by_css = by_css
        self.by_xpath = by_xpath
        self.by_text = by_text
        self.by_tag = by_tag
        self.by_attr = by_attr
        self.timeout = timeout
        
        self.node_type = "drissionpage_check_element_exists"
    
    def execute(self, context: CONTEXT) -> Dict[str, Any]:
        """执行检查元素存在
        
        Args:
            context: 工作流上下文
            
        Returns:
            执行结果
        """
        try:
            # 查找元素
            element = self._find_element(
                context=context,
                locator=self.locator,
                by_css=self.by_css,
                by_xpath=self.by_xpath,
                by_text=self.by_text,
                by_tag=self.by_tag,
                by_attr=self.by_attr,
                timeout=self.timeout
            )
            
            exists = element is not None
            
            # 更新上下文
            context['element_exists'] = exists
            context['checked_element'] = element
            
            return {
                'success': True,
                'exists': exists,
                'element_found': exists,
                'element_tag': getattr(element, 'tag', 'unknown') if element else None,
                'message': f"元素{'存在' if exists else '不存在'}"
            }
            
        except Exception as e:
            error_msg = self._handle_error(context, e)
            return {
                'success': False,
                'error': error_msg,
                'exists': False,
                'element_found': False,
                'message': f"检查元素存在失败: {error_msg}"
            }


class CheckElementVisibleNode(DrissionPageBaseNode):
    """检查元素可见节点
    
    检查指定元素是否可见。
    """
    
    def __init__(self, 
                 locator: str = None,
                 by_css: str = None,
                 by_xpath: str = None,
                 by_text: str = None,
                 by_tag: str = None,
                 by_attr: tuple = None,
                 timeout: float = 10.0,
                 **kwargs):
        """
        初始化检查元素可见节点
        
        Args:
            locator: 通用定位器
            by_css: CSS选择器
            by_xpath: XPath表达式
            by_text: 文本内容
            by_tag: 标签名
            by_attr: 属性元组
            timeout: 超时时间
        """
        super().__init__(
            name="检查元素可见",
            description=f"检查元素是否可见: {locator or by_css or by_xpath or by_text or by_tag or by_attr}",
            **kwargs
        )
        
        self.locator = locator
        self.by_css = by_css
        self.by_xpath = by_xpath
        self.by_text = by_text
        self.by_tag = by_tag
        self.by_attr = by_attr
        self.timeout = timeout
        
        self.node_type = "drissionpage_check_element_visible"
    
    def execute(self, context: CONTEXT) -> Dict[str, Any]:
        """执行检查元素可见
        
        Args:
            context: 工作流上下文
            
        Returns:
            执行结果
        """
        try:
            # 查找元素
            element = self._find_element(
                context=context,
                locator=self.locator,
                by_css=self.by_css,
                by_xpath=self.by_xpath,
                by_text=self.by_text,
                by_tag=self.by_tag,
                by_attr=self.by_attr,
                timeout=self.timeout
            )
            
            if element is None:
                return {
                    'success': True,
                    'exists': False,
                    'visible': False,
                    'message': '元素不存在，因此不可见'
                }
            
            # 检查可见性
            visible = self._is_element_visible(element)
            
            # 更新上下文
            context['element_visible'] = visible
            context['checked_element'] = element
            
            return {
                'success': True,
                'exists': True,
                'visible': visible,
                'element_tag': getattr(element, 'tag', 'unknown'),
                'message': f"元素{'可见' if visible else '不可见'}"
            }
            
        except Exception as e:
            error_msg = self._handle_error(context, e)
            return {
                'success': False,
                'error': error_msg,
                'exists': False,
                'visible': False,
                'message': f"检查元素可见失败: {error_msg}"
            }
    
    def _is_element_visible(self, element) -> bool:
        """检查元素是否可见"""
        try:
            if isinstance(element, ChromiumElement):
                return element.is_displayed
            elif isinstance(element, SessionElement):
                # SessionElement 假设存在即可见
                return True
            else:
                # 其他类型元素，尝试获取可见性
                if hasattr(element, 'is_displayed'):
                    return element.is_displayed
                elif hasattr(element, 'is_visible'):
                    return element.is_visible
                else:
                    return True
        except:
            return False


class CheckElementEnabledNode(DrissionPageBaseNode):
    """检查元素启用节点
    
    检查指定元素是否启用（可交互）。
    """
    
    def __init__(self, 
                 locator: str = None,
                 by_css: str = None,
                 by_xpath: str = None,
                 by_text: str = None,
                 by_tag: str = None,
                 by_attr: tuple = None,
                 timeout: float = 10.0,
                 **kwargs):
        """
        初始化检查元素启用节点
        
        Args:
            locator: 通用定位器
            by_css: CSS选择器
            by_xpath: XPath表达式
            by_text: 文本内容
            by_tag: 标签名
            by_attr: 属性元组
            timeout: 超时时间
        """
        super().__init__(
            name="检查元素启用",
            description=f"检查元素是否启用: {locator or by_css or by_xpath or by_text or by_tag or by_attr}",
            **kwargs
        )
        
        self.locator = locator
        self.by_css = by_css
        self.by_xpath = by_xpath
        self.by_text = by_text
        self.by_tag = by_tag
        self.by_attr = by_attr
        self.timeout = timeout
        
        self.node_type = "drissionpage_check_element_enabled"
    
    def execute(self, context: CONTEXT) -> Dict[str, Any]:
        """执行检查元素启用
        
        Args:
            context: 工作流上下文
            
        Returns:
            执行结果
        """
        try:
            # 查找元素
            element = self._find_element(
                context=context,
                locator=self.locator,
                by_css=self.by_css,
                by_xpath=self.by_xpath,
                by_text=self.by_text,
                by_tag=self.by_tag,
                by_attr=self.by_attr,
                timeout=self.timeout
            )
            
            if element is None:
                return {
                    'success': True,
                    'exists': False,
                    'enabled': False,
                    'message': '元素不存在，因此不可用'
                }
            
            # 检查启用状态
            enabled = self._is_element_enabled(element)
            
            # 更新上下文
            context['element_enabled'] = enabled
            context['checked_element'] = element
            
            return {
                'success': True,
                'exists': True,
                'enabled': enabled,
                'element_tag': getattr(element, 'tag', 'unknown'),
                'message': f"元素{'启用' if enabled else '禁用'}"
            }
            
        except Exception as e:
            error_msg = self._handle_error(context, e)
            return {
                'success': False,
                'error': error_msg,
                'exists': False,
                'enabled': False,
                'message': f"检查元素启用失败: {error_msg}"
            }
    
    def _is_element_enabled(self, element) -> bool:
        """检查元素是否启用"""
        try:
            if isinstance(element, ChromiumElement):
                return element.is_enabled
            elif isinstance(element, SessionElement):
                # SessionElement 假设存在即启用
                return True
            else:
                # 其他类型元素，尝试获取启用状态
                if hasattr(element, 'is_enabled'):
                    return element.is_enabled
                else:
                    return True
        except:
            return False


class CheckElementTextNode(DrissionPageBaseNode):
    """检查元素文本节点
    
    检查指定元素的文本内容。
    """
    
    def __init__(self, 
                 locator: str = None,
                 by_css: str = None,
                 by_xpath: str = None,
                 by_text: str = None,
                 by_tag: str = None,
                 by_attr: tuple = None,
                 expected_text: str = None,
                 text_contains: str = None,
                 text_pattern: str = None,
                 case_sensitive: bool = True,
                 timeout: float = 10.0,
                 **kwargs):
        """
        初始化检查元素文本节点
        
        Args:
            locator: 通用定位器
            by_css: CSS选择器
            by_xpath: XPath表达式
            by_text: 文本内容
            by_tag: 标签名
            by_attr: 属性元组
            expected_text: 期望的完整文本
            text_contains: 文本应包含的内容
            text_pattern: 文本正则表达式模式
            case_sensitive: 是否区分大小写
            timeout: 超时时间
        """
        super().__init__(
            name="检查元素文本",
            description=f"检查元素文本: {locator or by_css or by_xpath or by_text or by_tag or by_attr}",
            **kwargs
        )
        
        self.locator = locator
        self.by_css = by_css
        self.by_xpath = by_xpath
        self.by_text = by_text
        self.by_tag = by_tag
        self.by_attr = by_attr
        self.expected_text = expected_text
        self.text_contains = text_contains
        self.text_pattern = text_pattern
        self.case_sensitive = case_sensitive
        self.timeout = timeout
        
        self.node_type = "drissionpage_check_element_text"
    
    def execute(self, context: CONTEXT) -> Dict[str, Any]:
        """执行检查元素文本
        
        Args:
            context: 工作流上下文
            
        Returns:
            执行结果
        """
        try:
            # 查找元素
            element = self._find_element(
                context=context,
                locator=self.locator,
                by_css=self.by_css,
                by_xpath=self.by_xpath,
                by_text=self.by_text,
                by_tag=self.by_tag,
                by_attr=self.by_attr,
                timeout=self.timeout
            )
            
            if element is None:
                return {
                    'success': True,
                    'exists': False,
                    'text_match': False,
                    'actual_text': '',
                    'message': '元素不存在'
                }
            
            # 获取元素文本
            actual_text = element.text or ''
            
            # 检查文本匹配
            text_match = self._check_text_match(actual_text)
            
            # 更新上下文
            context['element_text'] = actual_text
            context['text_match'] = text_match
            context['checked_element'] = element
            
            return {
                'success': True,
                'exists': True,
                'text_match': text_match,
                'actual_text': actual_text,
                'expected_text': self.expected_text,
                'text_contains': self.text_contains,
                'text_pattern': self.text_pattern,
                'element_tag': getattr(element, 'tag', 'unknown'),
                'message': f"文本{'匹配' if text_match else '不匹配'}，实际文本: '{actual_text}'"
            }
            
        except Exception as e:
            error_msg = self._handle_error(context, e)
            return {
                'success': False,
                'error': error_msg,
                'exists': False,
                'text_match': False,
                'actual_text': '',
                'message': f"检查元素文本失败: {error_msg}"
            }
    
    def _check_text_match(self, actual_text: str) -> bool:
        """检查文本是否匹配"""
        try:
            # 处理大小写
            if not self.case_sensitive:
                actual_text = actual_text.lower()
            
            # 完整文本匹配
            if self.expected_text is not None:
                expected = self.expected_text
                if not self.case_sensitive:
                    expected = expected.lower()
                return actual_text == expected
            
            # 包含文本匹配
            if self.text_contains is not None:
                contains = self.text_contains
                if not self.case_sensitive:
                    contains = contains.lower()
                return contains in actual_text
            
            # 正则表达式匹配
            if self.text_pattern is not None:
                import re
                flags = 0 if self.case_sensitive else re.IGNORECASE
                return bool(re.search(self.text_pattern, actual_text, flags))
            
            # 如果没有指定检查条件，返回True
            return True
            
        except Exception:
            return False


class CheckElementAttributeNode(DrissionPageBaseNode):
    """检查元素属性节点
    
    检查指定元素的属性值。
    """
    
    def __init__(self, 
                 locator: str = None,
                 by_css: str = None,
                 by_xpath: str = None,
                 by_text: str = None,
                 by_tag: str = None,
                 by_attr: tuple = None,
                 attribute_name: str = None,
                 expected_value: str = None,
                 value_contains: str = None,
                 value_pattern: str = None,
                 case_sensitive: bool = True,
                 timeout: float = 10.0,
                 **kwargs):
        """
        初始化检查元素属性节点
        
        Args:
            locator: 通用定位器
            by_css: CSS选择器
            by_xpath: XPath表达式
            by_text: 文本内容
            by_tag: 标签名
            by_attr: 属性元组
            attribute_name: 属性名称
            expected_value: 期望的属性值
            value_contains: 属性值应包含的内容
            value_pattern: 属性值正则表达式模式
            case_sensitive: 是否区分大小写
            timeout: 超时时间
        """
        super().__init__(
            name="检查元素属性",
            description=f"检查元素属性 {attribute_name}: {locator or by_css or by_xpath or by_text or by_tag or by_attr}",
            **kwargs
        )
        
        self.locator = locator
        self.by_css = by_css
        self.by_xpath = by_xpath
        self.by_text = by_text
        self.by_tag = by_tag
        self.by_attr = by_attr
        self.attribute_name = attribute_name
        self.expected_value = expected_value
        self.value_contains = value_contains
        self.value_pattern = value_pattern
        self.case_sensitive = case_sensitive
        self.timeout = timeout
        
        self.node_type = "drissionpage_check_element_attribute"
    
    def execute(self, context: CONTEXT) -> Dict[str, Any]:
        """执行检查元素属性
        
        Args:
            context: 工作流上下文
            
        Returns:
            执行结果
        """
        try:
            # 查找元素
            element = self._find_element(
                context=context,
                locator=self.locator,
                by_css=self.by_css,
                by_xpath=self.by_xpath,
                by_text=self.by_text,
                by_tag=self.by_tag,
                by_attr=self.by_attr,
                timeout=self.timeout
            )
            
            if element is None:
                return {
                    'success': True,
                    'exists': False,
                    'attribute_match': False,
                    'actual_value': None,
                    'message': '元素不存在'
                }
            
            # 获取属性值
            actual_value = self._get_attribute_value(element)
            
            # 检查属性匹配
            attribute_match = self._check_attribute_match(actual_value)
            
            # 更新上下文
            context['element_attribute_value'] = actual_value
            context['attribute_match'] = attribute_match
            context['checked_element'] = element
            
            return {
                'success': True,
                'exists': True,
                'attribute_match': attribute_match,
                'attribute_name': self.attribute_name,
                'actual_value': actual_value,
                'expected_value': self.expected_value,
                'value_contains': self.value_contains,
                'value_pattern': self.value_pattern,
                'element_tag': getattr(element, 'tag', 'unknown'),
                'message': f"属性 {self.attribute_name} {'匹配' if attribute_match else '不匹配'}，实际值: '{actual_value}'"
            }
            
        except Exception as e:
            error_msg = self._handle_error(context, e)
            return {
                'success': False,
                'error': error_msg,
                'exists': False,
                'attribute_match': False,
                'actual_value': None,
                'message': f"检查元素属性失败: {error_msg}"
            }
    
    def _get_attribute_value(self, element) -> Optional[str]:
        """获取元素属性值"""
        try:
            if self.attribute_name:
                if hasattr(element, 'attr'):
                    return element.attr(self.attribute_name)
                elif hasattr(element, 'get_attribute'):
                    return element.get_attribute(self.attribute_name)
                else:
                    # 尝试直接访问属性
                    return getattr(element, self.attribute_name, None)
            return None
        except:
            return None
    
    def _check_attribute_match(self, actual_value: Optional[str]) -> bool:
        """检查属性是否匹配"""
        try:
            if actual_value is None:
                return self.expected_value is None
            
            actual_str = str(actual_value)
            
            # 处理大小写
            if not self.case_sensitive:
                actual_str = actual_str.lower()
            
            # 完整值匹配
            if self.expected_value is not None:
                expected = str(self.expected_value)
                if not self.case_sensitive:
                    expected = expected.lower()
                return actual_str == expected
            
            # 包含值匹配
            if self.value_contains is not None:
                contains = str(self.value_contains)
                if not self.case_sensitive:
                    contains = contains.lower()
                return contains in actual_str
            
            # 正则表达式匹配
            if self.value_pattern is not None:
                import re
                flags = 0 if self.case_sensitive else re.IGNORECASE
                return bool(re.search(self.value_pattern, actual_str, flags))
            
            # 如果没有指定检查条件，返回True
            return True
            
        except Exception:
            return False


class CheckElementCountNode(DrissionPageBaseNode):
    """检查元素数量节点
    
    检查匹配指定条件的元素数量。
    """
    
    def __init__(self, 
                 locator: str = None,
                 by_css: str = None,
                 by_xpath: str = None,
                 by_text: str = None,
                 by_tag: str = None,
                 by_attr: tuple = None,
                 expected_count: int = None,
                 min_count: int = None,
                 max_count: int = None,
                 timeout: float = 10.0,
                 **kwargs):
        """
        初始化检查元素数量节点
        
        Args:
            locator: 通用定位器
            by_css: CSS选择器
            by_xpath: XPath表达式
            by_text: 文本内容
            by_tag: 标签名
            by_attr: 属性元组
            expected_count: 期望的元素数量
            min_count: 最小元素数量
            max_count: 最大元素数量
            timeout: 超时时间
        """
        super().__init__(
            name="检查元素数量",
            description=f"检查元素数量: {locator or by_css or by_xpath or by_text or by_tag or by_attr}",
            **kwargs
        )
        
        self.locator = locator
        self.by_css = by_css
        self.by_xpath = by_xpath
        self.by_text = by_text
        self.by_tag = by_tag
        self.by_attr = by_attr
        self.expected_count = expected_count
        self.min_count = min_count
        self.max_count = max_count
        self.timeout = timeout
        
        self.node_type = "drissionpage_check_element_count"
    
    def execute(self, context: CONTEXT) -> Dict[str, Any]:
        """执行检查元素数量
        
        Args:
            context: 工作流上下文
            
        Returns:
            执行结果
        """
        try:
            # 查找所有元素
            elements = self._find_elements(
                context=context,
                locator=self.locator,
                by_css=self.by_css,
                by_xpath=self.by_xpath,
                by_text=self.by_text,
                by_tag=self.by_tag,
                by_attr=self.by_attr,
                timeout=self.timeout
            )
            
            actual_count = len(elements) if elements else 0
            
            # 检查数量匹配
            count_match = self._check_count_match(actual_count)
            
            # 更新上下文
            context['element_count'] = actual_count
            context['count_match'] = count_match
            context['found_elements'] = elements
            
            return {
                'success': True,
                'count_match': count_match,
                'actual_count': actual_count,
                'expected_count': self.expected_count,
                'min_count': self.min_count,
                'max_count': self.max_count,
                'elements_found': actual_count > 0,
                'message': f"找到 {actual_count} 个元素，{'符合' if count_match else '不符合'}预期"
            }
            
        except Exception as e:
            error_msg = self._handle_error(context, e)
            return {
                'success': False,
                'error': error_msg,
                'count_match': False,
                'actual_count': 0,
                'message': f"检查元素数量失败: {error_msg}"
            }
    
    def _check_count_match(self, actual_count: int) -> bool:
        """检查数量是否匹配"""
        try:
            # 精确数量匹配
            if self.expected_count is not None:
                return actual_count == self.expected_count
            
            # 范围匹配
            if self.min_count is not None and actual_count < self.min_count:
                return False
            
            if self.max_count is not None and actual_count > self.max_count:
                return False
            
            # 如果没有指定检查条件，返回True
            return True
            
        except Exception:
            return False