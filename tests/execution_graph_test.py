import unittest
from src.execution_graph import *
from src.analyzer import analyze, parse
from concurrent.futures import ThreadPoolExecutor


def two_params(x: 'param1', y: 'param2') -> 'result':
    return [x, y]


res_error_func = '''
def res_error(e: 'does_not_exist'):
    pass
'''


class ExecutionGraphTest(unittest.TestCase):
    param_seq = [('x', 'param1'), ('y', 'param2')]
    returns = 'result'
    name = 'two_params'
    node_dep_data = Dependency(param_seq, returns, None)

    def setUp(self) -> None:
        with open('test_src.py', 'r') as src:
            self.src = src.read()
            self.tree = parse(self.src)

        self.graph_dep_data = analyze(self.tree)

    def test_node_init(self):
        node = ExecutionNode(self.name, two_params, self.node_dep_data)
        self.assertFalse(node.is_independent())
        self.assertFalse(node.can_execute())
        self.assertFalse(node.executed)
        self.assertIsNone(node.result)

    def test_node_execute(self):
        node = ExecutionNode(self.name, two_params, self.node_dep_data)
        node.param_vals = {
            'param1': 1,
            'param2': 2
        }
        results_map = {}
        self.assertTrue(node.can_execute())
        with ThreadPoolExecutor() as executor:
            node.execute(results_map, executor)
        self.assertTrue(node.executed)
        self.assertEqual(node.result, [1, 2])
        self.assertEqual(results_map, {'two_params': [1, 2]})

    def test_node_cannot_execute(self):
        node = ExecutionNode(self.name, two_params, self.node_dep_data)
        node.param_vals = {'param1': 1}
        self.assertFalse(node.can_execute())
        self.assertRaises(AssertionError, node.execute, {}, None)

    def test_graph_init(self):
        graph = ExecutionGraph(self.tree, self.graph_dep_data)
        self.assertEqual(len(graph.root), 2)
        self.assertEqual(len(graph.branches), 4)

    def test_graph_execute_single_threaded(self):
        graph = ExecutionGraph(self.tree, self.graph_dep_data)
        start_params = {
            'f': [123, 'abc'],
            'g': [345]
        }
        results = graph.execute(start_params=start_params, max_workers=1)
        # takes approx 6 seconds
        expected = {
            'f': 123,
            'g': 345,
            'h': [123, 345],
            'a': [123, 345, 567],
            'b': [123, 345, 789],
            'c': [123, 345, 567, 123, 345, 789]
        }
        self.assertDictEqual(results, expected)

    def test_graph_execute_multi_threaded(self):
        graph = ExecutionGraph(self.tree, self.graph_dep_data)
        start_params = {
            'f': [123, 'abc'],
            'g': [345]
        }
        results = graph.execute(start_params, max_workers=2)
        # takes approx 4 seconds
        expected = {
            'f': 123,
            'g': 345,
            'h': [123, 345],
            'a': [123, 345, 567],
            'b': [123, 345, 789],
            'c': [123, 345, 567, 123, 345, 789]
        }
        self.assertDictEqual(results, expected)

    def test_graph_resolution_error(self):
        src = self.src + res_error_func
        tree = parse(src)
        dep_data = analyze(tree)
        self.assertRaises(DependencyResolutionError, ExecutionGraph, tree, dep_data)

    def test_cycle_error(self):
        with open('test_cycle_src.py', 'r') as src:
            tree = parse(src.read())
            dep_data = analyze(tree)

        self.assertRaises(NoRootNodeError, ExecutionGraph, tree, dep_data)


if __name__ == '__main__':
    unittest.main()
