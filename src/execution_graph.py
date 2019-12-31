import ast
from .analyzer import Dependency, returns_are_unique
from typing import List, Dict, Any, Union, Set
from concurrent.futures import ThreadPoolExecutor, Future, as_completed
from collections import defaultdict


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

    def is_independent(self) -> bool:
        return len(self.dep_data.dependencies) == 0

    def add_subscriber(self, node: 'ExecutionNode') -> None:
        self.subscribers.append(node)

    def can_execute(self) -> bool:
        """
        :return: Returns true if the node can be executed (all dependencies have been resolved)
        """
        for (_, argtype) in self.dep_data.dependencies:
            if argtype not in self.param_vals:
                return False
        return True

    def produces(self) -> str:
        return self.dep_data.returns

    def execute(self, results_map: dict, executor: ThreadPoolExecutor,
                start_params: List[Any] = None) -> Union[List[Future], None]:
        """
        Execute the node, store the result in results_map, and execute any subscribers if possible
        :param results_map: global map to store the results
        :param executor: a ThreadPoolExecutor to submit tasks to
        :param start_params: map of
        :return: a list of futures representing pending child tasks which are launched from this node
        """
        assert self.can_execute()
        if self.executed:
            return

        if self.is_independent():
            if start_params is not None:
                self.result = self.code(*start_params)
            else:
                self.result = self.code()
        else:
            param_sequence = [self.param_vals[argtype] for (_, argtype) in self.dep_data.dependencies]
            self.result = self.code(*param_sequence)

        results_map[self.name] = self.result
        self.executed = True

        futures = []
        for subscriber in self.subscribers:
            subscriber.param_vals[self.produces()] = self.result
            if subscriber.can_execute():
                futures.append(executor.submit(subscriber.execute, results_map, executor))

        return futures


class ExecutionGraph:
    """
    An execution graph is a collection of execution nodes (vertices) which are joined by dependencies (edges).
    Two nodes are dependent if the result of one is the parameter of the other.
    Independent nodes are considered the root (there may be multiple).
    """

    def __init__(self, tree: ast.Module, dep_data: Dict[str, Dependency]):
        """
        Construct an Execution Graph
        :param tree: an AST Module node produced by analyzer.parse(code)
        :param dep_data: the dependency data produced by analyzer.analyze(tree)
        :raises DuplicateReturnAnnotationError if two functions have the same return annotation
        :raises NoRootNodeError if every function has annotated parameters
        :raises DependencyResolutionError if no function which produces a dependency exists
        """

        # check output annotation of every function is unique, else graph cannot be built
        if not returns_are_unique(dep_data):
            raise DuplicateReturnAnnotationError

        bytecode = compile(tree, filename='<ast>', mode='exec')
        namespace = {}
        exec(bytecode, namespace)
        independent = set()
        dependent = set()
        for function_name, dependency in dep_data.items():
            function_code = namespace[function_name]
            node = ExecutionNode(function_name, function_code, dependency)
            if node.is_independent():
                independent.add(node)
            else:
                dependent.add(node)

        # assert a starting point exists
        if len(independent) == 0:
            raise NoRootNodeError

        # resolve all dependencies
        for node in dependent:
            depends_on = set([argType for (_, argType) in node.dep_data.dependencies])
            resolved = set()
            for indep_node in independent:
                if indep_node.produces() in depends_on:
                    indep_node.add_subscriber(node)
                    resolved.add(indep_node.produces())
            for dep_node in dependent:
                if node is not dep_node and dep_node.produces() in depends_on:
                    dep_node.add_subscriber(node)
                    resolved.add(dep_node.produces())

            # assert all dependencies have been resolved
            difference = depends_on.difference(resolved)
            if len(difference) != 0:
                raise DependencyResolutionError(difference)

        self.root = independent
        self.branches = dependent

    def execute(self, start_params: Dict[str, List[Any]] = None, max_workers: int = None) -> Dict[str, Any]:
        """
        Execute all nodes in the graph
        :return: map of all function names -> their results
        """
        results_map = {}
        sp_wrapper = defaultdict(list, start_params)

        with ThreadPoolExecutor(max_workers) as executor:
            futures = [
                executor.submit(
                    node.execute,
                    results_map=results_map,
                    executor=executor,
                    start_params=sp_wrapper[node.name]
                )
                for node in self.root
            ]
            ExecutionGraph.await_until_complete(futures)
        return results_map

    @staticmethod
    def await_until_complete(futures: List[Future]) -> None:
        """
        Blocks until all tasks AND child tasks have been completed
        :param futures: a List[Future] whose result() may be another List[Future]
        """
        for future in as_completed(futures):
            if isinstance(future, Future):
                ExecutionGraph.await_until_complete(future.result())


class DependencyResolutionError(Exception):
    def __init__(self, dependencies: Set[str]):
        self.message = 'Dependencies not resolved: ' + str(list(dependencies))

    def __str__(self):
        return self.message


class NoRootNodeError(Exception):
    def __init__(self):
        self.message = 'Error: graph does not have a root node. You need at least one function with no annotated ' \
                       'parameters '

    def __str__(self):
        return self.message


class DuplicateReturnAnnotationError(Exception):
    def __init__(self):
        self.message = 'Error: duplicate return annotations found. Return annotations must be unique'

    def __str__(self):
        return self.message
