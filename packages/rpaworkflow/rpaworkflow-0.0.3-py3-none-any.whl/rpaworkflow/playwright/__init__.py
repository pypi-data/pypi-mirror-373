#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Playwright工作流模块

本模块提供基于Playwright的Web自动化工作流节点，支持现代Web应用的自动化测试和操作。

Playwright特点：
- 支持多种浏览器：Chromium、Firefox、WebKit
- 现代Web应用支持：SPA、PWA等
- 强大的等待机制：自动等待元素可用
- 丰富的定位方式：CSS选择器、文本、角色、标签等
- 移动端支持：设备模拟、触摸操作
- 网络拦截：请求/响应监控和修改
- 视频录制：自动录制操作过程
- 并行执行：多浏览器并行测试

主要节点类型：
1. 浏览器管理：ConnectBrowserNode, CloseBrowserNode
2. 页面导航：NavigateNode, WaitForNavigationNode
3. 元素操作：ClickNode, InputTextNode, HoverNode
4. 等待机制：WaitNode, WaitForTimeoutNode
5. 信息获取：GetTextNode, GetAttributeNode
6. 截图录制：ScreenshotNode, VideoRecordingNode
7. 元素检查：ElementExistsNode, AssertElementNode
8. 页面滚动：ScrollNode, ScrollToTopNode

使用示例：
```python
from rpaworkflow.playwright import (
    ConnectBrowserNode, NavigateNode, ClickNode, 
    InputTextNode, ScreenshotNode, CloseBrowserNode
)
from rpaworkflow import WorkflowManager

# 创建工作流
workflow = WorkflowManager()

# 添加节点
workflow.add_node(ConnectBrowserNode(browser_type="chromium"))
workflow.add_node(NavigateNode(url="https://example.com"))
workflow.add_node(ClickNode(selector="#login-button"))
workflow.add_node(InputTextNode(selector="#username", text="user"))
workflow.add_node(ScreenshotNode(file_path="result.png"))
workflow.add_node(CloseBrowserNode())

# 执行工作流
workflow.run()
```
"""

# 工作流上下文
from .workflow_context import WorkflowPlaywrightContext, CONTEXT

# 基础节点
from .nodes.base import PlaywrightBaseNode

# 浏览器连接节点
from .nodes.connect_browser import ConnectBrowserNode

# 导航节点
from .nodes.navigate import (
    NavigateNode,
    WaitForNavigationNode,
    SetViewportNode
)

# 点击节点
from .nodes.click import (
    ClickNode,
    DoubleClickNode,
    RightClickNode,
    HoverNode
)

# 输入文本节点
from .nodes.input_text import (
    InputTextNode,
    TypeTextNode,
    KeyboardInputNode,
    ClearInputNode
)

# 等待节点
from .nodes.wait import (
    WaitNode,
    WaitForTimeoutNode,
    WaitForLoadStateNode,
    WaitForFunctionNode,
    WaitForResponseNode,
    WaitForRequestNode
)

# 截图节点
from .nodes.screenshot import (
    ScreenshotNode,
    PDFNode,
    VideoRecordingNode
)

# 获取文本节点
from .nodes.get_text import (
    GetTextNode,
    GetAllTextNode,
    GetAttributeNode,
    GetValueNode,
    GetPageInfoNode,
    GetElementCountNode
)

# 滚动节点
from .nodes.scroll import (
    ScrollNode,
    ScrollToTopNode,
    ScrollToBottomNode,
    ScrollByNode,
    GetScrollPositionNode,
    ScrollIntoViewNode
)

# 元素检查节点
from .nodes.element_check import (
    ElementExistsNode,
    ElementVisibleNode,
    ElementEnabledNode,
    ElementCheckedNode,
    ElementTextContainsNode,
    ElementAttributeNode,
    AssertElementNode
)

# 关闭浏览器节点
from .nodes.close_browser import (
    CloseBrowserNode,
    ClosePageNode,
    SwitchToPageNode,
    NewPageNode,
    GetPagesInfoNode
)

# 导出所有公共类
__all__ = [
    # 上下文
    'WorkflowPlaywrightContext',
    'CONTEXT',
    
    # 基础节点
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
    
    # 交互操作
    'ClickNode',
    'DoubleClickNode',
    'RightClickNode',
    'HoverNode',
    
    # 文本输入
    'InputTextNode',
    'TypeTextNode',
    'KeyboardInputNode',
    'ClearInputNode',
    
    # 等待机制
    'WaitNode',
    'WaitForTimeoutNode',
    'WaitForLoadStateNode',
    'WaitForFunctionNode',
    'WaitForResponseNode',
    'WaitForRequestNode',
    
    # 截图录制
    'ScreenshotNode',
    'PDFNode',
    'VideoRecordingNode',
    
    # 信息获取
    'GetTextNode',
    'GetAllTextNode',
    'GetAttributeNode',
    'GetValueNode',
    'GetPageInfoNode',
    'GetElementCountNode',
    
    # 页面滚动
    'ScrollNode',
    'ScrollToTopNode',
    'ScrollToBottomNode',
    'ScrollByNode',
    'GetScrollPositionNode',
    'ScrollIntoViewNode',
    
    # 元素检查
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
