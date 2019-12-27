import unittest
from src.execution_graph import *


def f(x: 'param1', y: 'param2') -> 'result':
    return [x, y]


class ExecutionNodeTest(unittest.TestCase):
    param_seq = [('x', 'param1'), ('y', 'param2')]
    returns = 'result'
    name = 'f'
    dep_data = Dependency(param_seq, returns, None)

    def test_init(self):
        node = ExecutionNode(self.name, f, self.dep_data)
        self.assertFalse(node.is_independent())
        self.assertFalse(node.can_execute())
        self.assertFalse(node.executed)
        self.assertIsNone(node.result)

    def test_execute(self):
        node = ExecutionNode(self.name, f, self.dep_data)
        node.param_vals = {
            'param1': 1,
            'param2': 2
        }
        self.assertTrue(node.can_execute())
        result = node.execute()
        self.assertEqual(result, [1, 2])
        self.assertTrue(node.executed)
        self.assertEqual(node.result, [1, 2])

    def test_cannot_execute(self):
        node = ExecutionNode(self.name, f, self.dep_data)
        node.param_vals = {'param1': 1}
        self.assertFalse(node.can_execute())
        self.assertRaises(AssertionError, node.execute)


if __name__ == '__main__':
    unittest.main()
