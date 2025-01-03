import numpy as np
import tkinter as tk
import tkinter.messagebox as msgbox
from tkinter import simpledialog


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


window_width = 1000
window_height = 600

# STARTING GRAPH
start_graph = {
    "S": {},
    "A": {},
    "B": {},
    "C": {},
    "D": {},
    "E": {},
    "F": {},
    "G": {},
    "H": {},
    "I": {},
    "J": {},
    "K": {},
    "L": {},
    "M": {},
    "N": {},
    "O": {},
    "P": {},
    "Q": {},
    "R": {},
    "T": {},
    "U": {},
    "V": {},
    "W": {},
    "X": {},
    "Y": {},
    "Z": {},
}
# FINAL NODES
final_nodes = ["D", "I", "J", "K"]
# STARTING HEURISTICS
start_H = {
    "S": 10,
    "A": 14,
    "B": 13,
    "C": 2,
    "D": 0,
    "E": 1,
    "F": 4,
    "G": 5,
    "H": 5,
    "I": 0,
    "J": 0,
    "K": 0,
    "L": 7,
    "M": 0,
    "N": 0,
    "O": 0,
    "P": 0,
    "Q": 0,
    "R": 0,
    "T": 0,
    "U": 0,
    "V": 0,
    "W": 0,
    "X": 0,
    "Y": 0,
    "Z": 0,
}
node_count = 13  # len(start_H)
graph = {
    "S": {"OR": [("A", 2), ("B", 5)]},
    "A": {"AND": [("C", 1), ("D", 1), ("E", 1)]},
    "B": {"AND": [("F", 1), ("G", 3)]},
    "C": {"OR": [("H", 2), ("I", 8)]},
    "D": {},
    "E": {"OR": [("I", 7), ("J", 1)]},
    "F": {"OR": [("J", 4), ("K", 3)]},
    "G": {"OR": [("K", 6), ("L", 5)]},
    "H": {},
    "I": {},
    "J": {},
    "K": {},
    "L": {},
}
H = start_H
node_entered = False
F_entered = False
G_entered = False
selected_node = None
nodes_list = []
nodes_list_iterations = []
nodes_solved = []
nodes_sequence = []
solution_tree = []
id2name = {}

iteration = 0
num_iterations = 1

#########################################################################
############################# AO* ALGORITHM #############################
#########################################################################


def ao_star():
    global \
        graph, \
        num_iterations, \
        nodes_list, \
        nodes_list_iterations, \
        nodes_solved, \
        nodes_sequence, \
        solution_tree, \
        id2name, \
        iteration, \
        num_iterations, \
        node_entered, \
        F_entered, \
        G_entered, \
        selected_node
    init_all()
    for i in range(100):
        if i == 0:
            node = Node("S")
            node.H = H["S"]
            nodes_list.append(node)
            update_F(nodes_list)
            print_tree(nodes_list)
        else:
            node = nodes_list[0]
            while node.developed:
                if node.type_ == "OR":
                    min_child = None
                    for child in node.children:
                        if child.solved:
                            continue
                        if min_child == None or child.F < min_child.F:
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
        subtrees = graph[node.name]
        nodes_sequence.append(node)

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
                new_node.H = H[child_name]
                new_node.level = node.level + 1
                if child_name in final_nodes:
                    new_node.final = True

                nodes_list.append(new_node)
                node.children.append(new_node)

        # if current node is one of the final nodes mark it as solved
        if node.name in final_nodes:
            node.solved = True

        # update all the F values and print tree
        update_F(nodes_list)
        print_tree(nodes_list)
        num_iterations += 1

        # GET SOLUTION
        starting_node = nodes_list[0]
        if starting_node.solved:
            stack = []
            solution_tree.append(starting_node)
            stack.append(starting_node)
            cost_sum = starting_node.F
            while stack:
                node_ = stack.pop()
                for child in node_.children:
                    if child.solved:
                        stack.append(child)
                        solution_tree.append(child)
                        cost_sum += child.F
            print(
                f"ALGORITHM FINISHED\nSOLUTION COST: {cost_sum}\nSOLUTION TREE: ",
                end="",
            )
            for solution_node in solution_tree:
                print(solution_node.name, end=" ")
            return


