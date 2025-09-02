#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
工作流u2上下文定义
"""

import uiautomator2
from typing import Optional, Dict, Any, TypeVar

from rpaworkflow.context import WorkflowContext


class WorkflowU2Context(WorkflowContext, total=False):
    # === 设备相关 ===
    device: Optional[uiautomator2.Device]  # 设备
    device_id: Optional[str]  # 设备ID
    screen_size: Optional[tuple]  # 屏幕尺寸

    # === UI自动化相关 ===
    last_screenshot: Optional[str]  # 最后一次截图路径
    last_element: Optional[Dict[str, Any]]  # 最后操作的元素信息
    last_text: Optional[str]  # 最后获取的文本
    last_click_position: Optional[tuple]  # 最后点击位置

    # === 应用相关 ===
    current_app: Optional[str]  # 当前应用包名
    app_version: Optional[str]  # 应用版本
    app_state: Optional[str]  # 应用状态


CONTEXT = TypeVar("CONTEXT", bound=WorkflowU2Context)
