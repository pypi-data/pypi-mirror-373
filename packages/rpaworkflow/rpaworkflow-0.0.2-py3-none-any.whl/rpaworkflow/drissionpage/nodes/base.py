#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DrissionPage 基础节点类

提供 DrissionPage 的基础功能和页面管理。
"""

from typing import Any, Union, List

from DrissionPage import ChromiumPage, SessionPage, WebPage
from DrissionPage._elements.chromium_element import ChromiumElement
from DrissionPage._elements.session_element import SessionElement
from DrissionPage.errors import ElementNotFoundError

from rpaworkflow.node import WorkflowNode
from ..workflow_context import CONTEXT


class DrissionPageBaseNode(WorkflowNode):
    """DrissionPage 基础节点类
    
    提供 DrissionPage 的基础功能和页面管理。
    """
    
    def __init__(self, name: str, description: str = "", **kwargs):
        super().__init__(name, description, **kwargs)
        self.node_type = "drissionpage_base"
    
    def _get_page(self, context: CONTEXT) -> Union[ChromiumPage, SessionPage, WebPage]:
        """获取页面实例
        
        Args:
            context: 工作流上下文
            
        Returns:
            页面实例
            
        Raises:
            ValueError: 如果页面实例不存在
        """
        page = context.get('page')
        if page is None:
            raise ValueError("页面实例不存在，请先创建页面")
        return page
    
    def _find_element(self, 
                     context: CONTEXT,
                     locator: str = None,
                     by_css: str = None,
                     by_xpath: str = None,
                     by_text: str = None,
                     by_tag: str = None,
                     by_attr: tuple = None,
                     index: int = 1,
                     timeout: float = None) -> Union[ChromiumElement, SessionElement]:
        """查找元素
        
        Args:
            context: 工作流上下文
            locator: 通用定位器（自动判断类型）
            by_css: CSS选择器
            by_xpath: XPath表达式
            by_text: 文本内容
            by_tag: 标签名
            by_attr: 属性元组 (属性名, 属性值)
            index: 元素索引（从1开始）
            timeout: 等待超时时间
            
        Returns:
            元素对象
            
        Raises:
            ElementNotFoundError: 元素未找到
        """
        page = self._get_page(context)
        
        try:
            # 根据不同的定位方式查找元素
            if by_css:
                element = page.ele(by_css, index=index, timeout=timeout)
                context['locator'] = by_css
                context['locator_type'] = 'css'
            elif by_xpath:
                element = page.ele(by_xpath, index=index, timeout=timeout)
                context['locator'] = by_xpath
                context['locator_type'] = 'xpath'
            elif by_text:
                element = page.ele(f'text:{by_text}', index=index, timeout=timeout)
                context['locator'] = by_text
                context['locator_type'] = 'text'
            elif by_tag:
                element = page.ele(f'tag:{by_tag}', index=index, timeout=timeout)
                context['locator'] = by_tag
                context['locator_type'] = 'tag'
            elif by_attr:
                attr_name, attr_value = by_attr
                element = page.ele(f'@{attr_name}={attr_value}', index=index, timeout=timeout)
                context['locator'] = f'{attr_name}={attr_value}'
                context['locator_type'] = 'attr'
            elif locator:
                # 自动判断定位器类型
                if locator.startswith('//'):
                    element = page.ele(locator, index=index, timeout=timeout)
                    context['locator_type'] = 'xpath'
                elif locator.startswith('text:'):
                    element = page.ele(locator, index=index, timeout=timeout)
                    context['locator_type'] = 'text'
                elif locator.startswith('tag:'):
                    element = page.ele(locator, index=index, timeout=timeout)
                    context['locator_type'] = 'tag'
                elif locator.startswith('@'):
                    element = page.ele(locator, index=index, timeout=timeout)
                    context['locator_type'] = 'attr'
                else:
                    # 默认作为CSS选择器
                    element = page.ele(locator, index=index, timeout=timeout)
                    context['locator_type'] = 'css'
                context['locator'] = locator
            else:
                raise ValueError("必须提供至少一种定位方式")
            
            if element is None:
                raise ElementNotFoundError("元素未找到")
            
            # 更新上下文
            context['element'] = element
            return element
            
        except Exception as e:
            context['last_error'] = str(e)
            raise
    
    def _find_elements(self, 
                      context: CONTEXT,
                      locator: str = None,
                      by_css: str = None,
                      by_xpath: str = None,
                      by_text: str = None,
                      by_tag: str = None,
                      by_attr: tuple = None,
                      timeout: float = None) -> List[Union[ChromiumElement, SessionElement]]:
        """查找多个元素
        
        Args:
            context: 工作流上下文
            locator: 通用定位器
            by_css: CSS选择器
            by_xpath: XPath表达式
            by_text: 文本内容
            by_tag: 标签名
            by_attr: 属性元组
            timeout: 等待超时时间
            
        Returns:
            元素列表
        """
        page = self._get_page(context)
        
        try:
            # 根据不同的定位方式查找元素
            if by_css:
                elements = page.eles(by_css, timeout=timeout)
                context['locator'] = by_css
                context['locator_type'] = 'css'
            elif by_xpath:
                elements = page.eles(by_xpath, timeout=timeout)
                context['locator'] = by_xpath
                context['locator_type'] = 'xpath'
            elif by_text:
                elements = page.eles(f'text:{by_text}', timeout=timeout)
                context['locator'] = by_text
                context['locator_type'] = 'text'
            elif by_tag:
                elements = page.eles(f'tag:{by_tag}', timeout=timeout)
                context['locator'] = by_tag
                context['locator_type'] = 'tag'
            elif by_attr:
                attr_name, attr_value = by_attr
                elements = page.eles(f'@{attr_name}={attr_value}', timeout=timeout)
                context['locator'] = f'{attr_name}={attr_value}'
                context['locator_type'] = 'attr'
            elif locator:
                # 自动判断定位器类型
                if locator.startswith('//'):
                    elements = page.eles(locator, timeout=timeout)
                    context['locator_type'] = 'xpath'
                elif locator.startswith('text:'):
                    elements = page.eles(locator, timeout=timeout)
                    context['locator_type'] = 'text'
                elif locator.startswith('tag:'):
                    elements = page.eles(locator, timeout=timeout)
                    context['locator_type'] = 'tag'
                elif locator.startswith('@'):
                    elements = page.eles(locator, timeout=timeout)
                    context['locator_type'] = 'attr'
                else:
                    # 默认作为CSS选择器
                    elements = page.eles(locator, timeout=timeout)
                    context['locator_type'] = 'css'
                context['locator'] = locator
            else:
                raise ValueError("必须提供至少一种定位方式")
            
            # 更新上下文
            context['elements'] = elements
            return elements
            
        except Exception as e:
            context['last_error'] = str(e)
            raise
    
    def _wait_for_element(self, 
                         context: CONTEXT,
                         locator: str,
                         timeout: float = 10.0,
                         condition: str = 'exist') -> bool:
        """等待元素满足条件
        
        Args:
            context: 工作流上下文
            locator: 元素定位器
            timeout: 超时时间
            condition: 等待条件 ('exist', 'visible', 'hidden', 'clickable')
            
        Returns:
            是否满足条件
        """
        page = self._get_page(context)
        
        try:
            if condition == 'exist':
                return page.wait.eles_loaded(locator, timeout=timeout)
            elif condition == 'visible':
                return page.wait.ele_displayed(locator, timeout=timeout)
            elif condition == 'hidden':
                return page.wait.ele_hidden(locator, timeout=timeout)
            elif condition == 'clickable':
                # DrissionPage 没有直接的 clickable 等待，使用 displayed 代替
                return page.wait.ele_displayed(locator, timeout=timeout)
            else:
                raise ValueError(f"不支持的等待条件: {condition}")
                
        except Exception as e:
            context['last_error'] = str(e)
            return False
    
    def _execute_script(self, 
                       context: CONTEXT,
                       script: str,
                       *args) -> Any:
        """执行JavaScript脚本
        
        Args:
            context: 工作流上下文
            script: JavaScript代码
            *args: 脚本参数
            
        Returns:
            脚本执行结果
        """
        page = self._get_page(context)
        
        # 只有 ChromiumPage 和 WebPage 支持 JavaScript
        if isinstance(page, SessionPage):
            raise ValueError("SessionPage 不支持 JavaScript 执行")
        
        try:
            return page.run_js(script, *args)
        except Exception as e:
            context['last_error'] = str(e)
            raise
    
    def _get_page_info(self, context: CONTEXT) -> dict:
        """获取页面信息
        
        Args:
            context: 工作流上下文
            
        Returns:
            页面信息字典
        """
        page = self._get_page(context)
        
        info = {
            'url': page.url,
            'title': page.title,
            'page_type': context.get('page_type', 'unknown')
        }
        
        # 更新上下文
        context['url'] = page.url
        context['title'] = page.title
        
        # 如果是 ChromiumPage，获取更多信息
        if isinstance(page, ChromiumPage):
            info.update({
                'ready_state': page._ready_state,
                'tab_count': len(page.tab_ids),
                'current_tab_id': page.tab_id
            })
            context['ready_state'] = page._ready_state
            context['tab_count'] = len(page.tab_ids)
            context['current_tab_id'] = page.tab_id
        
        return info
    
    def _handle_error(self, context: CONTEXT, error: Exception) -> str:
        """处理错误
        
        Args:
            context: 工作流上下文
            error: 异常对象
            
        Returns:
            错误信息
        """
        error_msg = str(error)
        context['last_error'] = error_msg
        
        # 增加错误计数
        error_count = context.get('error_count', 0)
        context['error_count'] = error_count + 1
        
        return error_msg