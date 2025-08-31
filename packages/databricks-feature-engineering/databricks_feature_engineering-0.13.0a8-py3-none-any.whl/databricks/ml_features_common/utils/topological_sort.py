from collections import defaultdict, deque
from queue import PriorityQueue
from typing import Callable, Dict, Hashable, List, Optional

__all__ = ["find_cycle", "topological_sort"]


class _NodeInfo:
    def __init__(self, node):
        self.node = node
        # number of non-processed predecessors.
        self.n_blockers = 0
        # list of nodes that depend on this node.
        self.successors = []


def find_cycle(
    node_dependencies: Dict[Hashable, List[Hashable]]
) -> Optional[List[Hashable]]:
    """
    Finds a cycle in the node_dependencies graph. Returns a list of node(s) that forms a cycle or
    None if no cycle can be found.
    :param node_dependencies: A dict with hashable objects as keys and their list of dependency
                    nodes as values.
    """
    # A stack used to perform DFS on the graph.
    stack = deque()
    # Another stack storing the path from root to current node in DFS. Used to detect cycle.
    backtrack_stack = []
    # A set of nodes that no cycle can be found starting from these nodes.
    resolved = set()
    # Create a copy of the dependency graph with defaultdict for convenience.
    default_dependency = defaultdict(list)
    default_dependency.update(node_dependencies)

    # Perform DFS on every node in the graph.
    for node in node_dependencies.keys():
        if node in resolved:
            # Skip a node if it's already resolved.
            continue
        # DFS from the node
        stack.append(node)
        while stack:
            top = stack[-1]
            if top not in backtrack_stack:
                # First time visiting this node. There will be a second visit after the dependencies
                # are resolved if it has dependencies.
                backtrack_stack.append(top)
            # If not expended after traversing the dependencies, meaning there is no dependency or
            # all dependencies are resolved.
            expanded = False
            for depend in default_dependency[top]:
                if depend in backtrack_stack:
                    # found a cycle
                    index = backtrack_stack.index(depend)
                    return backtrack_stack[index:]
                if depend in resolved:
                    continue
                # Only adding node to stack. backtrack_stack only contains nodes in the current DFS
                # path.
                stack.append(depend)
                expanded = True
            if not expanded:
                stack.pop()
                resolved.add(top)
                backtrack_stack.pop()
    return None


def _all_items_in_queue_should_be_grouped(
    queue: PriorityQueue, should_be_grouped: Callable
) -> bool:
    temp = []
    should_group = True
    # note: avoid using queue.qsize() because it's not guaranteed to be accurate.
    while not queue.empty():
        k, node = queue.get()
        temp.append((k, node))
        if not should_be_grouped(node):
            should_group = False
    for item in temp:
        queue.put(item)
    return should_group


def topological_sort(
    node_dependencies: Dict[Hashable, List[Hashable]],
    key: Callable = None,
    should_be_grouped: Callable = None,
) -> List[Hashable]:
    """
    Topological sort the given node_dependencies graph. Returns a sorted list of nodes.
    :param node_dependencies: A dict with hashable objects as keys and their list of dependency
                    nodes as values.
    :param key: a Callable that returns a sort key when called with a hashable object. The key is
                    used to break ties in topological sorting. An object with smaller key is added
                    to the result list first.
    :raises ValueError if a cycle is found in the graph.
    """
    # Calling a dedicated find_cycle function to be able to give a detailed error message.
    cycle = find_cycle(node_dependencies)
    if cycle is not None:
        raise ValueError(
            "Following nodes form a cycle: ",
            cycle,
            ". Please resolve any circular dependencies before calling Feature Store.",
        )

    # A priority-queue storing the nodes whose dependency has been resolved.
    # priority is determined by the given key function.
    ready_queue = PriorityQueue()
    # Map from node to _NodeInfo.
    nodes = {}
    if key is None:
        key = hash  # use the built-in hash function by default
    if should_be_grouped is None:
        should_be_grouped = lambda _: False
    # Perform Kahn's algorithm by traversing the graph starting from nodes without dependency.
    # Node is removed from its successors' dependency once resolved. And node whose dependency gets
    # all resolved is added to the priority queue.
    for node, dependencies in node_dependencies.items():
        # Initialize the graph to topologically sort based on the input node_dependencies.
        # All nodes, its successors and number of predecessors should be populated.
        if node not in nodes:
            nodes[node] = _NodeInfo(node)
        for dependency in dependencies:
            if dependency not in nodes:
                nodes[dependency] = _NodeInfo(dependency)
            nodes[dependency].successors.append(node)
        if len(dependencies):
            nodes[node].n_blockers = len(dependencies)
    # Initialize the ready_queue to start traversing the graph from nodes without any dependencies.
    for node, node_info in nodes.items():
        if node_info.n_blockers == 0:
            ready_queue.put((key(node), node))
    # At the end of the algorithm, result_list will have a topologically sorted listed of nodes.
    result_list = []

    def process_nodes(node_buffer, queue):
        for node in node_buffer:
            result_list.append(node)
            for successor in nodes[node].successors:
                s_info = nodes[successor]
                s_info.n_blockers -= 1
                if s_info.n_blockers == 0:
                    queue.put((key(successor), successor))

    while not ready_queue.empty():
        if _all_items_in_queue_should_be_grouped(ready_queue, should_be_grouped):
            batch_buffer = []
            while not ready_queue.empty():
                _, node = ready_queue.get()
                batch_buffer.append(node)
            process_nodes(batch_buffer, ready_queue)
        else:
            _, node = ready_queue.get()
            process_nodes([node], ready_queue)
    return result_list
