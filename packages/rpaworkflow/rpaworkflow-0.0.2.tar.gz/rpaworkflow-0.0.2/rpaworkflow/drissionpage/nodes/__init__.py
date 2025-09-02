#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DrissionPage 节点模块

导出所有DrissionPage相关的节点类。
"""

# 基础节点
from .base import DrissionPageBaseNode

# 连接和页面管理节点
from .connect_page import (
    ConnectPageNode,
    ConnectExistingPageNode,
    SwitchTabNode
)

# 导航节点
from .navigate import (
    NavigateNode,
    RefreshNode,
    BackNode,
    ForwardNode,
    NewTabNode,
    CloseTabNode as NavigateCloseTabNode  # 避免与close_page中的重名
)

# 点击节点
from .click import (
    ClickNode,
    ClickByCoordinateNode,
    HoverNode,
    DragAndDropNode
)

# 输入文本节点
from .input_text import (
    InputTextNode,
    ClearTextNode,
    SelectTextNode,
    UploadFileNode
)

# 等待节点
from .wait import (
    WaitNode,
    WaitForElementNode,
    WaitForPageLoadNode,
    WaitForUrlNode,
    WaitForTitleNode
)

# 获取文本和信息节点
from .get_text import (
    GetTextNode,
    GetAllTextNode,
    GetAttributeNode,
    GetPageInfoNode,
    GetElementInfoNode
)

# 截图和录制节点
from .screenshot import (
    ScreenshotNode,
    ElementScreenshotNode,
    RecordVideoNode
)

# 滚动节点
from .scroll import (
    ScrollNode,
    ScrollToElementNode,
    ScrollElementNode,
    WheelScrollNode
)

# 元素检查节点
from .check_element import (
    CheckElementExistsNode,
    CheckElementVisibleNode,
    CheckElementEnabledNode,
    CheckElementTextNode,
    CheckElementAttributeNode,
    CheckElementCountNode
)

# 表单操作节点
from .form import (
    SelectOptionNode,
    CheckboxNode,
    RadioButtonNode,
    SubmitFormNode,
    ResetFormNode
)

# 关闭页面节点
from .close_page import (
    ClosePageNode,
    CloseTabNode,
    QuitBrowserNode
)

# 导出所有节点类
__all__ = [
    # 基础节点
    'DrissionPageBaseNode',
    
    # 连接和页面管理节点
    'ConnectPageNode',
    'ConnectExistingPageNode',
    'SwitchTabNode',
    
    # 导航节点
    'NavigateNode',
    'RefreshNode',
    'BackNode',
    'ForwardNode',
    'NewTabNode',
    'NavigateCloseTabNode',
    
    # 点击节点
    'ClickNode',
    'ClickByCoordinateNode',
    'HoverNode',
    'DragAndDropNode',
    
    # 输入文本节点
    'InputTextNode',
    'ClearTextNode',
    'SelectTextNode',
    'UploadFileNode',
    
    # 等待节点
    'WaitNode',
    'WaitForElementNode',
    'WaitForPageLoadNode',
    'WaitForUrlNode',
    'WaitForTitleNode',
    
    # 获取文本和信息节点
    'GetTextNode',
    'GetAllTextNode',
    'GetAttributeNode',
    'GetPageInfoNode',
    'GetElementInfoNode',
    
    # 截图和录制节点
    'ScreenshotNode',
    'ElementScreenshotNode',
    'RecordVideoNode',
    
    # 滚动节点
    'ScrollNode',
    'ScrollToElementNode',
    'ScrollElementNode',
    'WheelScrollNode',
    
    # 元素检查节点
    'CheckElementExistsNode',
    'CheckElementVisibleNode',
    'CheckElementEnabledNode',
    'CheckElementTextNode',
    'CheckElementAttributeNode',
    'CheckElementCountNode',
    
    # 表单操作节点
    'SelectOptionNode',
    'CheckboxNode',
    'RadioButtonNode',
    'SubmitFormNode',
    'ResetFormNode',
    
    # 关闭页面节点
    'ClosePageNode',
    'CloseTabNode',
    'QuitBrowserNode'
]

# 版本信息
__version__ = '0.0.0' # 使用动态版本
__author__ = 'dragons96'
__description__ = 'DrissionPage nodes for RPA Workflow framework'
