#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DrissionPage 页面导航节点

提供页面导航、刷新、前进后退等功能。
"""

from typing import Dict, Any, Optional
from DrissionPage import ChromiumPage, SessionPage, WebPage

from .base import DrissionPageBaseNode
from ..workflow_context import CONTEXT


class NavigateNode(DrissionPageBaseNode):
    """页面导航节点
    
    导航到指定URL。
    """
    
    def __init__(self, 
                 url: str,
                 wait_complete: bool = True,
                 timeout: float = 30.0,
                 retry_times: int = 3,
                 retry_interval: float = 1.0,
                 **kwargs):
        """
        初始化页面导航节点
        
        Args:
            url: 目标URL
            wait_complete: 是否等待页面加载完成
            timeout: 超时时间
            retry_times: 重试次数
            retry_interval: 重试间隔
        """
        super().__init__(
            name="页面导航",
            description=f"导航到 {url}",
            **kwargs
        )
        
        self.url = url
        self.wait_complete = wait_complete
        self.timeout = timeout
        self.retry_times = retry_times
        self.retry_interval = retry_interval
        
        self.node_type = "drissionpage_navigate"
    
    def execute(self, context: CONTEXT) -> Dict[str, Any]:
        """执行页面导航
        
        Args:
            context: 工作流上下文
            
        Returns:
            执行结果
        """
        try:
            page = self._get_page(context)
            
            # 执行导航，支持重试
            last_error = None
            for attempt in range(self.retry_times + 1):
                try:
                    # 导航到URL
                    if isinstance(page, SessionPage):
                        # SessionPage 使用 get 方法
                        page.get(self.url, timeout=self.timeout)
                    else:
                        # ChromiumPage 和 WebPage 使用 get 方法
                        page.get(self.url, timeout=self.timeout)
                    
                    # 等待页面加载完成
                    if self.wait_complete and hasattr(page, 'wait'):
                        if isinstance(page, (ChromiumPage, WebPage)):
                            page.wait.load_start()
                    
                    break
                    
                except Exception as e:
                    last_error = e
                    if attempt < self.retry_times:
                        import time
                        time.sleep(self.retry_interval)
                        continue
                    else:
                        raise e
            
            # 更新上下文
            context['url'] = page.url
            context['title'] = page.title
            context['navigation_success'] = True
            
            # 获取页面信息
            page_info = self._get_page_info(context)
            
            return {
                'success': True,
                'url': page.url,
                'title': page.title,
                'page_info': page_info,
                'message': f"成功导航到: {page.url}"
            }
            
        except Exception as e:
            error_msg = self._handle_error(context, e)
            context['navigation_success'] = False
            return {
                'success': False,
                'error': error_msg,
                'target_url': self.url,
                'message': f"导航失败: {error_msg}"
            }


class RefreshNode(DrissionPageBaseNode):
    """页面刷新节点
    
    刷新当前页面。
    """
    
    def __init__(self, 
                 wait_complete: bool = True,
                 timeout: float = 30.0,
                 **kwargs):
        """
        初始化页面刷新节点
        
        Args:
            wait_complete: 是否等待页面加载完成
            timeout: 超时时间
        """
        super().__init__(
            name="页面刷新",
            description="刷新当前页面",
            **kwargs
        )
        
        self.wait_complete = wait_complete
        self.timeout = timeout
        
        self.node_type = "drissionpage_refresh"
    
    def execute(self, context: CONTEXT) -> Dict[str, Any]:
        """执行页面刷新
        
        Args:
            context: 工作流上下文
            
        Returns:
            执行结果
        """
        try:
            page = self._get_page(context)
            
            # 记录刷新前的URL
            old_url = page.url
            
            # 执行刷新
            if isinstance(page, SessionPage):
                # SessionPage 重新请求当前URL
                page.get(page.url, timeout=self.timeout)
            else:
                # ChromiumPage 和 WebPage 使用 refresh 方法
                page.refresh()
                
                # 等待页面加载完成
                if self.wait_complete and hasattr(page, 'wait'):
                    page.wait.load_start()
            
            # 更新上下文
            context['url'] = page.url
            context['title'] = page.title
            context['last_refresh_time'] = context.get('current_time', '')
            
            # 获取页面信息
            page_info = self._get_page_info(context)
            
            return {
                'success': True,
                'url': page.url,
                'title': page.title,
                'page_info': page_info,
                'message': f"成功刷新页面: {page.url}"
            }
            
        except Exception as e:
            error_msg = self._handle_error(context, e)
            return {
                'success': False,
                'error': error_msg,
                'message': f"页面刷新失败: {error_msg}"
            }


class BackNode(DrissionPageBaseNode):
    """页面后退节点
    
    后退到上一个页面。
    """
    
    def __init__(self, 
                 steps: int = 1,
                 wait_complete: bool = True,
                 **kwargs):
        """
        初始化页面后退节点
        
        Args:
            steps: 后退步数
            wait_complete: 是否等待页面加载完成
        """
        super().__init__(
            name="页面后退",
            description=f"后退 {steps} 步",
            **kwargs
        )
        
        self.steps = steps
        self.wait_complete = wait_complete
        
        self.node_type = "drissionpage_back"
    
    def execute(self, context: CONTEXT) -> Dict[str, Any]:
        """执行页面后退
        
        Args:
            context: 工作流上下文
            
        Returns:
            执行结果
        """
        try:
            page = self._get_page(context)
            
            # 只有 ChromiumPage 和 WebPage 支持后退
            if isinstance(page, SessionPage):
                raise ValueError("SessionPage 不支持页面后退操作")
            
            # 记录后退前的URL
            old_url = page.url
            
            # 执行后退
            for _ in range(self.steps):
                page.back()
                
                # 等待页面加载完成
                if self.wait_complete and hasattr(page, 'wait'):
                    page.wait.load_start()
            
            # 更新上下文
            context['url'] = page.url
            context['title'] = page.title
            context['navigation_history'] = context.get('navigation_history', []) + [old_url]
            
            # 获取页面信息
            page_info = self._get_page_info(context)
            
            return {
                'success': True,
                'old_url': old_url,
                'new_url': page.url,
                'steps': self.steps,
                'page_info': page_info,
                'message': f"成功后退 {self.steps} 步，从 {old_url} 到 {page.url}"
            }
            
        except Exception as e:
            error_msg = self._handle_error(context, e)
            return {
                'success': False,
                'error': error_msg,
                'steps': self.steps,
                'message': f"页面后退失败: {error_msg}"
            }


class ForwardNode(DrissionPageBaseNode):
    """页面前进节点
    
    前进到下一个页面。
    """
    
    def __init__(self, 
                 steps: int = 1,
                 wait_complete: bool = True,
                 **kwargs):
        """
        初始化页面前进节点
        
        Args:
            steps: 前进步数
            wait_complete: 是否等待页面加载完成
        """
        super().__init__(
            name="页面前进",
            description=f"前进 {steps} 步",
            **kwargs
        )
        
        self.steps = steps
        self.wait_complete = wait_complete
        
        self.node_type = "drissionpage_forward"
    
    def execute(self, context: CONTEXT) -> Dict[str, Any]:
        """执行页面前进
        
        Args:
            context: 工作流上下文
            
        Returns:
            执行结果
        """
        try:
            page = self._get_page(context)
            
            # 只有 ChromiumPage 和 WebPage 支持前进
            if isinstance(page, SessionPage):
                raise ValueError("SessionPage 不支持页面前进操作")
            
            # 记录前进前的URL
            old_url = page.url
            
            # 执行前进
            for _ in range(self.steps):
                page.forward()
                
                # 等待页面加载完成
                if self.wait_complete and hasattr(page, 'wait'):
                    page.wait.load_start()
            
            # 更新上下文
            context['url'] = page.url
            context['title'] = page.title
            
            # 获取页面信息
            page_info = self._get_page_info(context)
            
            return {
                'success': True,
                'old_url': old_url,
                'new_url': page.url,
                'steps': self.steps,
                'page_info': page_info,
                'message': f"成功前进 {self.steps} 步，从 {old_url} 到 {page.url}"
            }
            
        except Exception as e:
            error_msg = self._handle_error(context, e)
            return {
                'success': False,
                'error': error_msg,
                'steps': self.steps,
                'message': f"页面前进失败: {error_msg}"
            }


class NewTabNode(DrissionPageBaseNode):
    """新建标签页节点
    
    创建新的标签页并可选择导航到指定URL。
    """
    
    def __init__(self, 
                 url: str = None,
                 switch_to: bool = True,
                 wait_complete: bool = True,
                 **kwargs):
        """
        初始化新建标签页节点
        
        Args:
            url: 可选的导航URL
            switch_to: 是否切换到新标签页
            wait_complete: 是否等待页面加载完成
        """
        super().__init__(
            name="新建标签页",
            description=f"创建新标签页{f'并导航到 {url}' if url else ''}",
            **kwargs
        )
        
        self.url = url
        self.switch_to = switch_to
        self.wait_complete = wait_complete
        
        self.node_type = "drissionpage_new_tab"
    
    def execute(self, context: CONTEXT) -> Dict[str, Any]:
        """执行新建标签页
        
        Args:
            context: 工作流上下文
            
        Returns:
            执行结果
        """
        try:
            page = self._get_page(context)
            
            # 只有 ChromiumPage 和 WebPage 支持新建标签页
            if isinstance(page, SessionPage):
                raise ValueError("SessionPage 不支持新建标签页操作")
            
            # 记录当前标签页ID
            old_tab_id = page.tab_id
            
            # 创建新标签页
            if self.url:
                new_tab = page.new_tab(url=self.url)
            else:
                new_tab = page.new_tab()
            
            # 是否切换到新标签页
            if self.switch_to:
                page.to_tab(new_tab)
                
                # 等待页面加载完成
                if self.wait_complete and self.url and hasattr(page, 'wait'):
                    page.wait.load_start()
            
            # 更新上下文
            context['current_tab_id'] = page.tab_id if self.switch_to else old_tab_id
            context['new_tab_id'] = new_tab
            context['tab_count'] = len(page.tab_ids)
            
            if self.switch_to:
                context['url'] = page.url
                context['title'] = page.title
            
            # 获取页面信息
            page_info = self._get_page_info(context)
            
            return {
                'success': True,
                'old_tab_id': old_tab_id,
                'new_tab_id': new_tab,
                'switched': self.switch_to,
                'url': self.url,
                'page_info': page_info,
                'message': f"成功创建新标签页: {new_tab}{f'，并导航到 {self.url}' if self.url else ''}"
            }
            
        except Exception as e:
            error_msg = self._handle_error(context, e)
            return {
                'success': False,
                'error': error_msg,
                'url': self.url,
                'message': f"新建标签页失败: {error_msg}"
            }


class CloseTabNode(DrissionPageBaseNode):
    """关闭标签页节点
    
    关闭指定的标签页。
    """
    
    def __init__(self, 
                 tab_id: str = None,
                 close_current: bool = True,
                 **kwargs):
        """
        初始化关闭标签页节点
        
        Args:
            tab_id: 要关闭的标签页ID，为None时关闭当前标签页
            close_current: 是否关闭当前标签页（当tab_id为None时）
        """
        super().__init__(
            name="关闭标签页",
            description=f"关闭标签页 {tab_id or '(当前)'}",
            **kwargs
        )
        
        self.tab_id = tab_id
        self.close_current = close_current
        
        self.node_type = "drissionpage_close_tab"
    
    def execute(self, context: CONTEXT) -> Dict[str, Any]:
        """执行关闭标签页
        
        Args:
            context: 工作流上下文
            
        Returns:
            执行结果
        """
        try:
            page = self._get_page(context)
            
            # 只有 ChromiumPage 和 WebPage 支持关闭标签页
            if isinstance(page, SessionPage):
                raise ValueError("SessionPage 不支持关闭标签页操作")
            
            # 确定要关闭的标签页ID
            target_tab_id = self.tab_id or (page.tab_id if self.close_current else None)
            
            if not target_tab_id:
                raise ValueError("未指定要关闭的标签页")
            
            # 记录关闭前的信息
            old_tab_count = len(page.tab_ids)
            current_tab_id = page.tab_id
            
            # 关闭标签页
            page.close_tabs(target_tab_id)
            
            # 更新上下文
            context['tab_count'] = len(page.tab_ids)
            context['closed_tab_id'] = target_tab_id
            
            # 如果关闭的是当前标签页，需要切换到其他标签页
            if target_tab_id == current_tab_id and page.tab_ids:
                page.to_tab(page.tab_ids[0])
                context['current_tab_id'] = page.tab_ids[0]
                context['url'] = page.url
                context['title'] = page.title
            
            # 获取页面信息
            page_info = self._get_page_info(context)
            
            return {
                'success': True,
                'closed_tab_id': target_tab_id,
                'old_tab_count': old_tab_count,
                'new_tab_count': len(page.tab_ids),
                'page_info': page_info,
                'message': f"成功关闭标签页: {target_tab_id}"
            }
            
        except Exception as e:
            error_msg = self._handle_error(context, e)
            return {
                'success': False,
                'error': error_msg,
                'tab_id': self.tab_id,
                'message': f"关闭标签页失败: {error_msg}"
            }