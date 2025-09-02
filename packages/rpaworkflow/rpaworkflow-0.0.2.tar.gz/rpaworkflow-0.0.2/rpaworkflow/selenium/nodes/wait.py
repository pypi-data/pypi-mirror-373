#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
等待节点
"""

import time
from typing import Optional, Callable

from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from rpaworkflow.node import ActionNode
from rpaworkflow.selenium.nodes.base import SeleniumBaseNode
from rpaworkflow.selenium.workflow_context import CONTEXT


class WaitNode(SeleniumBaseNode, ActionNode):
    """等待节点

    用于等待元素出现、消失或其他条件满足
    不返回数据，只执行等待操作
    """

    def __init__(self,
                 name: str = "等待操作",
                 description: str = "等待元素或条件",
                 wait_type: str = "presence",  # presence, visibility, clickable, invisibility, time
                 by: Optional[str] = None,
                 value: Optional[str] = None,
                 timeout: int = 10,
                 poll_frequency: float = 0.5,
                 **kwargs):
        super().__init__(name, description, **kwargs)
        self.wait_type = wait_type
        self.by = by
        self.value = value
        self.timeout = timeout
        self.poll_frequency = poll_frequency

    def _get_wait_condition(self, by: str, value: str) -> Callable:
        """获取等待条件
        
        Args:
            by: 定位方式
            value: 定位值
            
        Returns:
            Callable: 等待条件
        """
        if self.wait_type == "presence":
            return EC.presence_of_element_located((by, value))
        elif self.wait_type == "visibility":
            return EC.visibility_of_element_located((by, value))
        elif self.wait_type == "clickable":
            return EC.element_to_be_clickable((by, value))
        elif self.wait_type == "invisibility":
            return EC.invisibility_of_element_located((by, value))
        elif self.wait_type == "text_present":
            return EC.text_to_be_present_in_element((by, value), self.text)
        elif self.wait_type == "title_contains":
            return EC.title_contains(value)
        elif self.wait_type == "url_contains":
            return EC.url_contains(value)
        else:
            raise ValueError(f"不支持的等待类型: {self.wait_type}")

    def execute(self, context: CONTEXT) -> None:
        """执行等待操作

        Args:
            context: 工作流上下文
        """
        # 从上下文或构造函数获取参数
        wait_type = self.wait_type
        by = self.by
        value = self.value
        timeout = self.timeout
        poll_frequency = self.poll_frequency

        driver = self.get_driver(context)

        if wait_type == "time":
            # 简单的时间等待
            self.logger.info(f"等待时间: {timeout}秒")
            time.sleep(timeout)
            return

        if not (by and value) and wait_type not in ["title_contains", "url_contains"]:
            raise ValueError("必须指定by和value，或者使用title_contains/url_contains等特殊等待类型")

        # 创建WebDriverWait对象
        wait = WebDriverWait(driver, timeout, poll_frequency=poll_frequency)

        # 获取等待条件
        condition = self._get_wait_condition(by, value)

        # 执行等待
        self.logger.info(f"等待条件: {wait_type}, {by}={value}, 超时: {timeout}秒")
        result = wait.until(condition)

        # 如果等待成功且返回了元素，存储到上下文
        if result and wait_type not in ["invisibility", "title_contains", "url_contains"]:
            context['last_element'] = result
            self.logger.info(f"等待条件满足，元素已找到")
        else:
            self.logger.info(f"等待条件满足")