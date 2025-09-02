#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DrissionPage 获取文本节点

提供获取页面和元素文本信息的功能。
"""

from typing import Dict, Any, List

from .base import DrissionPageBaseNode
from ..workflow_context import CONTEXT


class GetTextNode(DrissionPageBaseNode):
    """获取元素文本节点
    
    获取指定元素的文本内容。
    """
    
    def __init__(self, 
                 locator: str = None,
                 by_css: str = None,
                 by_xpath: str = None,
                 by_text: str = None,
                 by_tag: str = None,
                 by_attr: tuple = None,
                 text_type: str = "text",
                 strip_text: bool = True,
                 timeout: float = 10.0,
                 **kwargs):
        """
        初始化获取文本节点
        
        Args:
            locator: 通用定位器
            by_css: CSS选择器
            by_xpath: XPath表达式
            by_text: 文本内容
            by_tag: 标签名
            by_attr: 属性元组
            text_type: 文本类型 ('text', 'inner_text', 'text_content', 'raw_text')
            strip_text: 是否去除首尾空白字符
            timeout: 超时时间
        """
        super().__init__(
            name="获取文本",
            description=f"获取元素文本: {locator or by_css or by_xpath or by_text or by_tag or by_attr}",
            **kwargs
        )
        
        self.locator = locator
        self.by_css = by_css
        self.by_xpath = by_xpath
        self.by_text = by_text
        self.by_tag = by_tag
        self.by_attr = by_attr
        self.text_type = text_type
        self.strip_text = strip_text
        self.timeout = timeout
        
        self.node_type = "drissionpage_get_text"
    
    def execute(self, context: CONTEXT) -> Dict[str, Any]:
        """执行获取文本
        
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
                    'success': False,
                    'text': '',
                    'message': '未找到指定元素'
                }
            
            # 获取文本
            text = self._get_element_text(element)
            
            # 处理文本
            if self.strip_text and text:
                text = text.strip()
            
            # 更新上下文
            context['last_element'] = element
            context['last_text'] = text
            context['text_type'] = self.text_type
            
            return {
                'success': True,
                'text': text,
                'text_length': len(text) if text else 0,
                'text_type': self.text_type,
                'element_tag': getattr(element, 'tag', 'unknown'),
                'message': f"成功获取文本，长度: {len(text) if text else 0}"
            }
            
        except Exception as e:
            error_msg = self._handle_error(context, e)
            return {
                'success': False,
                'error': error_msg,
                'text': '',
                'message': f"获取文本失败: {error_msg}"
            }
    
    def _get_element_text(self, element) -> str:
        """获取元素文本"""
        try:
            if self.text_type == "text":
                return element.text or ""
            elif self.text_type == "inner_text":
                if hasattr(element, 'inner_text'):
                    return element.inner_text or ""
                else:
                    return element.text or ""
            elif self.text_type == "text_content":
                if hasattr(element, 'text_content'):
                    return element.text_content or ""
                else:
                    return element.text or ""
            elif self.text_type == "raw_text":
                if hasattr(element, 'raw_text'):
                    return element.raw_text or ""
                else:
                    return element.text or ""
            else:
                return element.text or ""
        except:
            return ""


