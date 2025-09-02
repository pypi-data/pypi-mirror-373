#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DrissionPage 截图节点

提供页面和元素截图功能。
"""

import os
from typing import Dict, Any

from DrissionPage import ChromiumPage, SessionPage
from DrissionPage._elements.session_element import SessionElement

from .base import DrissionPageBaseNode
from ..workflow_context import CONTEXT


class ScreenshotNode(DrissionPageBaseNode):
    """页面截图节点
    
    对当前页面进行截图。
    """
    
    def __init__(self, 
                 save_path: str = None,
                 filename: str = None,
                 full_page: bool = True,
                 quality: int = 90,
                 format: str = "png",
                 **kwargs):
        """
        初始化截图节点
        
        Args:
            save_path: 保存路径
            filename: 文件名（不包含扩展名）
            full_page: 是否截取整个页面
            quality: 图片质量（1-100，仅对JPEG有效）
            format: 图片格式 ('png', 'jpeg', 'jpg')
        """
        super().__init__(
            name="页面截图",
            description=f"截取页面图片: {save_path or 'default'}",
            **kwargs
        )
        
        self.save_path = save_path
        self.filename = filename
        self.full_page = full_page
        self.quality = max(1, min(100, quality))
        self.format = format.lower()
        
        self.node_type = "drissionpage_screenshot"
    
    def execute(self, context: CONTEXT) -> Dict[str, Any]:
        """执行截图
        
        Args:
            context: 工作流上下文
            
        Returns:
            执行结果
        """
        try:
            page = self._get_page(context)
            
            # 生成文件路径
            file_path = self._generate_file_path(context)
            
            # 确保目录存在
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            
            # 执行截图
            success = False
            if isinstance(page, SessionPage):
                # SessionPage 不支持截图
                return {
                    'success': False,
                    'file_path': file_path,
                    'message': 'SessionPage 不支持截图功能'
                }
            else:
                # ChromiumPage 和 WebPage 支持截图
                try:
                    if self.full_page:
                        # 全页面截图
                        if hasattr(page, 'get_screenshot'):
                            success = page.get_screenshot(path=file_path, full_page=True)
                        else:
                            success = page.screenshot(path=file_path, full_page=True)
                    else:
                        # 可视区域截图
                        if hasattr(page, 'get_screenshot'):
                            success = page.get_screenshot(path=file_path, full_page=False)
                        else:
                            success = page.screenshot(path=file_path, full_page=False)
                except Exception as e:
                    # 尝试其他方法
                    try:
                        success = page.screenshot(file_path)
                    except:
                        raise e
            
            # 检查文件是否创建成功
            file_exists = os.path.exists(file_path)
            file_size = os.path.getsize(file_path) if file_exists else 0
            
            # 更新上下文
            context['last_screenshot_path'] = file_path
            context['screenshot_success'] = success and file_exists
            context['screenshot_size'] = file_size
            
            if success and file_exists:
                return {
                    'success': True,
                    'file_path': file_path,
                    'file_size': file_size,
                    'full_page': self.full_page,
                    'format': self.format,
                    'message': f"截图成功保存到: {file_path}"
                }
            else:
                return {
                    'success': False,
                    'file_path': file_path,
                    'file_exists': file_exists,
                    'message': f"截图失败或文件未创建"
                }
            
        except Exception as e:
            error_msg = self._handle_error(context, e)
            return {
                'success': False,
                'error': error_msg,
                'file_path': file_path if 'file_path' in locals() else '',
                'message': f"截图失败: {error_msg}"
            }
    
    def _generate_file_path(self, context: CONTEXT) -> str:
        """生成文件路径"""
        import datetime
        
        # 确定保存目录
        if self.save_path:
            save_dir = self.save_path
        else:
            save_dir = context.get('screenshot_dir', './screenshots')
        
        # 确定文件名
        if self.filename:
            filename = self.filename
        else:
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"screenshot_{timestamp}"
        
        # 确定扩展名
        if self.format in ['jpg', 'jpeg']:
            ext = '.jpg'
        else:
            ext = '.png'
        
        return os.path.join(save_dir, f"{filename}{ext}")


class ElementScreenshotNode(DrissionPageBaseNode):
    """元素截图节点
    
    对指定元素进行截图。
    """
    
    def __init__(self, 
                 locator: str = None,
                 by_css: str = None,
                 by_xpath: str = None,
                 by_text: str = None,
                 by_tag: str = None,
                 by_attr: tuple = None,
                 save_path: str = None,
                 filename: str = None,
                 quality: int = 90,
                 format: str = "png",
                 scroll_to_element: bool = True,
                 timeout: float = 10.0,
                 **kwargs):
        """
        初始化元素截图节点
        
        Args:
            locator: 通用定位器
            by_css: CSS选择器
            by_xpath: XPath表达式
            by_text: 文本内容
            by_tag: 标签名
            by_attr: 属性元组
            save_path: 保存路径
            filename: 文件名（不包含扩展名）
            quality: 图片质量（1-100，仅对JPEG有效）
            format: 图片格式 ('png', 'jpeg', 'jpg')
            scroll_to_element: 是否滚动到元素
            timeout: 超时时间
        """
        super().__init__(
            name="元素截图",
            description=f"截取元素图片: {locator or by_css or by_xpath or by_text or by_tag or by_attr}",
            **kwargs
        )
        
        self.locator = locator
        self.by_css = by_css
        self.by_xpath = by_xpath
        self.by_text = by_text
        self.by_tag = by_tag
        self.by_attr = by_attr
        self.save_path = save_path
        self.filename = filename
        self.quality = max(1, min(100, quality))
        self.format = format.lower()
        self.scroll_to_element = scroll_to_element
        self.timeout = timeout
        
        self.node_type = "drissionpage_element_screenshot"
    
    def execute(self, context: CONTEXT) -> Dict[str, Any]:
        """执行元素截图
        
        Args:
            context: 工作流上下文
            
        Returns:
            执行结果
        """
        try:
            # 查找元素
            element = self._find_element(
                context=context,
                locator=self.locator,
                by_css=self.by_css,
                by_xpath=self.by_xpath,
                by_text=self.by_text,
                by_tag=self.by_tag,
                by_attr=self.by_attr,
                timeout=self.timeout
            )
            
            if element is None:
                return {
                    'success': False,
                    'file_path': '',
                    'message': '未找到指定元素'
                }
            
            # 检查元素类型
            if isinstance(element, SessionElement):
                return {
                    'success': False,
                    'file_path': '',
                    'message': 'SessionElement 不支持截图功能'
                }
            
            # 生成文件路径
            file_path = self._generate_file_path(context)
            
            # 确保目录存在
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            
            # 滚动到元素
            if self.scroll_to_element:
                try:
                    if hasattr(element, 'scroll_to'):
                        element.scroll_to()
                    elif hasattr(element, 'scroll_into_view'):
                        element.scroll_into_view()
                except:
                    pass
            
            # 执行截图
            success = False
            try:
                if hasattr(element, 'get_screenshot'):
                    success = element.get_screenshot(path=file_path)
                elif hasattr(element, 'screenshot'):
                    success = element.screenshot(path=file_path)
                else:
                    # 尝试使用页面截图并裁剪
                    success = self._screenshot_by_crop(element, file_path)
            except Exception as e:
                # 尝试其他方法
                try:
                    success = element.screenshot(file_path)
                except:
                    raise e
            
            # 检查文件是否创建成功
            file_exists = os.path.exists(file_path)
            file_size = os.path.getsize(file_path) if file_exists else 0
            
            # 更新上下文
            context['last_element'] = element
            context['last_screenshot_path'] = file_path
            context['screenshot_success'] = success and file_exists
            context['screenshot_size'] = file_size
            
            if success and file_exists:
                return {
                    'success': True,
                    'file_path': file_path,
                    'file_size': file_size,
                    'element_tag': getattr(element, 'tag', 'unknown'),
                    'format': self.format,
                    'message': f"元素截图成功保存到: {file_path}"
                }
            else:
                return {
                    'success': False,
                    'file_path': file_path,
                    'file_exists': file_exists,
                    'message': f"元素截图失败或文件未创建"
                }
            
        except Exception as e:
            error_msg = self._handle_error(context, e)
            return {
                'success': False,
                'error': error_msg,
                'file_path': file_path if 'file_path' in locals() else '',
                'message': f"元素截图失败: {error_msg}"
            }
    
    def _generate_file_path(self, context: CONTEXT) -> str:
        """生成文件路径"""
        import datetime
        
        # 确定保存目录
        if self.save_path:
            save_dir = self.save_path
        else:
            save_dir = context.get('screenshot_dir', './screenshots')
        
        # 确定文件名
        if self.filename:
            filename = self.filename
        else:
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"element_screenshot_{timestamp}"
        
        # 确定扩展名
        if self.format in ['jpg', 'jpeg']:
            ext = '.jpg'
        else:
            ext = '.png'
        
        return os.path.join(save_dir, f"{filename}{ext}")
    
    def _screenshot_by_crop(self, element, file_path: str) -> bool:
        """通过裁剪页面截图来获取元素截图"""
        try:
            # 获取元素位置和大小
            if hasattr(element, 'rect'):
                rect = element.rect
                x, y, width, height = rect['x'], rect['y'], rect['width'], rect['height']
            elif hasattr(element, 'location') and hasattr(element, 'size'):
                location = element.location
                size = element.size
                x, y = location['x'], location['y']
                width, height = size['width'], size['height']
            else:
                return False
            
            # 获取页面截图
            page = element.page if hasattr(element, 'page') else None
            if page is None:
                return False
            
            import tempfile
            with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as temp_file:
                temp_path = temp_file.name
            
            try:
                # 截取整个页面
                if hasattr(page, 'get_screenshot'):
                    page.get_screenshot(path=temp_path, full_page=False)
                else:
                    page.screenshot(path=temp_path, full_page=False)
                
                # 使用PIL裁剪图片
                try:
                    from PIL import Image
                    
                    with Image.open(temp_path) as img:
                        # 裁剪元素区域
                        cropped = img.crop((x, y, x + width, y + height))
                        cropped.save(file_path)
                    
                    return True
                except ImportError:
                    # 如果没有PIL，直接复制整个截图
                    import shutil
                    shutil.copy2(temp_path, file_path)
                    return True
                    
            finally:
                # 清理临时文件
                try:
                    os.unlink(temp_path)
                except:
                    pass
            
        except Exception:
            return False


class RecordVideoNode(DrissionPageBaseNode):
    """录制视频节点
    
    录制页面操作视频（仅支持ChromiumPage）。
    """
    
    def __init__(self, 
                 save_path: str = None,
                 filename: str = None,
                 action: str = "start",
                 **kwargs):
        """
        初始化录制视频节点
        
        Args:
            save_path: 保存路径
            filename: 文件名（不包含扩展名）
            action: 操作类型 ('start', 'stop')
        """
        super().__init__(
            name="录制视频",
            description=f"{action} 录制视频: {save_path or 'default'}",
            **kwargs
        )
        
        self.save_path = save_path
        self.filename = filename
        self.action = action.lower()
        
        self.node_type = "drissionpage_record_video"
    
    def execute(self, context: CONTEXT) -> Dict[str, Any]:
        """执行录制视频
        
        Args:
            context: 工作流上下文
            
        Returns:
            执行结果
        """
        try:
            page = self._get_page(context)
            
            # 检查页面类型
            if not isinstance(page, ChromiumPage):
                return {
                    'success': False,
                    'message': '只有 ChromiumPage 支持视频录制功能'
                }
            
            if self.action == "start":
                # 开始录制
                file_path = self._generate_file_path(context)
                
                # 确保目录存在
                os.makedirs(os.path.dirname(file_path), exist_ok=True)
                
                try:
                    if hasattr(page, 'start_recording'):
                        page.start_recording(save_path=file_path)
                    else:
                        return {
                            'success': False,
                            'message': '当前版本不支持视频录制功能'
                        }
                    
                    # 更新上下文
                    context['recording'] = True
                    context['recording_path'] = file_path
                    
                    return {
                        'success': True,
                        'action': 'start',
                        'file_path': file_path,
                        'message': f"开始录制视频到: {file_path}"
                    }
                    
                except Exception as e:
                    return {
                        'success': False,
                        'action': 'start',
                        'error': str(e),
                        'message': f"开始录制失败: {str(e)}"
                    }
            
            elif self.action == "stop":
                # 停止录制
                try:
                    if hasattr(page, 'stop_recording'):
                        page.stop_recording()
                    else:
                        return {
                            'success': False,
                            'message': '当前版本不支持视频录制功能'
                        }
                    
                    # 获取录制文件路径
                    file_path = context.get('recording_path', '')
                    file_exists = os.path.exists(file_path) if file_path else False
                    file_size = os.path.getsize(file_path) if file_exists else 0
                    
                    # 更新上下文
                    context['recording'] = False
                    context['last_recording_path'] = file_path
                    context['recording_size'] = file_size
                    
                    return {
                        'success': True,
                        'action': 'stop',
                        'file_path': file_path,
                        'file_exists': file_exists,
                        'file_size': file_size,
                        'message': f"停止录制，文件保存到: {file_path}" if file_exists else "停止录制"
                    }
                    
                except Exception as e:
                    return {
                        'success': False,
                        'action': 'stop',
                        'error': str(e),
                        'message': f"停止录制失败: {str(e)}"
                    }
            
            else:
                return {
                    'success': False,
                    'message': f"不支持的操作: {self.action}"
                }
            
        except Exception as e:
            error_msg = self._handle_error(context, e)
            return {
                'success': False,
                'error': error_msg,
                'action': self.action,
                'message': f"录制视频失败: {error_msg}"
            }
    
    def _generate_file_path(self, context: CONTEXT) -> str:
        """生成文件路径"""
        import datetime
        
        # 确定保存目录
        if self.save_path:
            save_dir = self.save_path
        else:
            save_dir = context.get('video_dir', './videos')
        
        # 确定文件名
        if self.filename:
            filename = self.filename
        else:
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"recording_{timestamp}"
        
        return os.path.join(save_dir, f"{filename}.mp4")