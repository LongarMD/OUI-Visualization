import itertools
import networkx as nx

BLUE = "#0020A1"
GREEN = "#00FF00"
YELLOW = "#FFFF00"
RED = "#FF1C6F"


class GraphNode:
    def __init__(self, name):
        self.name = name
        self.color = BLUE

    def toggle_color(self):
        self.color = GREEN if self.color == BLUE else BLUE


class DSeparationGraph:
    def __init__(self):
        self.graph = nx.DiGraph()
        self.nodes = {}

    def add_node(self, name):
        node = GraphNode(name)
        self.nodes[name] = node
        self.graph.add_node(name)

    def add_edge(self, from_node, to_node):
        self.graph.add_edge(from_node, to_node)

    def get_node_colors(self):
        """Return a list of node colors in the order of the nodes in the graph."""
        return [self.nodes[node].color for node in self.graph.nodes]


def get_node_type(graph, node, path):
    index = path.index(node)

    predecessors = set(graph.predecessors(node))
    successors = set(graph.successors(node))

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


def get_descendants(graph, node):
    return set(nx.descendants(graph, node))


def get_subsets_including_node(all_nodes, node):
    all_nodes = set(all_nodes)
    subsets = []
    for r in range(len(all_nodes) + 1):
        for subset in itertools.combinations(all_nodes, r):
            if node in subset:
                subsets.append(set(subset))
    return subsets


def get_subsets_excluding_node_and_descendants(all_nodes, node, descendants):
    nodes_to_exclude = {node} | descendants
    nodes_to_include = all_nodes - nodes_to_exclude
    subsets = []
    for r in range(len(nodes_to_include) + 1):
        for subset in itertools.combinations(nodes_to_include, r):
            subsets.append(set(subset))
    return subsets


def find_d_separating_sets(nx_graph, node1, node2):
    undirected_graph = nx_graph.to_undirected()
    undirected_paths = list(nx.all_simple_paths(undirected_graph, node1, node2))
    all_nodes = set(nx_graph.nodes) - {node1, node2}

    S_P_sets = []
    for path in undirected_paths:
        S_P = set()
        print("Path: ", path)
        for node in path:
            if node in {node1, node2}:
                continue

            node_type = get_node_type(nx_graph, node, path)

            descendants = get_descendants(nx_graph, node)

            S_X = []
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
