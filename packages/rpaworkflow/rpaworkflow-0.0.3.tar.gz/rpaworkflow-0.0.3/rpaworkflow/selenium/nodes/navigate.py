#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
导航节点
"""

from rpaworkflow.node import ActionNode
from rpaworkflow.selenium.nodes.base import SeleniumBaseNode
from rpaworkflow.selenium.workflow_context import CONTEXT


class NavigateNode(SeleniumBaseNode, ActionNode):
    """导航节点

    用于打开指定URL
    不返回数据，只执行导航操作
    """

    def __init__(self,
                 name: str = "导航操作",
                 description: str = "打开指定URL",
                 url: str = None,
                 wait_time: float = 0,
                 **kwargs):
        super().__init__(name, description, **kwargs)
        self.url = url
        self.wait_time = wait_time

    def execute(self, context: CONTEXT) -> None:
        """执行导航操作

        Args:
            context: 工作流上下文
        """
        # 从上下文或构造函数获取参数
        url = self.url
        wait_time = self.wait_time

        if not url:
            raise ValueError("必须指定url")

        driver = self.get_driver(context)

        # 执行导航
        self.logger.info(f"正在导航到: {url}")
        driver.get(url)

        # 等待页面加载
        if wait_time > 0:
            import time
            time.sleep(wait_time)

        # 更新上下文
        context['current_url'] = driver.current_url
        context['page_title'] = driver.title

        self.logger.info(f"导航完成: {driver.title}")