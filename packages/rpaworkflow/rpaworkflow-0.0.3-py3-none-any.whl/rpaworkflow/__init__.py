# -*- coding: utf-8 -*-
"""Workflow 包

这个包提供了工作流管理和节点执行的核心功能。

可用模块:
- rpaworkflow.selenium: 基于 Selenium 的 Web 自动化模块
- rpaworkflow.uiautomator2: 基于 UIAutomator2 的 Android 自动化模块  
- rpaworkflow.undetected_chromedriver: 基于 undetected-chromedriver 的反检测 Web 自动化模块
- rpaworkflow.playwright: 基于 Playwright 的现代 Web 自动化模块
- rpaworkflow.drissionpage: 基于 DrissionPage 的多功能 Web 自动化模块

使用示例:
    # Selenium Web 自动化
    from rpaworkflow.selenium import ConnectBrowserNode, NavigateNode
    
    # Android 自动化
    from rpaworkflow.uiautomator2 import ConnectDeviceNode, ClickNode
    
    # 反检测 Web 自动化
    from rpaworkflow.undetected_chromedriver import ConnectUndetectedChromeNode
    
    # Playwright 现代 Web 自动化
    from rpaworkflow.playwright import ConnectBrowserNode, ClickNode
    
    # DrissionPage 多功能 Web 自动化
    from rpaworkflow.drissionpage import ConnectPageNode, NavigateNode, ClickNode
"""

from .manager import WorkflowManager
from .func import or_, and_

# 导入所有通用节点类
from .nodes import (
    WaitTimeNode,
    LambdaActionNode,
    LambdaDataStorageNode,
)

__all__ = [
    'WorkflowManager',
    # 通用节点
    'WaitTimeNode',
    'LambdaActionNode',
    'LambdaDataStorageNode',
    # 通用函数
    'or_',
    'and_'
]

__version__ = '0.0.0' # 使用动态版本
__author__ = 'dragons96'