class GetAllTextNode(DrissionPageBaseNode):
    """获取所有元素文本节点
    
    获取所有匹配元素的文本内容。
    """
    
    def __init__(self, 
                 locator: str = None,
                 by_css: str = None,
                 by_xpath: str = None,
                 by_text: str = None,
                 by_tag: str = None,
                 by_attr: tuple = None,
                 text_type: str = "text",
                 strip_text: bool = True,
                 join_separator: str = None,
                 timeout: float = 10.0,
                 **kwargs):
        """
        初始化获取所有文本节点
        
        Args:
            locator: 通用定位器
            by_css: CSS选择器
            by_xpath: XPath表达式
            by_text: 文本内容
            by_tag: 标签名
            by_attr: 属性元组
            text_type: 文本类型
            strip_text: 是否去除首尾空白字符
            join_separator: 连接分隔符，如果提供则将所有文本连接成一个字符串
            timeout: 超时时间
        """
        super().__init__(
            name="获取所有文本",
            description=f"获取所有元素文本: {locator or by_css or by_xpath or by_text or by_tag or by_attr}",
            **kwargs
        )
        
        self.locator = locator
        self.by_css = by_css
        self.by_xpath = by_xpath
        self.by_text = by_text
        self.by_tag = by_tag
        self.by_attr = by_attr
        self.text_type = text_type
        self.strip_text = strip_text
        self.join_separator = join_separator
        self.timeout = timeout
        
        self.node_type = "drissionpage_get_all_text"
    
    def execute(self, context: CONTEXT) -> Dict[str, Any]:
        """执行获取所有文本
        
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
            
            if not elements:
                return {
                    'success': False,
                    'texts': [],
                    'joined_text': '',
                    'count': 0,
                    'message': '未找到匹配的元素'
                }
            
            # 获取所有文本
            texts = []
            for element in elements:
                text = self._get_element_text(element)
                if self.strip_text and text:
                    text = text.strip()
                texts.append(text)
            
            # 连接文本
            joined_text = ''
            if self.join_separator is not None:
                joined_text = self.join_separator.join(texts)
            
            # 更新上下文
            context['last_elements'] = elements
            context['last_texts'] = texts
            context['joined_text'] = joined_text
            context['text_type'] = self.text_type
            
            return {
                'success': True,
                'texts': texts,
                'joined_text': joined_text,
                'count': len(texts),
                'text_type': self.text_type,
                'total_length': sum(len(text) for text in texts),
                'message': f"成功获取 {len(texts)} 个元素的文本"
            }
            
        except Exception as e:
            error_msg = self._handle_error(context, e)
            return {
                'success': False,
                'error': error_msg,
                'texts': [],
                'joined_text': '',
                'count': 0,
                'message': f"获取所有文本失败: {error_msg}"
            }
    
    def _get_element_text(self, element) -> str:
        """获取元素文本"""
        try:
            if self.text_type == "text":
                return element.text or ""
            elif self.text_type == "inner_text":
                if hasattr(element, 'inner_text'):
                    return element.inner_text or ""
                else:
                    return element.text or ""
            elif self.text_type == "text_content":
                if hasattr(element, 'text_content'):
                    return element.text_content or ""
                else:
                    return element.text or ""
            elif self.text_type == "raw_text":
                if hasattr(element, 'raw_text'):
                    return element.raw_text or ""
                else:
                    return element.text or ""
            else:
                return element.text or ""
        except:
            return ""


class GetAttributeNode(DrissionPageBaseNode):
    """获取元素属性节点
    
    获取指定元素的属性值。
    """
    
    def __init__(self, 
                 locator: str = None,
                 by_css: str = None,
                 by_xpath: str = None,
                 by_text: str = None,
                 by_tag: str = None,
                 by_attr: tuple = None,
                 attribute_name: str = None,
                 timeout: float = 10.0,
                 **kwargs):
        """
        初始化获取属性节点
        
        Args:
            locator: 通用定位器
            by_css: CSS选择器
            by_xpath: XPath表达式
            by_text: 文本内容
            by_tag: 标签名
            by_attr: 属性元组
            attribute_name: 属性名称
            timeout: 超时时间
        """
        super().__init__(
            name="获取属性",
            description=f"获取元素属性 {attribute_name}: {locator or by_css or by_xpath or by_text or by_tag or by_attr}",
            **kwargs
        )
        
        self.locator = locator
        self.by_css = by_css
        self.by_xpath = by_xpath
        self.by_text = by_text
        self.by_tag = by_tag
        self.by_attr = by_attr
        self.attribute_name = attribute_name
        self.timeout = timeout
        
        self.node_type = "drissionpage_get_attribute"
    
    def execute(self, context: CONTEXT) -> Dict[str, Any]:
        """执行获取属性
        
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
                    'success': False,
                    'attribute_value': None,
                    'message': '未找到指定元素'
                }
            
            # 获取属性值
            attribute_value = None
            if self.attribute_name:
                try:
                    if hasattr(element, 'attr'):
                        attribute_value = element.attr(self.attribute_name)
                    elif hasattr(element, 'get_attribute'):
                        attribute_value = element.get_attribute(self.attribute_name)
                    else:
                        # 尝试直接访问属性
                        attribute_value = getattr(element, self.attribute_name, None)
                except:
                    attribute_value = None
            
            # 更新上下文
            context['last_element'] = element
            context['last_attribute_name'] = self.attribute_name
            context['last_attribute_value'] = attribute_value
            
            return {
                'success': True,
                'attribute_name': self.attribute_name,
                'attribute_value': attribute_value,
                'element_tag': getattr(element, 'tag', 'unknown'),
                'message': f"成功获取属性 {self.attribute_name}: {attribute_value}"
            }
            
        except Exception as e:
            error_msg = self._handle_error(context, e)
            return {
                'success': False,
                'error': error_msg,
                'attribute_value': None,
                'message': f"获取属性失败: {error_msg}"
            }


