from src.analyzer import parse, analyze
from src.execution_graph import ExecutionGraph
from typing import Dict, List, Any
from anycache import AnyCache

cache = AnyCache(cachedir='/tmp/anycache.cache', maxsize=1000000)


def run(src_file: str, start_params: Dict[str, List] = None, num_workers: int = None) -> Dict[str, Any]:
    """
    Run a source file using AcePy.
    :param src_file: source code file name.
    :param start_params: initial parameters as a Dict of function name -> param sequence.
    :param num_workers: maximum number of concurrent workers available.
                        If none specified then use cpu_count * 5.
    :return: the results of running each function as a Dict of function name -> result.
    """
    graph = create_exe_graph(src_file)
    return graph.execute(start_params, num_workers)


def clear_cache() -> None:
    """
    Cache is persistent between python runs. If source file changes during development, it is recommended to clear
    the cache as execution graph may not have been updated. Alternatively, disable the cache during development.
    """
    cache.clear()


@cache.anycache()
def create_exe_graph(src_file: str) -> ExecutionGraph:
    """
    Create an execution graph object. Caches output using anycache so does not recompute between runs.
    Cache key is source file name, value is a dill of the resulting execution graph
    :param src_file: source code filename.
    :return: An execution graph representation of the source file.
    """
    with open(src_file, 'r') as file:
        tree = parse(file.read())

    dep_data = analyze(tree)
    return ExecutionGraph(tree, dep_data)
