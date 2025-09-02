#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DrissionPage 表单操作节点

提供表单填写、提交、选择等功能。
"""

from typing import Dict, Any

from DrissionPage import ChromiumPage
from DrissionPage._elements.chromium_element import ChromiumElement
from DrissionPage._elements.session_element import SessionElement

from .base import DrissionPageBaseNode
from ..workflow_context import CONTEXT


class SelectOptionNode(DrissionPageBaseNode):
    """选择选项节点
    
    在下拉框或选择列表中选择指定选项。
    """
    
    def __init__(self, 
                 locator: str = None,
                 by_css: str = None,
                 by_xpath: str = None,
                 by_text: str = None,
                 by_tag: str = None,
                 by_attr: tuple = None,
                 option_text: str = None,
                 option_value: str = None,
                 option_index: int = None,
                 multiple: bool = False,
                 clear_first: bool = False,
                 timeout: float = 10.0,
                 **kwargs):
        """
        初始化选择选项节点
        
        Args:
            locator: 通用定位器
            by_css: CSS选择器
            by_xpath: XPath表达式
            by_text: 文本内容
            by_tag: 标签名
            by_attr: 属性元组
            option_text: 选项文本
            option_value: 选项值
            option_index: 选项索引
            multiple: 是否多选
            clear_first: 是否先清除已选择的选项
            timeout: 超时时间
        """
        super().__init__(
            name="选择选项",
            description=f"选择选项: {option_text or option_value or option_index}",
            **kwargs
        )
        
        self.locator = locator
        self.by_css = by_css
        self.by_xpath = by_xpath
        self.by_text = by_text
        self.by_tag = by_tag
        self.by_attr = by_attr
        self.option_text = option_text
        self.option_value = option_value
        self.option_index = option_index
        self.multiple = multiple
        self.clear_first = clear_first
        self.timeout = timeout
        
        self.node_type = "drissionpage_select_option"
    
    def execute(self, context: CONTEXT) -> Dict[str, Any]:
        """执行选择选项
        
        Args:
            context: 工作流上下文
            
        Returns:
            执行结果
        """
        try:
            # 查找选择框元素
            select_element = self._find_element(
                context=context,
                locator=self.locator,
                by_css=self.by_css,
                by_xpath=self.by_xpath,
                by_text=self.by_text,
                by_tag=self.by_tag,
                by_attr=self.by_attr,
                timeout=self.timeout
            )
            
            if select_element is None:
                return {
                    'success': False,
                    'error': '未找到选择框元素',
                    'message': '选择选项失败: 未找到选择框元素'
                }
            
            # 先清除选择（如果需要）
            if self.clear_first:
                self._clear_selection(select_element)
            
            # 执行选择
            selected_option = self._select_option(select_element)
            
            # 更新上下文
            context['last_selected_element'] = select_element
            context['selected_option'] = selected_option
            context['form_data'] = context.get('form_data', {})
            
            return {
                'success': True,
                'selected_option': selected_option,
                'option_text': self.option_text,
                'option_value': self.option_value,
                'option_index': self.option_index,
                'element_tag': getattr(select_element, 'tag', 'unknown'),
                'message': f"成功选择选项: {selected_option}"
            }
            
        except Exception as e:
            error_msg = self._handle_error(context, e)
            return {
                'success': False,
                'error': error_msg,
                'message': f"选择选项失败: {error_msg}"
            }
    
    def _clear_selection(self, select_element):
        """清除已选择的选项"""
        try:
            if isinstance(select_element, ChromiumElement):
                # 对于ChromiumElement，尝试取消所有选择
                if hasattr(select_element, 'clear'):
                    select_element.clear()
                else:
                    # 尝试通过JavaScript清除
                    page = self._get_page_instance({})
                    if page and hasattr(page, 'run_js'):
                        page.run_js("arguments[0].selectedIndex = -1;", select_element)
        except Exception:
            pass  # 忽略清除错误
    
    def _select_option(self, select_element) -> str:
        """选择选项"""
        try:
            if isinstance(select_element, ChromiumElement):
                return self._select_chromium_option(select_element)
            elif isinstance(select_element, SessionElement):
                return self._select_session_option(select_element)
            else:
                # 通用选择方法
                return self._select_generic_option(select_element)
        except Exception as e:
            raise Exception(f"选择选项失败: {str(e)}")
    
    def _select_chromium_option(self, select_element) -> str:
        """在ChromiumElement中选择选项"""
        try:
            # 按文本选择
            if self.option_text is not None:
                if hasattr(select_element, 'select'):
                    select_element.select(self.option_text)
                    return self.option_text
                else:
                    # 查找选项并点击
                    option = select_element.ele(f'option:contains("{self.option_text}")')
                    if option:
                        option.click()
                        return self.option_text
            
            # 按值选择
            if self.option_value is not None:
                if hasattr(select_element, 'select'):
                    select_element.select(value=self.option_value)
                    return self.option_value
                else:
                    option = select_element.ele(f'option[value="{self.option_value}"]')
                    if option:
                        option.click()
                        return self.option_value
            
            # 按索引选择
            if self.option_index is not None:
                if hasattr(select_element, 'select'):
                    select_element.select(index=self.option_index)
                    return f"索引 {self.option_index}"
                else:
                    options = select_element.eles('option')
                    if 0 <= self.option_index < len(options):
                        options[self.option_index].click()
                        return f"索引 {self.option_index}"
            
            raise Exception("未指定有效的选择条件")
            
        except Exception as e:
            raise Exception(f"ChromiumElement选择失败: {str(e)}")
    
    def _select_session_option(self, select_element) -> str:
        """在SessionElement中选择选项"""
        try:
            # SessionElement通常不支持直接选择，需要通过表单提交
            # 这里记录选择的值，在表单提交时使用
            selected_value = None
            
            if self.option_text is not None:
                selected_value = self.option_text
            elif self.option_value is not None:
                selected_value = self.option_value
            elif self.option_index is not None:
                selected_value = f"索引 {self.option_index}"
            
            if selected_value:
                # 记录到上下文中，供后续表单提交使用
                return selected_value
            
            raise Exception("未指定有效的选择条件")
            
        except Exception as e:
            raise Exception(f"SessionElement选择失败: {str(e)}")
    
    def _select_generic_option(self, select_element) -> str:
        """通用选择方法"""
        try:
            # 尝试各种选择方法
            if hasattr(select_element, 'select'):
                if self.option_text is not None:
                    select_element.select(self.option_text)
                    return self.option_text
                elif self.option_value is not None:
                    select_element.select(value=self.option_value)
                    return self.option_value
                elif self.option_index is not None:
                    select_element.select(index=self.option_index)
                    return f"索引 {self.option_index}"
            
            # 如果没有select方法，尝试点击选项
            if self.option_text is not None:
                return self.option_text
            elif self.option_value is not None:
                return self.option_value
            elif self.option_index is not None:
                return f"索引 {self.option_index}"
            
            raise Exception("未指定有效的选择条件")
            
        except Exception as e:
            raise Exception(f"通用选择失败: {str(e)}")


class CheckboxNode(DrissionPageBaseNode):
    """复选框操作节点
    
    选中或取消选中复选框。
    """
    
    def __init__(self, 
                 locator: str = None,
                 by_css: str = None,
                 by_xpath: str = None,
                 by_text: str = None,
                 by_tag: str = None,
                 by_attr: tuple = None,
                 checked: bool = True,
                 timeout: float = 10.0,
                 **kwargs):
        """
        初始化复选框操作节点
        
        Args:
            locator: 通用定位器
            by_css: CSS选择器
            by_xpath: XPath表达式
            by_text: 文本内容
            by_tag: 标签名
            by_attr: 属性元组
            checked: 是否选中
            timeout: 超时时间
        """
        super().__init__(
            name="复选框操作",
            description=f"{'选中' if checked else '取消选中'}复选框",
            **kwargs
        )
        
        self.locator = locator
        self.by_css = by_css
        self.by_xpath = by_xpath
        self.by_text = by_text
        self.by_tag = by_tag
        self.by_attr = by_attr
        self.checked = checked
        self.timeout = timeout
        
        self.node_type = "drissionpage_checkbox"
    
    def execute(self, context: CONTEXT) -> Dict[str, Any]:
        """执行复选框操作
        
        Args:
            context: 工作流上下文
            
        Returns:
            执行结果
        """
        try:
            # 查找复选框元素
            checkbox_element = self._find_element(
                context=context,
                locator=self.locator,
                by_css=self.by_css,
                by_xpath=self.by_xpath,
                by_text=self.by_text,
                by_tag=self.by_tag,
                by_attr=self.by_attr,
                timeout=self.timeout
            )
            
            if checkbox_element is None:
                return {
                    'success': False,
                    'error': '未找到复选框元素',
                    'message': '复选框操作失败: 未找到复选框元素'
                }
            
            # 获取当前状态
            current_checked = self._is_checkbox_checked(checkbox_element)
            
            # 如果状态不同，则点击切换
            if current_checked != self.checked:
                checkbox_element.click()
                final_checked = self.checked
            else:
                final_checked = current_checked
            
            # 更新上下文
            context['last_checkbox_element'] = checkbox_element
            context['checkbox_checked'] = final_checked
            context['form_data'] = context.get('form_data', {})
            
            return {
                'success': True,
                'checked': final_checked,
                'changed': current_checked != self.checked,
                'element_tag': getattr(checkbox_element, 'tag', 'unknown'),
                'message': f"复选框{'选中' if final_checked else '未选中'}"
            }
            
        except Exception as e:
            error_msg = self._handle_error(context, e)
            return {
                'success': False,
                'error': error_msg,
                'message': f"复选框操作失败: {error_msg}"
            }
    
    def _is_checkbox_checked(self, checkbox_element) -> bool:
        """检查复选框是否选中"""
        try:
            if isinstance(checkbox_element, ChromiumElement):
                return checkbox_element.is_checked
            elif isinstance(checkbox_element, SessionElement):
                # SessionElement检查checked属性
                checked_attr = checkbox_element.attr('checked')
                return checked_attr is not None and checked_attr != 'false'
            else:
                # 通用检查方法
                if hasattr(checkbox_element, 'is_checked'):
                    return checkbox_element.is_checked
                elif hasattr(checkbox_element, 'is_selected'):
                    return checkbox_element.is_selected
                else:
                    # 检查checked属性
                    checked_attr = getattr(checkbox_element, 'checked', None)
                    if checked_attr is not None:
                        return bool(checked_attr)
                    # 检查属性
                    if hasattr(checkbox_element, 'attr'):
                        checked_attr = checkbox_element.attr('checked')
                        return checked_attr is not None and checked_attr != 'false'
                    return False
        except Exception:
            return False


class RadioButtonNode(DrissionPageBaseNode):
    """单选按钮操作节点
    
    选择单选按钮。
    """
    
    def __init__(self, 
                 locator: str = None,
                 by_css: str = None,
                 by_xpath: str = None,
                 by_text: str = None,
                 by_tag: str = None,
                 by_attr: tuple = None,
                 value: str = None,
                 timeout: float = 10.0,
                 **kwargs):
        """
        初始化单选按钮操作节点
        
        Args:
            locator: 通用定位器
            by_css: CSS选择器
            by_xpath: XPath表达式
            by_text: 文本内容
            by_tag: 标签名
            by_attr: 属性元组
            value: 单选按钮的值
            timeout: 超时时间
        """
        super().__init__(
            name="单选按钮操作",
            description=f"选择单选按钮: {value or '指定选项'}",
            **kwargs
        )
        
        self.locator = locator
        self.by_css = by_css
        self.by_xpath = by_xpath
        self.by_text = by_text
        self.by_tag = by_tag
        self.by_attr = by_attr
        self.value = value
        self.timeout = timeout
        
        self.node_type = "drissionpage_radio_button"
    
    def execute(self, context: CONTEXT) -> Dict[str, Any]:
        """执行单选按钮操作
        
        Args:
            context: 工作流上下文
            
        Returns:
            执行结果
        """
        try:
            # 查找单选按钮元素
            radio_element = self._find_element(
                context=context,
                locator=self.locator,
                by_css=self.by_css,
                by_xpath=self.by_xpath,
                by_text=self.by_text,
                by_tag=self.by_tag,
                by_attr=self.by_attr,
                timeout=self.timeout
            )
            
            if radio_element is None:
                return {
                    'success': False,
                    'error': '未找到单选按钮元素',
                    'message': '单选按钮操作失败: 未找到单选按钮元素'
                }
            
            # 点击选择单选按钮
            radio_element.click()
            
            # 获取选中的值
            selected_value = self._get_radio_value(radio_element)
            
            # 更新上下文
            context['last_radio_element'] = radio_element
            context['selected_radio_value'] = selected_value
            context['form_data'] = context.get('form_data', {})
            
            return {
                'success': True,
                'selected_value': selected_value,
                'expected_value': self.value,
                'element_tag': getattr(radio_element, 'tag', 'unknown'),
                'message': f"成功选择单选按钮: {selected_value}"
            }
            
        except Exception as e:
            error_msg = self._handle_error(context, e)
            return {
                'success': False,
                'error': error_msg,
                'message': f"单选按钮操作失败: {error_msg}"
            }
    
    def _get_radio_value(self, radio_element) -> str:
        """获取单选按钮的值"""
        try:
            # 尝试获取value属性
            if hasattr(radio_element, 'attr'):
                value = radio_element.attr('value')
                if value:
                    return value
            
            # 尝试获取文本内容
            if hasattr(radio_element, 'text'):
                text = radio_element.text
                if text:
                    return text
            
            # 返回预期值或默认值
            return self.value or '已选择'
            
        except Exception:
            return self.value or '已选择'


class SubmitFormNode(DrissionPageBaseNode):
    """提交表单节点
    
    提交指定的表单。
    """
    
    def __init__(self, 
                 locator: str = None,
                 by_css: str = None,
                 by_xpath: str = None,
                 by_text: str = None,
                 by_tag: str = None,
                 by_attr: tuple = None,
                 submit_button_locator: str = None,
                 submit_by_enter: bool = False,
                 wait_after_submit: float = 2.0,
                 timeout: float = 10.0,
                 **kwargs):
        """
        初始化提交表单节点
        
        Args:
            locator: 表单定位器
            by_css: CSS选择器
            by_xpath: XPath表达式
            by_text: 文本内容
            by_tag: 标签名
            by_attr: 属性元组
            submit_button_locator: 提交按钮定位器
            submit_by_enter: 是否通过回车键提交
            wait_after_submit: 提交后等待时间
            timeout: 超时时间
        """
        super().__init__(
            name="提交表单",
            description="提交表单",
            **kwargs
        )
        
        self.locator = locator
        self.by_css = by_css
        self.by_xpath = by_xpath
        self.by_text = by_text
        self.by_tag = by_tag
        self.by_attr = by_attr
        self.submit_button_locator = submit_button_locator
        self.submit_by_enter = submit_by_enter
        self.wait_after_submit = wait_after_submit
        self.timeout = timeout
        
        self.node_type = "drissionpage_submit_form"
    
    def execute(self, context: CONTEXT) -> Dict[str, Any]:
        """执行提交表单
        
        Args:
            context: 工作流上下文
            
        Returns:
            执行结果
        """
        try:
            page = self._get_page_instance(context)
            if page is None:
                return {
                    'success': False,
                    'error': '未找到页面实例',
                    'message': '提交表单失败: 未找到页面实例'
                }
            
            # 记录提交前的URL
            before_url = self._get_page_url(page)
            
            # 执行提交
            if self.submit_by_enter:
                # 通过回车键提交
                self._submit_by_enter(context, page)
            elif self.submit_button_locator:
                # 通过点击提交按钮
                self._submit_by_button(context, page)
            else:
                # 查找表单并提交
                self._submit_form_element(context, page)
            
            # 等待提交完成
            if self.wait_after_submit > 0:
                import time
                time.sleep(self.wait_after_submit)
            
            # 记录提交后的URL
            after_url = self._get_page_url(page)
            url_changed = before_url != after_url
            
            # 更新上下文
            context['form_submitted'] = True
            context['url_before_submit'] = before_url
            context['url_after_submit'] = after_url
            context['url_changed'] = url_changed
            
            return {
                'success': True,
                'url_changed': url_changed,
                'before_url': before_url,
                'after_url': after_url,
                'submit_method': 'enter' if self.submit_by_enter else 'button' if self.submit_button_locator else 'form',
                'message': f"表单提交成功，URL{'已变化' if url_changed else '未变化'}"
            }
            
        except Exception as e:
            error_msg = self._handle_error(context, e)
            return {
                'success': False,
                'error': error_msg,
                'message': f"提交表单失败: {error_msg}"
            }
    
    def _submit_by_enter(self, context: CONTEXT, page):
        """通过回车键提交"""
        try:
            if isinstance(page, ChromiumPage):
                # 在当前焦点元素上按回车
                page.key.enter()
            else:
                raise Exception("SessionPage不支持按键操作")
        except Exception as e:
            raise Exception(f"回车提交失败: {str(e)}")
    
    def _submit_by_button(self, context: CONTEXT, page):
        """通过点击提交按钮"""
        try:
            # 查找提交按钮
            submit_button = page.ele(self.submit_button_locator)
            if submit_button is None:
                raise Exception(f"未找到提交按钮: {self.submit_button_locator}")
            
            # 点击提交按钮
            submit_button.click()
            
        except Exception as e:
            raise Exception(f"按钮提交失败: {str(e)}")
    
    def _submit_form_element(self, context: CONTEXT, page):
        """通过表单元素提交"""
        try:
            # 查找表单元素
            form_element = None
            if any([self.locator, self.by_css, self.by_xpath, self.by_text, self.by_tag, self.by_attr]):
                form_element = self._find_element(
                    context=context,
                    locator=self.locator,
                    by_css=self.by_css,
                    by_xpath=self.by_xpath,
                    by_text=self.by_text,
                    by_tag=self.by_tag,
                    by_attr=self.by_attr,
                    timeout=self.timeout
                )
            
            if form_element is None:
                # 查找页面中的第一个表单
                form_element = page.ele('form')
            
            if form_element is None:
                raise Exception("未找到表单元素")
            
            # 提交表单
            if hasattr(form_element, 'submit'):
                form_element.submit()
            else:
                # 查找表单中的提交按钮
                submit_button = form_element.ele('input[type="submit"]') or form_element.ele('button[type="submit"]') or form_element.ele('button')
                if submit_button:
                    submit_button.click()
                else:
                    raise Exception("表单中未找到提交按钮")
            
        except Exception as e:
            raise Exception(f"表单提交失败: {str(e)}")
    
    def _get_page_url(self, page) -> str:
        """获取页面URL"""
        try:
            if hasattr(page, 'url'):
                return page.url or ''
            return ''
        except Exception:
            return ''


class ResetFormNode(DrissionPageBaseNode):
    """重置表单节点
    
    重置指定的表单。
    """
    
    def __init__(self, 
                 locator: str = None,
                 by_css: str = None,
                 by_xpath: str = None,
                 by_text: str = None,
                 by_tag: str = None,
                 by_attr: tuple = None,
                 reset_button_locator: str = None,
                 timeout: float = 10.0,
                 **kwargs):
        """
        初始化重置表单节点
        
        Args:
            locator: 表单定位器
            by_css: CSS选择器
            by_xpath: XPath表达式
            by_text: 文本内容
            by_tag: 标签名
            by_attr: 属性元组
            reset_button_locator: 重置按钮定位器
            timeout: 超时时间
        """
        super().__init__(
            name="重置表单",
            description="重置表单",
            **kwargs
        )
        
        self.locator = locator
        self.by_css = by_css
        self.by_xpath = by_xpath
        self.by_text = by_text
        self.by_tag = by_tag
        self.by_attr = by_attr
        self.reset_button_locator = reset_button_locator
        self.timeout = timeout
        
        self.node_type = "drissionpage_reset_form"
    
    def execute(self, context: CONTEXT) -> Dict[str, Any]:
        """执行重置表单
        
        Args:
            context: 工作流上下文
            
        Returns:
            执行结果
        """
        try:
            page = self._get_page_instance(context)
            if page is None:
                return {
                    'success': False,
                    'error': '未找到页面实例',
                    'message': '重置表单失败: 未找到页面实例'
                }
            
            # 执行重置
            if self.reset_button_locator:
                # 通过点击重置按钮
                self._reset_by_button(page)
            else:
                # 查找表单并重置
                self._reset_form_element(context, page)
            
            # 更新上下文
            context['form_reset'] = True
            
            return {
                'success': True,
                'reset_method': 'button' if self.reset_button_locator else 'form',
                'message': '表单重置成功'
            }
            
        except Exception as e:
            error_msg = self._handle_error(context, e)
            return {
                'success': False,
                'error': error_msg,
                'message': f"重置表单失败: {error_msg}"
            }
    
    def _reset_by_button(self, page):
        """通过点击重置按钮"""
        try:
            # 查找重置按钮
            reset_button = page.ele(self.reset_button_locator)
            if reset_button is None:
                raise Exception(f"未找到重置按钮: {self.reset_button_locator}")
            
            # 点击重置按钮
            reset_button.click()
            
        except Exception as e:
            raise Exception(f"按钮重置失败: {str(e)}")
    
    def _reset_form_element(self, context: CONTEXT, page):
        """通过表单元素重置"""
        try:
            # 查找表单元素
            form_element = None
            if any([self.locator, self.by_css, self.by_xpath, self.by_text, self.by_tag, self.by_attr]):
                form_element = self._find_element(
                    context=context,
                    locator=self.locator,
                    by_css=self.by_css,
                    by_xpath=self.by_xpath,
                    by_text=self.by_text,
                    by_tag=self.by_tag,
                    by_attr=self.by_attr,
                    timeout=self.timeout
                )
            
            if form_element is None:
                # 查找页面中的第一个表单
                form_element = page.ele('form')
            
            if form_element is None:
                raise Exception("未找到表单元素")
            
            # 重置表单
            if hasattr(form_element, 'reset'):
                form_element.reset()
            else:
                # 查找表单中的重置按钮
                reset_button = form_element.ele('input[type="reset"]') or form_element.ele('button[type="reset"]')
                if reset_button:
                    reset_button.click()
                else:
                    raise Exception("表单中未找到重置按钮")
            
        except Exception as e:
            raise Exception(f"表单重置失败: {str(e)}")