from typing import Callable

from rpaworkflow.context import CONTEXT
from rpaworkflow.node import ActionNode, WorkflowNode, NodeStatus
from rpaworkflow.exception import NodeError


class ConditionNode(ActionNode):
    """条件节点"""

    def __init__(self, name: str = '条件节点', description: str = '条件节点',
                 condition: Callable[[CONTEXT], bool] = None,
                 true_node: WorkflowNode[CONTEXT] = None,
                 false_node: WorkflowNode[CONTEXT] = None,
                 **kwargs):
        super().__init__(name, description, **kwargs)
        self.condition = condition
        self.true_node = true_node
        self.false_node = false_node

    def execute(self, context: CONTEXT) -> None:
        # 检查条件函数是否存在
        if self.condition is None:
            raise NodeError(f'条件节点 {self.name} 未设置条件函数')
            
        # 根据条件选择分支
        if self.condition(context):
            node = self.true_node
        else:
            node = self.false_node
            
        # 检查选择的分支是否存在
        if node is None:
            raise NodeError(f'条件节点 {self.name} 未设置当前条件分支')

        # 执行选择的分支并处理错误
        status = node.run(context)
        if status != NodeStatus.SUCCESS:
            # 保留原始异常信息
            if hasattr(node, 'exception_info') and node.exception_info:
                raise NodeError(f'节点[{node.exception_info.node_name}]异常, 异常信息: {node.exception_info.error_message}\n{node.exception_info.traceback_info}')
            else:
                raise NodeError(f'节点[{node.name}]执行失败，状态: {status}')

