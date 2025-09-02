

class ContextReference:
    """上下文引用对象"""

    def __init__(self, key: str):
        self.key = key


def ctx(key: str) -> ContextReference:
    return ContextReference(key)
