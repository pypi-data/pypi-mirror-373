#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DrissionPage 文本输入节点

提供文本输入、清除、选择等功能。
"""

from typing import Dict, Any, Union

from DrissionPage._elements.chromium_element import ChromiumElement
from DrissionPage._elements.session_element import SessionElement

from .base import DrissionPageBaseNode
from ..workflow_context import CONTEXT


class InputTextNode(DrissionPageBaseNode):
    """文本输入节点
    
    在指定元素中输入文本。
    """
    
    def __init__(self, 
                 text: str,
                 locator: str = None,
                 by_css: str = None,
                 by_xpath: str = None,
                 by_text: str = None,
                 by_tag: str = None,
                 by_attr: tuple = None,
                 index: int = 1,
                 clear_first: bool = True,
                 timeout: float = 10.0,
                 wait_after: float = 0.5,
                 simulate_typing: bool = False,
                 typing_interval: float = 0.1,
                 **kwargs):
        """
        初始化文本输入节点
        
        Args:
            text: 要输入的文本
            locator: 通用定位器
            by_css: CSS选择器
            by_xpath: XPath表达式
            by_text: 文本内容
            by_tag: 标签名
            by_attr: 属性元组
            index: 元素索引
            clear_first: 是否先清除原有内容
            timeout: 查找元素超时时间
            wait_after: 输入后等待时间
            simulate_typing: 是否模拟逐字输入
            typing_interval: 逐字输入间隔
        """
        super().__init__(
            name="文本输入",
            description=f"输入文本: {text[:50]}{'...' if len(text) > 50 else ''}",
            **kwargs
        )
        
        self.text = text
        self.locator = locator
        self.by_css = by_css
        self.by_xpath = by_xpath
        self.by_text = by_text
        self.by_tag = by_tag
        self.by_attr = by_attr
        self.index = index
        self.clear_first = clear_first
        self.timeout = timeout
        self.wait_after = wait_after
        self.simulate_typing = simulate_typing
        self.typing_interval = typing_interval
        
        self.node_type = "drissionpage_input_text"
    
    def execute(self, context: CONTEXT) -> Dict[str, Any]:
        """执行文本输入
        
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
                index=self.index,
                timeout=self.timeout
            )
            
            # 清除原有内容
            if self.clear_first:
                if isinstance(element, ChromiumElement):
                    element.clear()
                else:
                    # SessionElement 使用 input 方法清除
                    element.input('')
            
            # 输入文本
            if self.simulate_typing and isinstance(element, ChromiumElement):
                # 模拟逐字输入
                for char in self.text:
                    element.input(char)
                    if self.typing_interval > 0:
                        import time
                        time.sleep(self.typing_interval)
            else:
                # 直接输入
                element.input(self.text)
            
            # 输入后等待
            if self.wait_after > 0:
                import time
                time.sleep(self.wait_after)
            
            # 更新上下文
            context['last_input_element'] = element
            context['last_input_text'] = self.text
            context['input_method'] = 'simulate_typing' if self.simulate_typing else 'direct'
            
            # 获取元素信息
            element_info = self._get_element_info(element)
            
            return {
                'success': True,
                'text': self.text,
                'text_length': len(self.text),
                'clear_first': self.clear_first,
                'simulate_typing': self.simulate_typing,
                'element_info': element_info,
                'message': f"成功输入文本: {self.text[:50]}{'...' if len(self.text) > 50 else ''}"
            }
            
        except Exception as e:
            error_msg = self._handle_error(context, e)
            return {
                'success': False,
                'error': error_msg,
                'text': self.text,
                'message': f"文本输入失败: {error_msg}"
            }
    
    def _get_element_info(self, element: Union[ChromiumElement, SessionElement]) -> dict:
        """获取元素信息"""
        try:
            info = {
                'tag': element.tag,
                'text': element.text,
            }
            
            # 获取常用属性
            for attr in ['id', 'class', 'name', 'type', 'placeholder', 'value']:
                try:
                    value = element.attr(attr)
                    if value:
                        info[attr] = value
                except:
                    pass
            
            # ChromiumElement 特有信息
            if isinstance(element, ChromiumElement):
                try:
                    info['is_enabled'] = element.is_enabled
                    info['is_displayed'] = element.is_displayed
                except:
                    pass
            
            return info
        except:
            return {'tag': 'unknown', 'text': ''}


