import ast


class Dependency:
    def __init__(self, args, returns, function):
        self.dependencies = args
        self.returns = returns
        self.function = function


def parse(code: str) -> ast.Module:
    """
    Parse source code string into an abstract syntax tree

    :param code: the source code
    :return: a single Module node of the abstract syntax tree
    """
    return ast.parse(code, mode='exec')


def analyze(tree: ast.Module) -> dict:
    """
    Analyze AST Module to produce a map of all functions to their parameters (dependencies) and return value (result)

    :param tree: an AST Module node
    :return: a dictionary with function names as key
    """
    functions = tree.body
    dependency_map = dict()

    for function in functions:
        args = set()
        for arg in function.args.args:
            print(ast.dump(arg))
            annotation = arg.annotation.id if arg.annotation is not None else None
            args.add((arg.arg, annotation))
        returns = function.returns.id if function.returns is not None else None
        dependency_map[function.name] = Dependency(args, returns, function)

    return dependency_map
