import unittest
import ast
from src.analyzer import *


class AnalyzerTest(unittest.TestCase):

    one_function = '''def f(x: param) -> result: return x'''

    def test_analyze(self):
        tree = parse(self.one_function)
        dependencies = analyze(tree)
        self.assertIn('f', dependencies)
        dependency_data = dependencies['f']
        self.assertIn(('x', 'param'), dependency_data.dependencies)
        self.assertEqual('result', dependency_data.returns)


if __name__ == '__main__':
    unittest.main()
