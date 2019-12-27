from .analyzer import Dependency


class ExecutionNode:
    def __init__(self, name: str, byte_code, dep_data: Dependency):
        self.name = name
        self.code = byte_code
        self.subscribers = []
        self.param_vals = {}  # map type -> val as they come in
        self.dep_data = dep_data
        self.executed = False
        self.result = None

    def is_independent(self):
        return len(self.dep_data.dependencies) == 0

    def add_subscriber(self, node):
        self.subscribers.append(node)

    def can_execute(self):
        for (_, argtype) in self.dep_data.dependencies:
            if argtype not in self.param_vals:
                return False
        return True

    def execute(self):
        assert self.can_execute()

        if self.executed:
            return self.result

        param_sequence = [self.param_vals[argtype] for (_, argtype) in self.dep_data.dependencies]
        self.result = self.code(*param_sequence)
        self.executed = True
        return self.result
