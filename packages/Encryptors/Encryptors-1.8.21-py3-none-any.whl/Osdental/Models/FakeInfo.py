from types import SimpleNamespace
from Osdental.Shared.Enums.GrahpqlOperation import GraphqlOperation

class FakeInfo:
    
    def __init__(self, context: dict, operation_name=GraphqlOperation.QUERY):
        self.context = context
        self.operation = SimpleNamespace(operation=operation_name)