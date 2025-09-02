#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Undetected Chrome 自动化模块

基于 undetected-chromedriver 的 Web 自动化模块，具有反检测功能。
提供了完整的浏览器自动化操作节点，可以绕过大多数反爬虫检测。

主要特性:
- 反检测功能，绕过 Cloudflare、reCAPTCHA 等
- 完整的浏览器操作支持
- 隐身模式和指纹伪装
- 代理支持
- 扩展和插件管理
- 性能优化选项

使用示例:
    from rpaworkflow.undetected_chromedriver import (
        ConnectUndetectedChromeNode,
        NavigateNode,
        ClickNode,
        WorkflowUndetectedChromeContext
    )
    
    # 创建工作流上下文
    context = WorkflowUndetectedChromeContext()
    
    # 连接浏览器
    connect_node = ConnectUndetectedChromeNode(
        headless=False,
        suppress_welcome=True,
        no_sandbox=True
    )
    connect_node.execute(context)
    
    # 导航到页面
    navigate_node = NavigateNode(url="https://example.com")
    navigate_node.execute(context)
"""

# 导入上下文
from .workflow_context import WorkflowUndetectedChromeContext, CONTEXT

# 导入所有节点
from .nodes import (
    # Undetected Chrome 特有节点
    UndetectedChromeBaseNode,
    ConnectBrowserNode,
    
    # 从 Selenium 导入的通用节点
    NavigateNode,
    ClickNode,
    InputTextNode,
    WaitNode,
    ScreenshotNode,
    GetTextNode,
    ScrollNode,
    CheckElementNode,
    CloseBrowserNode,
)

__all__ = [
    # 上下文
    'WorkflowUndetectedChromeContext',
    'CONTEXT',
    
    # Undetected Chrome 特有节点
    'UndetectedChromeBaseNode',
    'ConnectBrowserNode',
    
    # 通用操作节点（从 Selenium 导入）
    'NavigateNode',
    'ClickNode',
    'InputTextNode',
    'WaitNode',
    'ScreenshotNode',
    'GetTextNode',
    'ScrollNode',
    'CheckElementNode',
    'CloseBrowserNode',
]

# 版本信息
__version__ = '0.0.0' # 使用动态版本
__author__ = 'dragons96'
__description__ = 'Undetected Chrome automation module with anti-detection capabilities'

# 检查依赖
try:
    import undetected_chromedriver
except ImportError:
    import warnings
    warnings.warn(
        "undetected-chromedriver 未安装。请运行: uv pip install undetected-chromedriver",
        ImportWarning
    )

try:
    import selenium
except ImportError:
    import warnings
    warnings.warn(
        "selenium 未安装。请运行: uv pip install selenium",
        ImportWarning
    )