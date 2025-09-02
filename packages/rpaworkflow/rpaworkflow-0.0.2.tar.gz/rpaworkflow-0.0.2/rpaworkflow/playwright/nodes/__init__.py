#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Playwright节点模块

包含所有Playwright相关的工作流节点实现。
"""

# 基础节点
from .base import PlaywrightBaseNode

# 浏览器连接
from .connect_browser import ConnectBrowserNode

# 导航操作
from .navigate import (
    NavigateNode,
    WaitForNavigationNode,
    SetViewportNode
)

# 点击操作
from .click import (
    ClickNode,
    DoubleClickNode,
    RightClickNode,
    HoverNode
)

# 文本输入
from .input_text import (
    InputTextNode,
    TypeTextNode,
    KeyboardInputNode,
    ClearInputNode
)

# 等待操作
from .wait import (
    WaitNode,
    WaitForTimeoutNode,
    WaitForLoadStateNode,
    WaitForFunctionNode,
    WaitForResponseNode,
    WaitForRequestNode
)

# 截图录制
from .screenshot import (
    ScreenshotNode,
    PDFNode,
    VideoRecordingNode
)

# 文本获取
from .get_text import (
    GetTextNode,
    GetAllTextNode,
    GetAttributeNode,
    GetValueNode,
    GetPageInfoNode,
    GetElementCountNode
)

# 滚动操作
from .scroll import (
    ScrollNode,
    ScrollToTopNode,
    ScrollToBottomNode,
    ScrollByNode,
    GetScrollPositionNode,
    ScrollIntoViewNode
)

# 元素检查
from .element_check import (
    ElementExistsNode,
    ElementVisibleNode,
    ElementEnabledNode,
    ElementCheckedNode,
    ElementTextContainsNode,
    ElementAttributeNode,
    AssertElementNode
)

# 浏览器关闭
from .close_browser import (
    CloseBrowserNode,
    ClosePageNode,
    SwitchToPageNode,
    NewPageNode,
    GetPagesInfoNode
)

__all__ = [
    # 基础
    'PlaywrightBaseNode',
    
    # 浏览器管理
    'ConnectBrowserNode',
    'CloseBrowserNode',
    'ClosePageNode',
    'SwitchToPageNode',
    'NewPageNode',
    'GetPagesInfoNode',
    
    # 导航
    'NavigateNode',
    'WaitForNavigationNode',
    'SetViewportNode',
    
    # 交互
    'ClickNode',
    'DoubleClickNode',
    'RightClickNode',
    'HoverNode',
    
    # 输入
    'InputTextNode',
    'TypeTextNode',
    'KeyboardInputNode',
    'ClearInputNode',
    
    # 等待
    'WaitNode',
    'WaitForTimeoutNode',
    'WaitForLoadStateNode',
    'WaitForFunctionNode',
    'WaitForResponseNode',
    'WaitForRequestNode',
    
    # 截图
    'ScreenshotNode',
    'PDFNode',
    'VideoRecordingNode',
    
    # 获取
    'GetTextNode',
    'GetAllTextNode',
    'GetAttributeNode',
    'GetValueNode',
    'GetPageInfoNode',
    'GetElementCountNode',
    
    # 滚动
    'ScrollNode',
    'ScrollToTopNode',
    'ScrollToBottomNode',
    'ScrollByNode',
    'GetScrollPositionNode',
    'ScrollIntoViewNode',
    
    # 检查
    'ElementExistsNode',
    'ElementVisibleNode',
    'ElementEnabledNode',
    'ElementCheckedNode',
    'ElementTextContainsNode',
    'ElementAttributeNode',
    'AssertElementNode',
]

# 版本信息
__version__ = '0.0.0' # 使用动态版本
__author__ = 'dragons96'
__description__ = 'Playwright nodes for RPA Workflow framework'
