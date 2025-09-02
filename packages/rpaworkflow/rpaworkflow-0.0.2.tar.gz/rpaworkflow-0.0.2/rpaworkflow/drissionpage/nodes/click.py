#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DrissionPage 元素点击节点

提供各种点击操作功能。
"""

from typing import Dict, Any, Union

from DrissionPage import SessionPage
from DrissionPage._elements.chromium_element import ChromiumElement
from DrissionPage._elements.session_element import SessionElement

from .base import DrissionPageBaseNode
from ..workflow_context import CONTEXT


class ClickNode(DrissionPageBaseNode):
    """元素点击节点
    
    点击指定的页面元素。
    """
    
    def __init__(self, 
                 locator: str = None,
                 by_css: str = None,
                 by_xpath: str = None,
                 by_text: str = None,
                 by_tag: str = None,
                 by_attr: tuple = None,
                 index: int = 1,
                 click_type: str = "left",
                 times: int = 1,
                 interval: float = 0.1,
                 timeout: float = 10.0,
                 wait_after: float = 0.5,
                 scroll_to_element: bool = True,
                 **kwargs):
        """
        初始化点击节点
        
        Args:
            locator: 通用定位器
            by_css: CSS选择器
            by_xpath: XPath表达式
            by_text: 文本内容
            by_tag: 标签名
            by_attr: 属性元组
            index: 元素索引
            click_type: 点击类型 ('left', 'right', 'middle', 'double')
            times: 点击次数
            interval: 点击间隔
            timeout: 查找元素超时时间
            wait_after: 点击后等待时间
            scroll_to_element: 是否滚动到元素
        """
        super().__init__(
            name="元素点击",
            description=f"点击元素 {locator or by_css or by_xpath or by_text or by_tag or by_attr}",
            **kwargs
        )
        
        self.locator = locator
        self.by_css = by_css
        self.by_xpath = by_xpath
        self.by_text = by_text
        self.by_tag = by_tag
        self.by_attr = by_attr
        self.index = index
        self.click_type = click_type
        self.times = times
        self.interval = interval
        self.timeout = timeout
        self.wait_after = wait_after
        self.scroll_to_element = scroll_to_element
        
        self.node_type = "drissionpage_click"
    
    def execute(self, context: CONTEXT) -> Dict[str, Any]:
        """执行点击操作
        
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
            
            # 滚动到元素（如果需要且支持）
            if self.scroll_to_element and isinstance(element, ChromiumElement):
                element.scroll.to_see()
            
            # 执行点击操作
            for i in range(self.times):
                if self.click_type == "left":
                    element.click()
                elif self.click_type == "right":
                    if isinstance(element, ChromiumElement):
                        element.r_click()
                    else:
                        raise ValueError("SessionElement 不支持右键点击")
                elif self.click_type == "middle":
                    if isinstance(element, ChromiumElement):
                        element.m_click()
                    else:
                        raise ValueError("SessionElement 不支持中键点击")
                elif self.click_type == "double":
                    if isinstance(element, ChromiumElement):
                        element.d_click()
                    else:
                        # SessionElement 模拟双击
                        element.click()
                        import time
                        time.sleep(0.1)
                        element.click()
                else:
                    raise ValueError(f"不支持的点击类型: {self.click_type}")
                
                # 点击间隔
                if i < self.times - 1 and self.interval > 0:
                    import time
                    time.sleep(self.interval)
            
            # 点击后等待
            if self.wait_after > 0:
                import time
                time.sleep(self.wait_after)
            
            # 更新上下文
            context['last_clicked_element'] = element
            context['click_type'] = self.click_type
            context['click_times'] = self.times
            
            # 获取元素信息
            element_info = self._get_element_info(element)
            
            return {
                'success': True,
                'click_type': self.click_type,
                'times': self.times,
                'element_info': element_info,
                'message': f"成功{self.click_type}点击元素 {self.times} 次"
            }
            
        except Exception as e:
            error_msg = self._handle_error(context, e)
            return {
                'success': False,
                'error': error_msg,
                'click_type': self.click_type,
                'times': self.times,
                'message': f"点击元素失败: {error_msg}"
            }
    
    def _get_element_info(self, element: Union[ChromiumElement, SessionElement]) -> dict:
        """获取元素信息"""
        try:
            info = {
                'tag': element.tag,
                'text': element.text,
            }
            
            # 获取常用属性
            for attr in ['id', 'class', 'name', 'href', 'src', 'value']:
                try:
                    value = element.attr(attr)
                    if value:
                        info[attr] = value
                except:
                    pass
            
            # ChromiumElement 特有信息
            if isinstance(element, ChromiumElement):
                try:
                    info['rect'] = element.rect
                    info['is_displayed'] = element.is_displayed
                    info['is_enabled'] = element.is_enabled
                except:
                    pass
            
            return info
        except:
            return {'tag': 'unknown', 'text': ''}