class ClearTextNode(DrissionPageBaseNode):
    """清除文本节点
    
    清除指定元素中的文本内容。
    """
    
    def __init__(self, 
                 locator: str = None,
                 by_css: str = None,
                 by_xpath: str = None,
                 by_text: str = None,
                 by_tag: str = None,
                 by_attr: tuple = None,
                 index: int = 1,
                 timeout: float = 10.0,
                 wait_after: float = 0.5,
                 **kwargs):
        """
        初始化清除文本节点
        
        Args:
            locator: 通用定位器
            by_css: CSS选择器
            by_xpath: XPath表达式
            by_text: 文本内容
            by_tag: 标签名
            by_attr: 属性元组
            index: 元素索引
            timeout: 查找元素超时时间
            wait_after: 清除后等待时间
        """
        super().__init__(
            name="清除文本",
            description=f"清除元素文本 {locator or by_css or by_xpath or by_text or by_tag or by_attr}",
            **kwargs
        )
        
        self.locator = locator
        self.by_css = by_css
        self.by_xpath = by_xpath
        self.by_text = by_text
        self.by_tag = by_tag
        self.by_attr = by_attr
        self.index = index
        self.timeout = timeout
        self.wait_after = wait_after
        
        self.node_type = "drissionpage_clear_text"
    
    def execute(self, context: CONTEXT) -> Dict[str, Any]:
        """执行清除文本
        
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
                index=self.index,
                timeout=self.timeout
            )
            
            # 获取清除前的文本
            old_text = element.text
            
            # 清除文本
            if isinstance(element, ChromiumElement):
                element.clear()
            else:
                # SessionElement 使用 input 方法清除
                element.input('')
            
            # 清除后等待
            if self.wait_after > 0:
                import time
                time.sleep(self.wait_after)
            
            # 更新上下文
            context['last_cleared_element'] = element
            context['cleared_text'] = old_text
            
            # 获取元素信息
            element_info = self._get_element_info(element)
            
            return {
                'success': True,
                'old_text': old_text,
                'element_info': element_info,
                'message': f"成功清除文本: {old_text[:50]}{'...' if len(old_text) > 50 else ''}"
            }
            
        except Exception as e:
            error_msg = self._handle_error(context, e)
            return {
                'success': False,
                'error': error_msg,
                'message': f"清除文本失败: {error_msg}"
            }
    
    def _get_element_info(self, element: Union[ChromiumElement, SessionElement]) -> dict:
        """获取元素信息"""
        try:
            info = {
                'tag': element.tag,
                'text': element.text,
            }
            
            # 获取常用属性
            for attr in ['id', 'class', 'name', 'type', 'placeholder', 'value']:
                try:
                    value = element.attr(attr)
                    if value:
                        info[attr] = value
                except:
                    pass
            
            return info
        except:
            return {'tag': 'unknown', 'text': ''}


class SelectTextNode(DrissionPageBaseNode):
    """选择文本节点
    
    选择元素中的文本内容。
    """
    
    def __init__(self, 
                 locator: str = None,
                 by_css: str = None,
                 by_xpath: str = None,
                 by_text: str = None,
                 by_tag: str = None,
                 by_attr: tuple = None,
                 index: int = 1,
                 start: int = 0,
                 end: int = None,
                 timeout: float = 10.0,
                 wait_after: float = 0.5,
                 **kwargs):
        """
        初始化选择文本节点
        
        Args:
            locator: 通用定位器
            by_css: CSS选择器
            by_xpath: XPath表达式
            by_text: 文本内容
            by_tag: 标签名
            by_attr: 属性元组
            index: 元素索引
            start: 选择开始位置
            end: 选择结束位置（None表示到末尾）
            timeout: 查找元素超时时间
            wait_after: 选择后等待时间
        """
        super().__init__(
            name="选择文本",
            description=f"选择元素文本 {locator or by_css or by_xpath or by_text or by_tag or by_attr}",
            **kwargs
        )
        
        self.locator = locator
        self.by_css = by_css
        self.by_xpath = by_xpath
        self.by_text = by_text
        self.by_tag = by_tag
        self.by_attr = by_attr
        self.index = index
        self.start = start
        self.end = end
        self.timeout = timeout
        self.wait_after = wait_after
        
        self.node_type = "drissionpage_select_text"
    
    def execute(self, context: CONTEXT) -> Dict[str, Any]:
        """执行选择文本
        
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
                index=self.index,
                timeout=self.timeout
            )
            
            # 只有 ChromiumElement 支持文本选择
            if not isinstance(element, ChromiumElement):
                raise ValueError("SessionElement 不支持文本选择操作")
            
            # 获取当前文本
            current_text = element.text
            
            # 计算选择范围
            end_pos = self.end if self.end is not None else len(current_text)
            selected_text = current_text[self.start:end_pos]
            
            # 执行文本选择
            element.select(self.start, end_pos)
            
            # 选择后等待
            if self.wait_after > 0:
                import time
                time.sleep(self.wait_after)
            
            # 更新上下文
            context['last_selected_element'] = element
            context['selected_text'] = selected_text
            context['selection_range'] = (self.start, end_pos)
            
            # 获取元素信息
            element_info = self._get_element_info(element)
            
            return {
                'success': True,
                'selected_text': selected_text,
                'selection_range': (self.start, end_pos),
                'total_text_length': len(current_text),
                'element_info': element_info,
                'message': f"成功选择文本: {selected_text[:50]}{'...' if len(selected_text) > 50 else ''}"
            }
            
        except Exception as e:
            error_msg = self._handle_error(context, e)
            return {
                'success': False,
                'error': error_msg,
                'selection_range': (self.start, self.end),
                'message': f"选择文本失败: {error_msg}"
            }
    
    def _get_element_info(self, element: ChromiumElement) -> dict:
        """获取元素信息"""
        try:
            info = {
                'tag': element.tag,
                'text': element.text,
            }
            
            # 获取常用属性
            for attr in ['id', 'class', 'name', 'type', 'placeholder', 'value']:
                try:
                    value = element.attr(attr)
                    if value:
                        info[attr] = value
                except:
                    pass
            
            return info
        except:
            return {'tag': 'unknown', 'text': ''}


