#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DrissionPage 工作流上下文定义

DrissionPage 是一个基于 Python 的网页自动化工具，
结合了 requests 和 selenium 的优点，提供了更简洁的 API。
"""

from typing import Optional, Dict, Any, List, Union, TypeVar
from DrissionPage import ChromiumPage, SessionPage, WebPage
from DrissionPage._elements.chromium_element import ChromiumElement
from DrissionPage._elements.session_element import SessionElement

from rpaworkflow.context import WorkflowContext


class WorkflowDrissionPageContext(WorkflowContext, total=False):
    """DrissionPage 工作流上下文
    
    存储 DrissionPage 相关的状态信息，包括页面实例、元素、配置等。
    """
    
    # === 页面相关 ===
    page: Optional[Union[ChromiumPage, SessionPage, WebPage]]  # 页面实例
    page_type: Optional[str]  # 页面类型: 'chromium', 'session', 'web'
    url: Optional[str]  # 当前页面URL
    title: Optional[str]  # 页面标题
    html: Optional[str]  # 页面HTML源码
    
    # === 浏览器相关（ChromiumPage） ===
    browser_path: Optional[str]  # 浏览器可执行文件路径
    user_data_path: Optional[str]  # 用户数据目录
    headless: Optional[bool]  # 是否无头模式
    window_size: Optional[tuple]  # 窗口尺寸
    proxy: Optional[str]  # 代理设置
    
    # === 会话相关（SessionPage） ===
    session_headers: Optional[Dict[str, str]]  # 会话请求头
    session_cookies: Optional[Dict[str, str]]  # 会话Cookie
    session_timeout: Optional[float]  # 会话超时时间
    
    # === 元素相关 ===
    element: Optional[Union[ChromiumElement, SessionElement]]  # 当前操作的元素
    elements: Optional[List[Union[ChromiumElement, SessionElement]]]  # 元素列表
    text: Optional[str]  # 获取的文本内容
    attribute_value: Optional[str]  # 获取的属性值
    
    # === 定位相关 ===
    locator: Optional[str]  # 最后使用的定位器
    locator_type: Optional[str]  # 定位器类型: 'css', 'xpath', 'text', 'tag', 'attr'
    
    # === 操作相关 ===
    click_position: Optional[tuple]  # 点击位置坐标
    input_text: Optional[str]  # 输入的文本
    scroll_position: Optional[tuple]  # 滚动位置
    screenshot_path: Optional[str]  # 截图保存路径
    
    # === 等待相关 ===
    wait_timeout: Optional[float]  # 等待超时时间
    implicit_wait: Optional[float]  # 隐式等待时间
    
    # === 下载相关 ===
    download_path: Optional[str]  # 下载文件保存路径
    download_info: Optional[Dict[str, Any]]  # 下载信息
    
    # === 表单相关 ===
    form_data: Optional[Dict[str, Any]]  # 表单数据
    upload_files: Optional[List[str]]  # 上传的文件路径列表
    
    # === 网络相关 ===
    response_status: Optional[int]  # 响应状态码
    response_headers: Optional[Dict[str, str]]  # 响应头
    response_text: Optional[str]  # 响应文本
    response_json: Optional[Dict[str, Any]]  # 响应JSON数据
    
    # === 页面状态 ===
    page_loaded: Optional[bool]  # 页面是否加载完成
    ready_state: Optional[str]  # 页面就绪状态
    
    # === 标签页管理 ===
    tab_count: Optional[int]  # 标签页数量
    current_tab_id: Optional[str]  # 当前标签页ID
    tab_list: Optional[List[str]]  # 标签页ID列表
    
    # === 框架相关 ===
    frame_path: Optional[List[str]]  # 框架路径
    current_frame: Optional[str]  # 当前框架
    
    # === 调试相关 ===
    debug_mode: Optional[bool]  # 是否开启调试模式
    log_level: Optional[str]  # 日志级别
    
    # === 性能相关 ===
    load_mode: Optional[str]  # 加载模式: 'normal', 'eager', 'none'
    load_strategy: Optional[str]  # 加载策略
    
    # === 自定义配置 ===
    custom_config: Optional[Dict[str, Any]]  # 自定义配置
    user_agent: Optional[str]  # 用户代理
    
    # === 错误处理 ===
    last_error: Optional[str]  # 最后的错误信息
    error_count: Optional[int]  # 错误计数


CONTEXT = TypeVar("CONTEXT", bound=WorkflowDrissionPageContext)