def init_all():
    global \
        num_iterations, \
        nodes_list, \
        nodes_list_iterations, \
        nodes_solved, \
        nodes_sequence, \
        solution_tree, \
        id2name, \
        iteration, \
        num_iterations, \
        node_entered, \
        F_entered, \
        G_entered, \
        selected_node
    nodes_list = []
    nodes_list_iterations = []
    nodes_solved = []
    nodes_sequence = []
    solution_tree = []
    id2name = {}
    iteration = 0
    num_iterations = 1
    node_entered = False
    F_entered = False
    G_entered = False
    selected_node = None


def update_F(nodes_list):
    if nodes_list:
        for node in reversed(nodes_list):
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


def print_tree(nodes_list):
    solved_nodes = []
    node2f = {}
    for node in nodes_list:
        print(f"{node.name}: {node.F}, ", end="")
        print(type(node))
        node2f[node] = node.F
        if node.solved:
            solved_nodes.append(node)
    nodes_list_iterations.append(node2f)
    nodes_solved.append(solved_nodes)


#########################################################################
############################# VISUALIZATION #############################
#########################################################################


def test_FG():
    global F_entered, F_entry, G_entered, G_entry, nextstep, status_text, status_text2
    try:
        F_value = int(F_entry.get())
        G_value = int(G_entry.get())
        if 0 <= F_value <= 100 or F_value == 1000 and 0 <= G_value <= 100 or G_value == 1000:  # 1000 == inf
            print(f"Valid F: {F_value}, and G: {G_value}")
            # check if entered F is correct
            if (
                F_value == 1000 and nodes_list_iterations[iteration + 1][selected_node] == np.inf
            ) or F_value == nodes_list_iterations[iteration + 1][selected_node]:  # 1000 == inf
                F_entered = True
                F_entry.configure(bg="lightgreen")
            else:
                F_entry.configure(bg="firebrick2")
            # check if entered G is correct
            if G_value == selected_node.edge_cost:
                G_entry.configure(bg="lightgreen")
                G_entered = True
            else:
                G_entry.configure(bg="firebrick2")
        else:
            msgbox.showerror(
                "Error",
                "Entered F and G costs must be integers between 0 and 100, or 1000 for infinity",
            )
            F_entry.configure(bg="firebrick2")
            G_entry.configure(bg="firebrick2")
    except ValueError:
        msgbox.showerror(
            "Error",
            "Please enter valid integers for both F and G. \n\nValue 1000 represents infinity.",
        )

    if F_entered and G_entered:
        nextstep.configure(state=tk.NORMAL)
        testFG.configure(state=tk.DISABLED)
        status_text2.set("       correct F and G entered, press next step to continue       ")


def get_levels(graph):
    levels = []
    queue = [("S", 0)]
    while queue:
        node, level = queue.pop(0)
        if level == len(levels):
            levels.append([])
        if node not in levels[level]:
            levels[level].append(node)
        children = graph.get(node, {})
        for child_type in children.values():
            for child, _ in child_type:
                queue.append((child, level + 1))
    levels_ = {}
    for ix, l in enumerate(levels):
        levels_[ix] = l
    return levels_


def update_status():
    global node_entered, F_entered, G_entered, status_label, status_label2, testFG
    if not node_entered:
        canvas.bind("<Button-1>", on_node_click)
    if node_entered:
        G_entry.configure(state=tk.NORMAL)
        F_entry.configure(state=tk.NORMAL)
        status_text2.set("                     correct node selected, enter F and G                     ")
        status_label.configure(bg="lightgreen")
        status_label2.configure(bg="lightgreen")
        testFG.configure(state=tk.NORMAL)
    else:
        G_entry.configure(state=tk.DISABLED)
        F_entry.configure(state=tk.DISABLED)
        testFG.configure(state=tk.DISABLED)
        status_text2.set(
            "                       incorrect node selected, try again                       "
        )  # , bg="red")
        status_label.configure(bg="salmon")
        status_label2.configure(bg="salmon")
    if F_entered and G_entered:
        F_entered = False
        G_entered = False


def toggle_color(item_id, starting_color, new_color):
    current_color = canvas.itemcget(item_id, "fill")
    next_color = new_color if current_color != new_color else starting_color
    canvas.itemconfig(item_id, fill=next_color)
    canvas.after(1000, toggle_color, item_id, starting_color, new_color)


