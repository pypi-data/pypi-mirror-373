#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DrissionPage 等待节点

提供各种等待条件的功能。
"""

from typing import Dict, Any, Callable

from DrissionPage import SessionPage
from DrissionPage._elements.chromium_element import ChromiumElement

from .base import DrissionPageBaseNode
from ..workflow_context import CONTEXT


class WaitNode(DrissionPageBaseNode):
    """基础等待节点
    
    等待指定的时间。
    """
    
    def __init__(self, 
                 seconds: float,
                 **kwargs):
        """
        初始化等待节点
        
        Args:
            seconds: 等待时间（秒）
        """
        super().__init__(
            name="等待",
            description=f"等待 {seconds} 秒",
            **kwargs
        )
        
        self.seconds = seconds
        
        self.node_type = "drissionpage_wait"
    
    def execute(self, context: CONTEXT) -> Dict[str, Any]:
        """执行等待
        
        Args:
            context: 工作流上下文
            
        Returns:
            执行结果
        """
        try:
            import time
            
            start_time = time.time()
            time.sleep(self.seconds)
            actual_time = time.time() - start_time
            
            # 更新上下文
            context['last_wait_time'] = actual_time
            
            return {
                'success': True,
                'wait_time': self.seconds,
                'actual_time': actual_time,
                'message': f"成功等待 {actual_time:.2f} 秒"
            }
            
        except Exception as e:
            error_msg = self._handle_error(context, e)
            return {
                'success': False,
                'error': error_msg,
                'wait_time': self.seconds,
                'message': f"等待失败: {error_msg}"
            }


class WaitForElementNode(DrissionPageBaseNode):
    """等待元素节点
    
    等待指定元素出现或满足条件。
    """
    
    def __init__(self, 
                 locator: str = None,
                 by_css: str = None,
                 by_xpath: str = None,
                 by_text: str = None,
                 by_tag: str = None,
                 by_attr: tuple = None,
                 condition: str = "exist",
                 timeout: float = 10.0,
                 poll_frequency: float = 0.5,
                 **kwargs):
        """
        初始化等待元素节点
        
        Args:
            locator: 通用定位器
            by_css: CSS选择器
            by_xpath: XPath表达式
            by_text: 文本内容
            by_tag: 标签名
            by_attr: 属性元组
            condition: 等待条件 ('exist', 'visible', 'hidden', 'clickable', 'text_present')
            timeout: 超时时间
            poll_frequency: 轮询频率
        """
        super().__init__(
            name="等待元素",
            description=f"等待元素 {condition}: {locator or by_css or by_xpath or by_text or by_tag or by_attr}",
            **kwargs
        )
        
        self.locator = locator
        self.by_css = by_css
        self.by_xpath = by_xpath
        self.by_text = by_text
        self.by_tag = by_tag
        self.by_attr = by_attr
        self.condition = condition
        self.timeout = timeout
        self.poll_frequency = poll_frequency
        
        self.node_type = "drissionpage_wait_element"
    
    def execute(self, context: CONTEXT) -> Dict[str, Any]:
        """执行等待元素
        
        Args:
            context: 工作流上下文
            
        Returns:
            执行结果
        """
        try:
            import time
            
            page = self._get_page(context)
            start_time = time.time()
            
            # 构建定位器字符串
            target_locator = self._build_locator()
            
            # 根据条件等待
            success = False
            element = None
            
            if self.condition == "exist":
                success = self._wait_for_element_exist(page, target_locator)
            elif self.condition == "visible":
                success = self._wait_for_element_visible(page, target_locator)
            elif self.condition == "hidden":
                success = self._wait_for_element_hidden(page, target_locator)
            elif self.condition == "clickable":
                success = self._wait_for_element_clickable(page, target_locator)
            elif self.condition == "text_present":
                success = self._wait_for_text_present(page, target_locator)
            else:
                raise ValueError(f"不支持的等待条件: {self.condition}")
            
            actual_time = time.time() - start_time
            
            if success:
                # 尝试获取元素
                try:
                    element = self._find_element(
                        context=context,
                        locator=self.locator,
                        by_css=self.by_css,
                        by_xpath=self.by_xpath,
                        by_text=self.by_text,
                        by_tag=self.by_tag,
                        by_attr=self.by_attr,
                        timeout=1.0
                    )
                except:
                    pass
            
            # 更新上下文
            context['wait_condition'] = self.condition
            context['wait_success'] = success
            context['wait_actual_time'] = actual_time
            if element:
                context['waited_element'] = element
            
            if success:
                return {
                    'success': True,
                    'condition': self.condition,
                    'locator': target_locator,
                    'wait_time': actual_time,
                    'element_found': element is not None,
                    'message': f"成功等待元素 {self.condition} 条件满足，耗时 {actual_time:.2f} 秒"
                }
            else:
                return {
                    'success': False,
                    'condition': self.condition,
                    'locator': target_locator,
                    'timeout': self.timeout,
                    'message': f"等待元素 {self.condition} 条件超时，耗时 {actual_time:.2f} 秒"
                }
            
        except Exception as e:
            error_msg = self._handle_error(context, e)
            return {
                'success': False,
                'error': error_msg,
                'condition': self.condition,
                'message': f"等待元素失败: {error_msg}"
            }
    
    def _build_locator(self) -> str:
        """构建定位器字符串"""
        if self.by_css:
            return self.by_css
        elif self.by_xpath:
            return self.by_xpath
        elif self.by_text:
            return f'text:{self.by_text}'
        elif self.by_tag:
            return f'tag:{self.by_tag}'
        elif self.by_attr:
            attr_name, attr_value = self.by_attr
            return f'@{attr_name}={attr_value}'
        elif self.locator:
            return self.locator
        else:
            raise ValueError("必须提供定位器")
    
    def _wait_for_element_exist(self, page, locator: str) -> bool:
        """等待元素存在"""
        try:
            if hasattr(page, 'wait'):
                return page.wait.ele_loaded(locator, timeout=self.timeout)
            else:
                # SessionPage 没有 wait 对象，使用轮询
                return self._poll_condition(lambda: page.ele(locator) is not None)
        except:
            return False
    
    def _wait_for_element_visible(self, page, locator: str) -> bool:
        """等待元素可见"""
        try:
            if hasattr(page, 'wait'):
                return page.wait.ele_displayed(locator, timeout=self.timeout)
            else:
                # SessionPage 使用轮询
                return self._poll_condition(lambda: self._is_element_visible(page, locator))
        except:
            return False
    
    def _wait_for_element_hidden(self, page, locator: str) -> bool:
        """等待元素隐藏"""
        try:
            if hasattr(page, 'wait'):
                return page.wait.ele_hidden(locator, timeout=self.timeout)
            else:
                # SessionPage 使用轮询
                return self._poll_condition(lambda: not self._is_element_visible(page, locator))
        except:
            return False
    
    def _wait_for_element_clickable(self, page, locator: str) -> bool:
        """等待元素可点击"""
        try:
            # DrissionPage 没有直接的 clickable 等待，使用 displayed 代替
            if hasattr(page, 'wait'):
                return page.wait.ele_displayed(locator, timeout=self.timeout)
            else:
                return self._poll_condition(lambda: self._is_element_clickable(page, locator))
        except:
            return False
    
    def _wait_for_text_present(self, page, locator: str) -> bool:
        """等待文本出现"""
        try:
            return self._poll_condition(lambda: self._has_text(page, locator))
        except:
            return False
    
    def _poll_condition(self, condition_func: Callable) -> bool:
        """轮询条件"""
        import time
        
        start_time = time.time()
        while time.time() - start_time < self.timeout:
            try:
                if condition_func():
                    return True
            except:
                pass
            time.sleep(self.poll_frequency)
        return False
    
    def _is_element_visible(self, page, locator: str) -> bool:
        """检查元素是否可见"""
        try:
            element = page.ele(locator)
            if element is None:
                return False
            if isinstance(element, ChromiumElement):
                return element.is_displayed
            else:
                # SessionElement 假设存在即可见
                return True
        except:
            return False
    
    def _is_element_clickable(self, page, locator: str) -> bool:
        """检查元素是否可点击"""
        try:
            element = page.ele(locator)
            if element is None:
                return False
            if isinstance(element, ChromiumElement):
                return element.is_displayed and element.is_enabled
            else:
                # SessionElement 假设存在即可点击
                return True
        except:
            return False
    
    def _has_text(self, page, locator: str) -> bool:
        """检查元素是否有文本"""
        try:
            element = page.ele(locator)
            if element is None:
                return False
            return bool(element.text.strip())
        except:
            return False


class WaitForPageLoadNode(DrissionPageBaseNode):
    """等待页面加载节点
    
    等待页面加载完成。
    """
    
    def __init__(self, 
                 timeout: float = 30.0,
                 check_ready_state: bool = True,
                 **kwargs):
        """
        初始化等待页面加载节点
        
        Args:
            timeout: 超时时间
            check_ready_state: 是否检查页面就绪状态
        """
        super().__init__(
            name="等待页面加载",
            description="等待页面加载完成",
            **kwargs
        )
        
        self.timeout = timeout
        self.check_ready_state = check_ready_state
        
        self.node_type = "drissionpage_wait_page_load"
    
    def execute(self, context: CONTEXT) -> Dict[str, Any]:
        """执行等待页面加载
        
        Args:
            context: 工作流上下文
            
        Returns:
            执行结果
        """
        try:
            import time
            
            page = self._get_page(context)
            start_time = time.time()
            
            # 只有 ChromiumPage 和 WebPage 支持页面加载等待
            if isinstance(page, SessionPage):
                # SessionPage 简单等待一下
                time.sleep(1.0)
                success = True
            else:
                success = False
                
                # 等待页面开始加载
                if hasattr(page, 'wait'):
                    try:
                        page.wait.load_start(timeout=self.timeout)
                        success = True
                    except:
                        pass
                
                # 检查页面就绪状态
                if success and self.check_ready_state:
                    success = self._wait_for_ready_state(page)
            
            actual_time = time.time() - start_time
            
            # 更新上下文
            context['page_load_success'] = success
            context['page_load_time'] = actual_time
            
            if success:
                return {
                    'success': True,
                    'load_time': actual_time,
                    'ready_state': getattr(page, 'ready_state', 'unknown'),
                    'message': f"页面加载完成，耗时 {actual_time:.2f} 秒"
                }
            else:
                return {
                    'success': False,
                    'timeout': self.timeout,
                    'actual_time': actual_time,
                    'message': f"页面加载超时，耗时 {actual_time:.2f} 秒"
                }
            
        except Exception as e:
            error_msg = self._handle_error(context, e)
            return {
                'success': False,
                'error': error_msg,
                'message': f"等待页面加载失败: {error_msg}"
            }
    
    def _wait_for_ready_state(self, page) -> bool:
        """等待页面就绪状态"""
        import time
        
        start_time = time.time()
        while time.time() - start_time < self.timeout:
            try:
                if hasattr(page, 'ready_state') and page.ready_state == 'complete':
                    return True
            except:
                pass
            time.sleep(0.5)
        return False


class WaitForUrlNode(DrissionPageBaseNode):
    """等待URL节点
    
    等待页面URL包含指定内容或匹配模式。
    """
    
    def __init__(self, 
                 url_contains: str = None,
                 url_equals: str = None,
                 url_pattern: str = None,
                 timeout: float = 10.0,
                 poll_frequency: float = 0.5,
                 **kwargs):
        """
        初始化等待URL节点
        
        Args:
            url_contains: URL包含的文本
            url_equals: URL完全匹配的文本
            url_pattern: URL正则表达式模式
            timeout: 超时时间
            poll_frequency: 轮询频率
        """
        super().__init__(
            name="等待URL",
            description=f"等待URL变化: {url_contains or url_equals or url_pattern}",
            **kwargs
        )
        
        self.url_contains = url_contains
        self.url_equals = url_equals
        self.url_pattern = url_pattern
        self.timeout = timeout
        self.poll_frequency = poll_frequency
        
        self.node_type = "drissionpage_wait_url"
    
    def execute(self, context: CONTEXT) -> Dict[str, Any]:
        """执行等待URL
        
        Args:
            context: 工作流上下文
            
        Returns:
            执行结果
        """
        try:
            import time
            import re
            
            page = self._get_page(context)
            start_time = time.time()
            
            success = False
            current_url = ""
            
            while time.time() - start_time < self.timeout:
                try:
                    current_url = page.url
                    
                    if self.url_contains and self.url_contains in current_url:
                        success = True
                        break
                    elif self.url_equals and self.url_equals == current_url:
                        success = True
                        break
                    elif self.url_pattern and re.search(self.url_pattern, current_url):
                        success = True
                        break
                        
                except:
                    pass
                
                time.sleep(self.poll_frequency)
            
            actual_time = time.time() - start_time
            
            # 更新上下文
            context['url_wait_success'] = success
            context['url_wait_time'] = actual_time
            context['current_url'] = current_url
            
            if success:
                return {
                    'success': True,
                    'current_url': current_url,
                    'wait_time': actual_time,
                    'condition': {
                        'contains': self.url_contains,
                        'equals': self.url_equals,
                        'pattern': self.url_pattern
                    },
                    'message': f"URL条件满足，当前URL: {current_url}"
                }
            else:
                return {
                    'success': False,
                    'current_url': current_url,
                    'timeout': self.timeout,
                    'actual_time': actual_time,
                    'condition': {
                        'contains': self.url_contains,
                        'equals': self.url_equals,
                        'pattern': self.url_pattern
                    },
                    'message': f"等待URL条件超时，当前URL: {current_url}"
                }
            
        except Exception as e:
            error_msg = self._handle_error(context, e)
            return {
                'success': False,
                'error': error_msg,
                'message': f"等待URL失败: {error_msg}"
            }


class WaitForTitleNode(DrissionPageBaseNode):
    """等待标题节点
    
    等待页面标题包含指定内容或匹配模式。
    """
    
    def __init__(self, 
                 title_contains: str = None,
                 title_equals: str = None,
                 title_pattern: str = None,
                 timeout: float = 10.0,
                 poll_frequency: float = 0.5,
                 **kwargs):
        """
        初始化等待标题节点
        
        Args:
            title_contains: 标题包含的文本
            title_equals: 标题完全匹配的文本
            title_pattern: 标题正则表达式模式
            timeout: 超时时间
            poll_frequency: 轮询频率
        """
        super().__init__(
            name="等待标题",
            description=f"等待标题变化: {title_contains or title_equals or title_pattern}",
            **kwargs
        )
        
        self.title_contains = title_contains
        self.title_equals = title_equals
        self.title_pattern = title_pattern
        self.timeout = timeout
        self.poll_frequency = poll_frequency
        
        self.node_type = "drissionpage_wait_title"
    
    def execute(self, context: CONTEXT) -> Dict[str, Any]:
        """执行等待标题
        
        Args:
            context: 工作流上下文
            
        Returns:
            执行结果
        """
        try:
            import time
            import re
            
            page = self._get_page(context)
            start_time = time.time()
            
            success = False
            current_title = ""
            
            while time.time() - start_time < self.timeout:
                try:
                    current_title = page.title
                    
                    if self.title_contains and self.title_contains in current_title:
                        success = True
                        break
                    elif self.title_equals and self.title_equals == current_title:
                        success = True
                        break
                    elif self.title_pattern and re.search(self.title_pattern, current_title):
                        success = True
                        break
                        
                except:
                    pass
                
                time.sleep(self.poll_frequency)
            
            actual_time = time.time() - start_time
            
            # 更新上下文
            context['title_wait_success'] = success
            context['title_wait_time'] = actual_time
            context['current_title'] = current_title
            
            if success:
                return {
                    'success': True,
                    'current_title': current_title,
                    'wait_time': actual_time,
                    'condition': {
                        'contains': self.title_contains,
                        'equals': self.title_equals,
                        'pattern': self.title_pattern
                    },
                    'message': f"标题条件满足，当前标题: {current_title}"
                }
            else:
                return {
                    'success': False,
                    'current_title': current_title,
                    'timeout': self.timeout,
                    'actual_time': actual_time,
                    'condition': {
                        'contains': self.title_contains,
                        'equals': self.title_equals,
                        'pattern': self.title_pattern
                    },
                    'message': f"等待标题条件超时，当前标题: {current_title}"
                }
            
        except Exception as e:
            error_msg = self._handle_error(context, e)
            return {
                'success': False,
                'error': error_msg,
                'message': f"等待标题失败: {error_msg}"
            }