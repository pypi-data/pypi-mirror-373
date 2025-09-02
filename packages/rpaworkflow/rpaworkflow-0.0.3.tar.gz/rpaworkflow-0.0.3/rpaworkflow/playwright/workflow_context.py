#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
工作流playwright上下文定义
"""

from playwright.sync_api import Browser, BrowserContext, Page, Locator
from typing import Optional, Dict, Any, TypeVar, List, Union

from rpaworkflow.context import WorkflowContext


class WorkflowPlaywrightContext(WorkflowContext, total=False):
    # === 浏览器相关 ===
    browser: Optional[Browser]  # 浏览器实例
    browser_context: Optional[BrowserContext]  # 浏览器上下文
    page: Optional[Page]  # 页面实例
    browser_type: Optional[str]  # 浏览器类型 (chromium, firefox, webkit)
    viewport_size: Optional[Dict[str, int]]  # 视口尺寸
    current_url: Optional[str]  # 当前URL
    page_title: Optional[str]  # 页面标题
    
    # === 元素相关 ===
    last_locator: Optional[Locator]  # 最后操作的定位器
    last_locators: Optional[List[Locator]]  # 最后查找的定位器列表
    last_element_handle: Optional[Any]  # 最后的元素句柄
    last_text: Optional[str]  # 最后获取的文本
    last_attribute: Optional[str]  # 最后获取的属性值
    last_screenshot_path: Optional[str]  # 最后一次截图路径
    last_extracted_text: Optional[str]  # 最后提取的文本内容
    
    # === 操作相关 ===
    last_click_position: Optional[Dict[str, float]]  # 最后点击位置 {x, y}
    last_scroll_position: Optional[Dict[str, float]]  # 最后滚动位置
    last_input_text: Optional[str]  # 最后输入的文本
    last_keyboard_input: Optional[str]  # 最后的键盘输入
    
    # === 等待相关 ===
    default_timeout: Optional[float]  # 默认超时时间
    navigation_timeout: Optional[float]  # 导航超时时间
    
    # === 网络和存储 ===
    cookies: Optional[List[Dict[str, Any]]]  # Cookie信息
    local_storage: Optional[Dict[str, str]]  # 本地存储
    session_storage: Optional[Dict[str, str]]  # 会话存储
    
    # === 页面状态 ===
    page_load_state: Optional[str]  # 页面加载状态
    network_idle: Optional[bool]  # 网络是否空闲
    
    # === 多页面支持 ===
    all_pages: Optional[List[Page]]  # 所有页面
    active_page_index: Optional[int]  # 当前活跃页面索引
    
    # === 文件和下载 ===
    last_download_path: Optional[str]  # 最后下载文件路径
    upload_files: Optional[List[str]]  # 上传的文件列表
    
    # === 移动端支持 ===
    device_name: Optional[str]  # 设备名称
    is_mobile: Optional[bool]  # 是否为移动设备
    user_agent: Optional[str]  # 用户代理
    
    # === 调试和性能 ===
    tracing_enabled: Optional[bool]  # 是否启用追踪
    video_enabled: Optional[bool]  # 是否启用视频录制
    slow_mo: Optional[float]  # 慢动作延迟
    
    # === 权限和地理位置 ===
    permissions: Optional[List[str]]  # 权限列表
    geolocation: Optional[Dict[str, float]]  # 地理位置 {latitude, longitude}
    
    # === 代理和网络 ===
    proxy: Optional[Dict[str, str]]  # 代理配置
    offline: Optional[bool]  # 是否离线模式
    
    # === 安全和隐私 ===
    ignore_https_errors: Optional[bool]  # 是否忽略HTTPS错误
    bypass_csp: Optional[bool]  # 是否绕过CSP
    
    # === 自定义配置 ===
    extra_http_headers: Optional[Dict[str, str]]  # 额外的HTTP头
    locale: Optional[str]  # 语言环境
    timezone: Optional[str]  # 时区
    color_scheme: Optional[str]  # 颜色方案 (light, dark, no-preference)
    

CONTEXT = TypeVar("CONTEXT", bound=WorkflowPlaywrightContext)