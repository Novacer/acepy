import unittest
from src.analyzer import *

unique_returns = '''
def f(x) -> a:
    return 1

def g(x):
    return 1

def h(x) -> b:
    return 1

def a(x):
    return 1

def b(x) -> c:
    return 1

'''

duplicate_returns = unique_returns + '''
def c(x) -> a:
    return 1
'''

function_overloading = unique_returns + '''
def f():
    return 1
'''


class AnalyzerTest(unittest.TestCase):
    function_str = '''def f(x: 'param') -> 'result': return x'''
    function_named = '''def f(x: param) -> result: return x'''
    function_no_annotation = '''def f(x) -> result: return x'''

    def test_analyze_annotations(self):
        for function in [self.function_str, self.function_named]:
            tree = parse(function)
            dependencies = analyze(tree)
            self.assertIn('f', dependencies)
            dependency_data = dependencies['f']
            self.assertIn(('x', 'param'), dependency_data.dependencies)
            self.assertEqual('result', dependency_data.returns)

    def test_analyze_no_annotations(self):
        dependencies = analyze(parse(self.function_no_annotation))
        self.assertIn('f', dependencies)
        self.assertListEqual(dependencies['f'].dependencies, [])

    def test_returns_are_unique(self):
        dep = analyze(parse(unique_returns))
        self.assertTrue(returns_are_unique(dep))
        dep = analyze(parse(duplicate_returns))
        self.assertFalse(returns_are_unique(dep))

    def test_overload_error(self):
        tree = parse(function_overloading)
        self.assertRaises(FunctionOverloadError, analyze, tree)


if __name__ == '__main__':
    unittest.main()
