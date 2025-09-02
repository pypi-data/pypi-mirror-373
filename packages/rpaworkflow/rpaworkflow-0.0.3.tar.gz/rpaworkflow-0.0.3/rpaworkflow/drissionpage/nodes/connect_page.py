#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DrissionPage 页面连接节点

提供创建和连接 DrissionPage 页面的功能。
"""

from typing import Dict, Any

from DrissionPage import ChromiumOptions, SessionOptions
from DrissionPage import ChromiumPage, SessionPage, WebPage

from .base import DrissionPageBaseNode
from ..workflow_context import CONTEXT


class ConnectPageNode(DrissionPageBaseNode):
    """页面连接节点
    
    创建和连接 DrissionPage 页面实例。
    """
    
    def __init__(self, 
                 page_type: str = "chromium",
                 headless: bool = False,
                 window_size: tuple = (1920, 1080),
                 user_data_dir: str = None,
                 browser_path: str = None,
                 port: int = None,
                 timeout: float = 30.0,
                 proxy: str = None,
                 user_agent: str = None,
                 download_path: str = None,
                 extensions: list = None,
                 arguments: list = None,
                 session_config: dict = None,
                 **kwargs):
        """
        初始化页面连接节点
        
        Args:
            page_type: 页面类型 ('chromium', 'session', 'web')
            headless: 是否无头模式（仅 chromium）
            window_size: 窗口大小
            user_data_dir: 用户数据目录
            browser_path: 浏览器可执行文件路径
            port: 调试端口
            timeout: 连接超时时间
            proxy: 代理设置
            user_agent: 用户代理
            download_path: 下载路径
            extensions: 扩展列表
            arguments: 启动参数
            session_config: Session 配置
        """
        super().__init__(
            name="连接页面",
            description=f"创建 {page_type} 页面实例",
            **kwargs
        )
        
        self.page_type = page_type
        self.headless = headless
        self.window_size = window_size
        self.user_data_dir = user_data_dir
        self.browser_path = browser_path
        self.port = port
        self.timeout = timeout
        self.proxy = proxy
        self.user_agent = user_agent
        self.download_path = download_path
        self.extensions = extensions or []
        self.arguments = arguments or []
        self.session_config = session_config or {}
        
        self.node_type = "drissionpage_connect"
    
    def _create_chromium_page(self) -> ChromiumPage:
        """创建 ChromiumPage 实例"""
        # 配置 ChromiumOptions
        options = ChromiumOptions()
        
        # 基础配置
        if self.headless:
            options.headless()
        
        # if self.window_size:
        #     options.set_window_size(*self.window_size)
        
        if self.user_data_dir:
            options.set_user_data_path(self.user_data_dir)
        
        if self.browser_path:
            options.set_browser_path(self.browser_path)
        
        if self.port:
            options.set_local_port(self.port)
        
        if self.proxy:
            options.set_proxy(self.proxy)
        
        if self.user_agent:
            options.set_user_agent(self.user_agent)
        
        if self.download_path:
            options.set_download_path(self.download_path)
        
        # 添加扩展
        for extension in self.extensions:
            options.add_extension(extension)
        
        # 添加启动参数
        for arg in self.arguments:
            options.arguments.append(arg)

        # 创建页面
        return ChromiumPage(addr_or_opts=options,
                            # timeout=self.timeout
                            )
    
    def _create_session_page(self) -> SessionPage:
        """创建 SessionPage 实例"""
        # 配置 SessionOptions
        options = SessionOptions()
        
        # 基础配置
        if self.proxy:
            options.set_proxies(http=self.proxy, https=self.proxy)
        
        # if self.user_agent:
        #     options.set_user_agent(self.user_agent)
        
        if self.timeout:
            options.set_timeout(self.timeout)
        
        # 应用自定义配置
        for key, value in self.session_config.items():
            if hasattr(options, f'set_{key}'):
                getattr(options, f'set_{key}')(value)
        
        # 创建页面
        return SessionPage(session_or_options=options)
    
    def _create_web_page(self) -> WebPage:
        """创建 WebPage 实例"""
        # WebPage 结合了 ChromiumPage 和 SessionPage
        chromium_options = ChromiumOptions()
        session_options = SessionOptions()
        
        # 配置 ChromiumOptions
        if self.headless:
            chromium_options.headless()
        
        # if self.window_size:
        #     chromium_options.set_window_size(*self.window_size)
        
        if self.user_data_dir:
            chromium_options.set_user_data_path(self.user_data_dir)
        
        if self.browser_path:
            chromium_options.set_browser_path(self.browser_path)
        
        if self.port:
            chromium_options.set_local_port(self.port)
        
        if self.user_agent:
            chromium_options.set_user_agent(self.user_agent)
            # session_options.set_user_agent(self.user_agent)
        
        if self.download_path:
            chromium_options.set_download_path(self.download_path)
        
        # 配置代理
        if self.proxy:
            chromium_options.set_proxy(self.proxy)
            session_options.set_proxies(http=self.proxy, https=self.proxy)
        
        # 添加扩展和参数
        for extension in self.extensions:
            chromium_options.add_extension(extension)
        
        for arg in self.arguments:
            chromium_options.arguments.append(arg)
        
        # 配置 SessionOptions
        if self.timeout:
            session_options.set_timeout(self.timeout)
        
        # 应用自定义配置
        for key, value in self.session_config.items():
            if hasattr(session_options, f'set_{key}'):
                getattr(session_options, f'set_{key}')(value)
        
        # 创建页面
        return WebPage(chromium_options=chromium_options, session_or_options=session_options,
                       # timeout=self.timeout
                       )
    
    def execute(self, context: CONTEXT) -> Dict[str, Any]:
        """执行页面连接
        
        Args:
            context: 工作流上下文
            
        Returns:
            执行结果
        """
        try:
            # 创建页面实例
            if self.page_type.lower() == "chromium":
                page = self._create_chromium_page()
            elif self.page_type.lower() == "session":
                page = self._create_session_page()
            elif self.page_type.lower() == "web":
                page = self._create_web_page()
            else:
                raise ValueError(f"不支持的页面类型: {self.page_type}")
            
            # 更新上下文
            context['page'] = page
            context['page_type'] = self.page_type.lower()
            context['headless'] = self.headless
            context['window_size'] = self.window_size
            context['timeout'] = self.timeout
            
            # 获取页面信息
            page_info = self._get_page_info(context)
            
            return {
                'success': True,
                'page_type': self.page_type,
                'page_info': page_info,
                'message': f"成功创建 {self.page_type} 页面"
            }
            
        except Exception as e:
            error_msg = self._handle_error(context, e)
            return {
                'success': False,
                'error': error_msg,
                'message': f"创建 {self.page_type} 页面失败: {error_msg}"
            }


class ConnectExistingPageNode(DrissionPageBaseNode):
    """连接现有页面节点
    
    连接到已存在的浏览器页面。
    """
    
    def __init__(self, 
                 tab_id: str = None,
                 address: str = None,
                 port: int = 9222,
                 timeout: float = 30.0,
                 **kwargs):
        """
        初始化连接现有页面节点
        
        Args:
            tab_id: 标签页ID
            address: 浏览器地址
            port: 调试端口
            timeout: 连接超时时间
        """
        super().__init__(
            name="连接现有页面",
            description="连接到已存在的浏览器页面",
            **kwargs
        )
        
        self.tab_id = tab_id
        self.address = address or "127.0.0.1"
        self.port = port
        self.timeout = timeout
        
        self.node_type = "drissionpage_connect_existing"
    
    def execute(self, context: CONTEXT) -> Dict[str, Any]:
        """执行连接现有页面
        
        Args:
            context: 工作流上下文
            
        Returns:
            执行结果
        """
        try:
            # 构建连接地址
            if self.tab_id:
                addr = f"{self.address}:{self.port}/{self.tab_id}"
            else:
                addr = f"{self.address}:{self.port}"
            
            # 连接到现有页面
            page = ChromiumPage(addr_or_opts=addr, timeout=self.timeout)
            
            # 更新上下文
            context['page'] = page
            context['page_type'] = 'chromium'
            context['connected_address'] = addr
            context['timeout'] = self.timeout
            
            # 获取页面信息
            page_info = self._get_page_info(context)
            
            return {
                'success': True,
                'connected_address': addr,
                'page_info': page_info,
                'message': f"成功连接到现有页面: {addr}"
            }
            
        except Exception as e:
            error_msg = self._handle_error(context, e)
            return {
                'success': False,
                'error': error_msg,
                'message': f"连接现有页面失败: {error_msg}"
            }


class SwitchTabNode(DrissionPageBaseNode):
    """切换标签页节点
    
    在多个标签页之间切换。
    """
    
    def __init__(self, 
                 tab_id: str = None,
                 tab_index: int = None,
                 url_contains: str = None,
                 title_contains: str = None,
                 **kwargs):
        """
        初始化切换标签页节点
        
        Args:
            tab_id: 标签页ID
            tab_index: 标签页索引
            url_contains: URL包含的文本
            title_contains: 标题包含的文本
        """
        super().__init__(
            name="切换标签页",
            description="在多个标签页之间切换",
            **kwargs
        )
        
        self.tab_id = tab_id
        self.tab_index = tab_index
        self.url_contains = url_contains
        self.title_contains = title_contains
        
        self.node_type = "drissionpage_switch_tab"
    
    def execute(self, context: CONTEXT) -> Dict[str, Any]:
        """执行切换标签页
        
        Args:
            context: 工作流上下文
            
        Returns:
            执行结果
        """
        try:
            page = self._get_page(context)
            
            # 只有 ChromiumPage 支持标签页操作
            if not isinstance(page, ChromiumPage):
                raise ValueError("只有 ChromiumPage 支持标签页操作")
            
            # 根据不同条件切换标签页
            if self.tab_id:
                page.to_tab(self.tab_id)
                target_info = f"ID: {self.tab_id}"
            elif self.tab_index is not None:
                tab_ids = page.tab_ids
                if 0 <= self.tab_index < len(tab_ids):
                    page.to_tab(tab_ids[self.tab_index])
                    target_info = f"索引: {self.tab_index}"
                else:
                    raise ValueError(f"标签页索引 {self.tab_index} 超出范围")
            elif self.url_contains:
                # 查找包含指定URL的标签页
                found = False
                for tab_id in page.tab_ids:
                    page.to_tab(tab_id)
                    if self.url_contains in page.url:
                        found = True
                        target_info = f"URL包含: {self.url_contains}"
                        break
                if not found:
                    raise ValueError(f"未找到URL包含 '{self.url_contains}' 的标签页")
            elif self.title_contains:
                # 查找包含指定标题的标签页
                found = False
                for tab_id in page.tab_ids:
                    page.to_tab(tab_id)
                    if self.title_contains in page.title:
                        found = True
                        target_info = f"标题包含: {self.title_contains}"
                        break
                if not found:
                    raise ValueError(f"未找到标题包含 '{self.title_contains}' 的标签页")
            else:
                raise ValueError("必须指定切换条件")
            
            # 更新上下文
            context['current_tab_id'] = page.tab_id
            page_info = self._get_page_info(context)
            
            return {
                'success': True,
                'target_info': target_info,
                'current_tab_id': page.tab_id,
                'page_info': page_info,
                'message': f"成功切换到标签页: {target_info}"
            }
            
        except Exception as e:
            error_msg = self._handle_error(context, e)
            return {
                'success': False,
                'error': error_msg,
                'message': f"切换标签页失败: {error_msg}"
            }