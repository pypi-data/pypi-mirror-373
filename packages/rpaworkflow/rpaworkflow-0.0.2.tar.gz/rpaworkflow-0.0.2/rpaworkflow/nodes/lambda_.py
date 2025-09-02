from typing import Callable, Any

from rpaworkflow.node import ActionNode, DataStorageNode
from rpaworkflow.context import CONTEXT
from rpaworkflow.exception import NodeError


class LambdaActionNode(ActionNode):

    def execute(self, context: CONTEXT) -> None:
        if self.lambda_func is None:
            raise NodeError("Lambda函数不能为空")
        self.lambda_func(context)
        self.logger.info(f"LambdaActionNode: {self.name}")

    def __init__(self,
                 name: str = "Lambda Action",
                 description: str = "Lambda Action",
                 lambda_func: Callable[[CONTEXT], None] = None,
                 **kwargs):
        super().__init__(name, description, **kwargs)
        self.lambda_func = lambda_func


class LambdaDataStorageNode(DataStorageNode):

    def execute(self, context: CONTEXT) -> None:
        if self.lambda_func is None:
            raise NodeError("Lambda函数不能为空")
        result = self.lambda_func(context)
        self.store_data(context, result)
        self.logger.info(f"LambdaDataStorageNode: {self.output_key} = {result}")

    def __init__(self,
                 name: str = "Lambda Data Storage Node",
                 description: str = "Lambda Data Storage",
                 output_key: str = 'lambda_data_storage_key',
                 lambda_func: Callable[[CONTEXT], Any] = None,
                 **kwargs):
        super().__init__(name, description, output_key=output_key, **kwargs)
        self.lambda_func = lambda_func
