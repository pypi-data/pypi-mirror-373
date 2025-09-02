from typing import Type

from rpaworkflow.context import CONTEXT
from rpaworkflow.func.ctx import ContextReference
from rpaworkflow.node import WorkflowNode


class DelayWorkflowNode(WorkflowNode[CONTEXT]):
    """延迟节点"""

    def __init__(self, node_cls: Type[WorkflowNode]=None, **node_kwargs):
        super().__init__('延迟节点', '')
        self.node_cls = node_cls
        self.node_kwargs = node_kwargs

    def execute(self, context: CONTEXT) -> None:
        # 注入延迟上下文属性
        for k, v in self.node_kwargs.items():
            if isinstance(v, ContextReference):
                self.node_kwargs[k] = context[v.key]

        self.node_cls(**self.node_kwargs).run(context)
