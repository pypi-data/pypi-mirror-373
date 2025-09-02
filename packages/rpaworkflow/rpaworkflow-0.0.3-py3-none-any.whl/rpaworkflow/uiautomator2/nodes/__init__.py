# -*- coding: utf-8 -*-
"""
U2 通用操作节点包

这个包提供了基于 uiautomator2 的通用操作节点，可以用于任何 Android 应用的自动化。
不特定于抖音，可以复用于其他应用的自动化工作流。
"""

from .base import U2BaseNode
from .connect_device import ConnectDeviceNode
from .launch_app import LaunchAppNode
from .stop_app import StopAppNode
from .click import ClickNode
from .swipe import SwipeNode
from .input_text import InputTextNode
from .wait import WaitNode
from .screenshot import ScreenshotNode
from .key_event import KeyEventNode
from .check_element import CheckElementNode
from .get_text import GetTextNode
from .scroll import ScrollNode

__all__ = [
    'U2BaseNode',
    'ConnectDeviceNode',
    'LaunchAppNode',
    'StopAppNode',
    'ClickNode',
    'SwipeNode',
    'InputTextNode',
    'WaitNode',
    'ScreenshotNode',
    'KeyEventNode',
    'CheckElementNode',
    'GetTextNode',
    'ScrollNode',
]

# 版本信息
__version__ = '0.0.0' # 使用动态版本
__author__ = 'dragons96'
