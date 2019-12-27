import ast
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

    def add_subscriber(self, node: 'ExecutionNode'):
        self.subscribers.append(node)

    def can_execute(self):
        for (_, argtype) in self.dep_data.dependencies:
            if argtype not in self.param_vals:
                return False
        return True

    def produces(self):
        return self.dep_data.returns

    def execute(self, results_map: dict):
        assert self.can_execute()

        if self.executed:
            return self.result
        param_sequence = [self.param_vals[argtype] for (_, argtype) in self.dep_data.dependencies]
        self.result = self.code(*param_sequence)
        results_map[self.name] = self.result
        self.executed = True

        for subscriber in self.subscribers:
            subscriber.param_vals[self.produces()] = self.result

            if subscriber.can_execute():
                subscriber.execute(results_map)
        return self.result


class ExecutionGraph:
    def __init__(self, tree: ast.Module, dep_data: dict):
        self.codeMap = {}
        bytecode = compile(tree, filename='<ast>', mode='exec')
        namespace = {}
        exec(bytecode, namespace)
        independent = set()
        dependent = set()
        for function_name, dependency in dep_data.items():
            function_code = namespace[function_name]
            self.codeMap[function_name] = function_code
            node = ExecutionNode(function_name, function_code, dependency)
            if node.is_independent():
                independent.add(node)
            else:
                dependent.add(node)

        # resolve all dependencies
        for node in dependent:
            depends_on = set([argType for (_, argType) in node.dep_data.dependencies])
            for indep_node in independent:
                if indep_node.produces() in depends_on:
                    indep_node.add_subscriber(node)
            for dep_node in dependent:
                if node is not dep_node and dep_node.produces() in depends_on:
                    dep_node.add_subscriber(node)

            # TODO check if there is dependency not resolved

        self.root = independent
        self.branches = dependent

    def execute(self) -> dict:
        results_map = {}
        for node in self.root:
            node.execute(results_map)

        return results_map
