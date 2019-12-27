import unittest
from src.analyzer import *


class AnalyzerTest(unittest.TestCase):

    function_str = '''def f(x: 'param') -> 'result': return x'''
    function_named = '''def f(x: param) -> result: return x'''

    def test_analyze(self):
        for function in [self.function_str, self.function_named]:
            tree = parse(function)
            dependencies = analyze(tree)
            self.assertIn('f', dependencies)
            dependency_data = dependencies['f']
            self.assertIn(('x', 'param'), dependency_data.dependencies)
            self.assertEqual('result', dependency_data.returns)


if __name__ == '__main__':
    unittest.main()
