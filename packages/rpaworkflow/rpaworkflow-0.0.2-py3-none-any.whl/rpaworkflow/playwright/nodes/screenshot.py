#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
截图节点
"""
import os
from typing import Optional, Any, Dict, List

from rpaworkflow.node import DataStorageNode
from rpaworkflow.playwright.nodes.base import PlaywrightBaseNode
from rpaworkflow.playwright.workflow_context import CONTEXT


class ScreenshotNode(PlaywrightBaseNode, DataStorageNode):
    """截图节点

    用于对页面或元素进行截图
    """

    def __init__(self,
                 name: str = "截图",
                 description: str = "对页面或元素进行截图",
                 file_path: Optional[str] = None,
                 selector: Optional[str] = None,
                 by_role: Optional[str] = None,
                 by_text: Optional[str] = None,
                 by_label: Optional[str] = None,
                 full_page: bool = False,
                 quality: Optional[int] = None,
                 type: str = "png",  # png, jpeg
                 clip: Optional[Dict[str, float]] = None,
                 omit_background: bool = False,
                 **kwargs):
        super().__init__(name, description, output_key='screenshot_path', **kwargs)
        self.file_path = file_path
        self.selector = selector
        self.by_role = by_role
        self.by_text = by_text
        self.by_label = by_label
        self.full_page = full_page
        self.quality = quality
        self.type = type.lower()
        self.clip = clip
        self.omit_background = omit_background

    def execute(self, context: CONTEXT) -> Any:
        """执行截图操作"""
        page = self.get_page(context)
        
        try:
            # 确定截图路径
            if self.file_path:
                screenshot_path = self.file_path
            else:
                # 生成默认文件名
                import time
                timestamp = int(time.time())
                screenshot_path = f"screenshot_{timestamp}.{self.type}"
            
            # 确保目录存在
            os.makedirs(os.path.dirname(os.path.abspath(screenshot_path)), exist_ok=True)
            
            # 准备截图选项
            options = {
                "path": screenshot_path,
                "type": self.type,
                "full_page": self.full_page,
                "omit_background": self.omit_background,
            }
            
            if self.quality and self.type == "jpeg":
                options["quality"] = self.quality
            
            if self.clip:
                options["clip"] = self.clip
            
            # 判断是页面截图还是元素截图
            if any([self.selector, self.by_role, self.by_text, self.by_label]):
                # 元素截图
                if self.selector:
                    locator = self.locator(context, self.selector)
                elif self.by_role:
                    locator = self.get_by_role(context, self.by_role)
                elif self.by_text:
                    locator = self.get_by_text(context, self.by_text)
                elif self.by_label:
                    locator = self.get_by_label(context, self.by_label)
                
                self.logger.info(f"对元素进行截图: {screenshot_path}")
                locator.screenshot(**options)
                
                # 更新上下文
                context['last_locator'] = locator
            else:
                # 页面截图
                self.logger.info(f"对页面进行截图: {screenshot_path}")
                page.screenshot(**options)
            
            # 更新上下文
            context['last_screenshot_path'] = screenshot_path
            
            self.logger.info(f"截图完成: {screenshot_path}")
            
            return screenshot_path
            
        except Exception as e:
            self.logger.error(f"截图失败: {e}")
            raise


class PDFNode(PlaywrightBaseNode, DataStorageNode):
    """PDF生成节点

    用于将页面保存为PDF
    """

    def __init__(self,
                 name: str = "生成PDF",
                 description: str = "将页面保存为PDF",
                 file_path: Optional[str] = None,
                 format: str = "A4",  # A4, Letter, Legal, Tabloid, Ledger, A0-A6
                 landscape: bool = False,
                 print_background: bool = False,
                 margin: Optional[Dict[str, str]] = None,
                 page_ranges: Optional[str] = None,
                 prefer_css_page_size: bool = False,
                 **kwargs):
        super().__init__(name, description, output_key='pdf_path', **kwargs)
        self.file_path = file_path
        self.format = format
        self.landscape = landscape
        self.print_background = print_background
        self.margin = margin or {"top": "1cm", "right": "1cm", "bottom": "1cm", "left": "1cm"}
        self.page_ranges = page_ranges
        self.prefer_css_page_size = prefer_css_page_size

    def execute(self, context: CONTEXT) -> Any:
        """执行PDF生成操作"""
        page = self.get_page(context)
        
        try:
            # 确定PDF路径
            if self.file_path:
                pdf_path = self.file_path
            else:
                # 生成默认文件名
                import time
                timestamp = int(time.time())
                pdf_path = f"page_{timestamp}.pdf"
            
            # 确保目录存在
            os.makedirs(os.path.dirname(os.path.abspath(pdf_path)), exist_ok=True)
            
            # 准备PDF选项
            options = {
                "path": pdf_path,
                "format": self.format,
                "landscape": self.landscape,
                "print_background": self.print_background,
                "margin": self.margin,
                "prefer_css_page_size": self.prefer_css_page_size,
            }
            
            if self.page_ranges:
                options["page_ranges"] = self.page_ranges
            
            self.logger.info(f"生成PDF: {pdf_path}")
            page.pdf(**options)
            
            # 更新上下文
            context['last_pdf_path'] = pdf_path
            
            self.logger.info(f"PDF生成完成: {pdf_path}")
            
            return pdf_path
            
        except Exception as e:
            self.logger.error(f"PDF生成失败: {e}")
            raise


class VideoRecordingNode(PlaywrightBaseNode):
    """视频录制节点

    用于开始或停止视频录制
    """

    def __init__(self,
                 name: str = "视频录制",
                 description: str = "开始或停止视频录制",
                 action: str = "start",  # start, stop
                 dir: Optional[str] = None,
                 size: Optional[Dict[str, int]] = None,
                 **kwargs):
        super().__init__(name, description, **kwargs)
        self.action = action.lower()
        self.dir = dir
        self.size = size

    def execute(self, context: CONTEXT) -> Any:
        """执行视频录制操作"""
        browser_context = self.get_browser_context(context)
        
        try:
            if self.action == "start":
                # 开始录制
                options = {}
                if self.dir:
                    options["dir"] = self.dir
                if self.size:
                    options["size"] = self.size
                
                self.logger.info("开始视频录制")
                browser_context.start_tracing(**options)
                
                # 更新上下文
                context['video_recording'] = True
                
                return "started"
                
            elif self.action == "stop":
                # 停止录制
                self.logger.info("停止视频录制")
                video_path = browser_context.stop_tracing()
                
                # 更新上下文
                context['video_recording'] = False
                context['last_video_path'] = video_path
                
                self.logger.info(f"视频录制完成: {video_path}")
                
                return video_path
                
            else:
                raise ValueError(f"不支持的录制操作: {self.action}")
            
        except Exception as e:
            self.logger.error(f"视频录制操作失败: {e}")
            raise