class GetPageInfoNode(DrissionPageBaseNode):
    """获取页面信息节点
    
    获取当前页面的基本信息。
    """
    
    def __init__(self, 
                 info_types: List[str] = None,
                 **kwargs):
        """
        初始化获取页面信息节点
        
        Args:
            info_types: 要获取的信息类型列表
                       ['url', 'title', 'html', 'text', 'cookies', 'user_agent', 'size']
        """
        super().__init__(
            name="获取页面信息",
            description="获取当前页面信息",
            **kwargs
        )
        
        self.info_types = info_types or ['url', 'title']
        
        self.node_type = "drissionpage_get_page_info"
    
    def execute(self, context: CONTEXT) -> Dict[str, Any]:
        """执行获取页面信息
        
        Args:
            context: 工作流上下文
            
        Returns:
            执行结果
        """
        try:
            page = self._get_page(context)
            page_info = {}
            
            # 获取各种页面信息
            for info_type in self.info_types:
                try:
                    if info_type == 'url':
                        page_info['url'] = page.url
                    elif info_type == 'title':
                        page_info['title'] = page.title
                    elif info_type == 'html':
                        page_info['html'] = page.html
                    elif info_type == 'text':
                        if hasattr(page, 'text'):
                            page_info['text'] = page.text
                        else:
                            page_info['text'] = ''
                    elif info_type == 'cookies':
                        if hasattr(page, 'cookies'):
                            page_info['cookies'] = dict(page.cookies)
                        else:
                            page_info['cookies'] = {}
                    elif info_type == 'user_agent':
                        if hasattr(page, 'user_agent'):
                            page_info['user_agent'] = page.user_agent
                        else:
                            page_info['user_agent'] = ''
                    elif info_type == 'size':
                        if hasattr(page, 'size'):
                            page_info['size'] = page.size
                        elif hasattr(page, 'window_size'):
                            page_info['size'] = page.window_size
                        else:
                            page_info['size'] = None
                except Exception as e:
                    page_info[info_type] = f"获取失败: {str(e)}"
            
            # 更新上下文
            context['page_info'] = page_info
            context['current_url'] = page_info.get('url', '')
            context['current_title'] = page_info.get('title', '')
            
            return {
                'success': True,
                'page_info': page_info,
                'info_types': self.info_types,
                'message': f"成功获取页面信息: {', '.join(self.info_types)}"
            }
            
        except Exception as e:
            error_msg = self._handle_error(context, e)
            return {
                'success': False,
                'error': error_msg,
                'page_info': {},
                'message': f"获取页面信息失败: {error_msg}"
            }


class GetElementInfoNode(DrissionPageBaseNode):
    """获取元素信息节点
    
    获取指定元素的详细信息。
    """
    
    def __init__(self, 
                 locator: str = None,
                 by_css: str = None,
                 by_xpath: str = None,
                 by_text: str = None,
                 by_tag: str = None,
                 by_attr: tuple = None,
                 info_types: List[str] = None,
                 timeout: float = 10.0,
                 **kwargs):
        """
        初始化获取元素信息节点
        
        Args:
            locator: 通用定位器
            by_css: CSS选择器
            by_xpath: XPath表达式
            by_text: 文本内容
            by_tag: 标签名
            by_attr: 属性元组
            info_types: 要获取的信息类型列表
                       ['tag', 'text', 'html', 'attrs', 'size', 'location', 'visible', 'enabled']
            timeout: 超时时间
        """
        super().__init__(
            name="获取元素信息",
            description=f"获取元素信息: {locator or by_css or by_xpath or by_text or by_tag or by_attr}",
            **kwargs
        )
        
        self.locator = locator
        self.by_css = by_css
        self.by_xpath = by_xpath
        self.by_text = by_text
        self.by_tag = by_tag
        self.by_attr = by_attr
        self.info_types = info_types or ['tag', 'text', 'attrs']
        self.timeout = timeout
        
        self.node_type = "drissionpage_get_element_info"
    
    def execute(self, context: CONTEXT) -> Dict[str, Any]:
        """执行获取元素信息
        
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
                    'success': False,
                    'element_info': {},
                    'message': '未找到指定元素'
                }
            
            element_info = {}
            
            # 获取各种元素信息
            for info_type in self.info_types:
                try:
                    if info_type == 'tag':
                        element_info['tag'] = getattr(element, 'tag', 'unknown')
                    elif info_type == 'text':
                        element_info['text'] = element.text or ''
                    elif info_type == 'html':
                        if hasattr(element, 'html'):
                            element_info['html'] = element.html
                        else:
                            element_info['html'] = ''
                    elif info_type == 'attrs':
                        if hasattr(element, 'attrs'):
                            element_info['attrs'] = element.attrs
                        else:
                            element_info['attrs'] = {}
                    elif info_type == 'size':
                        if hasattr(element, 'size'):
                            element_info['size'] = element.size
                        else:
                            element_info['size'] = None
                    elif info_type == 'location':
                        if hasattr(element, 'location'):
                            element_info['location'] = element.location
                        elif hasattr(element, 'rect'):
                            element_info['location'] = element.rect
                        else:
                            element_info['location'] = None
                    elif info_type == 'visible':
                        if hasattr(element, 'is_displayed'):
                            element_info['visible'] = element.is_displayed
                        elif hasattr(element, 'is_visible'):
                            element_info['visible'] = element.is_visible
                        else:
                            element_info['visible'] = True  # SessionElement 假设可见
                    elif info_type == 'enabled':
                        if hasattr(element, 'is_enabled'):
                            element_info['enabled'] = element.is_enabled
                        else:
                            element_info['enabled'] = True  # SessionElement 假设启用
                except Exception as e:
                    element_info[info_type] = f"获取失败: {str(e)}"
            
            # 更新上下文
            context['last_element'] = element
            context['element_info'] = element_info
            
            return {
                'success': True,
                'element_info': element_info,
                'info_types': self.info_types,
                'message': f"成功获取元素信息: {', '.join(self.info_types)}"
            }
            
        except Exception as e:
            error_msg = self._handle_error(context, e)
            return {
                'success': False,
                'error': error_msg,
                'element_info': {},
                'message': f"获取元素信息失败: {error_msg}"
            }