class ClickByCoordinateNode(DrissionPageBaseNode):
    """坐标点击节点
    
    在指定坐标位置点击。
    """
    
    def __init__(self, 
                 x: int,
                 y: int,
                 click_type: str = "left",
                 times: int = 1,
                 interval: float = 0.1,
                 wait_after: float = 0.5,
                 **kwargs):
        """
        初始化坐标点击节点
        
        Args:
            x: X坐标
            y: Y坐标
            click_type: 点击类型
            times: 点击次数
            interval: 点击间隔
            wait_after: 点击后等待时间
        """
        super().__init__(
            name="坐标点击",
            description=f"在坐标 ({x}, {y}) 点击",
            **kwargs
        )
        
        self.x = x
        self.y = y
        self.click_type = click_type
        self.times = times
        self.interval = interval
        self.wait_after = wait_after
        
        self.node_type = "drissionpage_click_coordinate"
    
    def execute(self, context: CONTEXT) -> Dict[str, Any]:
        """执行坐标点击
        
        Args:
            context: 工作流上下文
            
        Returns:
            执行结果
        """
        try:
            page = self._get_page(context)
            
            # 只有 ChromiumPage 和 WebPage 支持坐标点击
            if isinstance(page, SessionPage):
                raise ValueError("SessionPage 不支持坐标点击")
            
            # 执行坐标点击
            for i in range(self.times):
                if self.click_type == "left":
                    page.click(self.x, self.y)
                elif self.click_type == "right":
                    page.r_click(self.x, self.y)
                elif self.click_type == "middle":
                    page.m_click(self.x, self.y)
                elif self.click_type == "double":
                    page.d_click(self.x, self.y)
                else:
                    raise ValueError(f"不支持的点击类型: {self.click_type}")
                
                # 点击间隔
                if i < self.times - 1 and self.interval > 0:
                    import time
                    time.sleep(self.interval)
            
            # 点击后等待
            if self.wait_after > 0:
                import time
                time.sleep(self.wait_after)
            
            # 更新上下文
            context['last_click_position'] = (self.x, self.y)
            context['click_type'] = self.click_type
            context['click_times'] = self.times
            
            return {
                'success': True,
                'position': (self.x, self.y),
                'click_type': self.click_type,
                'times': self.times,
                'message': f"成功在坐标 ({self.x}, {self.y}) {self.click_type}点击 {self.times} 次"
            }
            
        except Exception as e:
            error_msg = self._handle_error(context, e)
            return {
                'success': False,
                'error': error_msg,
                'position': (self.x, self.y),
                'click_type': self.click_type,
                'message': f"坐标点击失败: {error_msg}"
            }


