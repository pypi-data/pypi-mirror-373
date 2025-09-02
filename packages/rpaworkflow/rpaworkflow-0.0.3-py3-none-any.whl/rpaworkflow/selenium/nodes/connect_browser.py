#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
连接浏览器节点
"""
import os

from typing import Optional, Dict, Any

from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.edge.options import Options as EdgeOptions
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.safari.options import Options as SafariOptions

from rpaworkflow.node import DataStorageNode
from rpaworkflow.selenium.nodes.base import SeleniumBaseNode
from rpaworkflow.selenium.workflow_context import CONTEXT


class ConnectBrowserNode(SeleniumBaseNode, DataStorageNode):
    """连接浏览器节点

    用于启动浏览器并获取驱动
    将浏览器驱动存储到上下文中
    """

    def __init__(self,
                 name: str = "连接浏览器",
                 description: str = "启动浏览器并获取驱动",
                 browser_type: str = "chrome",
                 headless: bool = False,
                 window_size: Optional[tuple] = None,
                 user_data_dir: Optional[str] = None,
                 driver_executable_path: Optional[str] = None,
                 browser_executable_path: Optional[str] = None,
                 options: Optional[Dict[str, Any]] = None,
                 **kwargs):
        super().__init__(name, description, output_key='driver', **kwargs)
        self.browser_type = browser_type.lower()
        self.headless = headless
        self.window_size = window_size
        self.user_data_dir = user_data_dir
        self.browser_path = browser_executable_path
        self.executable_path = driver_executable_path
        self.options = options or {}

    def _create_chrome_driver(self) -> webdriver.Chrome:
        """创建Chrome驱动"""
        chrome_options = ChromeOptions()
        
        if self.headless:
            chrome_options.add_argument('--headless')
        
        if self.user_data_dir:
            chrome_options.add_argument(f'--user-data-dir={self.user_data_dir}')
        
        # 添加常用选项
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        
        # 添加自定义选项
        for key, value in self.options.items():
            if isinstance(value, bool) and value:
                chrome_options.add_argument(f'--{key}')
            elif value:
                chrome_options.add_argument(f'--{key}={value}')

        if self.browser_path:
            chrome_options.binary_location = self.browser_path

        if self.executable_path:
            return webdriver.Chrome(service=webdriver.ChromeService(
                executable_path=self.executable_path,
            ), options=chrome_options)
        else:
            return webdriver.Chrome(options=chrome_options)

    def _create_firefox_driver(self) -> webdriver.Firefox:
        """创建Firefox驱动"""
        firefox_options = FirefoxOptions()
        
        if self.headless:
            firefox_options.add_argument('--headless')
        
        # 添加自定义选项
        for key, value in self.options.items():
            if isinstance(value, bool) and value:
                firefox_options.add_argument(f'--{key}')
            elif value:
                firefox_options.add_argument(f'--{key}={value}')

        if self.browser_path:
            firefox_options.binary_location = self.browser_path

        if self.executable_path:
            return webdriver.Firefox(service=webdriver.FirefoxService(
                executable_path=self.executable_path,
            ), options=firefox_options)
        else:
            return webdriver.Firefox(options=firefox_options)

    def _create_edge_driver(self) -> webdriver.Edge:
        """创建Edge驱动"""
        edge_options = EdgeOptions()
        
        if self.headless:
            edge_options.add_argument('--headless')
        
        if self.user_data_dir:
            edge_options.add_argument(f'--user-data-dir={self.user_data_dir}')
        
        # 添加常用选项
        edge_options.add_argument('--no-sandbox')
        edge_options.add_argument('--disable-dev-shm-usage')
        edge_options.add_argument('--disable-gpu')
        
        # 添加自定义选项
        for key, value in self.options.items():
            if isinstance(value, bool) and value:
                edge_options.add_argument(f'--{key}')
            elif value:
                edge_options.add_argument(f'--{key}={value}')

        if self.browser_path:
            edge_options.binary_location = self.browser_path

        if self.executable_path:
            return webdriver.Edge(service=webdriver.EdgeService(
                executable_path=self.executable_path,
            ), options=edge_options)
        else:
            return webdriver.Edge(options=edge_options)

    def _create_safari_driver(self) -> webdriver.Safari:
        """创建Safari驱动"""

        safari_options = SafariOptions()

        if self.browser_path:
            safari_options.binary_location = self.browser_path

        if self.executable_path:
            return webdriver.Safari(service=webdriver.SafariService(
                executable_path=self.executable_path,
            ), options=safari_options)
        else:
            return webdriver.Safari(options=safari_options)

    def execute(self, context: CONTEXT) -> None:
        """执行浏览器连接

        Args:
            context: 工作流上下文
        """
        # 根据浏览器类型创建驱动
        if self.browser_type == "chrome":
            driver = self._create_chrome_driver()
        elif self.browser_type == "firefox":
            driver = self._create_firefox_driver()
        elif self.browser_type == "edge":
            driver = self._create_edge_driver()
        elif self.browser_type == "safari":
            driver = self._create_safari_driver()
        else:
            raise ValueError(f"不支持的浏览器类型: {self.browser_type}")
        
        # 设置窗口大小
        if self.window_size:
            driver.set_window_size(*self.window_size)
        else:
            driver.maximize_window()
        
        # 获取浏览器信息
        capabilities = driver.capabilities
        browser_name = capabilities.get('browserName', 'Unknown')
        browser_version = capabilities.get('browserVersion', 'Unknown')
        
        self.logger.info(f"浏览器连接成功: {browser_name} {browser_version}")
        
        # 存储浏览器信息到上下文
        context['browser_type'] = self.browser_type
        context['window_size'] = driver.get_window_size()
        
        # 存储驱动到指定键
        self.store_data(context, driver)