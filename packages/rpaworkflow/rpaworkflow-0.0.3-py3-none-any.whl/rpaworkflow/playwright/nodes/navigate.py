#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
导航节点
"""
from typing import Optional, Any

from rpaworkflow.node import DataStorageNode
from rpaworkflow.playwright.nodes.base import PlaywrightBaseNode
from rpaworkflow.playwright.workflow_context import CONTEXT


class NavigateNode(PlaywrightBaseNode, DataStorageNode):
    """导航节点

    用于页面导航操作，如访问URL、前进、后退、刷新等
    """

    def __init__(self,
                 name: str = "页面导航",
                 description: str = "导航到指定页面",
                 url: Optional[str] = None,
                 action: str = "goto",  # goto, back, forward, reload
                 wait_until: str = "load",  # load, domcontentloaded, networkidle
                 timeout: Optional[float] = None,
                 referer: Optional[str] = None,
                 wait_time: Optional[float] = None,
                 **kwargs):
        super().__init__(name, description, output_key='current_url', **kwargs)
        self.url = url
        self.action = action.lower()
        self.wait_until = wait_until
        self.timeout = timeout
        self.referer = referer
        self.wait_time = wait_time

    def execute(self, context: CONTEXT) -> Any:
        """执行导航操作"""
        page = self.get_page(context)
        
        try:
            if self.action == "goto":
                if not self.url:
                    raise ValueError("导航到页面需要提供URL")
                
                # 准备导航选项
                options = {
                    "wait_until": self.wait_until,
                }
                
                if self.timeout:
                    options["timeout"] = self.timeout * 1000  # 转换为毫秒
                    
                if self.referer:
                    options["referer"] = self.referer
                
                self.logger.info(f"导航到: {self.url}")
                response = page.goto(self.url, **options)
                
                # 更新上下文
                context['current_url'] = page.url
                context['page_title'] = page.title()
                
                # 如果有响应，记录状态
                if response:
                    self.logger.info(f"响应状态: {response.status}")
                    if response.status >= 400:
                        self.logger.warning(f"页面响应状态异常: {response.status}")
                
            elif self.action == "back":
                self.logger.info("页面后退")
                page.go_back(wait_until=self.wait_until, timeout=self.timeout * 1000 if self.timeout else None)
                context['current_url'] = page.url
                context['page_title'] = page.title()
                
            elif self.action == "forward":
                self.logger.info("页面前进")
                page.go_forward(wait_until=self.wait_until, timeout=self.timeout * 1000 if self.timeout else None)
                context['current_url'] = page.url
                context['page_title'] = page.title()
                
            elif self.action == "reload":
                self.logger.info("刷新页面")
                page.reload(wait_until=self.wait_until, timeout=self.timeout * 1000 if self.timeout else None)
                context['current_url'] = page.url
                context['page_title'] = page.title()
                
            else:
                raise ValueError(f"不支持的导航操作: {self.action}")
            
            # 等待额外时间
            if self.wait_time:
                self.logger.info(f"等待 {self.wait_time} 秒")
                page.wait_for_timeout(self.wait_time * 1000)
            
            # 更新页面加载状态
            context['page_load_state'] = self.wait_until
            
            current_url = page.url
            self.logger.info(f"当前页面: {current_url}")
            self.logger.info(f"页面标题: {page.title()}")
            
            return current_url
            
        except Exception as e:
            self.logger.error(f"导航操作失败: {e}")
            raise


class WaitForNavigationNode(PlaywrightBaseNode):
    """等待导航节点

    等待页面导航完成
    """

    def __init__(self,
                 name: str = "等待导航",
                 description: str = "等待页面导航完成",
                 url_pattern: Optional[str] = None,
                 wait_until: str = "load",
                 timeout: Optional[float] = None,
                 **kwargs):
        super().__init__(name, description, **kwargs)
        self.url_pattern = url_pattern
        self.wait_until = wait_until
        self.timeout = timeout

    def execute(self, context: CONTEXT) -> Any:
        """执行等待导航操作"""
        page = self.get_page(context)
        
        try:
            options = {
                "wait_until": self.wait_until,
            }
            
            if self.timeout:
                options["timeout"] = self.timeout * 1000
                
            if self.url_pattern:
                options["url"] = self.url_pattern
            
            self.logger.info(f"等待导航完成，状态: {self.wait_until}")
            if self.url_pattern:
                self.logger.info(f"URL模式: {self.url_pattern}")
            
            with page.expect_navigation(**options):
                pass  # 等待导航事件
            
            # 更新上下文
            context['current_url'] = page.url
            context['page_title'] = page.title()
            context['page_load_state'] = self.wait_until
            
            self.logger.info(f"导航完成，当前页面: {page.url}")
            
            return page.url
            
        except Exception as e:
            self.logger.error(f"等待导航失败: {e}")
            raise


class SetViewportNode(PlaywrightBaseNode):
    """设置视口节点

    设置页面视口大小
    """

    def __init__(self,
                 name: str = "设置视口",
                 description: str = "设置页面视口大小",
                 width: int = 1280,
                 height: int = 720,
                 **kwargs):
        super().__init__(name, description, **kwargs)
        self.width = width
        self.height = height

    def execute(self, context: CONTEXT) -> Any:
        """执行设置视口操作"""
        page = self.get_page(context)
        
        try:
            viewport = {"width": self.width, "height": self.height}
            
            self.logger.info(f"设置视口大小: {self.width}x{self.height}")
            page.set_viewport_size(**viewport)
            
            # 更新上下文
            context['viewport_size'] = viewport
            
            return viewport
            
        except Exception as e:
            self.logger.error(f"设置视口失败: {e}")
            raise