class HoverNode(DrissionPageBaseNode):
    """鼠标悬停节点
    
    在指定元素上悬停鼠标。
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
        初始化鼠标悬停节点
        
        Args:
            locator: 通用定位器
            by_css: CSS选择器
            by_xpath: XPath表达式
            by_text: 文本内容
            by_tag: 标签名
            by_attr: 属性元组
            index: 元素索引
            timeout: 查找元素超时时间
            wait_after: 悬停后等待时间
        """
        super().__init__(
            name="鼠标悬停",
            description=f"在元素上悬停 {locator or by_css or by_xpath or by_text or by_tag or by_attr}",
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
        
        self.node_type = "drissionpage_hover"
    
    def execute(self, context: CONTEXT) -> Dict[str, Any]:
        """执行鼠标悬停
        
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
            
            # 执行悬停操作
            if isinstance(element, ChromiumElement):
                element.hover()
            else:
                raise ValueError("SessionElement 不支持鼠标悬停操作")
            
            # 悬停后等待
            if self.wait_after > 0:
                import time
                time.sleep(self.wait_after)
            
            # 更新上下文
            context['last_hovered_element'] = element
            
            # 获取元素信息
            element_info = self._get_element_info(element)
            
            return {
                'success': True,
                'element_info': element_info,
                'message': "成功执行鼠标悬停操作"
            }
            
        except Exception as e:
            error_msg = self._handle_error(context, e)
            return {
                'success': False,
                'error': error_msg,
                'message': f"鼠标悬停失败: {error_msg}"
            }
    
    def _get_element_info(self, element: ChromiumElement) -> dict:
        """获取元素信息"""
        try:
            info = {
                'tag': element.tag,
                'text': element.text,
            }
            
            # 获取常用属性
            for attr in ['id', 'class', 'name', 'href', 'src', 'value']:
                try:
                    value = element.attr(attr)
                    if value:
                        info[attr] = value
                except:
                    pass
            
            # 获取位置信息
            try:
                info['rect'] = element.rect
            except:
                pass
            
            return info
        except:
            return {'tag': 'unknown', 'text': ''}


class DragAndDropNode(DrissionPageBaseNode):
    """拖拽节点
    
    拖拽元素到指定位置。
    """
    
    def __init__(self, 
                 source_locator: str = None,
                 source_by_css: str = None,
                 source_by_xpath: str = None,
                 source_by_text: str = None,
                 target_locator: str = None,
                 target_by_css: str = None,
                 target_by_xpath: str = None,
                 target_by_text: str = None,
                 target_x: int = None,
                 target_y: int = None,
                 timeout: float = 10.0,
                 wait_after: float = 1.0,
                 **kwargs):
        """
        初始化拖拽节点
        
        Args:
            source_locator: 源元素定位器
            source_by_css: 源元素CSS选择器
            source_by_xpath: 源元素XPath
            source_by_text: 源元素文本
            target_locator: 目标元素定位器
            target_by_css: 目标元素CSS选择器
            target_by_xpath: 目标元素XPath
            target_by_text: 目标元素文本
            target_x: 目标X坐标
            target_y: 目标Y坐标
            timeout: 超时时间
            wait_after: 拖拽后等待时间
        """
        super().__init__(
            name="拖拽操作",
            description="拖拽元素到指定位置",
            **kwargs
        )
        
        self.source_locator = source_locator
        self.source_by_css = source_by_css
        self.source_by_xpath = source_by_xpath
        self.source_by_text = source_by_text
        self.target_locator = target_locator
        self.target_by_css = target_by_css
        self.target_by_xpath = target_by_xpath
        self.target_by_text = target_by_text
        self.target_x = target_x
        self.target_y = target_y
        self.timeout = timeout
        self.wait_after = wait_after
        
        self.node_type = "drissionpage_drag_drop"
    
    def execute(self, context: CONTEXT) -> Dict[str, Any]:
        """执行拖拽操作
        
        Args:
            context: 工作流上下文
            
        Returns:
            执行结果
        """
        try:
            # 查找源元素
            source_element = self._find_element(
                context=context,
                locator=self.source_locator,
                by_css=self.source_by_css,
                by_xpath=self.source_by_xpath,
                by_text=self.source_by_text,
                timeout=self.timeout
            )
            
            # 只有 ChromiumElement 支持拖拽
            if not isinstance(source_element, ChromiumElement):
                raise ValueError("SessionElement 不支持拖拽操作")
            
            # 执行拖拽
            if self.target_x is not None and self.target_y is not None:
                # 拖拽到坐标
                source_element.drag_to((self.target_x, self.target_y))
                target_info = f"坐标 ({self.target_x}, {self.target_y})"
            else:
                # 拖拽到目标元素
                target_element = self._find_element(
                    context=context,
                    locator=self.target_locator,
                    by_css=self.target_by_css,
                    by_xpath=self.target_by_xpath,
                    by_text=self.target_by_text,
                    timeout=self.timeout
                )
                
                if not isinstance(target_element, ChromiumElement):
                    raise ValueError("目标元素必须是 ChromiumElement")
                
                source_element.drag_to(target_element)
                target_info = f"目标元素 {target_element.tag}"
            
            # 拖拽后等待
            if self.wait_after > 0:
                import time
                time.sleep(self.wait_after)
            
            # 更新上下文
            context['last_drag_source'] = source_element
            if self.target_x is None or self.target_y is None:
                context['last_drag_target'] = target_element
            else:
                context['last_drag_target_position'] = (self.target_x, self.target_y)
            
            return {
                'success': True,
                'source_info': self._get_element_info(source_element),
                'target_info': target_info,
                'message': f"成功拖拽元素到 {target_info}"
            }
            
        except Exception as e:
            error_msg = self._handle_error(context, e)
            return {
                'success': False,
                'error': error_msg,
                'message': f"拖拽操作失败: {error_msg}"
            }
    
    def _get_element_info(self, element: ChromiumElement) -> dict:
        """获取元素信息"""
        try:
            return {
                'tag': element.tag,
                'text': element.text,
                'rect': element.rect
            }
        except:
            return {'tag': 'unknown', 'text': ''}