# -*- coding: utf-8 -*-
"""
Selenium 通用操作节点包

这个包提供了基于 Selenium 的通用操作节点，可以用于任何 Web 应用的自动化。
不特定于某个网站，可以复用于其他Web应用的自动化工作流。
"""

from .base import SeleniumBaseNode
from .connect_browser import ConnectBrowserNode
from .navigate import NavigateNode
from .click import ClickNode
from .input_text import InputTextNode
from .wait import WaitNode
from .screenshot import ScreenshotNode
from .get_text import GetTextNode
from .scroll import ScrollNode
from .check_element import CheckElementNode
from .close_browser import CloseBrowserNode

__all__ = [
    'SeleniumBaseNode',
    'ConnectBrowserNode',
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