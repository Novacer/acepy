import unittest
from src.execution_graph import *
from src.analyzer import *
from concurrent.futures import ThreadPoolExecutor


def two_params(x: 'param1', y: 'param2') -> 'result':
    return [x, y]


class ExecutionGraphTest(unittest.TestCase):
    param_seq = [('x', 'param1'), ('y', 'param2')]
    returns = 'result'
    name = 'two_params'
    node_dep_data = Dependency(param_seq, returns, None)

    def setUp(self) -> None:
        with open('test_src.py', 'r') as src:
            self.tree = parse(src.read())

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
        results = graph.execute()
        expected = {
            'f': 123,
            'g': 345,
            'h': [123, 345],
            'a': [123, 345, 567],
            'b': [123, 345, 789],
            'c': [123, 345, 567, 123, 345, 789]
        }
        self.assertDictEqual(results, expected)


if __name__ == '__main__':
    unittest.main()
