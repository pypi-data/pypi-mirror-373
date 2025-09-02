#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DrissionPage 模块

提供基于DrissionPage的RPA工作流节点。

DrissionPage是一个强大的网页自动化工具，支持:
- ChromiumPage: 基于Chromium的页面操作
- SessionPage: 基于requests的HTTP会话
- WebPage: 结合两者优势的混合模式

本模块参考Selenium模块的设计风格，提供了完整的DrissionPage节点集合。
"""

# 导入工作流上下文
from .workflow_context import WorkflowDrissionPageContext

# 导入基础节点
from .nodes.base import DrissionPageBaseNode

# 导入所有功能节点
from .nodes import (
    # 连接和页面管理节点
    ConnectPageNode,
    ConnectExistingPageNode,
    SwitchTabNode,
    
    # 导航节点
    NavigateNode,
    RefreshNode,
    BackNode,
    ForwardNode,
    NewTabNode,
    NavigateCloseTabNode,
    
    # 点击节点
    ClickNode,
    ClickByCoordinateNode,
    HoverNode,
    DragAndDropNode,
    
    # 输入文本节点
    InputTextNode,
    ClearTextNode,
    SelectTextNode,
    UploadFileNode,
    
    # 等待节点
    WaitNode,
    WaitForElementNode,
    WaitForPageLoadNode,
    WaitForUrlNode,
    WaitForTitleNode,
    
    # 获取文本和信息节点
    GetTextNode,
    GetAllTextNode,
    GetAttributeNode,
    GetPageInfoNode,
    GetElementInfoNode,
    
    # 截图和录制节点
    ScreenshotNode,
    ElementScreenshotNode,
    RecordVideoNode,
    
    # 滚动节点
    ScrollNode,
    ScrollToElementNode,
    ScrollElementNode,
    WheelScrollNode,
    
    # 元素检查节点
    CheckElementExistsNode,
    CheckElementVisibleNode,
    CheckElementEnabledNode,
    CheckElementTextNode,
    CheckElementAttributeNode,
    CheckElementCountNode,
    
    # 表单操作节点
    SelectOptionNode,
    CheckboxNode,
    RadioButtonNode,
    SubmitFormNode,
    ResetFormNode,
    
    # 关闭页面节点
    ClosePageNode,
    CloseTabNode,
    QuitBrowserNode
)

# 创建默认上下文实例
CONTEXT = WorkflowDrissionPageContext()

# 导出所有公共接口
__all__ = [
    # 上下文
    'WorkflowDrissionPageContext',
    'CONTEXT',
    
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

# 模块级别的文档字符串
__doc__ = """
DrissionPage RPA Workflow 模块

这个模块为RPA Workflow框架提供了完整的DrissionPage节点集合。
DrissionPage是一个功能强大的网页自动化工具，支持多种操作模式:

1. ChromiumPage: 基于Chromium浏览器的页面操作
   - 支持JavaScript执行
   - 支持复杂的用户交互
   - 支持截图和录制
   - 适合需要完整浏览器功能的场景

2. SessionPage: 基于requests的HTTP会话
   - 高性能的HTTP请求
   - 适合API调用和数据抓取
   - 不需要浏览器界面
   - 适合批量数据处理

3. WebPage: 混合模式
   - 结合ChromiumPage和SessionPage的优势
   - 可以在两种模式间切换
   - 灵活适应不同场景需求

使用示例:

```python
from rpaworkflow.drissionpage import (
    ConnectPageNode,
    NavigateNode,
    ClickNode,
    InputTextNode,
    GetTextNode,
    ScreenshotNode,
    ClosePageNode,
    CONTEXT
)

# 创建工作流
workflow = [
    ConnectPageNode(page_type='chromium'),
    NavigateNode(url='https://example.com'),
    ClickNode(by_css='#login-button'),
    InputTextNode(by_css='#username', text='user'),
    InputTextNode(by_css='#password', text='pass'),
    ClickNode(by_css='#submit'),
    GetTextNode(by_css='.welcome-message'),
    ScreenshotNode(save_path='result.png'),
    ClosePageNode()
]

# 执行工作流
for node in workflow:
    result = node.execute(CONTEXT)
    print(f"{node.name}: {result['message']}")
```

节点分类:

1. 连接和页面管理:
   - ConnectPageNode: 创建页面连接
   - ConnectExistingPageNode: 连接现有页面
   - SwitchTabNode: 切换标签页

2. 导航操作:
   - NavigateNode: 导航到URL
   - RefreshNode: 刷新页面
   - BackNode/ForwardNode: 前进后退
   - NewTabNode: 新建标签页

3. 元素交互:
   - ClickNode: 点击元素
   - InputTextNode: 输入文本
   - HoverNode: 鼠标悬停
   - DragAndDropNode: 拖拽操作

4. 信息获取:
   - GetTextNode: 获取文本
   - GetAttributeNode: 获取属性
   - GetPageInfoNode: 获取页面信息

5. 等待和检查:
   - WaitNode: 等待时间
   - WaitForElementNode: 等待元素
   - CheckElementExistsNode: 检查元素存在

6. 表单操作:
   - SelectOptionNode: 选择下拉选项
   - CheckboxNode: 复选框操作
   - SubmitFormNode: 提交表单

7. 截图和录制:
   - ScreenshotNode: 页面截图
   - ElementScreenshotNode: 元素截图
   - RecordVideoNode: 录制视频

8. 页面管理:
   - ClosePageNode: 关闭页面
   - QuitBrowserNode: 退出浏览器

所有节点都继承自DrissionPageBaseNode，提供统一的接口和错误处理机制。
"""