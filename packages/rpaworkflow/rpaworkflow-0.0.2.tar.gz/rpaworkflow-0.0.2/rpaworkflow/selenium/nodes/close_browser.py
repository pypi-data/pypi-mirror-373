#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
关闭浏览器节点
"""

from rpaworkflow.selenium.nodes.base import SeleniumBaseNode
from rpaworkflow.selenium.workflow_context import CONTEXT
from rpaworkflow.node import ActionNode


class CloseBrowserNode(SeleniumBaseNode, ActionNode):
    """关闭浏览器节点

    用于关闭浏览器窗口或退出浏览器
    不返回数据，只执行关闭操作
    """

    def __init__(self,
                 name: str = "关闭浏览器",
                 description: str = "关闭浏览器窗口或退出浏览器",
                 close_type: str = "quit",  # close, quit
                 **kwargs):
        super().__init__(name, description, **kwargs)
        self.close_type = close_type

    def execute(self, context: CONTEXT) -> None:
        """执行关闭浏览器操作

        Args:
            context: 工作流上下文
        """
        # 从上下文或构造函数获取参数
        close_type = self.close_type

        driver = self.get_driver(context)
        
        if close_type == "close":
            # 关闭当前窗口
            driver.close()
            self.logger.info("当前浏览器窗口已关闭")
        elif close_type == "quit":
            # 退出浏览器（关闭所有窗口）
            driver.quit()
            self.logger.info("浏览器已退出")
            # 清理上下文中的驱动
            context['driver'] = None
        else:
            raise ValueError(f"不支持的关闭类型: {close_type}")