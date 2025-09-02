#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
点击节点
"""
from typing import Optional, Any, Dict, Union

from playwright.sync_api import Locator

from rpaworkflow.node import DataStorageNode
from rpaworkflow.playwright.nodes.base import PlaywrightBaseNode
from rpaworkflow.playwright.workflow_context import CONTEXT


class ClickNode(PlaywrightBaseNode, DataStorageNode):
    """点击节点

    用于点击页面元素
    """

    def __init__(self,
                 name: str = "点击元素",
                 description: str = "点击指定元素",
                 selector: Optional[str] = None,
                 # 定位方式
                 by_role: Optional[str] = None,
                 by_text: Optional[str] = None,
                 by_label: Optional[str] = None,
                 by_placeholder: Optional[str] = None,
                 by_alt_text: Optional[str] = None,
                 by_title: Optional[str] = None,
                 by_test_id: Optional[str] = None,
                 # 点击选项
                 button: str = "left",  # left, right, middle
                 click_count: int = 1,
                 delay: Optional[float] = None,
                 position: Optional[Dict[str, float]] = None,
                 modifiers: Optional[list] = None,
                 force: bool = False,
                 no_wait_after: bool = False,
                 timeout: Optional[float] = None,
                 trial: bool = False,
                 # 等待选项
                 wait_for_selector: bool = True,
                 wait_timeout: Optional[float] = None,
                 **kwargs):
        super().__init__(name, description, output_key='last_click_position', **kwargs)
        self.selector = selector
        self.by_role = by_role
        self.by_text = by_text
        self.by_label = by_label
        self.by_placeholder = by_placeholder
        self.by_alt_text = by_alt_text
        self.by_title = by_title
        self.by_test_id = by_test_id
        
        self.button = button
        self.click_count = click_count
        self.delay = delay
        self.position = position
        self.modifiers = modifiers or []
        self.force = force
        self.no_wait_after = no_wait_after
        self.timeout = timeout
        self.trial = trial
        
        self.wait_for_selector = wait_for_selector
        self.wait_timeout = wait_timeout

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
        elif self.by_placeholder:
            return self.get_by_placeholder(context, self.by_placeholder)
        elif self.by_alt_text:
            return self.get_by_alt_text(context, self.by_alt_text)
        elif self.by_title:
            return self.get_by_title(context, self.by_title)
        elif self.by_test_id:
            return self.get_by_test_id(context, self.by_test_id)
        else:
            raise ValueError("必须提供至少一种元素定位方式")

    def execute(self, context: CONTEXT) -> Any:
        """执行点击操作"""
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
            
            # 准备点击选项
            click_options = {
                "button": self.button,
                "click_count": self.click_count,
                "force": self.force,
                "no_wait_after": self.no_wait_after,
                "trial": self.trial,
            }
            
            if self.delay:
                click_options["delay"] = self.delay * 1000  # 转换为毫秒
                
            if self.position:
                click_options["position"] = self.position
                
            if self.modifiers:
                click_options["modifiers"] = self.modifiers
                
            if self.timeout:
                click_options["timeout"] = self.timeout * 1000
            
            # 记录点击信息
            element_info = self._get_element_info(locator)
            self.logger.info(f"点击元素: {element_info}")
            if self.position:
                self.logger.info(f"点击位置: {self.position}")
            
            # 执行点击
            locator.click(**click_options)
            
            # 获取点击位置
            if self.position:
                click_position = self.position
            else:
                # 获取元素中心位置
                bounding_box = locator.bounding_box()
                if bounding_box:
                    click_position = {
                        "x": bounding_box["x"] + bounding_box["width"] / 2,
                        "y": bounding_box["y"] + bounding_box["height"] / 2
                    }
                else:
                    click_position = {"x": 0, "y": 0}
            
            # 更新上下文
            context['last_locator'] = locator
            context['last_click_position'] = click_position
            
            self.logger.info(f"点击完成，位置: {click_position}")
            
            return click_position
            
        except Exception as e:
            self.logger.error(f"点击操作失败: {e}")
            raise

    def _get_element_info(self, locator: Locator) -> str:
        """获取元素信息用于日志"""
        try:
            if self.selector:
                return f"选择器: {self.selector}"
            elif self.by_role:
                return f"角色: {self.by_role}"
            elif self.by_text:
                return f"文本: {self.by_text}"
            elif self.by_label:
                return f"标签: {self.by_label}"
            elif self.by_placeholder:
                return f"占位符: {self.by_placeholder}"
            elif self.by_alt_text:
                return f"替代文本: {self.by_alt_text}"
            elif self.by_title:
                return f"标题: {self.by_title}"
            elif self.by_test_id:
                return f"测试ID: {self.by_test_id}"
            else:
                return "未知元素"
        except:
            return "元素信息获取失败"


class DoubleClickNode(ClickNode):
    """双击节点

    用于双击页面元素
    """

    def __init__(self,
                 name: str = "双击元素",
                 description: str = "双击指定元素",
                 **kwargs):
        # 移除click_count参数，因为dblclick不需要
        kwargs.pop('click_count', None)
        super().__init__(name, description, **kwargs)

    def execute(self, context: CONTEXT) -> Any:
        """执行双击操作"""
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
            
            # 准备双击选项
            dblclick_options = {
                "button": self.button,
                "force": self.force,
                "no_wait_after": self.no_wait_after,
            }
            
            if self.delay:
                dblclick_options["delay"] = self.delay * 1000
                
            if self.position:
                dblclick_options["position"] = self.position
                
            if self.modifiers:
                dblclick_options["modifiers"] = self.modifiers
                
            if self.timeout:
                dblclick_options["timeout"] = self.timeout * 1000
            
            # 记录双击信息
            element_info = self._get_element_info(locator)
            self.logger.info(f"双击元素: {element_info}")
            
            # 执行双击
            locator.dblclick(**dblclick_options)
            
            # 获取点击位置
            if self.position:
                click_position = self.position
            else:
                bounding_box = locator.bounding_box()
                if bounding_box:
                    click_position = {
                        "x": bounding_box["x"] + bounding_box["width"] / 2,
                        "y": bounding_box["y"] + bounding_box["height"] / 2
                    }
                else:
                    click_position = {"x": 0, "y": 0}
            
            # 更新上下文
            context['last_locator'] = locator
            context['last_click_position'] = click_position
            
            self.logger.info(f"双击完成，位置: {click_position}")
            
            return click_position
            
        except Exception as e:
            self.logger.error(f"双击操作失败: {e}")
            raise


class RightClickNode(ClickNode):
    """右键点击节点

    用于右键点击页面元素
    """

    def __init__(self,
                 name: str = "右键点击元素",
                 description: str = "右键点击指定元素",
                 **kwargs):
        kwargs['button'] = 'right'
        super().__init__(name, description, **kwargs)


class HoverNode(PlaywrightBaseNode):
    """悬停节点

    用于鼠标悬停在页面元素上
    """

    def __init__(self,
                 name: str = "悬停元素",
                 description: str = "鼠标悬停在指定元素上",
                 selector: Optional[str] = None,
                 by_role: Optional[str] = None,
                 by_text: Optional[str] = None,
                 by_label: Optional[str] = None,
                 position: Optional[Dict[str, float]] = None,
                 modifiers: Optional[list] = None,
                 force: bool = False,
                 no_wait_after: bool = False,
                 timeout: Optional[float] = None,
                 trial: bool = False,
                 **kwargs):
        super().__init__(name, description, **kwargs)
        self.selector = selector
        self.by_role = by_role
        self.by_text = by_text
        self.by_label = by_label
        self.position = position
        self.modifiers = modifiers or []
        self.force = force
        self.no_wait_after = no_wait_after
        self.timeout = timeout
        self.trial = trial

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
        """执行悬停操作"""
        try:
            # 获取定位器
            locator = self._get_locator(context)
            
            # 准备悬停选项
            hover_options = {
                "force": self.force,
                "no_wait_after": self.no_wait_after,
                "trial": self.trial,
            }
            
            if self.position:
                hover_options["position"] = self.position
                
            if self.modifiers:
                hover_options["modifiers"] = self.modifiers
                
            if self.timeout:
                hover_options["timeout"] = self.timeout * 1000
            
            self.logger.info(f"悬停元素: {self.selector or self.by_role or self.by_text}")
            
            # 执行悬停
            locator.hover(**hover_options)
            
            # 更新上下文
            context['last_locator'] = locator
            
            self.logger.info("悬停完成")
            
            return True
            
        except Exception as e:
            self.logger.error(f"悬停操作失败: {e}")
            raise