from rpaworkflow.context import CONTEXT
from rpaworkflow.node import ActionNode, DataStorageNode
from rpaworkflow.exception import NodeError


class ErrorNode(ActionNode):
    """异常错误节点"""

    def __init__(self, name: str = '错误节点', description: str = '', error=None, **kwargs):
        super().__init__(name, description, **kwargs)
        self.error = error

    def execute(self, context: CONTEXT) -> None:
        assert self.error, '错误节点错误信息不能为空'

        if isinstance(self.error, Exception):
            raise self.error

        raise NodeError(self.error)


class ErrorStorageNode(DataStorageNode):

    def __init__(self, name: str = '错误节点', description: str = '', output_key='error', error=None, **kwargs):
        super().__init__(name, description, output_key=output_key, **kwargs)
        self.error = error

    def execute(self, context: CONTEXT) -> None:
        assert self.error, '错误节点错误信息不能为空'

        error = self.error
        if not isinstance(self.error, Exception):
            error = NodeError(self.error)

        self.store_data(context, error)

        raise error