def on_node_click(event):
    global node_entered, selected_node
    item = canvas.find_closest(event.x, event.y)
    item_id = item[0]
    node = id2name.get(item_id)
    if node:
        # change color of selected node for 1 second to green if correct and red if wrong
        if node.name == nodes_sequence[iteration].name:
            starting_color = canvas.itemcget(item_id, "fill")
            toggle_color(item_id, starting_color, "medium sea green")
            canvas.unbind("<Button-1>")
            node_entered = True
            selected_node = node
        else:
            starting_color = canvas.itemcget(item_id, "fill")
            toggle_color(item_id, starting_color, "firebrick2")
            node_entered = False
        update_status()


def set_graph(tree):
    global graph, H, node_count, final_nodes
    if tree == 1:
        final_nodes = ["D", "I", "J", "K"]
        graph = {
            "S": {"OR": [("A", 2), ("B", 5)]},
            "A": {"AND": [("C", 1), ("D", 1), ("E", 1)]},
            "B": {"AND": [("F", 1), ("G", 3)]},
            "C": {"OR": [("H", 2), ("I", 8)]},
            "E": {"OR": [("I", 7), ("J", 1)]},
            "F": {"OR": [("J", 4), ("K", 3)]},
            "G": {"OR": [("K", 6), ("L", 5)]},
            "D": {},
            "H": {},
            "I": {},
            "J": {},
            "K": {},
            "L": {},
        }
        H = {
            "S": 10,
            "A": 14,
            "B": 13,
            "C": 2,
            "D": 0,
            "E": 1,
            "F": 4,
            "G": 5,
            "H": 5,
            "I": 0,
            "J": 0,
            "K": 0,
            "L": 7,
        }
    elif tree == 2:
        final_nodes = ["J", "K", "L", "M", "N"]
        graph = {
            "S": {"OR": [("A", 2), ("B", 1)]},
            "A": {"AND": [("C", 1), ("D", 1), ("E", 1)]},
            "B": {"AND": [("F", 1), ("G", 3), ("H", 2)]},
            "C": {"OR": [("I", 5), ("J", 4)]},
            "D": {"OR": [("J", 1), ("K", 1)]},
            "E": {"OR": [("K", 1), ("L", 1)]},
            "F": {"OR": [("L", 4), ("M", 3)]},
            "G": {"OR": [("M", 6), ("N", 5)]},
            "H": {"OR": [("N", 6), ("O", 5)]},
            "I": {},
            "J": {},
            "K": {},
            "L": {},
            "M": {},
            "N": {},
            "O": {},
            "P": {},
        }
        H = {
            "S": 2,
            "A": 4,
            "B": 6,
            "C": 8,
            "D": 10,
            "E": 12,
            "F": 14,
            "G": 12,
            "H": 10,
            "I": 8,
            "J": 6,
            "K": 4,
            "L": 2,
            "M": 2,
            "N": 4,
            "O": 6,
            "P": 8,
        }
    elif tree == 3:
        final_nodes = ["G", "H"]
        graph = {
            "S": {"OR": [("A", 5), ("B", 3)]},
            "A": {"OR": [("C", 1), ("D", 1), ("E", 5), ("F", 1)]},
            "B": {"OR": [("G", 2), ("H", 8), ("I", 7), ("J", 1)]},
            "C": {},
            "D": {},
            "E": {},
            "F": {},
            "G": {},
            "H": {},
            "I": {},
            "J": {},
        }
        H = {
            "S": 2,
            "A": 4,
            "B": 6,
            "C": 8,
            "D": 10,
            "E": 12,
            "F": 14,
            "G": 12,
            "H": 10,
            "I": 8,
            "J": 6,
        }
    elif tree == 4:
        final_nodes = ["N", "M", "I", "J", "K"]
        graph = {
            "S": {"OR": [("A", 2), ("B", 5)]},
            "A": {"AND": [("C", 1), ("D", 1)]},
            "B": {"AND": [("E", 5), ("F", 1)]},
            "C": {"OR": [("G", 2), ("H", 8)]},
            "D": {"OR": [("I", 7), ("J", 1)]},
            "E": {"OR": [("K", 7), ("L", 1)]},
            "F": {"OR": [("M", 4), ("N", 3)]},
            "G": {},
            "H": {},
            "I": {},
            "J": {},
            "K": {},
            "L": {},
            "M": {},
            "N": {},
        }
        H = {
            "S": 2,
            "A": 4,
            "B": 6,
            "C": 8,
            "D": 10,
            "E": 12,
            "F": 14,
            "G": 12,
            "H": 10,
            "I": 8,
            "J": 6,
            "K": 4,
            "L": 2,
            "M": 2,
            "N": 4,
        }
    elif tree == 5:
        final_nodes = ["P", "O", "R", "Q", "W", "U", "T", "V", "M"]
        graph = {
            "S": {"OR": [("A", 15), ("B", 2)]},
            "A": {"AND": [("C", 3), ("D", 4)]},
            "B": {"AND": [("E", 5), ("F", 6)]},
            "C": {"OR": [("G", 7), ("H", 8)]},
            "D": {"OR": [("I", 9), ("J", 8)]},
            "E": {"OR": [("K", 7), ("L", 6)]},
            "F": {"OR": [("M", 5), ("N", 4)]},
            "G": {"OR": [("O", 3), ("P", 2)]},
            "H": {"OR": [("P", 2), ("R", 2)]},
            "I": {"OR": [("R", 1), ("Q", 2)]},
            "J": {"OR": [("Q", 2)]},
            "K": {"OR": [("T", 3), ("U", 2)]},
            "L": {"OR": [("U", 4), ("V", 2)]},
            "M": {"OR": [("V", 5), ("W", 2)]},
            "N": {"OR": [("W", 6)]},
            "O": {},
            "P": {},
            "R": {},
            "Q": {},
            "T": {},
            "U": {},
            "V": {},
            "W": {},
        }
        H = {
            "S": 1,
            "A": 2,
            "B": 3,
            "C": 4,
            "D": 5,
            "E": 6,
            "F": 7,
            "G": 8,
            "H": 9,
            "I": 8,
            "J": 7,
            "K": 6,
            "L": 5,
            "M": 4,
            "N": 3,
            "O": 2,
            "P": 1,
            "R": 2,
            "Q": 3,
            "T": 4,
            "U": 5,
            "V": 6,
            "W": 7,
        }
    node_count = len(H)
    main()


