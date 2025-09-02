#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
关闭浏览器节点
"""
from typing import Optional, Any

from rpaworkflow.playwright.nodes.base import PlaywrightBaseNode
from rpaworkflow.playwright.workflow_context import CONTEXT


class CloseBrowserNode(PlaywrightBaseNode):
    """关闭浏览器节点

    用于关闭浏览器实例
    """

    def __init__(self,
                 name: str = "关闭浏览器",
                 description: str = "关闭浏览器实例",
                 close_type: str = "all",  # all, page, context, browser
                 **kwargs):
        super().__init__(name, description, **kwargs)
        self.close_type = close_type.lower()

    def execute(self, context: CONTEXT) -> Any:
        """执行关闭浏览器操作"""
        try:
            if self.close_type == "page":
                # 只关闭当前页面
                page = context.get('page')
                if page and not page.is_closed():
                    self.logger.info("关闭当前页面")
                    page.close()
                    context['page'] = None
                    result = "页面已关闭"
                else:
                    result = "页面已经关闭或不存在"
                    
            elif self.close_type == "context":
                # 关闭浏览器上下文
                browser_context = context.get('browser_context')
                if browser_context:
                    self.logger.info("关闭浏览器上下文")
                    browser_context.close()
                    context['browser_context'] = None
                    context['page'] = None
                    result = "浏览器上下文已关闭"
                else:
                    result = "浏览器上下文已经关闭或不存在"
                    
            elif self.close_type == "browser":
                # 关闭浏览器实例
                browser = context.get('browser')
                if browser:
                    self.logger.info("关闭浏览器实例")
                    browser.close()
                    context['browser'] = None
                    context['browser_context'] = None
                    context['page'] = None
                    result = "浏览器实例已关闭"
                else:
                    result = "浏览器实例已经关闭或不存在"
                    
            elif self.close_type == "all":
                # 关闭所有（默认行为）
                self.logger.info("关闭所有浏览器资源")
                
                # 关闭页面
                page = context.get('page')
                if page and not page.is_closed():
                    page.close()
                    context['page'] = None
                
                # 关闭浏览器上下文
                browser_context = context.get('browser_context')
                if browser_context:
                    browser_context.close()
                    context['browser_context'] = None
                
                # 关闭浏览器实例
                browser = context.get('browser')
                if browser:
                    browser.close()
                    context['browser'] = None
                
                # 关闭Playwright实例
                playwright = context.get('playwright')
                if playwright:
                    playwright.stop()
                    context['playwright'] = None
                
                result = "所有浏览器资源已关闭"
                
            else:
                raise ValueError(f"不支持的关闭类型: {self.close_type}")
            
            # 清理相关上下文信息
            if self.close_type in ["page", "context", "browser", "all"]:
                context['current_url'] = None
                context['page_title'] = None
                context['last_locator'] = None
                context['last_element_handle'] = None
                context['last_text'] = None
                context['last_screenshot_path'] = None
            
            self.logger.info(result)
            
            return result
            
        except Exception as e:
            self.logger.error(f"关闭浏览器失败: {e}")
            raise


class ClosePageNode(PlaywrightBaseNode):
    """关闭页面节点

    用于关闭指定页面或当前页面
    """

    def __init__(self,
                 name: str = "关闭页面",
                 description: str = "关闭指定页面或当前页面",
                 page_index: Optional[int] = None,  # None表示当前页面
                 **kwargs):
        super().__init__(name, description, **kwargs)
        self.page_index = page_index

    def execute(self, context: CONTEXT) -> Any:
        """执行关闭页面操作"""
        try:
            if self.page_index is None:
                # 关闭当前页面
                page = context.get('page')
                if page and not page.is_closed():
                    self.logger.info("关闭当前页面")
                    page.close()
                    context['page'] = None
                    result = "当前页面已关闭"
                else:
                    result = "当前页面已经关闭或不存在"
            else:
                # 关闭指定索引的页面
                browser_context = context.get('browser_context')
                if browser_context:
                    pages = browser_context.pages
                    if 0 <= self.page_index < len(pages):
                        target_page = pages[self.page_index]
                        self.logger.info(f"关闭页面索引 {self.page_index}")
                        target_page.close()
                        
                        # 如果关闭的是当前页面，更新上下文
                        if context.get('page') == target_page:
                            context['page'] = None
                        
                        result = f"页面索引 {self.page_index} 已关闭"
                    else:
                        result = f"页面索引 {self.page_index} 不存在"
                else:
                    result = "浏览器上下文不存在"
            
            self.logger.info(result)
            
            return result
            
        except Exception as e:
            self.logger.error(f"关闭页面失败: {e}")
            raise


class SwitchToPageNode(PlaywrightBaseNode):
    """切换页面节点

    用于在多个页面之间切换
    """

    def __init__(self,
                 name: str = "切换页面",
                 description: str = "在多个页面之间切换",
                 page_index: Optional[int] = None,
                 page_url: Optional[str] = None,
                 page_title: Optional[str] = None,
                 **kwargs):
        super().__init__(name, description, **kwargs)
        self.page_index = page_index
        self.page_url = page_url
        self.page_title = page_title

    def execute(self, context: CONTEXT) -> Any:
        """执行切换页面操作"""
        browser_context = self.get_browser_context(context)
        
        try:
            pages = browser_context.pages
            target_page = None
            
            if self.page_index is not None:
                # 按索引切换
                if 0 <= self.page_index < len(pages):
                    target_page = pages[self.page_index]
                    self.logger.info(f"切换到页面索引 {self.page_index}")
                else:
                    raise ValueError(f"页面索引 {self.page_index} 不存在")
                    
            elif self.page_url:
                # 按URL切换
                for page in pages:
                    if self.page_url in page.url:
                        target_page = page
                        self.logger.info(f"切换到URL包含 '{self.page_url}' 的页面")
                        break
                if not target_page:
                    raise ValueError(f"未找到URL包含 '{self.page_url}' 的页面")
                    
            elif self.page_title:
                # 按标题切换
                for page in pages:
                    if self.page_title in page.title():
                        target_page = page
                        self.logger.info(f"切换到标题包含 '{self.page_title}' 的页面")
                        break
                if not target_page:
                    raise ValueError(f"未找到标题包含 '{self.page_title}' 的页面")
                    
            else:
                raise ValueError("必须提供page_index、page_url或page_title中的一个")
            
            # 切换到目标页面
            target_page.bring_to_front()
            
            # 更新上下文
            context['page'] = target_page
            context['current_url'] = target_page.url
            context['page_title'] = target_page.title()
            
            result = {
                "url": target_page.url,
                "title": target_page.title(),
                "index": pages.index(target_page)
            }
            
            self.logger.info(f"已切换到页面: {result['title']} - {result['url']}")
            
            return result
            
        except Exception as e:
            self.logger.error(f"切换页面失败: {e}")
            raise


class NewPageNode(PlaywrightBaseNode):
    """新建页面节点

    用于在当前浏览器上下文中创建新页面
    """

    def __init__(self,
                 name: str = "新建页面",
                 description: str = "在当前浏览器上下文中创建新页面",
                 url: Optional[str] = None,
                 switch_to_new: bool = True,
                 **kwargs):
        super().__init__(name, description, **kwargs)
        self.url = url
        self.switch_to_new = switch_to_new

    def execute(self, context: CONTEXT) -> Any:
        """执行新建页面操作"""
        browser_context = self.get_browser_context(context)
        
        try:
            # 创建新页面
            self.logger.info("创建新页面")
            new_page = browser_context.new_page()
            
            # 如果提供了URL，导航到该URL
            if self.url:
                self.logger.info(f"导航到: {self.url}")
                new_page.goto(self.url)
            
            # 如果需要切换到新页面
            if self.switch_to_new:
                context['page'] = new_page
                context['current_url'] = new_page.url
                context['page_title'] = new_page.title()
                self.logger.info("已切换到新页面")
            
            result = {
                "url": new_page.url,
                "title": new_page.title(),
                "switched": self.switch_to_new
            }
            
            self.logger.info(f"新页面创建完成: {result['title']} - {result['url']}")
            
            return result
            
        except Exception as e:
            self.logger.error(f"新建页面失败: {e}")
            raise


class GetPagesInfoNode(PlaywrightBaseNode):
    """获取页面信息节点

    用于获取所有打开页面的信息
    """

    def __init__(self,
                 name: str = "获取页面信息",
                 description: str = "获取所有打开页面的信息",
                 **kwargs):
        super().__init__(name, description, **kwargs)

    def execute(self, context: CONTEXT) -> Any:
        """执行获取页面信息操作"""
        browser_context = self.get_browser_context(context)
        
        try:
            pages = browser_context.pages
            current_page = context.get('page')
            
            pages_info = []
            for i, page in enumerate(pages):
                page_info = {
                    "index": i,
                    "url": page.url,
                    "title": page.title(),
                    "is_current": page == current_page,
                    "is_closed": page.is_closed()
                }
                pages_info.append(page_info)
            
            self.logger.info(f"获取到 {len(pages_info)} 个页面信息")
            
            # 更新上下文
            context['pages_info'] = pages_info
            
            return pages_info
            
        except Exception as e:
            self.logger.error(f"获取页面信息失败: {e}")
            raise