#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DrissionPage 关闭页面节点

提供页面关闭、标签页管理等功能。
"""

from typing import Dict, Any, Optional, List
from DrissionPage import ChromiumPage, SessionPage, WebPage

from .base import DrissionPageBaseNode
from ..workflow_context import WorkflowDrissionPageContext


class ClosePageNode(DrissionPageBaseNode):
    """关闭页面节点
    
    关闭当前页面或指定页面。
    """
    
    def __init__(self, 
                 close_all_tabs: bool = False,
                 close_browser: bool = False,
                 save_cookies: bool = True,
                 **kwargs):
        """
        初始化关闭页面节点
        
        Args:
            close_all_tabs: 是否关闭所有标签页
            close_browser: 是否关闭整个浏览器
            save_cookies: 是否保存Cookie
        """
        super().__init__(
            name="关闭页面",
            description="关闭页面或浏览器",
            **kwargs
        )
        
        self.close_all_tabs = close_all_tabs
        self.close_browser = close_browser
        self.save_cookies = save_cookies
        
        self.node_type = "drissionpage_close_page"
    
    def execute(self, context: WorkflowDrissionPageContext) -> Dict[str, Any]:
        """执行关闭页面
        
        Args:
            context: 工作流上下文
            
        Returns:
            执行结果
        """
        try:
            page = self._get_page_instance(context)
            if page is None:
                return {
                    'success': True,
                    'message': '页面实例不存在，无需关闭',
                    'already_closed': True
                }
            
            # 保存Cookie（如果需要）
            cookies_saved = False
            if self.save_cookies:
                cookies_saved = self._save_cookies(context, page)
            
            # 获取页面信息
            page_info = self._get_page_info_before_close(page)
            
            # 执行关闭操作
            if self.close_browser:
                self._close_browser(page)
                close_action = "关闭浏览器"
            elif self.close_all_tabs:
                self._close_all_tabs(page)
                close_action = "关闭所有标签页"
            else:
                self._close_current_page(page)
                close_action = "关闭当前页面"
            
            # 清理上下文
            self._cleanup_context(context)
            
            return {
                'success': True,
                'close_action': close_action,
                'cookies_saved': cookies_saved,
                'page_info': page_info,
                'message': f"{close_action}成功"
            }
            
        except Exception as e:
            error_msg = self._handle_error(context, e)
            return {
                'success': False,
                'error': error_msg,
                'message': f"关闭页面失败: {error_msg}"
            }
    
    def _save_cookies(self, context: WorkflowDrissionPageContext, page) -> bool:
        """保存Cookie"""
        try:
            if isinstance(page, (ChromiumPage, WebPage)):
                cookies = page.get_cookies()
                if cookies:
                    context['saved_cookies'] = cookies
                    return True
            elif isinstance(page, SessionPage):
                # SessionPage的Cookie通过session对象获取
                if hasattr(page, 'session') and hasattr(page.session, 'cookies'):
                    cookies = dict(page.session.cookies)
                    if cookies:
                        context['saved_cookies'] = cookies
                        return True
            return False
        except Exception:
            return False
    
    def _get_page_info_before_close(self, page) -> Dict[str, Any]:
        """获取关闭前的页面信息"""
        try:
            info = {
                'page_type': type(page).__name__,
                'url': getattr(page, 'url', ''),
                'title': getattr(page, 'title', ''),
                'tab_count': 0
            }
            
            # 获取标签页数量
            if isinstance(page, (ChromiumPage, WebPage)):
                try:
                    if hasattr(page, 'tab_ids'):
                        info['tab_count'] = len(page.tab_ids)
                    elif hasattr(page, 'tabs'):
                        info['tab_count'] = len(page.tabs)
                except Exception:
                    pass
            
            return info
        except Exception:
            return {'page_type': 'unknown', 'url': '', 'title': '', 'tab_count': 0}
    
    def _close_browser(self, page):
        """关闭整个浏览器"""
        try:
            if isinstance(page, (ChromiumPage, WebPage)):
                if hasattr(page, 'quit'):
                    page.quit()
                elif hasattr(page, 'close'):
                    page.close()
                else:
                    # 尝试关闭所有标签页
                    self._close_all_tabs(page)
            elif isinstance(page, SessionPage):
                # SessionPage关闭session
                if hasattr(page, 'close'):
                    page.close()
                elif hasattr(page, 'session') and hasattr(page.session, 'close'):
                    page.session.close()
        except Exception as e:
            raise Exception(f"关闭浏览器失败: {str(e)}")
    
    def _close_all_tabs(self, page):
        """关闭所有标签页"""
        try:
            if isinstance(page, (ChromiumPage, WebPage)):
                if hasattr(page, 'close_tabs'):
                    # 关闭所有标签页
                    page.close_tabs()
                elif hasattr(page, 'tab_ids'):
                    # 逐个关闭标签页
                    tab_ids = list(page.tab_ids)
                    for tab_id in tab_ids:
                        try:
                            page.close_tab(tab_id)
                        except Exception:
                            continue
                elif hasattr(page, 'close'):
                    page.close()
            elif isinstance(page, SessionPage):
                # SessionPage只能关闭自身
                if hasattr(page, 'close'):
                    page.close()
        except Exception as e:
            raise Exception(f"关闭所有标签页失败: {str(e)}")
    
    def _close_current_page(self, page):
        """关闭当前页面"""
        try:
            if isinstance(page, (ChromiumPage, WebPage)):
                if hasattr(page, 'close_tab'):
                    # 关闭当前标签页
                    current_tab = getattr(page, 'tab_id', None)
                    if current_tab:
                        page.close_tab(current_tab)
                    else:
                        page.close_tab()
                elif hasattr(page, 'close'):
                    page.close()
            elif isinstance(page, SessionPage):
                # SessionPage关闭session
                if hasattr(page, 'close'):
                    page.close()
        except Exception as e:
            raise Exception(f"关闭当前页面失败: {str(e)}")
    
    def _cleanup_context(self, context: WorkflowDrissionPageContext):
        """清理上下文"""
        try:
            # 清理页面相关的上下文
            context['page_instance'] = None
            context['current_page'] = None
            context['browser_instance'] = None
            
            # 保留一些重要信息
            context['page_closed'] = True
            context['close_timestamp'] = self._get_current_timestamp()
            
        except Exception:
            pass  # 忽略清理错误
    
    def _get_current_timestamp(self) -> str:
        """获取当前时间戳"""
        try:
            import datetime
            return datetime.datetime.now().isoformat()
        except Exception:
            return ''


class CloseTabNode(DrissionPageBaseNode):
    """关闭标签页节点
    
    关闭指定的标签页。
    """
    
    def __init__(self, 
                 tab_id: str = None,
                 tab_index: int = None,
                 tab_url_contains: str = None,
                 tab_title_contains: str = None,
                 close_current: bool = True,
                 **kwargs):
        """
        初始化关闭标签页节点
        
        Args:
            tab_id: 标签页ID
            tab_index: 标签页索引
            tab_url_contains: 标签页URL包含的内容
            tab_title_contains: 标签页标题包含的内容
            close_current: 是否关闭当前标签页（当没有指定其他条件时）
        """
        super().__init__(
            name="关闭标签页",
            description=f"关闭标签页: {tab_id or tab_index or tab_url_contains or tab_title_contains or '当前'}",
            **kwargs
        )
        
        self.tab_id = tab_id
        self.tab_index = tab_index
        self.tab_url_contains = tab_url_contains
        self.tab_title_contains = tab_title_contains
        self.close_current = close_current
        
        self.node_type = "drissionpage_close_tab"
    
    def execute(self, context: WorkflowDrissionPageContext) -> Dict[str, Any]:
        """执行关闭标签页
        
        Args:
            context: 工作流上下文
            
        Returns:
            执行结果
        """
        try:
            page = self._get_page_instance(context)
            if page is None:
                return {
                    'success': False,
                    'error': '未找到页面实例',
                    'message': '关闭标签页失败: 未找到页面实例'
                }
            
            if not isinstance(page, (ChromiumPage, WebPage)):
                return {
                    'success': False,
                    'error': 'SessionPage不支持标签页操作',
                    'message': '关闭标签页失败: SessionPage不支持标签页操作'
                }
            
            # 查找要关闭的标签页
            target_tab = self._find_target_tab(page)
            
            if target_tab is None:
                return {
                    'success': False,
                    'error': '未找到目标标签页',
                    'message': '关闭标签页失败: 未找到目标标签页'
                }
            
            # 获取标签页信息
            tab_info = self._get_tab_info(page, target_tab)
            
            # 关闭标签页
            self._close_tab(page, target_tab)
            
            # 更新上下文
            context['closed_tab_info'] = tab_info
            context['last_closed_tab'] = target_tab
            
            return {
                'success': True,
                'closed_tab': target_tab,
                'tab_info': tab_info,
                'message': f"成功关闭标签页: {target_tab}"
            }
            
        except Exception as e:
            error_msg = self._handle_error(context, e)
            return {
                'success': False,
                'error': error_msg,
                'message': f"关闭标签页失败: {error_msg}"
            }
    
    def _find_target_tab(self, page) -> Optional[str]:
        """查找目标标签页"""
        try:
            # 按ID查找
            if self.tab_id:
                return self.tab_id
            
            # 按索引查找
            if self.tab_index is not None:
                if hasattr(page, 'tab_ids'):
                    tab_ids = list(page.tab_ids)
                    if 0 <= self.tab_index < len(tab_ids):
                        return tab_ids[self.tab_index]
            
            # 按URL或标题查找
            if self.tab_url_contains or self.tab_title_contains:
                return self._find_tab_by_content(page)
            
            # 关闭当前标签页
            if self.close_current:
                return getattr(page, 'tab_id', None)
            
            return None
            
        except Exception:
            return None
    
    def _find_tab_by_content(self, page) -> Optional[str]:
        """根据内容查找标签页"""
        try:
            if not hasattr(page, 'tab_ids'):
                return None
            
            current_tab = getattr(page, 'tab_id', None)
            
            for tab_id in page.tab_ids:
                try:
                    # 切换到标签页获取信息
                    page.to_tab(tab_id)
                    
                    # 检查URL
                    if self.tab_url_contains:
                        url = getattr(page, 'url', '')
                        if self.tab_url_contains in url:
                            return tab_id
                    
                    # 检查标题
                    if self.tab_title_contains:
                        title = getattr(page, 'title', '')
                        if self.tab_title_contains in title:
                            return tab_id
                            
                except Exception:
                    continue
            
            # 恢复到原标签页
            if current_tab:
                try:
                    page.to_tab(current_tab)
                except Exception:
                    pass
            
            return None
            
        except Exception:
            return None
    
    def _get_tab_info(self, page, tab_id: str) -> Dict[str, Any]:
        """获取标签页信息"""
        try:
            current_tab = getattr(page, 'tab_id', None)
            
            # 切换到目标标签页
            if tab_id != current_tab:
                page.to_tab(tab_id)
            
            info = {
                'tab_id': tab_id,
                'url': getattr(page, 'url', ''),
                'title': getattr(page, 'title', ''),
                'is_current': tab_id == current_tab
            }
            
            # 恢复到原标签页
            if tab_id != current_tab and current_tab:
                try:
                    page.to_tab(current_tab)
                except Exception:
                    pass
            
            return info
            
        except Exception:
            return {'tab_id': tab_id, 'url': '', 'title': '', 'is_current': False}
    
    def _close_tab(self, page, tab_id: str):
        """关闭标签页"""
        try:
            if hasattr(page, 'close_tab'):
                page.close_tab(tab_id)
            else:
                raise Exception("页面不支持关闭标签页操作")
        except Exception as e:
            raise Exception(f"关闭标签页失败: {str(e)}")


class QuitBrowserNode(DrissionPageBaseNode):
    """退出浏览器节点
    
    完全退出浏览器进程。
    """
    
    def __init__(self, 
                 force_quit: bool = False,
                 save_session: bool = True,
                 cleanup_temp_files: bool = True,
                 **kwargs):
        """
        初始化退出浏览器节点
        
        Args:
            force_quit: 是否强制退出
            save_session: 是否保存会话
            cleanup_temp_files: 是否清理临时文件
        """
        super().__init__(
            name="退出浏览器",
            description="完全退出浏览器进程",
            **kwargs
        )
        
        self.force_quit = force_quit
        self.save_session = save_session
        self.cleanup_temp_files = cleanup_temp_files
        
        self.node_type = "drissionpage_quit_browser"
    
    def execute(self, context: WorkflowDrissionPageContext) -> Dict[str, Any]:
        """执行退出浏览器
        
        Args:
            context: 工作流上下文
            
        Returns:
            执行结果
        """
        try:
            page = self._get_page_instance(context)
            if page is None:
                return {
                    'success': True,
                    'message': '浏览器实例不存在，无需退出',
                    'already_quit': True
                }
            
            # 保存会话信息（如果需要）
            session_saved = False
            if self.save_session:
                session_saved = self._save_session_info(context, page)
            
            # 获取浏览器信息
            browser_info = self._get_browser_info(page)
            
            # 执行退出
            self._quit_browser(page)
            
            # 清理临时文件（如果需要）
            cleanup_result = False
            if self.cleanup_temp_files:
                cleanup_result = self._cleanup_temp_files(context)
            
            # 完全清理上下文
            self._complete_cleanup_context(context)
            
            return {
                'success': True,
                'browser_info': browser_info,
                'session_saved': session_saved,
                'temp_files_cleaned': cleanup_result,
                'force_quit': self.force_quit,
                'message': '浏览器退出成功'
            }
            
        except Exception as e:
            error_msg = self._handle_error(context, e)
            return {
                'success': False,
                'error': error_msg,
                'message': f"退出浏览器失败: {error_msg}"
            }
    
    def _save_session_info(self, context: WorkflowDrissionPageContext, page) -> bool:
        """保存会话信息"""
        try:
            session_info = {
                'page_type': type(page).__name__,
                'timestamp': self._get_current_timestamp()
            }
            
            # 保存Cookie
            if isinstance(page, (ChromiumPage, WebPage)):
                try:
                    cookies = page.get_cookies()
                    if cookies:
                        session_info['cookies'] = cookies
                except Exception:
                    pass
            elif isinstance(page, SessionPage):
                try:
                    if hasattr(page, 'session') and hasattr(page.session, 'cookies'):
                        cookies = dict(page.session.cookies)
                        if cookies:
                            session_info['cookies'] = cookies
                except Exception:
                    pass
            
            # 保存当前URL
            try:
                session_info['last_url'] = getattr(page, 'url', '')
            except Exception:
                pass
            
            context['saved_session_info'] = session_info
            return True
            
        except Exception:
            return False
    
    def _get_browser_info(self, page) -> Dict[str, Any]:
        """获取浏览器信息"""
        try:
            info = {
                'page_type': type(page).__name__,
                'browser_type': 'unknown',
                'process_id': None,
                'tab_count': 0
            }
            
            # 获取浏览器类型
            if isinstance(page, ChromiumPage):
                info['browser_type'] = 'chromium'
            elif isinstance(page, SessionPage):
                info['browser_type'] = 'session'
            elif isinstance(page, WebPage):
                info['browser_type'] = 'web'
            
            # 获取进程ID
            try:
                if hasattr(page, 'browser') and hasattr(page.browser, 'process'):
                    info['process_id'] = page.browser.process.pid
            except Exception:
                pass
            
            # 获取标签页数量
            try:
                if hasattr(page, 'tab_ids'):
                    info['tab_count'] = len(page.tab_ids)
            except Exception:
                pass
            
            return info
            
        except Exception:
            return {'page_type': 'unknown', 'browser_type': 'unknown', 'process_id': None, 'tab_count': 0}
    
    def _quit_browser(self, page):
        """退出浏览器"""
        try:
            if isinstance(page, (ChromiumPage, WebPage)):
                if self.force_quit:
                    # 强制退出
                    if hasattr(page, 'quit'):
                        page.quit()
                    elif hasattr(page, 'browser') and hasattr(page.browser, 'quit'):
                        page.browser.quit()
                else:
                    # 正常退出
                    if hasattr(page, 'close'):
                        page.close()
                    elif hasattr(page, 'quit'):
                        page.quit()
            elif isinstance(page, SessionPage):
                # SessionPage关闭session
                if hasattr(page, 'close'):
                    page.close()
                elif hasattr(page, 'session') and hasattr(page.session, 'close'):
                    page.session.close()
        except Exception as e:
            if not self.force_quit:
                raise Exception(f"退出浏览器失败: {str(e)}")
            # 强制退出时忽略错误
    
    def _cleanup_temp_files(self, context: WorkflowDrissionPageContext) -> bool:
        """清理临时文件"""
        try:
            # 这里可以添加清理临时文件的逻辑
            # 例如清理下载文件、截图文件等
            temp_files_cleaned = 0
            
            # 清理截图文件
            screenshot_paths = context.get('screenshot_paths', [])
            for path in screenshot_paths:
                try:
                    import os
                    if os.path.exists(path):
                        os.remove(path)
                        temp_files_cleaned += 1
                except Exception:
                    continue
            
            # 清理下载文件（如果配置了自动清理）
            download_paths = context.get('download_paths', [])
            for path in download_paths:
                try:
                    import os
                    if os.path.exists(path):
                        os.remove(path)
                        temp_files_cleaned += 1
                except Exception:
                    continue
            
            context['temp_files_cleaned_count'] = temp_files_cleaned
            return temp_files_cleaned > 0
            
        except Exception:
            return False
    
    def _complete_cleanup_context(self, context: WorkflowDrissionPageContext):
        """完全清理上下文"""
        try:
            # 清理所有页面相关的上下文
            keys_to_clear = [
                'page_instance', 'current_page', 'browser_instance',
                'last_element', 'last_clicked_element', 'last_input_element',
                'screenshot_paths', 'download_paths', 'form_data'
            ]
            
            for key in keys_to_clear:
                if key in context:
                    context[key] = None
            
            # 设置退出标记
            context['browser_quit'] = True
            context['quit_timestamp'] = self._get_current_timestamp()
            
        except Exception:
            pass  # 忽略清理错误
    
    def _get_current_timestamp(self) -> str:
        """获取当前时间戳"""
        try:
            import datetime
            return datetime.datetime.now().isoformat()
        except Exception:
            return ''