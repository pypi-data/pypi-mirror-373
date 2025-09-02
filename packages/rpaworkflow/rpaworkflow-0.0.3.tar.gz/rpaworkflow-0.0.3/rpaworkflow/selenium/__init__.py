from .nodes import *
from .workflow_context import WorkflowSeleniumContext, CONTEXT

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
    'WorkflowSeleniumContext',
    'CONTEXT',
]

# 版本信息
__version__ = '0.0.0' # 使用动态版本
__author__ = 'dragons96'