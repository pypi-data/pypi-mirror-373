#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
连接 Undetected Chrome 浏览器节点
"""

import os
import time
from typing import Optional, Dict, Any, List, Tuple

import undetected_chromedriver

try:
    import undetected_chromedriver as uc
except ImportError:
    uc = None

from rpaworkflow.node import DataStorageNode
from rpaworkflow.undetected_chromedriver.nodes.base import UndetectedChromeBaseNode
from rpaworkflow.undetected_chromedriver.workflow_context import CONTEXT


class ConnectBrowserNode(UndetectedChromeBaseNode, DataStorageNode):
    """连接 Undetected Chrome 浏览器节点

    使用 undetected-chromedriver 启动 Chrome 浏览器，具有反检测功能
    将浏览器驱动存储到上下文中
    """

    def __init__(self,
                 name: str = "连接Undetected Chrome",
                 description: str = "启动具有反检测功能的Chrome浏览器",
                 version_main: Optional[int] = None,
                 headless: bool = False,
                 user_data_dir: Optional[str] = None,
                 driver_executable_path: Optional[str] = None,
                 browser_executable_path: Optional[str] = None,
                 user_multi_procs: bool = False,
                 use_subprocess: bool = True,
                 debug: bool = False,
                 log_level: int = 0,
                 # 反检测配置
                 patcher_force_close: bool = False,
                 suppress_welcome: bool = True,
                 no_sandbox: bool = True,
                 # 代理配置
                 proxy_server: Optional[str] = None,
                 proxy_auth: Optional[Tuple[str, str]] = None,
                 # 窗口和显示配置
                 window_size: Optional[Tuple[int, int]] = None,
                 viewport_size: Optional[Tuple[int, int]] = None,
                 # 隐身和隐私配置
                 user_agent: Optional[str] = None,
                 timezone: Optional[str] = None,
                 language: Optional[str] = None,
                 geolocation: Optional[Tuple[float, float]] = None,
                 # 性能配置
                 disable_images: bool = False,
                 disable_javascript: bool = False,
                 disable_plugins: bool = False,
                 disable_notifications: bool = True,
                 # 扩展和偏好
                 extensions: Optional[List[str]] = None,
                 prefs: Optional[Dict[str, Any]] = None,
                 # 其他Chrome选项
                 chrome_options: Optional[List[str]] = None,
                 chrome_type = undetected_chromedriver.Chrome,
                 **kwargs):

        if uc is None:
            raise ImportError("需要安装 undetected-chromedriver: uv pip install undetected-chromedriver")

        super().__init__(name, description, output_key='driver', **kwargs)

        # 基础配置
        self.version_main = version_main
        self.headless = headless
        self.user_data_dir = user_data_dir
        self.driver_executable_path = driver_executable_path
        self.browser_executable_path = browser_executable_path
        self.user_multi_procs = user_multi_procs
        self.use_subprocess = use_subprocess
        self.debug = debug
        self.log_level = log_level

        # 反检测配置
        self.patcher_force_close = patcher_force_close
        self.suppress_welcome = suppress_welcome
        self.no_sandbox = no_sandbox

        # 代理配置
        self.proxy_server = proxy_server
        self.proxy_auth = proxy_auth

        # 窗口和显示配置
        self.window_size = window_size
        self.viewport_size = viewport_size

        # 隐身和隐私配置
        self.user_agent = user_agent
        self.timezone = timezone
        self.language = language
        self.geolocation = geolocation

        # 性能配置
        self.disable_images = disable_images
        self.disable_javascript = disable_javascript
        self.disable_plugins = disable_plugins
        self.disable_notifications = disable_notifications

        # 扩展和偏好
        self.extensions = extensions or []
        self.prefs = prefs or {}
        self.chrome_options = chrome_options or []
        self.chrome_type = chrome_type

    def _prepare_chrome_options(self) -> uc.ChromeOptions:
        """准备Chrome选项"""
        options = uc.ChromeOptions()

        # 禁用各种功能
        if self.disable_notifications:
            options.add_argument('--disable-notifications')
            options.add_argument('--disable-popup-blocking')

        if self.disable_images:
            self.prefs['profile.managed_default_content_settings.images'] = 2

        if self.disable_javascript:
            self.prefs['profile.managed_default_content_settings.javascript'] = 2

        if self.disable_plugins:
            options.add_argument('--disable-plugins')

        # 代理设置
        if self.proxy_server:
            options.add_argument(f'--proxy-server={self.proxy_server}')
            if self.proxy_auth:
                username, password = self.proxy_auth
                options.add_argument(f'--proxy-auth={username}:{password}')

        # 用户代理
        if self.user_agent:
            options.add_argument(f'--user-agent={self.user_agent}')

        # 语言设置
        if self.language:
            options.add_argument(f'--lang={self.language}')
            self.prefs['intl.accept_languages'] = self.language

        # 扩展
        for extension in self.extensions:
            if os.path.exists(extension):
                options.add_extension(extension)

        # 偏好设置
        if self.prefs:
            options.add_experimental_option('prefs', self.prefs)

        # 自定义Chrome选项
        for option in self.chrome_options:
            options.add_argument(option)

        return options

    def _create_driver(self) -> uc.Chrome:
        """创建 Undetected Chrome 驱动"""
        options = self._prepare_chrome_options()

        # 创建驱动
        driver = self.chrome_type(headless=self.headless,
                                  no_sandbox=self.no_sandbox,
                                  suppress_welcome=self.suppress_welcome,
                                  user_data_dir=self.user_data_dir,
                                  browser_executable_path=self.browser_executable_path,
                                  driver_executable_path=self.driver_executable_path,
                                  version_main=self.version_main,
                                  use_subprocess=self.use_subprocess,
                                  user_multi_procs=self.user_multi_procs,
                                  debug=self.debug,
                                  log_level=self.log_level,
                                  patcher_force_close=self.patcher_force_close,
                                  options=options)

        return driver

    def _apply_post_creation_settings(self, driver: uc.Chrome, context: CONTEXT) -> None:
        """应用创建后的设置"""
        # 设置窗口大小
        if self.window_size:
            driver.set_window_size(*self.window_size)
        else:
            driver.maximize_window()

        # 应用隐身设置
        self.apply_stealth_settings(context, driver)

        # 执行反检测脚本
        stealth_script = """
        Object.defineProperty(navigator, 'webdriver', {
            get: () => undefined,
        });

        Object.defineProperty(navigator, 'plugins', {
            get: () => [1, 2, 3, 4, 5],
        });

        Object.defineProperty(navigator, 'languages', {
            get: () => ['zh-CN', 'zh', 'en'],
        });

        window.chrome = {
            runtime: {},
        };

        Object.defineProperty(navigator, 'permissions', {
            get: () => ({
                query: () => Promise.resolve({ state: 'granted' }),
            }),
        });
        """

        try:
            driver.execute_script(stealth_script)
        except Exception as e:
            self.logger.warning(f"执行反检测脚本失败: {e}")

    def execute(self, context: CONTEXT) -> None:
        """执行浏览器连接

        Args:
            context: 工作流上下文
        """
        try:
            # 创建驱动
            driver = self._create_driver()

            # 等待驱动完全启动
            time.sleep(2)

            # 存储配置到上下文
            context['undetected_version'] = self.version_main
            context['user_multi_procs'] = self.user_multi_procs
            context['use_subprocess'] = self.use_subprocess
            context['debug'] = self.debug
            context['driver_executable_path'] = self.driver_executable_path
            context['browser_executable_path'] = self.browser_executable_path
            context['log_level'] = self.log_level

            # 反检测配置
            context['patcher_force_close'] = self.patcher_force_close
            context['suppress_welcome'] = self.suppress_welcome
            context['no_sandbox'] = self.no_sandbox
            context['detection_evasion_enabled'] = True
            context['stealth_mode'] = True

            # 代理配置
            context['proxy_server'] = self.proxy_server
            context['proxy_auth'] = self.proxy_auth

            # 扩展和插件
            context['extensions'] = self.extensions
            context['prefs'] = self.prefs

            # 性能和资源配置
            context['disable_images'] = self.disable_images
            context['disable_javascript'] = self.disable_javascript
            context['disable_plugins'] = self.disable_plugins
            context['disable_notifications'] = self.disable_notifications

            # 指纹和隐私配置
            context['user_agent'] = self.user_agent
            context['viewport_size'] = self.viewport_size
            context['timezone'] = self.timezone
            context['language'] = self.language
            context['geolocation'] = self.geolocation

            # 应用创建后设置
            self._apply_post_creation_settings(driver, context)

            # 获取浏览器信息
            capabilities = driver.capabilities
            browser_name = capabilities.get('browserName', 'Chrome')
            browser_version = capabilities.get('browserVersion', 'Unknown')

            self.logger.info(f"Undetected Chrome 连接成功: {browser_name} {browser_version}")
            self.logger.info(f"反检测功能已启用，隐身模式: {context.get('stealth_mode', False)}")

            # 存储浏览器信息到上下文
            context['browser_type'] = 'undetected_chromedriver'
            context['window_size'] = driver.get_window_size()

            # 存储驱动到指定键
            self.store_data(context, driver)

        except Exception as e:
            self.logger.error(f"连接 Undetected Chrome 失败: {e}")
            raise
