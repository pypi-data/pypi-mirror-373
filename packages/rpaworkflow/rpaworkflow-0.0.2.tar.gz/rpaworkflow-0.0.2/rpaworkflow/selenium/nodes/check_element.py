#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
检查元素节点
"""

from selenium.common.exceptions import NoSuchElementException, TimeoutException

from rpaworkflow.node import DataStorageNode
from rpaworkflow.selenium.nodes.base import SeleniumBaseNode
from rpaworkflow.selenium.workflow_context import CONTEXT


class CheckElementNode(SeleniumBaseNode, DataStorageNode):
    """检查元素节点

    用于检查元素是否存在、可见、可点击等
    将检查结果存储到上下文中
    """

    def __init__(self,
                 name: str = "检查元素",
                 description: str = "检查元素状态",
                 by: str = None,
                 value: str = None,
                 check_type: str = "exists",  # exists, visible, clickable, enabled, selected
                 timeout: int = 5,
                 **kwargs):
        super().__init__(name, description, output_key='element_check_result', **kwargs)
        self.by = by
        self.value = value
        self.check_type = check_type
        self.timeout = timeout

    def execute(self, context: CONTEXT) -> None:
        """执行检查元素操作

        Args:
            context: 工作流上下文
        """
        # 从上下文或构造函数获取参数
        by = self.by
        value = self.value
        check_type = self.check_type
        timeout = self.timeout

        if not (by and value):
            raise ValueError("必须指定by和value")

        driver = self.get_driver(context)
        result = False
        element = None
        
        try:
            if check_type == "exists":
                # 检查元素是否存在
                try:
                    element = self.find_element(context, by, value, timeout)
                    result = element is not None
                except (NoSuchElementException, TimeoutException):
                    result = False
                    
            elif check_type == "visible":
                # 检查元素是否可见
                try:
                    element = self.wait_for_element_visible(context, by, value, timeout)
                    result = element.is_displayed()
                except (NoSuchElementException, TimeoutException):
                    result = False
                    
            elif check_type == "clickable":
                # 检查元素是否可点击
                try:
                    element = self.wait_for_element_clickable(context, by, value, timeout)
                    result = element.is_enabled() and element.is_displayed()
                except (NoSuchElementException, TimeoutException):
                    result = False
                    
            elif check_type == "enabled":
                # 检查元素是否启用
                try:
                    element = self.find_element(context, by, value, timeout)
                    result = element.is_enabled()
                except (NoSuchElementException, TimeoutException):
                    result = False
                    
            elif check_type == "selected":
                # 检查元素是否选中（适用于复选框、单选按钮等）
                try:
                    element = self.find_element(context, by, value, timeout)
                    result = element.is_selected()
                except (NoSuchElementException, TimeoutException):
                    result = False
                    
            else:
                raise ValueError(f"不支持的检查类型: {check_type}")
                
        except Exception as e:
            self.logger.error(f"检查元素时发生错误: {str(e)}")
            result = False
        
        # 存储元素到上下文（如果找到了）
        if element:
            context['last_element'] = element
        
        # 存储检查结果到上下文
        check_result = {
            'exists': result,
            'check_type': check_type,
            'by': by,
            'value': value,
            'element': element
        }
        
        self.store_data(context, check_result)
        
        self.logger.info(f"元素检查结果: {by}={value}, {check_type}={result}")