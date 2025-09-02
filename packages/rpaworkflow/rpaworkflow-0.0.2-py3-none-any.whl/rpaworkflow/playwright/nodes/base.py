#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Playwright 基础节点类

提供 Playwright 的基础功能和浏览器管理。
"""
from typing import Any, Generic, List, Optional, Union, Dict, Callable

from playwright.sync_api import Page, Locator, Browser, BrowserContext, expect

from rpaworkflow.node import WorkflowNode
from rpaworkflow.playwright.workflow_context import CONTEXT


class PlaywrightBaseNode(WorkflowNode, Generic[CONTEXT]):
    """Playwright 基础节点类

    提供 Playwright 的基础功能和浏览器管理。
    """

    def __init__(self, name: str, description: str, **kwargs):
        super().__init__(name, description, **kwargs)

    def get_browser(self, context: CONTEXT) -> Browser:
        """获取浏览器实例
        
        Args:
            context: 工作流上下文
            
        Returns:
            Browser: 浏览器实例
        """
        return context['browser']
    
    def get_browser_context(self, context: CONTEXT) -> BrowserContext:
        """获取浏览器上下文
        
        Args:
            context: 工作流上下文
            
        Returns:
            BrowserContext: 浏览器上下文
        """
        return context['browser_context']

    def get_page(self, context: CONTEXT) -> Page:
        """获取当前页面
        
        Args:
            context: 工作流上下文
            
        Returns:
            Page: 页面实例
        """
        return context['page']

    def locator(self, context: CONTEXT, selector: str) -> Locator:
        """获取元素定位器
        
        Args:
            context: 工作流上下文
            selector: 选择器
            
        Returns:
            Locator: 元素定位器
        """
        page = self.get_page(context)
        return page.locator(selector)

    def get_by_role(self, context: CONTEXT, role: str, **kwargs) -> Locator:
        """通过角色获取元素
        
        Args:
            context: 工作流上下文
            role: 角色名称
            **kwargs: 其他参数
            
        Returns:
            Locator: 元素定位器
        """
        page = self.get_page(context)
        return page.get_by_role(role, **kwargs)

    def get_by_text(self, context: CONTEXT, text: str, **kwargs) -> Locator:
        """通过文本获取元素
        
        Args:
            context: 工作流上下文
            text: 文本内容
            **kwargs: 其他参数
            
        Returns:
            Locator: 元素定位器
        """
        page = self.get_page(context)
        return page.get_by_text(text, **kwargs)

    def get_by_label(self, context: CONTEXT, text: str, **kwargs) -> Locator:
        """通过标签获取元素
        
        Args:
            context: 工作流上下文
            text: 标签文本
            **kwargs: 其他参数
            
        Returns:
            Locator: 元素定位器
        """
        page = self.get_page(context)
        return page.get_by_label(text, **kwargs)

    def get_by_placeholder(self, context: CONTEXT, text: str, **kwargs) -> Locator:
        """通过占位符获取元素
        
        Args:
            context: 工作流上下文
            text: 占位符文本
            **kwargs: 其他参数
            
        Returns:
            Locator: 元素定位器
        """
        page = self.get_page(context)
        return page.get_by_placeholder(text, **kwargs)

    def get_by_alt_text(self, context: CONTEXT, text: str, **kwargs) -> Locator:
        """通过替代文本获取元素
        
        Args:
            context: 工作流上下文
            text: 替代文本
            **kwargs: 其他参数
            
        Returns:
            Locator: 元素定位器
        """
        page = self.get_page(context)
        return page.get_by_alt_text(text, **kwargs)

    def get_by_title(self, context: CONTEXT, text: str, **kwargs) -> Locator:
        """通过标题获取元素
        
        Args:
            context: 工作流上下文
            text: 标题文本
            **kwargs: 其他参数
            
        Returns:
            Locator: 元素定位器
        """
        page = self.get_page(context)
        return page.get_by_title(text, **kwargs)

    def get_by_test_id(self, context: CONTEXT, test_id: str) -> Locator:
        """通过测试ID获取元素
        
        Args:
            context: 工作流上下文
            test_id: 测试ID
            
        Returns:
            Locator: 元素定位器
        """
        page = self.get_page(context)
        return page.get_by_test_id(test_id)

    def wait_for_selector(self, context: CONTEXT, selector: str, **kwargs) -> Optional[Locator]:
        """等待选择器出现
        
        Args:
            context: 工作流上下文
            selector: 选择器
            **kwargs: 其他参数
            
        Returns:
            Optional[Locator]: 元素定位器
        """
        page = self.get_page(context)
        page.wait_for_selector(selector, **kwargs)
        return page.locator(selector)

    def wait_for_load_state(self, context: CONTEXT, state: str = 'load', **kwargs) -> None:
        """等待页面加载状态
        
        Args:
            context: 工作流上下文
            state: 加载状态，可选值: 'load', 'domcontentloaded', 'networkidle'
            **kwargs: 其他参数
        """
        page = self.get_page(context)
        page.wait_for_load_state(state, **kwargs)
        context['page_load_state'] = state

    def wait_for_function(self, context: CONTEXT, expression: str, **kwargs) -> Any:
        """等待JavaScript函数执行
        
        Args:
            context: 工作流上下文
            expression: JavaScript表达式
            **kwargs: 其他参数
            
        Returns:
            Any: 执行结果
        """
        page = self.get_page(context)
        return page.wait_for_function(expression, **kwargs)

    def expect_locator(self, locator: Locator, **kwargs) -> None:
        """断言定位器状态
        
        Args:
            locator: 元素定位器
            **kwargs: 其他参数，如 to_be_visible=True, to_be_enabled=True 等
        """
        assertion = expect(locator)
        
        for key, value in kwargs.items():
            if hasattr(assertion, key):
                method = getattr(assertion, key)
                if callable(method):
                    method(value)

    def evaluate(self, context: CONTEXT, expression: str, arg: Any = None) -> Any:
        """执行JavaScript
        
        Args:
            context: 工作流上下文
            expression: JavaScript表达式
            arg: 参数
            
        Returns:
            Any: 执行结果
        """
        page = self.get_page(context)
        return page.evaluate(expression, arg)

    def evaluate_handle(self, context: CONTEXT, expression: str, arg: Any = None) -> Any:
        """执行JavaScript并返回句柄
        
        Args:
            context: 工作流上下文
            expression: JavaScript表达式
            arg: 参数
            
        Returns:
            Any: 执行结果句柄
        """
        page = self.get_page(context)
        handle = page.evaluate_handle(expression, arg)
        context['last_element_handle'] = handle
        return handle