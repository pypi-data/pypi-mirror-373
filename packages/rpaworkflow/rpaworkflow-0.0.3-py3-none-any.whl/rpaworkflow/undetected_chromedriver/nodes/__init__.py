#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Undetected Chrome 操作节点包

这个包提供了基于 undetected-chromedriver 的操作节点，具有反检测功能。
大部分通用操作节点直接从 selenium 模块导入，只实现 undetected-chromedriver 特有的功能。
"""

# Undetected Chrome 特有节点
from .base import UndetectedChromeBaseNode
from .connect_browser import ConnectBrowserNode

# 从 Selenium 模块导入通用操作节点
try:
    from rpaworkflow.selenium.nodes import (
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
except ImportError:
    # 如果 selenium 模块不可用，定义空的类以避免导入错误
    class NavigateNode:
        def __init__(self, *args, **kwargs):
            raise ImportError("需要安装 selenium 模块才能使用通用操作节点")
    
    class ClickNode:
        def __init__(self, *args, **kwargs):
            raise ImportError("需要安装 selenium 模块才能使用通用操作节点")
    
    class InputTextNode:
        def __init__(self, *args, **kwargs):
            raise ImportError("需要安装 selenium 模块才能使用通用操作节点")
    
    class WaitNode:
        def __init__(self, *args, **kwargs):
            raise ImportError("需要安装 selenium 模块才能使用通用操作节点")
    
    class ScreenshotNode:
        def __init__(self, *args, **kwargs):
            raise ImportError("需要安装 selenium 模块才能使用通用操作节点")
    
    class GetTextNode:
        def __init__(self, *args, **kwargs):
            raise ImportError("需要安装 selenium 模块才能使用通用操作节点")
    
    class ScrollNode:
        def __init__(self, *args, **kwargs):
            raise ImportError("需要安装 selenium 模块才能使用通用操作节点")
    
    class CheckElementNode:
        def __init__(self, *args, **kwargs):
            raise ImportError("需要安装 selenium 模块才能使用通用操作节点")
    
    class CloseBrowserNode:
        def __init__(self, *args, **kwargs):
            raise ImportError("需要安装 selenium 模块才能使用通用操作节点")


__all__ = [
    # Undetected Chrome 特有节点
    'UndetectedChromeBaseNode',
    'ConnectBrowserNode',
    
    # 从 Selenium 导入的通用节点
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