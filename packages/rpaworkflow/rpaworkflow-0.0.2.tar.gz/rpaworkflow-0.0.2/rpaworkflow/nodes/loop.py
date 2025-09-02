from typing import Callable

from rpaworkflow.context import CONTEXT
from rpaworkflow.node import ActionNode, WorkflowNode, NodeStatus
from rpaworkflow.exception import NodeError


class LoopNode(ActionNode):

    def __init__(self, name: str = "循环节点", description: str = "循环节点",
                 loop_condition: Callable[[CONTEXT], bool] = None,
                 loop_node: WorkflowNode[CONTEXT] = None, max_loops: int = -1, **kwargs):
        super().__init__(name, description, **kwargs)
        self.loop_condition = loop_condition
        self.loop_node = loop_node
        self.max_loops = max_loops

    def execute(self, context: CONTEXT) -> None:
        # 检查循环条件和循环节点是否存在
        if self.loop_condition is None:
            raise NodeError(f'循环节点 {self.name} 未设置循环条件')
        if self.loop_node is None:
            raise NodeError(f'循环节点 {self.name} 未设置循环体')
            
        # 记录循环次数，用于调试和监控
        loop_count = 0
        max_loops = self.max_loops
        
        try:
            while self.loop_condition(context):
                loop_count += 1
                if max_loops > 0 and loop_count > max_loops:
                    raise NodeError(f'循环节点 {self.name} 超过最大循环次数 {max_loops}')
                    
                # 执行循环体并处理错误
                status = self.loop_node.run(context)
                if status != NodeStatus.SUCCESS:
                    # 保留原始异常信息
                    if hasattr(self.loop_node, 'exception_info') and self.loop_node.exception_info:
                        raise NodeError(f'循环节点 {self.name} 第 {loop_count} 次循环失败，'
                                       f'节点[{self.loop_node.exception_info.node_name}]异常，'
                                       f'异常信息: {self.loop_node.exception_info.error_message}')
                    else:
                        raise NodeError(f'循环节点 {self.name} 第 {loop_count} 次循环失败，状态: {status}')
        except Exception as e:
            # 将循环次数添加到上下文，便于调试
            context['loop_counts'] = context.get('loop_counts', {}) 
            context['loop_counts'][self.name] = loop_count
            raise e
