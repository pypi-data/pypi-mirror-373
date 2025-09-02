#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
连接浏览器节点
"""
import os
from typing import Optional, Dict, Any, List

from playwright.sync_api import sync_playwright, Browser, BrowserContext, Page

from rpaworkflow.node import DataStorageNode
from rpaworkflow.playwright.nodes.base import PlaywrightBaseNode
from rpaworkflow.playwright.workflow_context import CONTEXT


class ConnectBrowserNode(PlaywrightBaseNode, DataStorageNode):
    """连接浏览器节点

    用于启动浏览器并获取驱动
    将浏览器实例存储到上下文中
    """

    def __init__(self,
                 name: str = "连接浏览器",
                 description: str = "启动浏览器并获取实例",
                 browser_type: str = "chromium",
                 headless: bool = False,
                 viewport: Optional[Dict[str, int]] = None,
                 user_data_dir: Optional[str] = None,
                 executable_path: Optional[str] = None,
                 args: Optional[List[str]] = None,
                 ignore_default_args: Optional[List[str]] = None,
                 proxy: Optional[Dict[str, str]] = None,
                 downloads_path: Optional[str] = None,
                 slow_mo: Optional[float] = None,
                 timeout: Optional[float] = None,
                 # 上下文选项
                 user_agent: Optional[str] = None,
                 locale: Optional[str] = None,
                 timezone: Optional[str] = None,
                 geolocation: Optional[Dict[str, float]] = None,
                 permissions: Optional[List[str]] = None,
                 extra_http_headers: Optional[Dict[str, str]] = None,
                 offline: bool = False,
                 http_credentials: Optional[Dict[str, str]] = None,
                 device_scale_factor: Optional[float] = None,
                 is_mobile: bool = False,
                 has_touch: bool = False,
                 color_scheme: Optional[str] = None,
                 reduced_motion: Optional[str] = None,
                 forced_colors: Optional[str] = None,
                 # 录制选项
                 record_video_dir: Optional[str] = None,
                 record_video_size: Optional[Dict[str, int]] = None,
                 record_har_path: Optional[str] = None,
                 # 安全选项
                 ignore_https_errors: bool = False,
                 bypass_csp: bool = False,
                 # 设备模拟
                 device_name: Optional[str] = None,
                 **kwargs):
        super().__init__(name, description, output_key='browser', **kwargs)
        self.browser_type = browser_type.lower()
        self.headless = headless
        self.viewport = viewport or {"width": 1280, "height": 720}
        self.user_data_dir = user_data_dir
        self.executable_path = executable_path
        self.args = args or []
        self.ignore_default_args = ignore_default_args
        self.proxy = proxy
        self.downloads_path = downloads_path
        self.slow_mo = slow_mo
        self.timeout = timeout
        
        # 上下文选项
        self.user_agent = user_agent
        self.locale = locale
        self.timezone = timezone
        self.geolocation = geolocation
        self.permissions = permissions
        self.extra_http_headers = extra_http_headers
        self.offline = offline
        self.http_credentials = http_credentials
        self.device_scale_factor = device_scale_factor
        self.is_mobile = is_mobile
        self.has_touch = has_touch
        self.color_scheme = color_scheme
        self.reduced_motion = reduced_motion
        self.forced_colors = forced_colors
        
        # 录制选项
        self.record_video_dir = record_video_dir
        self.record_video_size = record_video_size
        self.record_har_path = record_har_path
        
        # 安全选项
        self.ignore_https_errors = ignore_https_errors
        self.bypass_csp = bypass_csp
        
        # 设备模拟
        self.device_name = device_name
        
        self.playwright = None

    def _prepare_browser_options(self) -> Dict[str, Any]:
        """准备浏览器启动选项"""
        options = {
            "headless": self.headless,
        }
        
        if self.executable_path:
            options["executable_path"] = self.executable_path
        
        if self.args:
            options["args"] = self.args
            
        if self.ignore_default_args:
            options["ignore_default_args"] = self.ignore_default_args
            
        if self.proxy:
            options["proxy"] = self.proxy
            
        if self.downloads_path:
            options["downloads_path"] = self.downloads_path
            
        if self.slow_mo:
            options["slow_mo"] = self.slow_mo
            
        if self.timeout:
            options["timeout"] = self.timeout
            
        return options

    def _prepare_context_options(self) -> Dict[str, Any]:
        """准备浏览器上下文选项"""
        options = {
            "viewport": self.viewport,
            "ignore_https_errors": self.ignore_https_errors,
            "bypass_csp": self.bypass_csp,
            "offline": self.offline,
            "is_mobile": self.is_mobile,
            "has_touch": self.has_touch,
        }
        
        if self.user_agent:
            options["user_agent"] = self.user_agent
            
        if self.locale:
            options["locale"] = self.locale
            
        if self.timezone:
            options["timezone_id"] = self.timezone
            
        if self.geolocation:
            options["geolocation"] = self.geolocation
            
        if self.permissions:
            options["permissions"] = self.permissions
            
        if self.extra_http_headers:
            options["extra_http_headers"] = self.extra_http_headers
            
        if self.http_credentials:
            options["http_credentials"] = self.http_credentials
            
        if self.device_scale_factor:
            options["device_scale_factor"] = self.device_scale_factor
            
        if self.color_scheme:
            options["color_scheme"] = self.color_scheme
            
        if self.reduced_motion:
            options["reduced_motion"] = self.reduced_motion
            
        if self.forced_colors:
            options["forced_colors"] = self.forced_colors
            
        if self.record_video_dir:
            options["record_video_dir"] = self.record_video_dir
            if self.record_video_size:
                options["record_video_size"] = self.record_video_size
                
        if self.record_har_path:
            options["record_har_path"] = self.record_har_path
            
        if self.user_data_dir:
            # 对于持久化上下文
            options["user_data_dir"] = self.user_data_dir
            
        return options

    def _create_browser(self) -> Browser:
        """创建浏览器实例"""
        self.playwright = sync_playwright().start()
        
        browser_options = self._prepare_browser_options()
        
        if self.browser_type == "chromium":
            return self.playwright.chromium.launch(**browser_options)
        elif self.browser_type == "firefox":
            return self.playwright.firefox.launch(**browser_options)
        elif self.browser_type == "webkit":
            return self.playwright.webkit.launch(**browser_options)
        else:
            raise ValueError(f"不支持的浏览器类型: {self.browser_type}")

    def _create_context_and_page(self, browser: Browser) -> tuple[BrowserContext, Page]:
        """创建浏览器上下文和页面"""
        context_options = self._prepare_context_options()
        
        # 如果指定了设备名称，使用设备模拟
        if self.device_name:
            device = self.playwright.devices.get(self.device_name)
            if device:
                context_options.update(device)
        
        # 如果有用户数据目录，创建持久化上下文
        if self.user_data_dir:
            # 移除不适用于持久化上下文的选项
            persistent_options = {k: v for k, v in context_options.items() 
                                if k not in ['user_data_dir']}
            browser_context = browser.new_persistent_context(
                user_data_dir=self.user_data_dir,
                **persistent_options
            )
            # 获取第一个页面或创建新页面
            pages = browser_context.pages
            if pages:
                page = pages[0]
            else:
                page = browser_context.new_page()
        else:
            browser_context = browser.new_context(**context_options)
            page = browser_context.new_page()
        
        return browser_context, page

    def execute(self, context: CONTEXT) -> Any:
        """执行连接浏览器操作"""
        try:
            # 创建浏览器
            browser = self._create_browser()
            
            # 创建上下文和页面
            browser_context, page = self._create_context_and_page(browser)
            
            # 存储到上下文
            context['browser'] = browser
            context['browser_context'] = browser_context
            context['page'] = page
            context['browser_type'] = self.browser_type
            context['viewport_size'] = self.viewport
            context['is_mobile'] = self.is_mobile
            context['device_name'] = self.device_name
            context['user_agent'] = self.user_agent or page.evaluate("navigator.userAgent")
            
            # 设置默认超时
            if self.timeout:
                page.set_default_timeout(self.timeout * 1000)  # 转换为毫秒
                context['default_timeout'] = self.timeout
            
            # 初始化页面列表
            context['all_pages'] = [page]
            context['active_page_index'] = 0
            
            # 设置其他配置
            if self.geolocation:
                context['geolocation'] = self.geolocation
            if self.permissions:
                context['permissions'] = self.permissions
            if self.proxy:
                context['proxy'] = self.proxy
            if self.locale:
                context['locale'] = self.locale
            if self.timezone:
                context['timezone'] = self.timezone
            if self.color_scheme:
                context['color_scheme'] = self.color_scheme
                
            # 录制配置
            if self.record_video_dir:
                context['video_enabled'] = True
            if self.slow_mo:
                context['slow_mo'] = self.slow_mo
                
            # 安全配置
            context['ignore_https_errors'] = self.ignore_https_errors
            context['bypass_csp'] = self.bypass_csp
            context['offline'] = self.offline
            
            self.logger.info(f"成功连接 {self.browser_type} 浏览器")
            self.logger.info(f"视口大小: {self.viewport}")
            if self.device_name:
                self.logger.info(f"设备模拟: {self.device_name}")
            
            return browser
            
        except Exception as e:
            self.logger.error(f"连接浏览器失败: {e}")
            # 清理资源
            if hasattr(self, 'playwright') and self.playwright:
                try:
                    self.playwright.stop()
                except:
                    pass
            raise

    def cleanup(self, context: CONTEXT) -> None:
        """清理资源"""
        try:
            if 'browser' in context:
                browser = context['browser']
                if browser:
                    browser.close()
                    
            if hasattr(self, 'playwright') and self.playwright:
                self.playwright.stop()
                
        except Exception as e:
            self.logger.warning(f"清理浏览器资源时出错: {e}")