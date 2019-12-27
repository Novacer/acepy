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
    functions = [node for node in tree.body if isinstance(node, ast.FunctionDef)]
    dependency_map = dict()

    for function in functions:
        args = []
        for arg in function.args.args:
            annotation = None
            if arg.annotation is not None:
                if isinstance(arg.annotation, ast.Str):
                    annotation = arg.annotation.s
                else:
                    annotation = arg.annotation.id
            args.append((arg.arg, annotation))

        returns = None
        if function.returns is not None:
            if isinstance(function.returns, ast.Str):
                returns = function.returns.s
            else:
                returns = function.returns.id
        dependency_map[function.name] = Dependency(args, returns, function)

    return dependency_map
