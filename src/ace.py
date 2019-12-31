from src.analyzer import parse, analyze
from src.execution_graph import ExecutionGraph
from anycache import anycache


def run(src_file: str, start_params=None, num_workers=None):
    graph = create_exe_graph(src_file)
    return graph.execute(start_params, num_workers)


@anycache(cachedir='/tmp/anycache.cache')
def create_exe_graph(src_file: str):
    with open(src_file, 'r') as file:
        tree = parse(file.read())

    dep_data = analyze(tree)
    return ExecutionGraph(tree, dep_data)
