from typing import Dict, List, Set, Tuple, FrozenSet
import itertools
import networkx as nx
import random

BLUE = "#0020A1"
GREEN = "#00FF00"
YELLOW = "#FFFF00"
RED = "#FF1C6F"


class GraphNode:
    def __init__(self, name: str) -> None:
        self.name: str = name
        self.color: str = BLUE

    def toggle_color(self) -> None:
        self.color = GREEN if self.color == BLUE else BLUE


class DSeparationGraph:
    def __init__(self) -> None:
        self.graph: nx.DiGraph = nx.DiGraph()
        self.nodes: Dict[str, GraphNode] = {}

    def add_node(self, name: str) -> None:
        node = GraphNode(name)
        self.nodes[name] = node
        self.graph.add_node(name)

    def add_edge(self, from_node: str, to_node: str) -> None:
        self.graph.add_edge(from_node, to_node)

    def get_node_colors(self) -> List[str]:
        """Return a list of node colors in the order of the nodes in the graph."""
        return [self.nodes[node].color for node in self.graph.nodes]


def get_node_type(graph: nx.DiGraph, node: str, path: List[str]) -> str:
    index = path.index(node)

    predecessors: Set[str] = set(graph.predecessors(node))
    successors: Set[str] = set(graph.successors(node))

    if index > 0 and index < len(path) - 1:
        prev_node = path[index - 1]
        next_node = path[index + 1]
        if (
            prev_node in predecessors
            and next_node in successors
            or prev_node in successors
            and next_node in predecessors
        ):
            return "serial"
        if prev_node in predecessors and next_node in predecessors:
            return "convergent"
        if prev_node in successors and next_node in successors:
            return "divergent"
    return "unknown"


def get_descendants(graph: nx.DiGraph, node: str) -> Set[str]:
    return set(nx.descendants(graph, node))


def get_subsets_including_node(all_nodes: Set[str], node: str) -> List[Set[str]]:
    all_nodes = set(all_nodes)
    subsets: List[Set[str]] = []
    for r in range(len(all_nodes) + 1):
        for subset in itertools.combinations(all_nodes, r):
            if node in subset:
                subsets.append(set(subset))
    return subsets


def get_subsets_excluding_node_and_descendants(all_nodes: Set[str], node: str, descendants: Set[str]) -> List[Set[str]]:
    nodes_to_exclude = {node} | descendants
    nodes_to_include = all_nodes - nodes_to_exclude
    subsets: List[Set[str]] = []
    for r in range(len(nodes_to_include) + 1):
        for subset in itertools.combinations(nodes_to_include, r):
            subsets.append(set(subset))
    return subsets


def find_d_separating_sets(nx_graph: nx.DiGraph, node1: str, node2: str) -> Set[Tuple[str, ...]]:
    undirected_graph = nx_graph.to_undirected()
    undirected_paths = list(nx.all_simple_paths(undirected_graph, node1, node2))
    all_nodes = set(nx_graph.nodes) - {node1, node2}

    S_P_sets: List[Set[FrozenSet[str]]] = []
    for path in undirected_paths:
        S_P: Set[FrozenSet[str]] = set()
        print("Path: ", path)
        for node in path:
            if node in {node1, node2}:
                continue

            node_type = get_node_type(nx_graph, node, path)

            descendants = get_descendants(nx_graph, node)

            S_X: List[Set[str]] = []
            if node_type in ["divergent", "serial"]:
                S_X = get_subsets_including_node(all_nodes, node)
            elif node_type == "convergent":
                S_X = get_subsets_excluding_node_and_descendants(all_nodes, node, descendants)
            else:
                print("burek")
                continue

            print("Vozišče: ", node, ", Tip: ", node_type, ", Množice: ", S_X)

            S_P.update(frozenset(subset) for subset in S_X)

        print("Množice, ki d-ločujejo izbrani vozlišči, glede na pot: ", S_P)
        S_P_sets.append(S_P)

    E = set.intersection(*S_P_sets) if S_P_sets else set()
    E = {tuple(sorted(s)) for s in E}
    print("KONČNA REŠITEV: ", E, "\n")
    return E


def get_random_adjacency_matrix() -> str:
    """Generate a random adjacency matrix for the graph.

    Returns:
        str: A string representation of the random adjacency matrix
    """

    # Generate 4-7 nodes
    num_nodes = random.randint(4, 7)
    edges: List[Tuple[str, str]] = []

    # Ensure the graph is connected by adding a path through all nodes
    for node in range(1, num_nodes):
        parent = random.randint(0, node - 1)
        edges.append((chr(ord("A") + parent), chr(ord("A") + node)))

    # Add additional random edges with 0.4 probability
    for node in range(1, num_nodes):
        for potential_parent in range(node):
            if random.random() < 0.4:
                parent = chr(ord("A") + potential_parent)
                child = chr(ord("A") + node)
                edge = (parent, child)
                if edge not in edges:  # Avoid duplicates
                    edges.append(edge)

    # Convert to adjacency matrix string format
    return "\n".join(f"{parent} {child}" for parent, child in edges)
