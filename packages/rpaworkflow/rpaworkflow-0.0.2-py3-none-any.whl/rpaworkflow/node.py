#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
工作流节点基类 V2 - 优化版本

主要改进：
1. 使用TypedDict定义的上下文
2. 节点不返回数据，而是将数据存储到上下文
3. 通过构造函数参数指定数据存储的key
4. 简化执行逻辑
"""
import pdb
import time
import traceback
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any, Dict, Optional, Callable, List, Generic

from loguru import logger

from rpaworkflow.context import CONTEXT
from rpaworkflow.exception import NodeError


class NodeStatus(Enum):
    """节点状态枚举"""
    PENDING = "pending"      # 等待执行
    RUNNING = "running"      # 正在执行
    SUCCESS = "success"      # 执行成功
    FAILED = "failed"        # 执行失败
    RETRYING = "retrying"    # 重试中
    SKIPPED = "skipped"      # 跳过
    WARNING = "warning"      # 警告（执行成功但有问题）


@dataclass
class NodeException:
    """节点异常信息"""
    node_name: str
    error_message: str
    error_type: str
    traceback_info: str
    timestamp: datetime
    screenshot_path: Optional[str] = None
    context_snapshot: Optional[Dict[str, Any]] = None

    def __str__(self):
        return f"{self.node_name} 节点执行异常：{self.error_message}\n{self.traceback_info}"


class WorkflowNode(ABC, Generic[CONTEXT]):
    """工作流节点基类

    主要特性：
    1. 不返回数据，数据存储到上下文
    2. 支持指定数据存储的key
    3. 简化的执行逻辑
    4. 更好的错误处理
    """

    def __init__(self,
                 name: str,
                 description: str = "",
                 output_key: Optional[str] = None,
                 max_retries: int = 0,
                 timeout: Optional[float] = None,
                 required_context_keys: Optional[List[str]] = None,
                 ignore_error_logs: bool = False,
                 debugger: bool = False):
        """
        初始化节点

        Args:
            name: 节点名称
            description: 节点描述
            output_key: 输出数据存储到上下文的key，如果为None则不存储输出数据
            max_retries: 最大重试次数
            timeout: 执行超时时间（秒）
            required_context_keys: 必需的上下文键列表
            ignore_error_logs: 忽略异常日志, 当异常情况符合预期时, 将该值设置为true可忽略错误日志
            debugger: 基于pdb的调试模式, 开启后可针对特定节点的execute进行调试
        """
        self.name = name
        self.description = description
        self.output_key = output_key
        self.max_retries = max_retries
        self.timeout = timeout
        self.required_context_keys = required_context_keys or []

        # 运行时状态
        self.status = NodeStatus.PENDING
        self.retry_count = 0
        self.start_time: Optional[float] = None
        self.end_time: Optional[float] = None
        self.last_error: Optional[str] = None

        # 异常处理回调
        self.exception_handler: Optional[Callable[[NodeException, CONTEXT], bool]] = None
        self.ignore_error_logs = ignore_error_logs

        # 日志记录器
        self.logger = logger.bind(node=self.name)
        self.exception_info = None
        self.debugger = debugger

    @abstractmethod
    def execute(self, context: CONTEXT) -> None:
        """执行节点逻辑

        Args:
            context: 工作流上下文

        Note:
            - 不返回数据，如需存储数据请直接修改context
            - 如果设置了output_key，可以调用self.set_output()存储输出数据
            - 如果执行失败，抛出异常即可
        """
        pass

    def validate_context(self, context: CONTEXT) -> bool:
        """验证上下文是否包含必需的键

        Args:
            context: 工作流上下文

        Returns:
            bool: 验证是否通过
        """
        missing_keys = []
        for key in self.required_context_keys:
            if key not in context:
                missing_keys.append(key)

        if missing_keys:
            self.logger.error(f"缺少必需的上下文键: {missing_keys}")
            return False

        return True

    def set_output(self, context: CONTEXT, data: Any) -> None:
        """设置输出数据到上下文

        Args:
            context: 工作流上下文
            data: 要存储的数据
        """
        if self.output_key:
            context[self.output_key] = data
            self.logger.debug(f"输出数据已存储到上下文键: {self.output_key}")
        else:
            self.logger.warning("未设置output_key，无法存储输出数据")

    def get_input(self, context: CONTEXT, key: str, default: Any = None) -> Any:
        """从上下文获取输入数据

        Args:
            context: 工作流上下文
            key: 键名
            default: 默认值

        Returns:
            Any: 输入数据
        """
        return context.get(key, default)

    def set_context_value(self, context: CONTEXT, key: str, value: Any) -> None:
        """设置上下文值

        Args:
            context: 工作流上下文
            key: 键名
            value: 值
        """
        context[key] = value
        self.logger.debug(f"上下文值已设置: {key} = {value}")

    def pre_execute(self, context: CONTEXT) -> bool:
        """执行前的预处理

        Args:
            context: 工作流上下文

        Returns:
            bool: 是否可以继续执行
        """
        # 验证必需的上下文键
        if not self.validate_context(context):
            return False

        # 更新当前节点信息
        context['current_node'] = self.name

        return True

    def post_execute(self, context: CONTEXT, success: bool) -> None:
        """执行后的后处理

        Args:
            context: 工作流上下文
            success: 是否执行成功
        """
        # 记录执行时间
        if self.start_time and self.end_time:
            execution_time = self.end_time - self.start_time
            if 'execution_times' not in context:
                context['execution_times'] = {}
            context['execution_times'][self.name] = execution_time

        # 更新错误计数
        if not success:
            error_count = context.get('error_count', 0)
            context['error_count'] = error_count + 1

    def run(self, context: CONTEXT) -> NodeStatus:
        """运行节点

        Args:
            context: 工作流上下文

        Returns:
            NodeStatus: 节点执行状态
        """
        # 参数验证
        if context is None:
            self.logger.error(f"节点 \"{self.name}\" 执行失败: 上下文不能为空")
            self.status = NodeStatus.FAILED
            return self.status
            
        # 重置异常信息
        self.exception_info = None
        
        # 设置状态和开始时间
        self.status = NodeStatus.RUNNING
        self.start_time = time.time()

        self.logger.info(f"开始执行节点: \"{self.name}\"")

        try:
            # 预处理
            if not self.pre_execute(context):
                self.status = NodeStatus.SKIPPED
                self.end_time = time.time()
                self.logger.info(f"节点 \"{self.name}\" 被跳过")
                return self.status

            # 执行主逻辑
            if self.debugger:
                pdb.runcall(self.execute, context)
            else:
                self.execute(context)

            # 执行成功
            self.status = NodeStatus.SUCCESS
            self.end_time = time.time()

            # 后处理
            self.post_execute(context, True)

            self.logger.info(f"节点 \"{self.name}\" 执行成功")
            return self.status

        except Exception as e:
            self.end_time = time.time()
            error_msg = str(e)
            traceback_info = traceback.format_exc()

            if not self.ignore_error_logs:
                self.logger.error(f"节点 \"{self.name}\" 执行异常: {error_msg}")
                self.logger.error(f"异常堆栈: {traceback_info}")

            # 记录错误信息
            self.last_error = error_msg

            # 创建异常信息
            exception_info = NodeException(
                node_name=self.name,
                error_message=error_msg,
                error_type=type(e).__name__,
                traceback_info=traceback_info,
                timestamp=datetime.now(),
                context_snapshot=dict(context)  # 创建上下文快照
            )

            self.exception_info = exception_info

            recovery_success = True
            # 如果有异常处理器，尝试处理修复异常
            if self.exception_handler:
                # 调用异常处理器
                try:
                    recovery_success = self.exception_handler(exception_info, context)
                    if recovery_success:
                        self.logger.info(f"节点 \"{self.name}\" 异常恢复成功")
                    else:
                        self.logger.warning(f"节点 \"{self.name}\" 异常恢复失败")
                except Exception as recovery_error:
                    if not self.ignore_error_logs:
                        self.logger.error(f"节点 \"{self.name}\" 异常处理器执行失败: {str(recovery_error)}")
                    recovery_success = False

            # 处理重试逻辑
            if self.retry_count < self.max_retries and recovery_success:
                self.retry_count += 1
                self.status = NodeStatus.RETRYING

                self.logger.info(f"节点 \"{self.name}\" 触发异常处理器，第 {self.retry_count} 次重试")
                return self.run(context)


            # 执行失败
            self.status = NodeStatus.FAILED

            # 后处理
            self.post_execute(context, False)

            return self.status

    def set_exception_handler(self, handler: Callable[[NodeException, CONTEXT], bool]):
        """设置异常处理器

        Args:
            handler: 异常处理函数，返回True表示恢复成功，False表示恢复失败
        """
        self.exception_handler = handler

    def reset(self):
        """重置节点状态"""
        self.status = NodeStatus.PENDING
        self.retry_count = 0
        self.start_time = None
        self.end_time = None
        self.last_error = None

    def get_execution_info(self) -> Dict[str, Any]:
        """获取节点执行信息

        Returns:
            Dict[str, Any]: 执行信息
        """
        execution_time = None
        if self.start_time and self.end_time:
            execution_time = self.end_time - self.start_time

        return {
            'name': self.name,
            'description': self.description,
            'status': self.status.value,
            'retry_count': self.retry_count,
            'execution_time': execution_time,
            'last_error': self.last_error,
            'output_key': self.output_key,
            'exception_info': self.exception_info,
        }

    def __str__(self):
        return f"WorkflowNode(name={self.name}, status={self.status.value}, output_key={self.output_key})"

    def __and__(self, other: 'WorkflowNode[CONTEXT]'):
        if isinstance(self, MergeWorkflowNode) and self.merge_type == 'and':
            self.name += ' & ' + other.name
            self.description += ' & ' + other.description
            self.nodes.append(other)
            return self
        return MergeWorkflowNode(name=self.name + ' & ' + other.name,
                                 description=self.description + ' & ' + other.description,
                                 merge_type='and',
                                 nodes=[self, other])

    def __or__(self, other):
        if isinstance(self, MergeWorkflowNode) and self.merge_type == 'or':
            self.name = self.name + ' | ' + other.name
            self.description = self.description + ' | ' + other.description
            self.nodes.append(other)
            return self
        return MergeWorkflowNode(name=self.name + ' | ' + other.name,
                                 description=self.description + ' | ' + other.description,
                                 merge_type='or',
                                 nodes=[self, other])

    def __repr__(self):
        return self.__str__()


class MergeWorkflowNode(WorkflowNode[CONTEXT]):
    """合并工作流节点

    用于将多个工作流节点合并为一个节点，并返回合并后的结果
    """

    def __init__(self,
                 name: str,
                 description: str = "",
                 merge_type: str = 'and',
                 nodes: list[WorkflowNode[CONTEXT]] = None,
                 **kwargs):
        super().__init__(name, description, **kwargs)
        self.merge_type = merge_type
        self.nodes = nodes or []

    def execute(self, context: CONTEXT) -> None:
        node_count = len(self.nodes)
        if node_count == 0:
            return
            
        if self.merge_type == 'and':
            for node in self.nodes:
                status = node.run(context)
                if status != NodeStatus.SUCCESS:
                    self.ignore_error_logs = node.ignore_error_logs
                    # 保留原始异常信息
                    if hasattr(node, 'exception_info') and node.exception_info:
                        error_msg = f"节点 \"{self.name}\" -> \"{node.name}\" 执行失败: {node.exception_info.error_message}"
                        # 使用 raise from 语法链接异常
                        original_error = NodeError(node.exception_info.error_message)
                        raise NodeError(error_msg) from original_error
                    else:
                        raise NodeError(f"节点 \"{self.name}\" -> \"{node.name}\" 执行失败，状态: {status}")
        elif self.merge_type == 'or':
            errors = []
            for node in self.nodes:
                status = node.run(context)
                if status == NodeStatus.SUCCESS:
                    return
                # 收集所有错误信息
                if hasattr(node, 'exception_info') and node.exception_info:
                    errors.append(f"{node.name}: {node.exception_info.error_message}")
                else:
                    errors.append(f"{node.name}: 执行失败，状态: {status}")
            # 所有节点都失败时，提供详细的错误信息
            error_details = "\n".join(errors)
            raise NodeError(f"节点 \"{self.name}\" 执行失败，所有分支均失败:\n{error_details}")
        else:
            raise ValueError("不合法的合并类型, 仅支持and, or")



class DataStorageNode(WorkflowNode[CONTEXT]):
    """数据存储节点基类

    专门用于需要存储数据的节点
    """

    def __init__(self,
                 name: str,
                 description: str = "",
                 output_key: str = None,  # 数据存储节点必须指定output_key
                 **kwargs):
        if not output_key:
            raise ValueError("数据存储节点必须指定output_key参数")

        super().__init__(name, description, output_key=output_key, **kwargs)

    def store_data(self, context: CONTEXT, data: Any) -> None:
        """存储数据到上下文

        Args:
            context: 工作流上下文
            data: 要存储的数据
        """
        self.set_output(context, data)
        self.logger.info(f"数据已存储到上下文键: {self.output_key}")


class ActionNode(WorkflowNode):
    """动作节点基类

    专门用于执行动作但不需要存储数据的节点
    """

    def __init__(self,
                 name: str,
                 description: str = "",
                 **kwargs):
        # 动作节点通常不需要output_key
        super().__init__(name, description, output_key=None, **kwargs)
