from rpaworkflow.context import CONTEXT
from rpaworkflow.node import ActionNode


class EmptyNode(ActionNode):

    def execute(self, context: CONTEXT) -> None:
        pass

    def __init__(self,
                 name: str = "空节点",
                 description: str = "空节点, 不做任何事, 可用作占位符节点",
                 **kwargs):
        super().__init__(name, description, **kwargs)