class UploadFileNode(DrissionPageBaseNode):
    """文件上传节点
    
    上传文件到指定的文件输入元素。
    """
    
    def __init__(self, 
                 file_path: str,
                 locator: str = None,
                 by_css: str = None,
                 by_xpath: str = None,
                 by_text: str = None,
                 by_tag: str = None,
                 by_attr: tuple = None,
                 index: int = 1,
                 timeout: float = 10.0,
                 wait_after: float = 1.0,
                 **kwargs):
        """
        初始化文件上传节点
        
        Args:
            file_path: 要上传的文件路径
            locator: 通用定位器
            by_css: CSS选择器
            by_xpath: XPath表达式
            by_text: 文本内容
            by_tag: 标签名
            by_attr: 属性元组
            index: 元素索引
            timeout: 查找元素超时时间
            wait_after: 上传后等待时间
        """
        super().__init__(
            name="文件上传",
            description=f"上传文件: {file_path}",
            **kwargs
        )
        
        self.file_path = file_path
        self.locator = locator
        self.by_css = by_css
        self.by_xpath = by_xpath
        self.by_text = by_text
        self.by_tag = by_tag
        self.by_attr = by_attr
        self.index = index
        self.timeout = timeout
        self.wait_after = wait_after
        
        self.node_type = "drissionpage_upload_file"
    
    def execute(self, context: CONTEXT) -> Dict[str, Any]:
        """执行文件上传
        
        Args:
            context: 工作流上下文
            
        Returns:
            执行结果
        """
        try:
            import os
            
            # 检查文件是否存在
            if not os.path.exists(self.file_path):
                raise FileNotFoundError(f"文件不存在: {self.file_path}")
            
            # 查找文件输入元素
            element = self._find_element(
                context=context,
                locator=self.locator,
                by_css=self.by_css,
                by_xpath=self.by_xpath,
                by_text=self.by_text,
                by_tag=self.by_tag,
                by_attr=self.by_attr,
                index=self.index,
                timeout=self.timeout
            )
            
            # 检查元素类型
            if element.tag.lower() != 'input' or element.attr('type') != 'file':
                raise ValueError("元素不是文件输入类型")
            
            # 上传文件
            if isinstance(element, ChromiumElement):
                element.input(self.file_path)
            else:
                # SessionElement 不支持文件上传
                raise ValueError("SessionElement 不支持文件上传")
            
            # 上传后等待
            if self.wait_after > 0:
                import time
                time.sleep(self.wait_after)
            
            # 更新上下文
            context['last_upload_element'] = element
            context['uploaded_file_path'] = self.file_path
            context['uploaded_file_name'] = os.path.basename(self.file_path)
            
            # 获取文件信息
            file_info = {
                'file_path': self.file_path,
                'file_name': os.path.basename(self.file_path),
                'file_size': os.path.getsize(self.file_path)
            }
            
            # 获取元素信息
            element_info = self._get_element_info(element)
            
            return {
                'success': True,
                'file_info': file_info,
                'element_info': element_info,
                'message': f"成功上传文件: {os.path.basename(self.file_path)}"
            }
            
        except Exception as e:
            error_msg = self._handle_error(context, e)
            return {
                'success': False,
                'error': error_msg,
                'file_path': self.file_path,
                'message': f"文件上传失败: {error_msg}"
            }
    
    def _get_element_info(self, element: ChromiumElement) -> dict:
        """获取元素信息"""
        try:
            info = {
                'tag': element.tag,
                'type': element.attr('type'),
            }
            
            # 获取常用属性
            for attr in ['id', 'class', 'name', 'accept', 'multiple']:
                try:
                    value = element.attr(attr)
                    if value:
                        info[attr] = value
                except:
                    pass
            
            return info
        except:
            return {'tag': 'unknown', 'type': 'unknown'}