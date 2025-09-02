#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
等待节点
"""
from typing import Optional, Any, Union, Callable

from playwright.sync_api import Locator, expect

from rpaworkflow.node import DataStorageNode
from rpaworkflow.playwright.nodes.base import PlaywrightBaseNode
from rpaworkflow.playwright.workflow_context import CONTEXT


class WaitNode(PlaywrightBaseNode, DataStorageNode):
    """等待节点

    用于等待各种条件满足
    """

    def __init__(self,
                 name: str = "等待条件",
                 description: str = "等待指定条件满足",
                 condition: str = "selector",  # selector, visible, hidden, enabled, disabled, text, value
                 selector: Optional[str] = None,
                 by_role: Optional[str] = None,
                 by_text: Optional[str] = None,
                 by_label: Optional[str] = None,
                 expected_text: Optional[str] = None,
                 expected_value: Optional[str] = None,
                 timeout: float = 30.0,
                 **kwargs):
        super().__init__(name, description, output_key='wait_result', **kwargs)
        self.condition = condition.lower()
        self.selector = selector
        self.by_role = by_role
        self.by_text = by_text
        self.by_label = by_label
        self.expected_text = expected_text
        self.expected_value = expected_value
        self.timeout = timeout

    def _get_locator(self, context: CONTEXT) -> Locator:
        """获取元素定位器"""
        if self.selector:
            return self.locator(context, self.selector)
        elif self.by_role:
            return self.get_by_role(context, self.by_role)
        elif self.by_text:
            return self.get_by_text(context, self.by_text)
        elif self.by_label:
            return self.get_by_label(context, self.by_label)
        else:
            raise ValueError("必须提供至少一种元素定位方式")

    def execute(self, context: CONTEXT) -> Any:
        """执行等待操作"""
        try:
            timeout_ms = self.timeout * 1000
            
            if self.condition == "selector":
                # 等待选择器出现
                locator = self._get_locator(context)
                self.logger.info(f"等待元素出现，超时: {self.timeout}秒")
                locator.wait_for(state="attached", timeout=timeout_ms)
                result = True
                
            elif self.condition == "visible":
                # 等待元素可见
                locator = self._get_locator(context)
                self.logger.info(f"等待元素可见，超时: {self.timeout}秒")
                locator.wait_for(state="visible", timeout=timeout_ms)
                result = True
                
            elif self.condition == "hidden":
                # 等待元素隐藏
                locator = self._get_locator(context)
                self.logger.info(f"等待元素隐藏，超时: {self.timeout}秒")
                locator.wait_for(state="hidden", timeout=timeout_ms)
                result = True
                
            elif self.condition == "enabled":
                # 等待元素启用
                locator = self._get_locator(context)
                self.logger.info(f"等待元素启用，超时: {self.timeout}秒")
                expect(locator).to_be_enabled(timeout=timeout_ms)
                result = True
                
            elif self.condition == "disabled":
                # 等待元素禁用
                locator = self._get_locator(context)
                self.logger.info(f"等待元素禁用，超时: {self.timeout}秒")
                expect(locator).to_be_disabled(timeout=timeout_ms)
                result = True
                
            elif self.condition == "text":
                # 等待文本内容
                if not self.expected_text:
                    raise ValueError("等待文本条件需要提供expected_text参数")
                locator = self._get_locator(context)
                self.logger.info(f"等待文本内容: {self.expected_text}，超时: {self.timeout}秒")
                expect(locator).to_contain_text(self.expected_text, timeout=timeout_ms)
                result = self.expected_text
                
            elif self.condition == "value":
                # 等待输入值
                if not self.expected_value:
                    raise ValueError("等待值条件需要提供expected_value参数")
                locator = self._get_locator(context)
                self.logger.info(f"等待输入值: {self.expected_value}，超时: {self.timeout}秒")
                expect(locator).to_have_value(self.expected_value, timeout=timeout_ms)
                result = self.expected_value
                
            else:
                raise ValueError(f"不支持的等待条件: {self.condition}")
            
            # 更新上下文
            if 'locator' in locals():
                context['last_locator'] = locator
            
            self.logger.info(f"等待条件满足: {self.condition}")
            
            return result
            
        except Exception as e:
            self.logger.error(f"等待操作失败: {e}")
            raise


class WaitForTimeoutNode(PlaywrightBaseNode):
    """等待超时节点

    用于等待指定时间
    """

    def __init__(self,
                 name: str = "等待时间",
                 description: str = "等待指定时间",
                 timeout: float = 1.0,
                 **kwargs):
        super().__init__(name, description, **kwargs)
        self.timeout = timeout

    def execute(self, context: CONTEXT) -> Any:
        """执行等待时间操作"""
        page = self.get_page(context)
        
        try:
            self.logger.info(f"等待 {self.timeout} 秒")
            page.wait_for_timeout(self.timeout * 1000)
            
            self.logger.info("等待完成")
            
            return self.timeout
            
        except Exception as e:
            self.logger.error(f"等待时间失败: {e}")
            raise


class WaitForLoadStateNode(PlaywrightBaseNode):
    """等待页面加载状态节点

    用于等待页面加载到指定状态
    """

    def __init__(self,
                 name: str = "等待页面加载",
                 description: str = "等待页面加载到指定状态",
                 state: str = "load",  # load, domcontentloaded, networkidle
                 timeout: Optional[float] = None,
                 **kwargs):
        super().__init__(name, description, **kwargs)
        self.state = state
        self.timeout = timeout

    def execute(self, context: CONTEXT) -> Any:
        """执行等待页面加载操作"""
        page = self.get_page(context)
        
        try:
            self.logger.info(f"等待页面加载状态: {self.state}")
            
            if self.timeout:
                page.wait_for_load_state(self.state, timeout=self.timeout * 1000)
            else:
                page.wait_for_load_state(self.state)
            
            # 更新上下文
            context['page_load_state'] = self.state
            
            self.logger.info(f"页面加载完成: {self.state}")
            
            return self.state
            
        except Exception as e:
            self.logger.error(f"等待页面加载失败: {e}")
            raise


class WaitForFunctionNode(PlaywrightBaseNode):
    """等待JavaScript函数节点

    用于等待JavaScript函数返回真值
    """

    def __init__(self,
                 name: str = "等待JavaScript函数",
                 description: str = "等待JavaScript函数返回真值",
                 expression: str = "",
                 arg: Optional[Any] = None,
                 timeout: Optional[float] = None,
                 polling: Union[float, str] = "raf",  # raf, mutation, 或数字(毫秒)
                 **kwargs):
        super().__init__(name, description, **kwargs)
        self.expression = expression
        self.arg = arg
        self.timeout = timeout
        self.polling = polling

    def execute(self, context: CONTEXT) -> Any:
        """执行等待JavaScript函数操作"""
        page = self.get_page(context)
        
        try:
            self.logger.info(f"等待JavaScript函数: {self.expression}")
            
            options = {}
            if self.timeout:
                options["timeout"] = self.timeout * 1000
            if self.polling != "raf":
                options["polling"] = self.polling
            
            result = page.wait_for_function(self.expression, arg=self.arg, **options)
            
            self.logger.info("JavaScript函数条件满足")
            
            return result.json_value() if result else None
            
        except Exception as e:
            self.logger.error(f"等待JavaScript函数失败: {e}")
            raise


class WaitForResponseNode(PlaywrightBaseNode):
    """等待响应节点

    用于等待特定的网络响应
    """

    def __init__(self,
                 name: str = "等待响应",
                 description: str = "等待特定的网络响应",
                 url_pattern: str = "",
                 timeout: Optional[float] = None,
                 **kwargs):
        super().__init__(name, description, **kwargs)
        self.url_pattern = url_pattern
        self.timeout = timeout

    def execute(self, context: CONTEXT) -> Any:
        """执行等待响应操作"""
        page = self.get_page(context)
        
        try:
            self.logger.info(f"等待响应: {self.url_pattern}")
            
            options = {}
            if self.timeout:
                options["timeout"] = self.timeout * 1000
            
            with page.expect_response(self.url_pattern, **options) as response_info:
                pass
            
            response = response_info.value
            
            self.logger.info(f"收到响应: {response.url}, 状态: {response.status}")
            
            return {
                "url": response.url,
                "status": response.status,
                "headers": dict(response.headers),
            }
            
        except Exception as e:
            self.logger.error(f"等待响应失败: {e}")
            raise


class WaitForRequestNode(PlaywrightBaseNode):
    """等待请求节点

    用于等待特定的网络请求
    """

    def __init__(self,
                 name: str = "等待请求",
                 description: str = "等待特定的网络请求",
                 url_pattern: str = "",
                 timeout: Optional[float] = None,
                 **kwargs):
        super().__init__(name, description, **kwargs)
        self.url_pattern = url_pattern
        self.timeout = timeout

    def execute(self, context: CONTEXT) -> Any:
        """执行等待请求操作"""
        page = self.get_page(context)
        
        try:
            self.logger.info(f"等待请求: {self.url_pattern}")
            
            options = {}
            if self.timeout:
                options["timeout"] = self.timeout * 1000
            
            with page.expect_request(self.url_pattern, **options) as request_info:
                pass
            
            request = request_info.value
            
            self.logger.info(f"捕获请求: {request.url}, 方法: {request.method}")
            
            return {
                "url": request.url,
                "method": request.method,
                "headers": dict(request.headers),
                "post_data": request.post_data,
            }
            
        except Exception as e:
            self.logger.error(f"等待请求失败: {e}")
            raise