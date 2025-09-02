#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
输入文本节点
"""
from typing import Optional, Any, List

from playwright.sync_api import Locator

from rpaworkflow.node import DataStorageNode
from rpaworkflow.playwright.nodes.base import PlaywrightBaseNode
from rpaworkflow.playwright.workflow_context import CONTEXT


class InputTextNode(PlaywrightBaseNode, DataStorageNode):
    """输入文本节点

    用于在输入框中输入文本
    """

    def __init__(self,
                 name: str = "输入文本",
                 description: str = "在指定元素中输入文本",
                 text: str = "",
                 selector: Optional[str] = None,
                 # 定位方式
                 by_role: Optional[str] = None,
                 by_label: Optional[str] = None,
                 by_placeholder: Optional[str] = None,
                 by_test_id: Optional[str] = None,
                 # 输入选项
                 clear_first: bool = True,
                 delay: Optional[float] = None,
                 no_wait_after: bool = False,
                 timeout: Optional[float] = None,
                 force: bool = False,
                 # 等待选项
                 wait_for_selector: bool = True,
                 wait_timeout: Optional[float] = None,
                 **kwargs):
        super().__init__(name, description, output_key='last_input_text', **kwargs)
        self.text = text
        self.selector = selector
        self.by_role = by_role
        self.by_label = by_label
        self.by_placeholder = by_placeholder
        self.by_test_id = by_test_id
        
        self.clear_first = clear_first
        self.delay = delay
        self.no_wait_after = no_wait_after
        self.timeout = timeout
        self.force = force
        
        self.wait_for_selector = wait_for_selector
        self.wait_timeout = wait_timeout

    def _get_locator(self, context: CONTEXT) -> Locator:
        """获取元素定位器"""
        if self.selector:
            return self.locator(context, self.selector)
        elif self.by_role:
            return self.get_by_role(context, self.by_role)
        elif self.by_label:
            return self.get_by_label(context, self.by_label)
        elif self.by_placeholder:
            return self.get_by_placeholder(context, self.by_placeholder)
        elif self.by_test_id:
            return self.get_by_test_id(context, self.by_test_id)
        else:
            raise ValueError("必须提供至少一种元素定位方式")

    def execute(self, context: CONTEXT) -> Any:
        """执行输入文本操作"""
        try:
            # 获取定位器
            locator = self._get_locator(context)
            
            # 等待元素出现
            if self.wait_for_selector:
                wait_timeout = self.wait_timeout or self.timeout
                if wait_timeout:
                    locator.wait_for(timeout=wait_timeout * 1000)
                else:
                    locator.wait_for()
            
            # 清空输入框
            if self.clear_first:
                self.logger.info("清空输入框")
                locator.clear(timeout=self.timeout * 1000 if self.timeout else None)
            
            # 准备输入选项
            fill_options = {
                "force": self.force,
                "no_wait_after": self.no_wait_after,
            }
            
            if self.timeout:
                fill_options["timeout"] = self.timeout * 1000
            
            # 记录输入信息
            element_info = self._get_element_info()
            self.logger.info(f"在元素中输入文本: {element_info}")
            self.logger.info(f"输入内容: {self.text}")
            
            # 执行输入
            locator.fill(self.text, **fill_options)
            
            # 如果设置了延迟，使用type方法
            if self.delay:
                locator.clear()
                type_options = {
                    "delay": self.delay * 1000,  # 转换为毫秒
                    "no_wait_after": self.no_wait_after,
                }
                if self.timeout:
                    type_options["timeout"] = self.timeout * 1000
                
                locator.type(self.text, **type_options)
            
            # 更新上下文
            context['last_locator'] = locator
            context['last_input_text'] = self.text
            
            self.logger.info("文本输入完成")
            
            return self.text
            
        except Exception as e:
            self.logger.error(f"输入文本失败: {e}")
            raise

    def _get_element_info(self) -> str:
        """获取元素信息用于日志"""
        if self.selector:
            return f"选择器: {self.selector}"
        elif self.by_role:
            return f"角色: {self.by_role}"
        elif self.by_label:
            return f"标签: {self.by_label}"
        elif self.by_placeholder:
            return f"占位符: {self.by_placeholder}"
        elif self.by_test_id:
            return f"测试ID: {self.by_test_id}"
        else:
            return "未知元素"


class TypeTextNode(PlaywrightBaseNode, DataStorageNode):
    """逐字输入文本节点

    用于逐字符输入文本，模拟真实用户输入
    """

    def __init__(self,
                 name: str = "逐字输入文本",
                 description: str = "逐字符输入文本",
                 text: str = "",
                 selector: Optional[str] = None,
                 by_role: Optional[str] = None,
                 by_label: Optional[str] = None,
                 by_placeholder: Optional[str] = None,
                 delay: float = 0.1,  # 每个字符间的延迟
                 timeout: Optional[float] = None,
                 **kwargs):
        super().__init__(name, description, output_key='last_input_text', **kwargs)
        self.text = text
        self.selector = selector
        self.by_role = by_role
        self.by_label = by_label
        self.by_placeholder = by_placeholder
        self.delay = delay
        self.timeout = timeout

    def _get_locator(self, context: CONTEXT) -> Locator:
        """获取元素定位器"""
        if self.selector:
            return self.locator(context, self.selector)
        elif self.by_role:
            return self.get_by_role(context, self.by_role)
        elif self.by_label:
            return self.get_by_label(context, self.by_label)
        elif self.by_placeholder:
            return self.get_by_placeholder(context, self.by_placeholder)
        else:
            raise ValueError("必须提供至少一种元素定位方式")

    def execute(self, context: CONTEXT) -> Any:
        """执行逐字输入操作"""
        try:
            # 获取定位器
            locator = self._get_locator(context)
            
            # 等待元素出现并聚焦
            locator.wait_for()
            locator.focus()
            
            # 准备输入选项
            type_options = {
                "delay": self.delay * 1000,  # 转换为毫秒
            }
            
            if self.timeout:
                type_options["timeout"] = self.timeout * 1000
            
            self.logger.info(f"逐字输入文本: {self.text}")
            self.logger.info(f"字符间延迟: {self.delay}秒")
            
            # 执行逐字输入
            locator.type(self.text, **type_options)
            
            # 更新上下文
            context['last_locator'] = locator
            context['last_input_text'] = self.text
            
            self.logger.info("逐字输入完成")
            
            return self.text
            
        except Exception as e:
            self.logger.error(f"逐字输入失败: {e}")
            raise


class KeyboardInputNode(PlaywrightBaseNode, DataStorageNode):
    """键盘输入节点

    用于发送键盘按键
    """

    def __init__(self,
                 name: str = "键盘输入",
                 description: str = "发送键盘按键",
                 key: str = "",
                 keys: Optional[List[str]] = None,
                 delay: Optional[float] = None,
                 **kwargs):
        super().__init__(name, description, output_key='last_keyboard_input', **kwargs)
        self.key = key
        self.keys = keys or []
        self.delay = delay

    def execute(self, context: CONTEXT) -> Any:
        """执行键盘输入操作"""
        page = self.get_page(context)
        
        try:
            if self.key:
                # 发送单个按键
                self.logger.info(f"发送按键: {self.key}")
                if self.delay:
                    page.keyboard.press(self.key, delay=self.delay * 1000)
                else:
                    page.keyboard.press(self.key)
                
                context['last_keyboard_input'] = self.key
                return self.key
                
            elif self.keys:
                # 发送多个按键
                self.logger.info(f"发送按键序列: {self.keys}")
                for key in self.keys:
                    if self.delay:
                        page.keyboard.press(key, delay=self.delay * 1000)
                    else:
                        page.keyboard.press(key)
                
                context['last_keyboard_input'] = '+'.join(self.keys)
                return self.keys
            else:
                raise ValueError("必须提供按键或按键序列")
            
        except Exception as e:
            self.logger.error(f"键盘输入失败: {e}")
            raise


class ClearInputNode(PlaywrightBaseNode):
    """清空输入节点

    用于清空输入框内容
    """

    def __init__(self,
                 name: str = "清空输入",
                 description: str = "清空输入框内容",
                 selector: Optional[str] = None,
                 by_role: Optional[str] = None,
                 by_label: Optional[str] = None,
                 by_placeholder: Optional[str] = None,
                 timeout: Optional[float] = None,
                 **kwargs):
        super().__init__(name, description, **kwargs)
        self.selector = selector
        self.by_role = by_role
        self.by_label = by_label
        self.by_placeholder = by_placeholder
        self.timeout = timeout

    def _get_locator(self, context: CONTEXT) -> Locator:
        """获取元素定位器"""
        if self.selector:
            return self.locator(context, self.selector)
        elif self.by_role:
            return self.get_by_role(context, self.by_role)
        elif self.by_label:
            return self.get_by_label(context, self.by_label)
        elif self.by_placeholder:
            return self.get_by_placeholder(context, self.by_placeholder)
        else:
            raise ValueError("必须提供至少一种元素定位方式")

    def execute(self, context: CONTEXT) -> Any:
        """执行清空操作"""
        try:
            # 获取定位器
            locator = self._get_locator(context)
            
            self.logger.info("清空输入框")
            
            # 执行清空
            locator.clear(timeout=self.timeout * 1000 if self.timeout else None)
            
            # 更新上下文
            context['last_locator'] = locator
            context['last_input_text'] = ""
            
            self.logger.info("清空完成")
            
            return True
            
        except Exception as e:
            self.logger.error(f"清空输入失败: {e}")
            raise