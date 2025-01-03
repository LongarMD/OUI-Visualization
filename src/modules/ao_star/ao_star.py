from typing import Dict, List, Set, Tuple, Optional, Union
from dataclasses import dataclass


@dataclass
class Node:
    name: str
    parent: Optional["Node"] = None
    children: List["Node"] = None
    type_: str = ""  # "AND" or "OR"
    edge_cost: float = 0
    H: float = 0
    F: float = 0
    level: int = 0
    developed: bool = False
    searched: bool = False
    solved: bool = False
    final: bool = False
    infinite: bool = False

    def __post_init__(self):
        if self.children is None:
            self.children = []


# Type aliases for clarity
NodeName = str
Cost = Union[int, float]
EdgeInfo = Tuple[NodeName, Cost]
SubtreeInfo = Dict[str, List[EdgeInfo]]  # e.g. {"OR": [("A", 2), ("B", 5)]}
GraphStructure = Dict[NodeName, SubtreeInfo]
HeuristicValues = Dict[NodeName, float]


class AOStarSolver:
    """
    A class implementing the AO* algorithm for solving AND/OR graphs.
    """

    def __init__(self, graph: GraphStructure, heuristics: HeuristicValues, final_nodes: Set[NodeName]):
        self.graph: GraphStructure = graph
        self.H: HeuristicValues = heuristics
        self.final_nodes: Set[NodeName] = final_nodes

        # State tracking
        self.nodes_list: List[Node] = []
        self.nodes_list_iterations: List[Dict[Node, float]] = []
        self.nodes_solved: List[List[Node]] = []
        self.nodes_sequence: List[Node] = []
        self.solution_tree: List[Node] = []

    def solve(self) -> Optional[Tuple[List[Node], float]]:
        """
        Execute the AO* algorithm to find a solution.

        Returns:
            Tuple containing solution tree and total cost, or None if no solution found
        """
        self._init_search()

        for _ in range(100):  # Max iterations
            if len(self.nodes_list) == 0:
                self._init_start_node()
            else:
                node = self._get_next_node()
                if node is None:
                    print("Algorithm finished, no solution found")
                    return None

                self._expand_node(node)

            # Check if we found a solution
            starting_node = self.nodes_list[0]
            if starting_node.solved:
                return self._extract_solution()
        return None

    def _init_search(self) -> None:
        """Reset all state variables for a new search."""
        self.nodes_list.clear()
        self.nodes_list_iterations.clear()
        self.nodes_solved.clear()
        self.nodes_sequence.clear()
        self.solution_tree.clear()

    def _init_start_node(self) -> None:
        """Initialize the start node 'S' and add it to nodes list."""
        node = Node("S")
        node.H = self.H["S"]
        self.nodes_list.append(node)
        self._update_F()
        self._print_tree()

    def _get_next_node(self) -> Optional[Node]:
        """
        Find the next node to expand based on the AO* strategy.

        Returns:
            The next node to expand, or None if no valid node is found
        """
        node = self.nodes_list[0]
        while node.developed:
            if node.type_ == "OR":
                min_child = self._get_min_unsolved_child(node)
                if min_child is None:
                    return None
                node = min_child
            else:  # AND node
                next_node = self._get_next_unsearched_child(node)
                if next_node is None:
                    return None
                node = next_node
        return node

    def _get_min_unsolved_child(self, node: Node) -> Optional[Node]:
        """Get child with minimum F value that isn't solved."""
        min_child = None
        for child in node.children:
            if child.solved:
                continue
            if min_child is None or child.F < min_child.F:
                min_child = child
        return min_child

    def _get_next_unsearched_child(self, node: Node) -> Optional[Node]:
        """Get next unsearched and unsolved child."""
        for child in node.children:
            if not child.searched and not child.solved:
                return child
        return None

    def _expand_node(self, node: Node) -> None:
        """Expand a node by generating its children."""
        node.developed = True
        subtrees = self.graph[node.name]
        self.nodes_sequence.append(node)

        if len(subtrees) == 0 and not node.final:
            node.infinite = True
            return

        for subtree in subtrees:
            if subtree == "AND":
                node.type_ = "AND"
            elif subtree == "OR":
                node.type_ = "OR"

            children = subtrees[subtree]
            for child_name, cost in children:
                self._create_child_node(node, child_name, cost)

        if node.name in self.final_nodes:
            node.solved = True

        self._update_F()
        self._print_tree()

    def _create_child_node(self, parent: Node, child_name: NodeName, cost: Cost) -> None:
        """Create and initialize a new child node."""
        new_node = Node(child_name)
        new_node.parent = parent
        new_node.edge_cost = cost
        new_node.H = self.H[child_name]
        new_node.level = parent.level + 1
        if child_name in self.final_nodes:
            new_node.final = True

        self.nodes_list.append(new_node)
        parent.children.append(new_node)

    def _update_F(self) -> None:
        """Update F values for all nodes in reverse order."""
        if not self.nodes_list:
            return

        for node in reversed(self.nodes_list):
            if node.infinite:
                node.F = float("inf")
            elif len(node.children) == 0:
                node.F = node.edge_cost + node.H
            else:
                self._update_node_F(node)

    def _update_node_F(self, node: Node) -> None:
        """Update F value for a specific node based on its type."""
        if node.type_ == "AND":
            children_sum = sum(child.F for child in node.children)
            node.F = node.edge_cost + children_sum

            solved_count = sum(1 for child in node.children if child.solved)
            developed_count = sum(1 for child in node.children if child.developed)

            if solved_count == len(node.children):
                node.solved = True
            if developed_count == len(node.children):
                node.searched = True

        elif node.type_ == "OR":
            children_values = [child.F for child in node.children]
            node.F = node.edge_cost + min(children_values)

            developed_count = sum(1 for child in node.children if child.developed)
            if any(child.solved for child in node.children):
                node.solved = True
            if developed_count == len(node.children):
                node.searched = True

    def _extract_solution(self) -> Tuple[List[Node], float]:
        """Extract and return the solution path and cost."""
        starting_node = self.nodes_list[0]
        stack = [starting_node]
        self.solution_tree = [starting_node]
        cost_sum = starting_node.F

        while stack:
            node = stack.pop()
            for child in node.children:
                if child.solved:
                    stack.append(child)
                    self.solution_tree.append(child)
                    cost_sum += child.F

        solution_path = " ".join(node.name for node in self.solution_tree)
        print(f"ALGORITHM FINISHED\nSOLUTION COST: {cost_sum}\nSOLUTION TREE: {solution_path}")
        return self.solution_tree, cost_sum

    def _print_tree(self) -> None:
        """Print current state of the tree."""
        solved_nodes = []
        node2f: Dict[Node, float] = {}

        for node in self.nodes_list:
            print(f"{node.name}: {node.F}, ", end="")
            node2f[node] = node.F
            if node.solved:
                solved_nodes.append(node)

        self.nodes_list_iterations.append(node2f)
        self.nodes_solved.append(solved_nodes)
