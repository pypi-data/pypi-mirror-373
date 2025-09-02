#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DrissionPage 滚动节点

提供页面和元素滚动功能。
"""

from typing import Dict, Any, Tuple

from DrissionPage import SessionPage
from DrissionPage._elements.session_element import SessionElement

from .base import DrissionPageBaseNode
from ..workflow_context import CONTEXT


class ScrollNode(DrissionPageBaseNode):
    """页面滚动节点
    
    滚动页面到指定位置。
    """
    
    def __init__(self, 
                 x: int = None,
                 y: int = None,
                 delta_x: int = None,
                 delta_y: int = None,
                 direction: str = None,
                 distance: int = None,
                 smooth: bool = True,
                 **kwargs):
        """
        初始化滚动节点
        
        Args:
            x: 滚动到的X坐标（绝对位置）
            y: 滚动到的Y坐标（绝对位置）
            delta_x: X方向滚动距离（相对位置）
            delta_y: Y方向滚动距离（相对位置）
            direction: 滚动方向 ('up', 'down', 'left', 'right', 'top', 'bottom')
            distance: 滚动距离（像素）
            smooth: 是否平滑滚动
        """
        super().__init__(
            name="页面滚动",
            description=f"滚动页面: {direction or f'({x}, {y})' or f'delta({delta_x}, {delta_y})'}",
            **kwargs
        )
        
        self.x = x
        self.y = y
        self.delta_x = delta_x
        self.delta_y = delta_y
        self.direction = direction
        self.distance = distance or 300
        self.smooth = smooth
        
        self.node_type = "drissionpage_scroll"
    
    def execute(self, context: CONTEXT) -> Dict[str, Any]:
        """执行滚动
        
        Args:
            context: 工作流上下文
            
        Returns:
            执行结果
        """
        try:
            page = self._get_page(context)
            
            # 获取当前滚动位置
            current_x, current_y = self._get_scroll_position(page)
            
            # 计算目标位置
            target_x, target_y = self._calculate_target_position(
                page, current_x, current_y
            )
            
            # 执行滚动
            success = self._perform_scroll(page, target_x, target_y)
            
            # 获取滚动后位置
            new_x, new_y = self._get_scroll_position(page)
            
            # 更新上下文
            context['scroll_position'] = {'x': new_x, 'y': new_y}
            context['scroll_success'] = success
            context['scroll_delta'] = {
                'x': new_x - current_x,
                'y': new_y - current_y
            }
            
            return {
                'success': success,
                'current_position': {'x': current_x, 'y': current_y},
                'target_position': {'x': target_x, 'y': target_y},
                'new_position': {'x': new_x, 'y': new_y},
                'delta': {'x': new_x - current_x, 'y': new_y - current_y},
                'message': f"滚动完成，从 ({current_x}, {current_y}) 到 ({new_x}, {new_y})"
            }
            
        except Exception as e:
            error_msg = self._handle_error(context, e)
            return {
                'success': False,
                'error': error_msg,
                'message': f"滚动失败: {error_msg}"
            }
    
    def _get_scroll_position(self, page) -> Tuple[int, int]:
        """获取当前滚动位置"""
        try:
            if isinstance(page, SessionPage):
                # SessionPage 不支持滚动位置获取
                return 0, 0
            else:
                # ChromiumPage 和 WebPage
                if hasattr(page, 'scroll_position'):
                    pos = page.scroll_position
                    return pos.get('x', 0), pos.get('y', 0)
                else:
                    # 使用JavaScript获取
                    script = "return [window.pageXOffset || document.documentElement.scrollLeft, window.pageYOffset || document.documentElement.scrollTop];"
                    result = page.run_js(script)
                    if isinstance(result, list) and len(result) >= 2:
                        return int(result[0]), int(result[1])
                    return 0, 0
        except:
            return 0, 0
    
    def _calculate_target_position(self, page, current_x: int, current_y: int) -> Tuple[int, int]:
        """计算目标滚动位置"""
        # 绝对位置
        if self.x is not None and self.y is not None:
            return self.x, self.y
        
        # 相对位置
        if self.delta_x is not None or self.delta_y is not None:
            target_x = current_x + (self.delta_x or 0)
            target_y = current_y + (self.delta_y or 0)
            return target_x, target_y
        
        # 方向滚动
        if self.direction:
            if self.direction == 'up':
                return current_x, max(0, current_y - self.distance)
            elif self.direction == 'down':
                return current_x, current_y + self.distance
            elif self.direction == 'left':
                return max(0, current_x - self.distance), current_y
            elif self.direction == 'right':
                return current_x + self.distance, current_y
            elif self.direction == 'top':
                return current_x, 0
            elif self.direction == 'bottom':
                # 滚动到页面底部
                try:
                    if isinstance(page, SessionPage):
                        return current_x, 999999  # 大数值
                    else:
                        script = "return document.body.scrollHeight || document.documentElement.scrollHeight;"
                        height = page.run_js(script)
                        return current_x, int(height) if height else 999999
                except:
                    return current_x, 999999
        
        # 默认不滚动
        return current_x, current_y
    
    def _perform_scroll(self, page, target_x: int, target_y: int) -> bool:
        """执行滚动操作"""
        try:
            if isinstance(page, SessionPage):
                # SessionPage 不支持滚动
                return False
            else:
                # ChromiumPage 和 WebPage
                if hasattr(page, 'scroll_to'):
                    page.scroll_to(x=target_x, y=target_y)
                    return True
                else:
                    # 使用JavaScript滚动
                    if self.smooth:
                        script = f"window.scrollTo({{left: {target_x}, top: {target_y}, behavior: 'smooth'}});"
                    else:
                        script = f"window.scrollTo({target_x}, {target_y});"
                    page.run_js(script)
                    return True
        except Exception:
            return False


class ScrollToElementNode(DrissionPageBaseNode):
    """滚动到元素节点
    
    滚动页面使指定元素可见。
    """
    
    def __init__(self, 
                 locator: str = None,
                 by_css: str = None,
                 by_xpath: str = None,
                 by_text: str = None,
                 by_tag: str = None,
                 by_attr: tuple = None,
                 position: str = "center",
                 offset_x: int = 0,
                 offset_y: int = 0,
                 smooth: bool = True,
                 timeout: float = 10.0,
                 **kwargs):
        """
        初始化滚动到元素节点
        
        Args:
            locator: 通用定位器
            by_css: CSS选择器
            by_xpath: XPath表达式
            by_text: 文本内容
            by_tag: 标签名
            by_attr: 属性元组
            position: 滚动位置 ('top', 'center', 'bottom')
            offset_x: X方向偏移
            offset_y: Y方向偏移
            smooth: 是否平滑滚动
            timeout: 超时时间
        """
        super().__init__(
            name="滚动到元素",
            description=f"滚动到元素: {locator or by_css or by_xpath or by_text or by_tag or by_attr}",
            **kwargs
        )
        
        self.locator = locator
        self.by_css = by_css
        self.by_xpath = by_xpath
        self.by_text = by_text
        self.by_tag = by_tag
        self.by_attr = by_attr
        self.position = position
        self.offset_x = offset_x
        self.offset_y = offset_y
        self.smooth = smooth
        self.timeout = timeout
        
        self.node_type = "drissionpage_scroll_to_element"
    
    def execute(self, context: CONTEXT) -> Dict[str, Any]:
        """执行滚动到元素
        
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
                    'message': '未找到指定元素'
                }
            
            # 获取当前滚动位置
            page = self._get_page(context)
            current_x, current_y = self._get_scroll_position(page)
            
            # 执行滚动
            success = self._scroll_to_element(element)
            
            # 获取滚动后位置
            new_x, new_y = self._get_scroll_position(page)
            
            # 更新上下文
            context['last_element'] = element
            context['scroll_position'] = {'x': new_x, 'y': new_y}
            context['scroll_success'] = success
            context['scroll_delta'] = {
                'x': new_x - current_x,
                'y': new_y - current_y
            }
            
            return {
                'success': success,
                'element_tag': getattr(element, 'tag', 'unknown'),
                'current_position': {'x': current_x, 'y': current_y},
                'new_position': {'x': new_x, 'y': new_y},
                'delta': {'x': new_x - current_x, 'y': new_y - current_y},
                'position': self.position,
                'message': f"滚动到元素完成，位置变化: ({new_x - current_x}, {new_y - current_y})"
            }
            
        except Exception as e:
            error_msg = self._handle_error(context, e)
            return {
                'success': False,
                'error': error_msg,
                'message': f"滚动到元素失败: {error_msg}"
            }
    
    def _get_scroll_position(self, page) -> Tuple[int, int]:
        """获取当前滚动位置"""
        try:
            if isinstance(page, SessionPage):
                return 0, 0
            else:
                if hasattr(page, 'scroll_position'):
                    pos = page.scroll_position
                    return pos.get('x', 0), pos.get('y', 0)
                else:
                    script = "return [window.pageXOffset || document.documentElement.scrollLeft, window.pageYOffset || document.documentElement.scrollTop];"
                    result = page.run_js(script)
                    if isinstance(result, list) and len(result) >= 2:
                        return int(result[0]), int(result[1])
                    return 0, 0
        except:
            return 0, 0
    
    def _scroll_to_element(self, element) -> bool:
        """滚动到元素"""
        try:
            if isinstance(element, SessionElement):
                # SessionElement 不支持滚动
                return False
            
            # 尝试使用元素的滚动方法
            if hasattr(element, 'scroll_to'):
                element.scroll_to()
                return True
            elif hasattr(element, 'scroll_into_view'):
                element.scroll_into_view()
                return True
            else:
                # 使用JavaScript滚动
                page = element.page if hasattr(element, 'page') else None
                if page and hasattr(page, 'run_js'):
                    # 获取元素位置
                    script = """
                    var element = arguments[0];
                    var rect = element.getBoundingClientRect();
                    var scrollTop = window.pageYOffset || document.documentElement.scrollTop;
                    var scrollLeft = window.pageXOffset || document.documentElement.scrollLeft;
                    return {
                        x: rect.left + scrollLeft,
                        y: rect.top + scrollTop,
                        width: rect.width,
                        height: rect.height
                    };
                    """
                    
                    try:
                        rect = page.run_js(script, element)
                        if rect:
                            # 计算滚动位置
                            target_x = rect['x'] + self.offset_x
                            if self.position == 'center':
                                target_y = rect['y'] - (page.size[1] // 2) + (rect['height'] // 2) + self.offset_y
                            elif self.position == 'top':
                                target_y = rect['y'] + self.offset_y
                            elif self.position == 'bottom':
                                target_y = rect['y'] - page.size[1] + rect['height'] + self.offset_y
                            else:
                                target_y = rect['y'] + self.offset_y
                            
                            # 执行滚动
                            if self.smooth:
                                scroll_script = f"window.scrollTo({{left: {target_x}, top: {target_y}, behavior: 'smooth'}});"
                            else:
                                scroll_script = f"window.scrollTo({target_x}, {target_y});"
                            
                            page.run_js(scroll_script)
                            return True
                    except:
                        pass
                
                return False
        except Exception:
            return False


class ScrollElementNode(DrissionPageBaseNode):
    """滚动元素节点
    
    滚动指定元素内部的内容。
    """
    
    def __init__(self, 
                 locator: str = None,
                 by_css: str = None,
                 by_xpath: str = None,
                 by_text: str = None,
                 by_tag: str = None,
                 by_attr: tuple = None,
                 delta_x: int = None,
                 delta_y: int = None,
                 direction: str = None,
                 distance: int = None,
                 smooth: bool = True,
                 timeout: float = 10.0,
                 **kwargs):
        """
        初始化滚动元素节点
        
        Args:
            locator: 通用定位器
            by_css: CSS选择器
            by_xpath: XPath表达式
            by_text: 文本内容
            by_tag: 标签名
            by_attr: 属性元组
            delta_x: X方向滚动距离
            delta_y: Y方向滚动距离
            direction: 滚动方向 ('up', 'down', 'left', 'right', 'top', 'bottom')
            distance: 滚动距离（像素）
            smooth: 是否平滑滚动
            timeout: 超时时间
        """
        super().__init__(
            name="滚动元素",
            description=f"滚动元素内容: {locator or by_css or by_xpath or by_text or by_tag or by_attr}",
            **kwargs
        )
        
        self.locator = locator
        self.by_css = by_css
        self.by_xpath = by_xpath
        self.by_text = by_text
        self.by_tag = by_tag
        self.by_attr = by_attr
        self.delta_x = delta_x
        self.delta_y = delta_y
        self.direction = direction
        self.distance = distance or 300
        self.smooth = smooth
        self.timeout = timeout
        
        self.node_type = "drissionpage_scroll_element"
    
    def execute(self, context: CONTEXT) -> Dict[str, Any]:
        """执行滚动元素
        
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
                    'message': '未找到指定元素'
                }
            
            if isinstance(element, SessionElement):
                return {
                    'success': False,
                    'message': 'SessionElement 不支持元素滚动'
                }
            
            # 获取当前滚动位置
            current_x, current_y = self._get_element_scroll_position(element)
            
            # 计算目标位置
            target_x, target_y = self._calculate_target_position(
                element, current_x, current_y
            )
            
            # 执行滚动
            success = self._perform_element_scroll(element, target_x, target_y)
            
            # 获取滚动后位置
            new_x, new_y = self._get_element_scroll_position(element)
            
            # 更新上下文
            context['last_element'] = element
            context['element_scroll_position'] = {'x': new_x, 'y': new_y}
            context['element_scroll_success'] = success
            context['element_scroll_delta'] = {
                'x': new_x - current_x,
                'y': new_y - current_y
            }
            
            return {
                'success': success,
                'element_tag': getattr(element, 'tag', 'unknown'),
                'current_position': {'x': current_x, 'y': current_y},
                'target_position': {'x': target_x, 'y': target_y},
                'new_position': {'x': new_x, 'y': new_y},
                'delta': {'x': new_x - current_x, 'y': new_y - current_y},
                'message': f"元素滚动完成，位置变化: ({new_x - current_x}, {new_y - current_y})"
            }
            
        except Exception as e:
            error_msg = self._handle_error(context, e)
            return {
                'success': False,
                'error': error_msg,
                'message': f"滚动元素失败: {error_msg}"
            }
    
    def _get_element_scroll_position(self, element) -> Tuple[int, int]:
        """获取元素滚动位置"""
        try:
            page = element.page if hasattr(element, 'page') else None
            if page and hasattr(page, 'run_js'):
                script = """
                var element = arguments[0];
                return [element.scrollLeft || 0, element.scrollTop || 0];
                """
                result = page.run_js(script, element)
                if isinstance(result, list) and len(result) >= 2:
                    return int(result[0]), int(result[1])
            return 0, 0
        except:
            return 0, 0
    
    def _calculate_target_position(self, element, current_x: int, current_y: int) -> Tuple[int, int]:
        """计算目标滚动位置"""
        # 相对位置
        if self.delta_x is not None or self.delta_y is not None:
            target_x = current_x + (self.delta_x or 0)
            target_y = current_y + (self.delta_y or 0)
            return target_x, target_y
        
        # 方向滚动
        if self.direction:
            if self.direction == 'up':
                return current_x, max(0, current_y - self.distance)
            elif self.direction == 'down':
                return current_x, current_y + self.distance
            elif self.direction == 'left':
                return max(0, current_x - self.distance), current_y
            elif self.direction == 'right':
                return current_x + self.distance, current_y
            elif self.direction == 'top':
                return current_x, 0
            elif self.direction == 'bottom':
                # 滚动到元素底部
                try:
                    page = element.page if hasattr(element, 'page') else None
                    if page and hasattr(page, 'run_js'):
                        script = "return arguments[0].scrollHeight || 0;"
                        height = page.run_js(script, element)
                        return current_x, int(height) if height else 999999
                except:
                    pass
                return current_x, 999999
        
        # 默认不滚动
        return current_x, current_y
    
    def _perform_element_scroll(self, element, target_x: int, target_y: int) -> bool:
        """执行元素滚动操作"""
        try:
            page = element.page if hasattr(element, 'page') else None
            if page and hasattr(page, 'run_js'):
                if self.smooth:
                    script = f"""
                    var element = arguments[0];
                    element.scrollTo({{left: {target_x}, top: {target_y}, behavior: 'smooth'}});
                    """
                else:
                    script = f"""
                    var element = arguments[0];
                    element.scrollLeft = {target_x};
                    element.scrollTop = {target_y};
                    """
                page.run_js(script, element)
                return True
            return False
        except Exception:
            return False


class WheelScrollNode(DrissionPageBaseNode):
    """鼠标滚轮滚动节点
    
    使用鼠标滚轮进行滚动。
    """
    
    def __init__(self, 
                 x: int = None,
                 y: int = None,
                 delta_x: int = 0,
                 delta_y: int = 0,
                 locator: str = None,
                 by_css: str = None,
                 by_xpath: str = None,
                 by_text: str = None,
                 by_tag: str = None,
                 by_attr: tuple = None,
                 timeout: float = 10.0,
                 **kwargs):
        """
        初始化鼠标滚轮滚动节点
        
        Args:
            x: 滚动位置X坐标
            y: 滚动位置Y坐标
            delta_x: X方向滚动量
            delta_y: Y方向滚动量
            locator: 元素定位器（在元素上滚动）
            by_css: CSS选择器
            by_xpath: XPath表达式
            by_text: 文本内容
            by_tag: 标签名
            by_attr: 属性元组
            timeout: 超时时间
        """
        super().__init__(
            name="鼠标滚轮滚动",
            description=f"鼠标滚轮滚动: ({delta_x}, {delta_y})",
            **kwargs
        )
        
        self.x = x
        self.y = y
        self.delta_x = delta_x
        self.delta_y = delta_y
        self.locator = locator
        self.by_css = by_css
        self.by_xpath = by_xpath
        self.by_text = by_text
        self.by_tag = by_tag
        self.by_attr = by_attr
        self.timeout = timeout
        
        self.node_type = "drissionpage_wheel_scroll"
    
    def execute(self, context: CONTEXT) -> Dict[str, Any]:
        """执行鼠标滚轮滚动
        
        Args:
            context: 工作流上下文
            
        Returns:
            执行结果
        """
        try:
            page = self._get_page(context)
            
            if isinstance(page, SessionPage):
                return {
                    'success': False,
                    'message': 'SessionPage 不支持鼠标滚轮操作'
                }
            
            # 确定滚动位置
            scroll_x, scroll_y = self._determine_scroll_position(context, page)
            
            # 执行滚轮滚动
            success = self._perform_wheel_scroll(page, scroll_x, scroll_y)
            
            # 更新上下文
            context['wheel_scroll_position'] = {'x': scroll_x, 'y': scroll_y}
            context['wheel_scroll_delta'] = {'x': self.delta_x, 'y': self.delta_y}
            context['wheel_scroll_success'] = success
            
            return {
                'success': success,
                'position': {'x': scroll_x, 'y': scroll_y},
                'delta': {'x': self.delta_x, 'y': self.delta_y},
                'message': f"鼠标滚轮滚动完成，位置: ({scroll_x}, {scroll_y})，滚动量: ({self.delta_x}, {self.delta_y})"
            }
            
        except Exception as e:
            error_msg = self._handle_error(context, e)
            return {
                'success': False,
                'error': error_msg,
                'message': f"鼠标滚轮滚动失败: {error_msg}"
            }
    
    def _determine_scroll_position(self, context: CONTEXT, page) -> Tuple[int, int]:
        """确定滚动位置"""
        # 如果指定了坐标
        if self.x is not None and self.y is not None:
            return self.x, self.y
        
        # 如果指定了元素
        if any([self.locator, self.by_css, self.by_xpath, self.by_text, self.by_tag, self.by_attr]):
            try:
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
                
                if element and hasattr(element, 'rect'):
                    rect = element.rect
                    return rect['x'] + rect['width'] // 2, rect['y'] + rect['height'] // 2
                elif element and hasattr(element, 'location') and hasattr(element, 'size'):
                    location = element.location
                    size = element.size
                    return location['x'] + size['width'] // 2, location['y'] + size['height'] // 2
            except:
                pass
        
        # 默认使用页面中心
        try:
            if hasattr(page, 'size'):
                size = page.size
                return size[0] // 2, size[1] // 2
            else:
                return 400, 300  # 默认位置
        except:
            return 400, 300
    
    def _perform_wheel_scroll(self, page, x: int, y: int) -> bool:
        """执行鼠标滚轮滚动"""
        try:
            if hasattr(page, 'scroll'):
                # 使用DrissionPage的滚动方法
                page.scroll(x=x, y=y, delta_x=self.delta_x, delta_y=self.delta_y)
                return True
            elif hasattr(page, 'wheel'):
                # 使用wheel方法
                page.wheel(x=x, y=y, delta_x=self.delta_x, delta_y=self.delta_y)
                return True
            else:
                # 使用JavaScript模拟滚轮事件
                script = f"""
                var event = new WheelEvent('wheel', {{
                    deltaX: {self.delta_x},
                    deltaY: {self.delta_y},
                    clientX: {x},
                    clientY: {y},
                    bubbles: true,
                    cancelable: true
                }});
                document.elementFromPoint({x}, {y}).dispatchEvent(event);
                """
                page.run_js(script)
                return True
        except Exception:
            return False