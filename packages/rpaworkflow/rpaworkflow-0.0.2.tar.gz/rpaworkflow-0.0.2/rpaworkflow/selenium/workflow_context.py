#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
工作流selenium上下文定义
"""

from selenium import webdriver
from selenium.webdriver.remote.webelement import WebElement
from typing import Optional, Dict, Any, TypeVar, List

from rpaworkflow.context import WorkflowContext


class WorkflowSeleniumContext(WorkflowContext, total=False):
    # === 浏览器相关 ===
    driver: Optional[webdriver.Chrome | webdriver.Firefox | webdriver.Edge | webdriver.Safari]  # 浏览器驱动
    browser_type: Optional[str]  # 浏览器类型
    window_size: Optional[tuple]  # 窗口尺寸
    current_url: Optional[str]  # 当前URL
    page_title: Optional[str]  # 页面标题
    
    # === 元素相关 ===
    last_element: Optional[WebElement]  # 最后操作的元素
    last_elements: Optional[List[WebElement]]  # 最后查找的元素列表
    last_text: Optional[str]  # 最后获取的文本
    last_attribute: Optional[str]  # 最后获取的属性值
    last_screenshot: Optional[str]  # 最后一次截图路径
    
    # === 操作相关 ===
    last_click_position: Optional[tuple]  # 最后点击位置
    last_scroll_position: Optional[tuple]  # 最后滚动位置
    last_input_text: Optional[str]  # 最后输入的文本
    
    # === 等待相关 ===
    implicit_wait: Optional[float]  # 隐式等待时间
    explicit_wait: Optional[float]  # 显式等待时间
    
    # === Cookie和存储 ===
    cookies: Optional[List[Dict[str, Any]]]  # Cookie信息
    local_storage: Optional[Dict[str, str]]  # 本地存储
    session_storage: Optional[Dict[str, str]]  # 会话存储


CONTEXT = TypeVar("CONTEXT", bound=WorkflowSeleniumContext)