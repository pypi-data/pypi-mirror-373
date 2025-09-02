#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Undetected Chrome 工作流上下文

定义 Undetected Chrome 相关的上下文信息，继承自 Selenium 上下文。
"""

from typing import Optional, Dict, Any, List, Tuple, TypeVar

from rpaworkflow.selenium.workflow_context import WorkflowSeleniumContext


class WorkflowUndetectedChromeContext(WorkflowSeleniumContext, total=False):
    """
    Undetected Chrome 工作流上下文
    
    继承自 WorkflowSeleniumContext，添加 undetected-chromedriver 特有的上下文信息
    """
    
    # Undetected Chrome 特有配置
    undetected_version: Optional[int]  # undetected-chromedriver 版本
    user_multi_procs: Optional[bool]  # 是否使用多进程
    use_subprocess: Optional[bool]  # 是否使用子进程
    debug: Optional[bool]  # 是否开启调试模式
    driver_executable_path: Optional[str]  # 驱动可执行文件路径
    browser_executable_path: Optional[str]  # 浏览器可执行文件路径
    log_level: Optional[int]  # 日志级别
    
    # 反检测相关配置
    patcher_force_close: Optional[bool]  # 是否强制关闭补丁
    suppress_welcome: Optional[bool]  # 是否抑制欢迎页面
    no_sandbox: Optional[bool]  # 是否禁用沙盒
    
    # 代理配置
    proxy_server: Optional[str]  # 代理服务器
    proxy_auth: Optional[Tuple[str, str]]  # 代理认证 (username, password)
    
    # 扩展和插件
    extensions: Optional[List[str]]  # 扩展路径列表
    prefs: Optional[Dict[str, Any]]  # Chrome 偏好设置
    
    # 性能和资源配置
    disable_images: Optional[bool]  # 是否禁用图片加载
    disable_javascript: Optional[bool]  # 是否禁用JavaScript
    disable_plugins: Optional[bool]  # 是否禁用插件
    disable_notifications: Optional[bool]  # 是否禁用通知
    
    # 指纹和隐私配置
    user_agent: Optional[str]  # 自定义User-Agent
    viewport_size: Optional[Tuple[int, int]]  # 视口大小
    timezone: Optional[str]  # 时区设置
    language: Optional[str]  # 语言设置
    geolocation: Optional[Tuple[float, float]]  # 地理位置 (latitude, longitude)
    
    # 反检测状态
    detection_evasion_enabled: Optional[bool]  # 是否启用反检测
    stealth_mode: Optional[bool]  # 是否启用隐身模式
    webrtc_leak_prevention: Optional[bool]  # 是否防止WebRTC泄露
    
    # 会话管理
    session_persistence: Optional[bool]  # 是否持久化会话
    profile_path: Optional[str]  # 用户配置文件路径
    

# 类型别名，用于类型提示
CONTEXT = TypeVar("CONTEXT", bound=WorkflowUndetectedChromeContext)
