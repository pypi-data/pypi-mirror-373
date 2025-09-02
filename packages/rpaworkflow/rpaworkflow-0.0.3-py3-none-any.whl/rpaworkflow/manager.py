import json
import time
import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import List, Dict, Any, Optional, Callable, Type

from loguru import logger

from .context import CONTEXT, create_workflow_context, WorkflowContext
from .node import WorkflowNode, NodeStatus, NodeException


class WorkflowStatus(Enum):
    """工作流状态枚举"""
    PENDING = "pending"  # 等待执行
    RUNNING = "running"  # 正在执行
    SUCCESS = "success"  # 执行成功
    FAILED = "failed"  # 执行失败
    PAUSED = "paused"  # 暂停
    CANCELLED = "cancelled"  # 取消


@dataclass
class WorkflowResult:
    """工作流执行结果"""
    status: WorkflowStatus
    total_nodes: int
    success_nodes: int
    failed_nodes: int
    skipped_nodes: int
    execution_time: float
    node_executions: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    context: Optional[CONTEXT] = None
    error_message: Optional[str] = None
    error_node: Optional[WorkflowNode] = None


class WorkflowManager:
    """工作流管理器"""

    def __init__(self, name: str, description: str = "", workflow_id: str = None,
                 context_cls: Type[CONTEXT] = WorkflowContext,
                 continue_on_failure: bool = False,
                 max_failures: int = None):
        """
        初始化工作流管理器
        
        Args:
            name: 工作流名称
            description: 工作流描述
            workflow_id: 工作流ID，如果不提供则自动生成
            context_cls: 上下文类型
            continue_on_failure: 节点失败时是否继续执行后续节点
            max_failures: 最大允许失败节点数，超过此数量将停止工作流，仅当continue_on_failure=True时有效
        """
        self.name = name
        self.description = description
        self.workflow_id = workflow_id or str(uuid.uuid4())
        self.nodes: List[WorkflowNode] = []
        self.context: CONTEXT = create_workflow_context(
            workflow_id=self.workflow_id,
            workflow_name=name,
            execution_id=str(uuid.uuid4()),
            ctx_cls=context_cls,
        )
        self.status = WorkflowStatus.PENDING
        self.current_node_index = 0
        self.start_time: Optional[float] = None
        self.end_time: Optional[float] = None
        
        # 错误处理配置
        self.continue_on_failure = continue_on_failure
        self.max_failures = max_failures

        # 结束额外节点, 无论异常与否均会执行, 且不保障执行状态
        self.finally_node = None

        # 全局异常处理器
        self.global_exception_handler: Optional[Callable[[NodeException, CONTEXT], bool]] = None

        # 工作流事件回调
        self.on_workflow_start: Optional[Callable] = None
        self.on_workflow_complete: Optional[Callable] = None
        self.on_node_start: Optional[Callable] = None
        self.on_node_complete: Optional[Callable] = None
        self.on_workflow_error: Optional[Callable] = None
        logger.info(f'创建工作流: {name}')

    def set_finally_node(self, node: WorkflowNode):
        self.finally_node = node
        logger.info(f"设置结束节点: {node.name} 为工作流 {self.name} 的结束节点")

    def add_node(self, node: WorkflowNode) -> 'WorkflowManager':
        """添加节点

        Args:
            node: 工作流节点V2

        Returns:
            WorkflowManager: 返回自身，支持链式调用
        """
        self.nodes.append(node)

        # 如果设置了全局异常处理器，为节点设置异常处理器
        if self.global_exception_handler:
            node.set_exception_handler(self.global_exception_handler)

        logger.info(f"添加节点: {node.name} 到工作流 {self.name}")
        return self

    def add_nodes(self, nodes: List[WorkflowNode]) -> 'WorkflowManager':
        """批量添加节点

        Args:
            nodes: 节点列表

        Returns:
            WorkflowManager: 返回自身，支持链式调用
        """
        for node in nodes:
            self.add_node(node)
        return self

    def set_context(self, key: str, value: Any) -> 'WorkflowManager':
        """设置上下文数据

        Args:
            key: 键
            value: 值

        Returns:
            WorkflowManager: 返回自身，支持链式调用
        """
        self.context[key] = value  # type: ignore
        return self

    def get_context(self, key: str, default: Any = None) -> Any:
        """获取上下文数据

        Args:
            key: 键
            default: 默认值

        Returns:
            Any: 上下文值
        """
        return self.context.get(key, default)  # type: ignore

    def update_context(self, data: Dict[str, Any]) -> 'WorkflowManager':
        """更新上下文数据

        Args:
            data: 要更新的数据

        Returns:
            WorkflowManager: 返回自身，支持链式调用
        """
        self.context.update(data)
        return self

    def set_global_exception_handler(self, handler: Callable[[NodeException, CONTEXT], bool]):
        """设置全局异常处理器

        Args:
            handler: 异常处理函数，接收NodeException和WorkflowContext，返回bool表示是否恢复成功
        """
        self.global_exception_handler = handler

        # 为所有已添加的节点设置异常处理器
        for node in self.nodes:
            node.set_exception_handler(handler)

    def get_workflow_state(self) -> Dict[str, Any]:
        """获取工作流当前状态

        Returns:
            Dict[str, Any]: 工作流状态信息
        """
        return {
            "workflow_id": self.workflow_id,
            "workflow_name": self.name,
            "workflow_status": self.status.value,
            "total_nodes": len(self.nodes),
            "current_node_index": self.current_node_index,
            "current_node_name": self.nodes[self.current_node_index].name if self.current_node_index < len(
                self.nodes) else None,
            "completed_nodes": [
                {
                    "name": node.name,
                    "status": node.status.value,
                    "execution_time": (node.end_time - node.start_time) if node.start_time and node.end_time else 0,
                    "retry_count": node.retry_count,
                    "last_error": node.last_error
                }
                for i, node in enumerate(self.nodes) if i < self.current_node_index
            ],
            "context": dict(self.context)
        }

    def run(self, start_from: int = 0) -> WorkflowResult:
        """执行工作流

        Args:
            start_from: 从第几个节点开始执行

        Returns:
            WorkflowResult: 工作流执行结果
        """
        if not self.nodes:
            logger.warning(f"工作流 {self.name} 没有节点，无法执行")
            return WorkflowResult(
                status=WorkflowStatus.FAILED,
                total_nodes=0,
                success_nodes=0,
                failed_nodes=0,
                skipped_nodes=0,
                execution_time=0,
                error_message="工作流没有节点"
            )

        self.status = WorkflowStatus.RUNNING
        self.start_time = time.time()
        self.current_node_index = start_from

        logger.info(f"开始执行工作流: {self.name}，共 {len(self.nodes)} 个节点")

        # 触发工作流开始事件
        if self.on_workflow_start:
            try:
                self.on_workflow_start(self)
            except Exception as e:
                logger.error(f"工作流开始事件回调执行失败: {str(e)}")

        last_node = None
        node_results = {}
        success_count = 0
        failed_count = 0
        skipped_count = 0

        try:
            # 执行节点
            for i in range(start_from, len(self.nodes)):
                last_node = self.nodes[i]
                self.current_node_index = i
                node = self.nodes[i]

                logger.info(f"执行节点 {i + 1}/{len(self.nodes)}: {node.name}")

                # 触发节点开始事件
                if self.on_node_start:
                    try:
                        self.on_node_start(node, self)
                    except Exception as e:
                        logger.error(f"节点开始事件回调执行失败: {str(e)}")

                # 执行节点 - 使用新的v2节点接口
                node_status = node.run(self.context)

                # 获取节点执行信息
                execution_info = node.get_execution_info()
                node_results[node.name] = execution_info

                # 触发节点完成事件
                if self.on_node_complete:
                    try:
                        self.on_node_complete(node, execution_info, self)
                    except Exception as e:
                        logger.error(f"节点完成事件回调执行失败: {str(e)}")

                # 统计结果
                if node_status == NodeStatus.SUCCESS:
                    success_count += 1
                elif node_status == NodeStatus.FAILED:
                    failed_count += 1
                    
                    # 根据配置决定是否继续执行
                    if self.continue_on_failure:
                        # 检查是否超过最大失败数
                        if self.max_failures is not None and failed_count >= self.max_failures:
                            logger.error(f"节点 {node.name} 执行失败，已达到最大失败数 {self.max_failures}，停止工作流")
                            break
                        logger.warning(f"节点 {node.name} 执行失败，但配置为继续执行后续节点")
                    else:
                        # 默认行为：节点失败，停止执行
                        logger.error(f"节点 {node.name} 执行失败，停止工作流")
                        break
                elif node_status == NodeStatus.SKIPPED:
                    skipped_count += 1

            # 判断工作流执行结果
            if failed_count > 0:
                self.status = WorkflowStatus.FAILED
            else:
                self.status = WorkflowStatus.SUCCESS

        except Exception as e:
            logger.error(f"工作流 {self.name} 执行异常: {str(e)}")
            self.status = WorkflowStatus.FAILED

            # 触发工作流错误事件
            if self.on_workflow_error:
                try:
                    self.on_workflow_error(e, self)
                except Exception as callback_error:
                    logger.error(f"工作流错误事件回调执行失败: {str(callback_error)}")

        finally:
            if self.finally_node:
                self.finally_node.run(self.context)

        self.end_time = time.time()
        execution_time = self.end_time - self.start_time

        # 创建工作流结果
        workflow_result = WorkflowResult(
            status=self.status,
            total_nodes=len(self.nodes),
            success_nodes=success_count,
            failed_nodes=failed_count,
            skipped_nodes=skipped_count,
            execution_time=execution_time,
            node_executions=node_results,
            context=self.context,
            error_message=f'节点[{last_node.exception_info.node_name}]异常, 异常信息: {last_node.exception_info.error_message}\n{last_node.exception_info.traceback_info}' if last_node and last_node.exception_info else None,
            error_node=last_node if last_node and last_node.exception_info else None,
        )

        logger.info(f"工作流 {self.name} 执行完成，状态: {self.status.value}")
        logger.info(
            f"执行时间: {execution_time:.2f}秒，成功: {success_count}，失败: {failed_count}，跳过: {skipped_count}")

        # 触发工作流完成事件
        if self.on_workflow_complete:
            try:
                self.on_workflow_complete(workflow_result, self)
            except Exception as e:
                logger.error(f"工作流完成事件回调执行失败: {str(e)}")

        return workflow_result

    def pause(self):
        """暂停工作流"""
        if self.status == WorkflowStatus.RUNNING:
            self.status = WorkflowStatus.PAUSED
            logger.info(f"工作流 {self.name} 已暂停")

    def resume(self):
        """恢复工作流"""
        if self.status == WorkflowStatus.PAUSED:
            self.status = WorkflowStatus.RUNNING
            logger.info(f"工作流 {self.name} 已恢复")

    def cancel(self):
        """取消工作流"""
        self.status = WorkflowStatus.CANCELLED
        logger.info(f"工作流 {self.name} 已取消")

    def reset(self):
        """重置工作流"""
        self.status = WorkflowStatus.PENDING
        self.current_node_index = 0
        self.start_time = None
        self.end_time = None

        # 重置所有节点
        for node in self.nodes:
            node.reset()

        logger.info(f"工作流 {self.name} 已重置")

    def get_node_by_name(self, name: str) -> Optional[WorkflowNode]:
        """根据名称获取节点

        Args:
            name: 节点名称

        Returns:
            Optional[WorkflowNode]: 节点对象，如果不存在返回None
        """
        for node in self.nodes:
            if node.name == name:
                return node
        return None

    def export_state(self) -> str:
        """导出工作流状态为JSON字符串

        Returns:
            str: JSON格式的状态信息
        """
        state = self.get_workflow_state()
        return json.dumps(state, ensure_ascii=False, indent=2)

    def __str__(self):
        return f"WorkflowManager(name={self.name}, nodes={len(self.nodes)}, status={self.status.value})"

    def __repr__(self):
        return self.__str__()
