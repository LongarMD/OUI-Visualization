from typing import Dict, List, Set, Tuple, Optional, Union
import numpy as np


class Node:
    def __init__(self, name):
        self.name = name
        self.F = 0
        self.H = 0
        self.parent = None
        self.edge_cost = 0
        self.children = []
        self.type_ = None
        self.final = False
        self.developed = False
        self.solved = False
        self.searched = False
        self.infinite = False
        self.level = 0


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

    graph: GraphStructure
    H: HeuristicValues
    final_nodes: Set[NodeName]

    def __init__(self, graph: GraphStructure, heuristics: HeuristicValues, final_nodes: Set[NodeName]):
        self.graph = graph
        self.H = heuristics
        self.final_nodes = final_nodes

        # State tracking
        self.nodes_list: List[Node] = []
        self.nodes_list_iterations: List[Dict[NodeName, float]] = []
        self.nodes_solved: List[List[Node]] = []
        self.nodes_sequence: List[Node] = []
        self.solution_tree: List[Node] = []
        self.num_iterations: int = 0

    def update_F(self):
        if not self.nodes_list:
            return
        for node in reversed(self.nodes_list):
            if node.infinite:
                node.F = np.inf
            elif len(node.children) == 0:
                node.F = node.edge_cost + node.H
            else:
                if node.type_ == "AND":
                    children_sum = 0
                    solved_count = 0
                    developed_count = 0
                    for child in node.children:
                        children_sum += child.F
                        if child.solved:
                            solved_count += 1
                        if child.developed:
                            developed_count += 1
                    node.F = node.edge_cost + children_sum
                    if solved_count == len(node.children):
                        node.solved = True
                    if developed_count == len(node.children):
                        node.searched = True
                elif node.type_ == "OR":
                    children_values = []
                    solved_count = 0
                    developed_count = 0
                    for child in node.children:
                        children_values.append(child.F)
                        if child.developed:
                            developed_count += 1
                        if child.solved:
                            node.solved = True
                    node.F = node.edge_cost + min(children_values)
                    if developed_count == len(node.children):
                        node.searched = True

    def solve(self) -> Optional[Tuple[List[Node], float]]:
        """
        Execute the AO* algorithm to find a solution.

        Returns:
            Tuple containing solution tree and total cost, or None if no solution found
        """

        for i in range(100):
            if i == 0:
                node = Node("S")
                node.H = self.H["S"]
                self.nodes_list.append(node)
                self.update_F()
                self._print_tree()
            else:
                node = self.nodes_list[0]
                while node.developed:
                    if node.type_ == "OR":
                        min_child = None
                        for child in node.children:
                            if child.solved:
                                continue
                            if min_child is None or child.F < min_child.F:
                                min_child = child
                        node = min_child
                    else:
                        finished = True
                        for child in node.children:
                            if child.searched or child.solved:
                                continue
                            node = child
                            finished = False
                            break
                        if finished:
                            print("Algorithm finished, no solution found")
                            return

            node.developed = True
            subtrees = self.graph[node.name]
            self.nodes_sequence.append(node)

            if len(subtrees) == 0 and not node.final:
                node.infinite = True  # = np.inf #float("inf")

            for subtree in subtrees:
                if subtree == "AND":
                    node.type_ = "AND"
                elif subtree == "OR":
                    node.type_ = "OR"

                children = subtrees[subtree]
                for child in children:
                    child_name, cost = child
                    new_node = Node(child_name)
                    new_node.parent = node
                    new_node.edge_cost = cost
                    new_node.H = self.H[child_name]
                    new_node.level = node.level + 1
                    if child_name in self.final_nodes:
                        new_node.final = True

                    self.nodes_list.append(new_node)
                    node.children.append(new_node)

            # if current node is one of the final nodes mark it as solved
            if node.name in self.final_nodes:
                node.solved = True

            # update all the F values and print tree
            self.update_F()
            self._print_tree()
            self.num_iterations += 1

            # GET SOLUTION
            starting_node = self.nodes_list[0]
            if starting_node.solved:
                stack = []
                self.solution_tree.append(starting_node)
                stack.append(starting_node)
                cost_sum = starting_node.F
                while stack:
                    node_ = stack.pop()
                    for child in node_.children:
                        if child.solved:
                            stack.append(child)
                            self.solution_tree.append(child)
                            cost_sum += child.F
                print(
                    f"ALGORITHM FINISHED\nSOLUTION COST: {cost_sum}\nSOLUTION TREE: ",
                    end="",
                )
                for solution_node in self.solution_tree:
                    print(solution_node.name, end=" ")
                return

    def _print_tree(self) -> None:
        """Print current state of the tree."""
        solved_nodes = []
        node2f = {}
        for node in self.nodes_list:
            print(f"{node.name}: {node.F}, ", end="")
            node2f[node] = node.F
            if node.solved:
                solved_nodes.append(node)
        self.nodes_list_iterations.append(node2f)
        self.nodes_solved.append(solved_nodes)

    @property
    def node_count(self) -> int:
        """Number of nodes in the graph"""
        return len(self.H)

    def get_levels(self):
        levels = []
        queue = [("S", 0)]
        while queue:
            node, level = queue.pop(0)
            if level == len(levels):
                levels.append([])
            if node not in levels[level]:
                levels[level].append(node)
            children = self.graph.get(node, {})
            for child_type in children.values():
                for child, _ in child_type:
                    queue.append((child, level + 1))
        levels_ = {}
        for ix, i in enumerate(levels):
            levels_[ix] = i
        return levels_
