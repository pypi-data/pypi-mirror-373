from typing import Optional

from rpaworkflow.node import ActionNode
from rpaworkflow.uiautomator2.nodes.base import U2BaseNode
from rpaworkflow.uiautomator2.workflow_context import CONTEXT


class StopAppNode(U2BaseNode, ActionNode):

    def __init__(self,
                 name: str = "停止应用",
                 description: str = "停止Android应用",
                 package_name: Optional[str] = None,
                 device_id: Optional[str] = None,
                 **kwargs):
        super().__init__(name, description, device_id=device_id, **kwargs)
        self.package_name = package_name

    def execute(self, context: CONTEXT) -> None:
        """执行应用启动

        Args:
            context: 工作流上下文
        """
        package_name = self.package_name

        if not package_name:
            raise ValueError("必须指定package_name")


        device = self.get_device(context)
        device.app_stop(self.package_name)

        self.logger.info(f"停止应用 {package_name} 成功")