def draw_tree(canvas):
    global id2name
    id2name = {}
    start_y = 105
    # legend
    canvas.create_text(35, start_y, fill="black", text="Legend:")
    canvas.create_oval(20, start_y + 15, 35, start_y + 30, outline="black", fill="gray")
    canvas.create_text(85, start_y + 22, fill="black", text="- revealed nodes")
    canvas.create_oval(20, start_y + 35, 35, start_y + 50, outline="black", fill="black")
    canvas.create_text(91, start_y + 42, fill="black", text="- developed nodes")
    canvas.create_oval(20, start_y + 55, 35, start_y + 70, outline="black", fill="goldenrod3")
    canvas.create_text(80, start_y + 62, fill="black", text="- solved nodes")
    canvas.create_oval(20, start_y + 75, 35, start_y + 90, outline="black", fill="lightgreen")
    canvas.create_text(86, start_y + 82, fill="black", text="- solution nodes")
    # different starting trees
    canvas.create_text(window_width - 50, start_y, fill="black", text="Examples")
    graph_button1 = tk.Button(root, text="Graph 1", command=lambda: set_graph(1))
    canvas.create_window(window_width - 50, start_y + 30, window=graph_button1)
    graph_button2 = tk.Button(root, text="Graph 2", command=lambda: set_graph(2))
    canvas.create_window(window_width - 50, start_y + 60, window=graph_button2)
    graph_button3 = tk.Button(root, text="Graph 3", command=lambda: set_graph(3))
    canvas.create_window(window_width - 50, start_y + 90, window=graph_button3)
    graph_button4 = tk.Button(root, text="Graph 4", command=lambda: set_graph(4))
    canvas.create_window(window_width - 50, start_y + 120, window=graph_button4)
    graph_button5 = tk.Button(root, text="Graph 5", command=lambda: set_graph(5))
    canvas.create_window(window_width - 50, start_y + 150, window=graph_button5)
    # edit starting graph
    graph_button = tk.Button(root, text="Starting graph", command=show_graph)
    canvas.create_window(window_width // 2, start_y, window=graph_button)
    # edit starting heuristics
    heuristics_button = tk.Button(root, text="Starting heuristics", command=show_heuristics)
    canvas.create_window(window_width // 2, 25, window=heuristics_button)
    canvas.create_line(5, 80, window_width - 5, 80, fill="gray")
    node_names = ""
    node_heuristics = ""
    for i, (names, heuristics) in enumerate(H.items()):
        if i == node_count:
            break
        node_names += str(names).rjust(10, " ")
        node_heuristics += str(heuristics).rjust(10, " ")
    canvas.create_text(window_width // 2, 50, fill="black", text=node_names)
    canvas.create_text(window_width // 2, 65, fill="black", text=node_heuristics)

    ##### FIRST TREE #####
    levels = get_levels(graph)
    # GET POSITIONS
    positions = {}
    last_y = 0
    scale = 110
    for l in levels:
        y_offset = start_y + 30 + l * scale // 2
        if y_offset > last_y:
            last_y = y_offset
        level = levels[l]
        num_nodes = len(level)
        x_positions = [0]
        if num_nodes > 1:
            step = (2 * l * scale) // (num_nodes - 1)
            x_positions = np.arange(-l * scale, l * scale + 1, step)
        for ix, n in enumerate(level):
            x = window_width // 2 + x_positions[ix]
            y = y_offset
            node_type = graph[n]
            if "OR" in node_type:
                node_type = "OR"
            elif "AND" in node_type:
                node_type = "AND"
            else:
                node_type = None
            positions[n] = (x, y, node_type)

    # DRAW NODES
    node_size = 10
    for node, pos in positions.items():
        x, y, node_type = pos
        # create nodes
        canvas.create_oval(x - node_size, y - node_size, x + node_size, y + node_size, outline="black")
        # mark final nodes
        if node in final_nodes:
            canvas.create_oval(
                x - node_size + 2,
                y - node_size + 2,
                x + node_size - 2,
                y + node_size - 2,
                outline="black",
            )
        # node names
        canvas.create_text(x, y, fill="black", text=node)
        # node type
        if node_type:
            canvas.create_text(x, y + 20, fill="blue", text=node_type)

    # DRAW EDGES WITH WEIGHTS
    for node, edges in graph.items():
        if "OR" in graph[node]:
            edges = graph[node]["OR"]
        elif "AND" in graph[node]:
            edges = graph[node]["AND"]
        else:
            edges = []
        for edge, weight in edges:
            x1, y1, _ = positions[node]
            x2, y2, _ = positions[edge]
            # create edges
            canvas.create_line(x1, y1 + node_size, x2, y2 - node_size, fill="gray")
            # add weight text in the middle of the edges
            canvas.create_text(
                (x1 + x2) / 2 + 5,
                (y1 + y2) / 2 + 5,
                text=str(weight),
                fill="darkblue",
                font=("Arial", 10),
            )

    ##### SECOND TREE #####
    current_nodes = nodes_list_iterations[iteration]
    levels = {}
    last_y += 50
    canvas.create_line(5, last_y - 15, window_width - 5, last_y - 15, fill="gray")
    canvas.create_text(window_width // 2, last_y + 10, fill="black", text="Simulation graph")

    # get levels
    for curr_node in current_nodes:
        curr_level = curr_node.level
        if curr_level not in levels:
            levels[curr_level] = []
        levels[curr_level].append(curr_node)
    for level in levels.values():
        level.sort(key=lambda node: node.parent.name if node.parent else "")

    # GET POSITIONS
    positions = {}
    for l in levels:
        levels[l].sort(key=lambda node: node.parent.name if node.parent else "")
        level = levels[l]
        num_nodes = len(level)
        x_positions = [0]
        if num_nodes > 1:
            step = (2 * l * scale) // (num_nodes - 1)
            x_positions = np.arange(-l * scale, l * scale + 1, step)
        for ix, n in enumerate(level):
            x = window_width // 2 + x_positions[ix]
            y = 35 + l * 50
            positions[n] = (x, y)

    # DRAW EDGES WITH WEIGHTS
    for node, position in positions.items():
        for child_node in node.children:
            if child_node in current_nodes:
                x1, y1 = position
                y1 += last_y
                x2, y2 = positions[child_node]
                y2 += last_y
                canvas.create_line(x1, y1, x2, y2, fill="gray64")
                canvas.create_text(
                    (x1 + x2) / 2 + 5,
                    (y1 + y2) / 2 + 5,
                    text=str(child_node.edge_cost),
                    fill="black",
                    font=("Arial", 10),
                )

    # DRAW NODES
    for node, pos in positions.items():
        x, y = pos
        y += last_y
        if node in solution_tree and iteration == num_iterations - 1:  # solution nodes are green
            node_id = canvas.create_oval(x - 10, y - 10, x + 10, y + 10, fill="lightgreen", outline="black")
            canvas.create_text(x, y, fill="black", text=node.name)
        elif node in nodes_solved[iteration]:  # solved nodes are yellow
            node_id = canvas.create_oval(x - 10, y - 10, x + 10, y + 10, fill="goldenrod3", outline="black")
            canvas.create_text(x, y, fill="black", text=node.name)
        elif node in nodes_sequence[:iteration]:  # developed nodes are black
            node_id = canvas.create_oval(x - 10, y - 10, x + 10, y + 10, fill="black", outline="black")
            canvas.create_text(x, y, fill="white", text=node.name)
        else:  # revealed nodes are gray
            node_id = canvas.create_oval(x - 10, y - 10, x + 10, y + 10, fill="gray75", outline="black")
            canvas.create_text(x, y, fill="black", text=node.name)
        if node in nodes_sequence[:iteration] and node.type_:  # node type
            canvas.create_text(x, y + 20, fill="blue", text=node.type_)
        # show F values
        if node in nodes_list_iterations[iteration - 1]:
            canvas.create_text(x + 40, y, fill="black", text=f"F({node.name})={current_nodes[node]}")
        # save position for node id
        id2name[node_id] = node

    # HELP BUTTON
    help_button = tk.Button(root, text="Help", command=display_help)
    canvas.create_window(25, 20, window=help_button)

    # skip next step
    hint_button = tk.Button(root, text="Skip", command=next_step)
    canvas.create_window(25, 50, window=hint_button)

    canvas.create_line(5, window_height - 10, window_width - 5, window_height - 10, fill="gray")


def next_step():
    global iteration, num_iterations, node_entered, F_entry, G_entry, testFG, status_label, status_label2, status_text2
    iteration += 1
    if iteration < num_iterations:
        canvas.delete("all")
        draw_tree(canvas)
        node_entered = False
        F_entry.delete(0, tk.END)
        G_entry.delete(0, tk.END)
        F_entry.configure(bg="white")
        G_entry.configure(bg="white")
        update_status()
    nextstep.configure(state=tk.DISABLED)
    testFG.configure(state=tk.DISABLED)
    status_label.configure(bg="tan1")
    status_label2.configure(bg="tan1")
    status_text2.set("                   select the next node to be developed                     ")
    if num_iterations <= iteration + 1:
        canvas.unbind("<Button-1>")
        status_label.configure(bg="lightblue")
        status_label2.configure(bg="lightblue")
        if nodes_list[0].solved:
            status_text2.set("      algorithm finished, solution treen is marked in green       ")
        else:
            status_text2.set("                   algorithm finished, no solution found                    ")


def display_help():
    cues = "F(N) = H(N) + G(N) = cost(parent, N) + H(N)\n• if node == leaf: H(N) = h(n)\n• if node_type == 'OR' then: H(n) = min(F(N_i))\n• if node_type == 'AND' then: H(n) = sum(F(N_i))\n• at OR type nodes we develop the most promising subtree until its cost exceeds the cost of the alternative subtree\n• at AND type nodes, we develop subtrees one by one in alphabetical order until each one is fully developed."
    msgbox.showinfo(
        "How to use the AO* algorithm visualisation tool",
        "The AO* algorithm simulation includes a graph, starting heuristics table, and a status bar for guidance. To navigate the simulation:\n\n1. Choose a node to develop.\n\n2. Input the node's F and G values, guided by provided cues.\n\n3. Confirm correct values to proceed, repeating the process.\n\n4. Completion is achieved when a solution tree is identified.\n\nNodes and heuristics can be adjusted using the respective buttons. The 'Skip' button allows progression without specific node selection or value entry. \nThe value 1000 denotes infinity.",
    )


root = tk.Tk()
root.title("AO* Algorithm Simulation")


def main():
    global \
        canvas, \
        F_entry, \
        G_entry, \
        status_text2, \
        nextstep, \
        testFG, \
        status_label, \
        status_label2, \
        window_height, \
        window_width, \
        iteration, \
        num_iterations
    # update_H_graph()
    ao_star()

    # F cost
    F_label = tk.Label(root, text="Enter F cost:")
    F_label.grid(column=3, row=1)
    F_entry = tk.Entry(root)
    F_entry.grid(column=4, row=1)
    F_entry.configure(state=tk.DISABLED)

    # G cost
    G_label = tk.Label(root, text="Enter G cost:")
    G_label.grid(column=3, row=2)
    G_entry = tk.Entry(root)
    G_entry.grid(column=4, row=2)
    G_entry.configure(state=tk.DISABLED)

    # submit F and G
    testFG = tk.Button(root, text="Submit", command=test_FG)
    testFG.grid(column=4, row=3)
    testFG.configure(state=tk.DISABLED)

    # get next step
    nextstep = tk.Button(root, text="Next step", command=next_step)
    nextstep.grid(column=2, row=3)
    nextstep.configure(state=tk.DISABLED)

    # current status
    status_text = tk.StringVar()
    status_text.set("                                             STATUS:                                             ")
    status_label = tk.Label(root, textvariable=status_text, bg="tan1")
    status_label.grid(column=2, row=1)

    # current status2
    status_text2 = tk.StringVar()
    status_text2.set("             	select the first node to start the algorithm                ")
    status_label2 = tk.Label(root, textvariable=status_text2, bg="tan1")
    status_label2.grid(column=2, row=2)

    # set window start position
    window_height = 720
    root.geometry(f"+{25}+{0}")

    # canvas for trees
    canvas = tk.Canvas(root, width=window_width, height=window_height)
    canvas.grid(row=0, column=0, columnspan=7)
    canvas.bind("<Button-1>", on_node_click)

    # draw the trees
    draw_tree(canvas)

    root.mainloop()


def update_H_graph():
    global start_graph, start_H, graph, H, node_count
    H = {}
    for i, key in enumerate(start_H.keys()):
        if i == node_count:
            break
        H[key] = start_H[key]


# edit starting heuristics
class HeuristicsDialog(simpledialog.Dialog):
    def body(self, master):
        self.entries = {}
        # create heuristic entries
        for i, key in enumerate(H.keys()):
            tk.Label(master, text=key).grid(row=i, sticky="w")
            self.entries[key] = tk.Entry(master)
            self.entries[key].grid(row=i, column=1, sticky="w")
            self.entries[key].insert(0, str(H[key]))
        return self.entries["S"]

    def apply(self):
        self.result = {key: int(self.entries[key].get()) for key in H.keys()}


def show_heuristics():
    dialog = HeuristicsDialog(root, title="Edit starting Heuristics")
    result = dialog.result
    if result:
        for res in result:
            if not (0 <= result[res] and result[res] <= 100):
                msgbox.showerror("Error", "Entered heuristics must be integers between 0 and 100")
                return
            start_H[res] = result[res]
        main()
        print("sucessfuly updated heuristics")
    else:
        print("error while trying to update the starting heuristics")


# edit starting graph
class GraphDialog(simpledialog.Dialog):
    def body(self, master):
        global node_count
        self.entries = {}

        label = tk.Label(master, text="Edit starting graph nodes")
        label.grid(row=0, column=0, columnspan=2)
        # create node entries
        for i, key in enumerate(graph.keys()):
            tk.Label(master, text=key).grid(row=i + 1, sticky="w")
            self.entries[key] = tk.Entry(master)
            self.entries[key].grid(row=i + 1, column=1, sticky="w")
            self.entries[key].insert(0, graph[key])
        # add a new node
        self.add_button = tk.Button(master, text="Add new node", command=self.add_node)
        self.add_button.grid(row=node_count + 3, column=0, columnspan=2)
        if node_count >= len(start_graph):
            self.add_button.configure(state=tk.DISABLED)

        # edit final nodes
        label = tk.Label(master, text="")
        label.grid(row=node_count + 4, columnspan=2)
        label = tk.Label(master, text="Edit final nodes")
        label.grid(row=node_count + 5, columnspan=2)
        self.entry = tk.Entry(master)
        self.entry.grid(row=node_count + 6, columnspan=2)
        self.entry.insert(0, str(final_nodes))

        return self.entries["S"]

    def apply(self):
        global final_nodes
        self.result = {}
        for key in graph.keys():
            entry = self.entries[key].get()
            self.result[key] = eval(entry)
        final_nodes = self.entry.get()

    def add_node(self):
        global node_count, graph
        for i, key in enumerate(start_graph.keys()):
            if i == node_count:
                graph[key] = {}
        node_count += 1
        main()

    def edit_final(self):
        global node_count, graph
        node_count += 1
        for i, key in enumerate(start_graph.keys()):
            if i == node_count:
                graph[key] = {}
        main()


def show_graph():
    global graph
    dialog = GraphDialog(root, title="Edit starting graph")
    result = dialog.result
    if result:
        graph = result
        main()
    else:
        print("error while trying to update the starting graph")


main()
