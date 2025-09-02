#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
滚动节点
"""
from typing import Optional, Any, Dict

from rpaworkflow.playwright.nodes.base import PlaywrightBaseNode
from rpaworkflow.playwright.workflow_context import CONTEXT


class ScrollNode(PlaywrightBaseNode):
    """滚动节点

    用于页面或元素滚动操作
    """

    def __init__(self,
                 name: str = "滚动",
                 description: str = "页面或元素滚动操作",
                 selector: Optional[str] = None,
                 by_role: Optional[str] = None,
                 by_text: Optional[str] = None,
                 by_label: Optional[str] = None,
                 scroll_type: str = "wheel",  # wheel, to_position, into_view
                 delta_x: float = 0,
                 delta_y: float = 0,
                 x: Optional[float] = None,
                 y: Optional[float] = None,
                 **kwargs):
        super().__init__(name, description, **kwargs)
        self.selector = selector
        self.by_role = by_role
        self.by_text = by_text
        self.by_label = by_label
        self.scroll_type = scroll_type.lower()
        self.delta_x = delta_x
        self.delta_y = delta_y
        self.x = x
        self.y = y

    def execute(self, context: CONTEXT) -> Any:
        """执行滚动操作"""
        page = self.get_page(context)
        
        try:
            if self.scroll_type == "wheel":
                # 鼠标滚轮滚动
                if any([self.selector, self.by_role, self.by_text, self.by_label]):
                    # 元素滚动
                    if self.selector:
                        locator = self.locator(context, self.selector)
                    elif self.by_role:
                        locator = self.get_by_role(context, self.by_role)
                    elif self.by_text:
                        locator = self.get_by_text(context, self.by_text)
                    elif self.by_label:
                        locator = self.get_by_label(context, self.by_label)
                    
                    self.logger.info(f"元素滚动: delta_x={self.delta_x}, delta_y={self.delta_y}")
                    locator.hover()
                    page.mouse.wheel(self.delta_x, self.delta_y)
                    
                    # 更新上下文
                    context['last_locator'] = locator
                else:
                    # 页面滚动
                    self.logger.info(f"页面滚动: delta_x={self.delta_x}, delta_y={self.delta_y}")
                    page.mouse.wheel(self.delta_x, self.delta_y)
                
                result = {"delta_x": self.delta_x, "delta_y": self.delta_y}
                
            elif self.scroll_type == "to_position":
                # 滚动到指定位置
                if self.x is None or self.y is None:
                    raise ValueError("滚动到指定位置需要提供x和y坐标")
                
                self.logger.info(f"滚动到位置: x={self.x}, y={self.y}")
                page.evaluate(f"window.scrollTo({self.x}, {self.y})")
                
                result = {"x": self.x, "y": self.y}
                
            elif self.scroll_type == "into_view":
                # 滚动元素到视图中
                if not any([self.selector, self.by_role, self.by_text, self.by_label]):
                    raise ValueError("滚动到视图需要提供元素定位方式")
                
                if self.selector:
                    locator = self.locator(context, self.selector)
                elif self.by_role:
                    locator = self.get_by_role(context, self.by_role)
                elif self.by_text:
                    locator = self.get_by_text(context, self.by_text)
                elif self.by_label:
                    locator = self.get_by_label(context, self.by_label)
                
                self.logger.info("滚动元素到视图中")
                locator.scroll_into_view_if_needed()
                
                # 更新上下文
                context['last_locator'] = locator
                
                result = "scrolled_into_view"
                
            else:
                raise ValueError(f"不支持的滚动类型: {self.scroll_type}")
            
            self.logger.info(f"滚动操作完成: {self.scroll_type}")
            
            return result
            
        except Exception as e:
            self.logger.error(f"滚动操作失败: {e}")
            raise


class ScrollToTopNode(PlaywrightBaseNode):
    """滚动到顶部节点

    用于滚动到页面顶部
    """

    def __init__(self,
                 name: str = "滚动到顶部",
                 description: str = "滚动到页面顶部",
                 **kwargs):
        super().__init__(name, description, **kwargs)

    def execute(self, context: CONTEXT) -> Any:
        """执行滚动到顶部操作"""
        page = self.get_page(context)
        
        try:
            self.logger.info("滚动到页面顶部")
            page.evaluate("window.scrollTo(0, 0)")
            
            self.logger.info("滚动到顶部完成")
            
            return {"x": 0, "y": 0}
            
        except Exception as e:
            self.logger.error(f"滚动到顶部失败: {e}")
            raise


class ScrollToBottomNode(PlaywrightBaseNode):
    """滚动到底部节点

    用于滚动到页面底部
    """

    def __init__(self,
                 name: str = "滚动到底部",
                 description: str = "滚动到页面底部",
                 **kwargs):
        super().__init__(name, description, **kwargs)

    def execute(self, context: CONTEXT) -> Any:
        """执行滚动到底部操作"""
        page = self.get_page(context)
        
        try:
            self.logger.info("滚动到页面底部")
            page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            
            # 获取滚动位置
            scroll_position = page.evaluate("({x: window.pageXOffset, y: window.pageYOffset})")
            
            self.logger.info(f"滚动到底部完成: {scroll_position}")
            
            return scroll_position
            
        except Exception as e:
            self.logger.error(f"滚动到底部失败: {e}")
            raise


class ScrollByNode(PlaywrightBaseNode):
    """相对滚动节点

    用于相对当前位置滚动
    """

    def __init__(self,
                 name: str = "相对滚动",
                 description: str = "相对当前位置滚动",
                 delta_x: float = 0,
                 delta_y: float = 0,
                 **kwargs):
        super().__init__(name, description, **kwargs)
        self.delta_x = delta_x
        self.delta_y = delta_y

    def execute(self, context: CONTEXT) -> Any:
        """执行相对滚动操作"""
        page = self.get_page(context)
        
        try:
            self.logger.info(f"相对滚动: delta_x={self.delta_x}, delta_y={self.delta_y}")
            
            # 获取当前滚动位置
            current_position = page.evaluate("({x: window.pageXOffset, y: window.pageYOffset})")
            
            # 计算新位置
            new_x = current_position["x"] + self.delta_x
            new_y = current_position["y"] + self.delta_y
            
            # 滚动到新位置
            page.evaluate(f"window.scrollTo({new_x}, {new_y})")
            
            # 获取实际滚动位置
            actual_position = page.evaluate("({x: window.pageXOffset, y: window.pageYOffset})")
            
            self.logger.info(f"相对滚动完成: {actual_position}")
            
            return actual_position
            
        except Exception as e:
            self.logger.error(f"相对滚动失败: {e}")
            raise


class GetScrollPositionNode(PlaywrightBaseNode):
    """获取滚动位置节点

    用于获取当前滚动位置
    """

    def __init__(self,
                 name: str = "获取滚动位置",
                 description: str = "获取当前滚动位置",
                 **kwargs):
        super().__init__(name, description, **kwargs)

    def execute(self, context: CONTEXT) -> Any:
        """执行获取滚动位置操作"""
        page = self.get_page(context)
        
        try:
            # 获取滚动位置和页面尺寸信息
            scroll_info = page.evaluate("""
                ({
                    x: window.pageXOffset,
                    y: window.pageYOffset,
                    scrollWidth: document.body.scrollWidth,
                    scrollHeight: document.body.scrollHeight,
                    clientWidth: document.documentElement.clientWidth,
                    clientHeight: document.documentElement.clientHeight
                })
            """)
            
            self.logger.info(f"当前滚动位置: x={scroll_info['x']}, y={scroll_info['y']}")
            
            # 更新上下文
            context['scroll_position'] = scroll_info
            
            return scroll_info
            
        except Exception as e:
            self.logger.error(f"获取滚动位置失败: {e}")
            raise


class ScrollIntoViewNode(PlaywrightBaseNode):
    """滚动到视图节点

    用于将指定元素滚动到视图中
    """

    def __init__(self,
                 name: str = "滚动到视图",
                 description: str = "将指定元素滚动到视图中",
                 selector: Optional[str] = None,
                 by_role: Optional[str] = None,
                 by_text: Optional[str] = None,
                 by_label: Optional[str] = None,
                 block: str = "start",  # start, center, end, nearest
                 inline: str = "nearest",  # start, center, end, nearest
                 **kwargs):
        super().__init__(name, description, **kwargs)
        self.selector = selector
        self.by_role = by_role
        self.by_text = by_text
        self.by_label = by_label
        self.block = block
        self.inline = inline

    def execute(self, context: CONTEXT) -> Any:
        """执行滚动到视图操作"""
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
            
            self.logger.info(f"滚动元素到视图中: block={self.block}, inline={self.inline}")
            
            # 使用JavaScript滚动到视图
            locator.evaluate(f"""
                element => element.scrollIntoView({{
                    block: '{self.block}',
                    inline: '{self.inline}',
                    behavior: 'smooth'
                }})
            """)
            
            # 更新上下文
            context['last_locator'] = locator
            
            self.logger.info("滚动到视图完成")
            
            return {"block": self.block, "inline": self.inline}
            
        except Exception as e:
            self.logger.error(f"滚动到视图失败: {e}")
            raise