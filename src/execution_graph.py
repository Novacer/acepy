import ast
from .analyzer import Dependency


class ExecutionNode:
    """
    An execution node represents a single function which takes zero or more arguments and returns a single value.
    A node can be executed if and only if all of its parameters (dependencies) have been resolved.
    Otherwise, a node is defined to be blocking.
    A node can have zero or more subscribers, which are other nodes that depend on the output of the current node.
    """
    def __init__(self, name: str, function_reference, dep_data: Dependency):
        """
        Constructs an execution node
        :param name: string representing name of the function
        :param function_reference: reference to the function in memory
        :param dep_data: dependency data of the function
        """
        self.name = name
        self.code = function_reference
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
        """
        :return: Returns true if the node can be executed (all dependencies have been resolved)
        """
        for (_, argtype) in self.dep_data.dependencies:
            if argtype not in self.param_vals:
                return False
        return True

    def produces(self):
        return self.dep_data.returns

    def execute(self, results_map: dict):
        """
        Execute the node, store the result in results_map, and execute any subscribers if possible
        :param results_map: global map to store the results
        :return: the result of executing this node
        """
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
    """
    An execution graph is a collection of execution nodes (vertices) which are joined by dependencies (edges).
    Two nodes are dependent if the result of one is the parameter of the other.
    Independent nodes are considered the root (there may be multiple).
    """
    def __init__(self, tree: ast.Module, dep_data: dict):
        """
        Construct an Execution Graph
        :param tree: an AST Module node produced by analyzer.parse(code)
        :param dep_data: the dependency data produced by analyzer.analyze(tree)
        """
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
        """
        Execute all nodes in the graph
        :return: map of all function names -> their results
        """
        # TODO add ability to pass arguments to root nodes (like user id etc)
        results_map = {}
        for node in self.root:
            node.execute(results_map)

        return results_map
