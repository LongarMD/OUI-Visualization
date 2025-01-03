import itertools
import networkx as nx
import tkinter as tk
import tkinter.messagebox as msgbox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# from networkx.drawing.nx_agraph import graphviz_layout
import numpy as np


after_id = None


class GraphNode:
    def __init__(self, name):
        self.name = name
        self.color = blue

    def toggle_color(self):
        self.color = green if self.color == blue else blue


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


def highlight_sets_sequentially(sets, current_index=0, separated_nodes=None):
    global root, active_nodes, after_id

    sets.sort(key=len)

    if not separated_nodes:
        separated_nodes = active_nodes.copy()

    for node in G.nodes.values():
        node.color = blue
        active_nodes.clear()

    if not sets:
        draw_graph(d_separating_sets=list(), separated_nodes=separated_nodes)
        return

    current_set = sets[current_index]
    for node_name in current_set:
        if node_name in G.nodes:
            G.nodes[node_name].color = yellow

    # Redraw the graph with updated colors
    draw_graph(sets, separated_nodes)

    # Schedule the next set to be highlighted
    next_index = (current_index + 1) % len(sets)
    after_id = root.after(
        2000, lambda: highlight_sets_sequentially(sets, next_index, separated_nodes)
    )


def draw_graph(d_separating_sets=None, separated_nodes=None):
    global ax, canvas, pos, fig

    ax.clear()

    node_colors = G.get_node_colors()

    # Draw the graph using the node colors
    nx.draw(
        G.graph,
        pos,
        with_labels=False,
        node_color=node_colors,
        edge_color="black",
        node_size=700,
        ax=ax,
    )

    # Manually draw labels with specific font colors
    for node, (x, y) in pos.items():
        if G.nodes[node].color == blue:
            font_color = green
        elif G.nodes[node].color == green:
            font_color = blue
        else:
            font_color = red

        ax.text(
            x,
            y,
            node,
            color=font_color,
            fontsize=10,
            ha="center",
            va="center",
            fontweight="bold",
        )

    fig.tight_layout()

    if d_separating_sets is not None:
        d_separating_sets.sort(key=len)
        textstr = (
            "D-Separating Sets of "
            + separated_nodes[0]
            + " and "
            + separated_nodes[1]
            + ":\n"
        )
        if len(d_separating_sets) == 0:
            textstr += "No D-Separating Sets\n"
        for i, s in enumerate(d_separating_sets):
            if s == set():
                textstr += "∅\n"
            textstr += "{" + ", ".join(s) + "}\n"

        props = dict(boxstyle="square", facecolor=yellow, alpha=0.5)
        ax.text(
            0.05,
            0.95,
            textstr,
            transform=ax.transAxes,
            fontsize=10,
            color=red,
            fontweight="bold",
            verticalalignment="top",
            bbox=props,
        )

    canvas.draw_idle()


def init_graph():
    global G, pos, active_nodes, adj_matrix_input, root, after_id

    # Stop highlighting
    if after_id:
        root.after_cancel(after_id)
        after_id = None

    _G = DSeparationGraph()

    input_text = adj_matrix_input.get("1.0", tk.END)
    if not validate(input_text):
        msgbox.showerror("Invalid Input", "Please enter a valid adjacency matrix.")
        return

    user_defined_adjacency_matrix = parse_adjacency_input(input_text)

    unique_nodes = set()
    for from_node, to_nodes in user_defined_adjacency_matrix.items():
        if from_node not in unique_nodes:
            _G.add_node(from_node)
            unique_nodes.add(from_node)
        for to_node in to_nodes:
            if to_node not in unique_nodes:
                _G.add_node(to_node)
                unique_nodes.add(to_node)
            _G.add_edge(from_node, to_node)

    if not nx.is_directed_acyclic_graph(_G.graph):
        msgbox.showerror("Invalid Input", "The graph must be directed and acyclic.")
        return
    G = _G

    # pos = graphviz_layout(G.graph, prog='dot')  # Positioning of the nodes
    pos = nx.circular_layout(G.graph)
    active_nodes = []

    # Initial graph drawing
    draw_graph()


def point_inside_circle(point, circle_center, radius):
    return (
        np.sqrt((point[0] - circle_center[0]) ** 2 + (point[1] - circle_center[1]) ** 2)
        < radius
    )


def on_click(event):
    global pos, G, active_nodes

    # Click coordinates
    x, y = event.xdata, event.ydata
    if x is None or y is None:  # Click was outside the axes
        return

    # Check each node to see if it was clicked
    for node, position in pos.items():
        if point_inside_circle((x, y), position, 0.1):
            current_node = G.nodes[node]
            current_node.toggle_color()

            if current_node.color == green:
                active_nodes.append(node)
            else:
                active_nodes.remove(node)

            if len(active_nodes) > 2:
                oldest_active_node = active_nodes.pop(0)
                G.nodes[oldest_active_node].toggle_color()

            draw_graph()
            break


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
                S_X = get_subsets_excluding_node_and_descendants(
                    all_nodes, node, descendants
                )
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


def d_separation():
    global G, active_nodes

    if len(active_nodes) != 2:
        msgbox.showerror("Error", "Please select exactly two nodes")
        return

    node1, node2 = active_nodes
    E = find_d_separating_sets(G.graph, node1, node2)

    highlight_sets_sequentially(list(E))


def parse_adjacency_input(input_text):
    adjacency_matrix = {}
    for line in input_text.strip().split("\n"):
        from_node, to_node = line.split()
        if from_node in adjacency_matrix:
            adjacency_matrix[from_node].append(to_node)
        else:
            adjacency_matrix[from_node] = [to_node]
    return adjacency_matrix


def validate(text):
    valid_chars = set("ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz1234567890 ")
    for line in text.strip().split("\n"):
        if not set(line).issubset(valid_chars):
            return False

        parts = line.split()
        if len(parts) != 2:
            return False

        from_node, to_node = parts
        if not from_node or not to_node:
            return False

    return True


default_adjacency_matrix = """A B
A C
B D
B E
C E
"""
blue = "#0020A1"
green = "#00FF00"
yellow = "#FFFF00"
red = "#FF1C6F"


def main():
    global data, ax, canvas, active_nodes, adj_matrix_input, root, fig

    active_nodes = []
    data = np.array([]).reshape(0, 2)

    bg_color = "#000826"

    root = tk.Tk()
    root.title("D-Separation Visualization")
    root.configure(bg=bg_color)

    font_style = ("Courier New", 14, "bold")

    input_frame = tk.Frame(root, padx=5, pady=5, bg=bg_color)
    input_frame.grid(row=0, column=0, sticky="ew")

    adj_matrix_input = tk.Text(
        input_frame, height=5, width=20, font=font_style, bg=blue, fg=green
    )
    adj_matrix_input.pack(padx=5, pady=5, fill="both", expand=True)
    adj_matrix_input.insert(tk.END, default_adjacency_matrix)

    btn_frame = tk.Frame(root, padx=5, pady=5, bg=bg_color)
    btn_frame.grid(row=1, column=0, sticky="ew")

    btn_init_graph = tk.Button(
        btn_frame,
        text="Generate Graph",
        command=init_graph,
        font=font_style,
        bg=blue,
        fg=green,
    )
    btn_init_graph.pack(side="left", padx=5, pady=5, fill="x", expand=True)

    btn_d_separation = tk.Button(
        btn_frame,
        text="Find D-separating Sets",
        command=d_separation,
        font=font_style,
        bg=blue,
        fg=green,
    )
    btn_d_separation.pack(side="left", padx=5, pady=5, fill="x", expand=True)

    fig, ax = plt.subplots(figsize=(8, 8))
    fig.patch.set_facecolor("black")
    ax.set_facecolor("black")
    canvas = FigureCanvasTkAgg(fig, master=root)
    canvas_widget = canvas.get_tk_widget()
    canvas_widget.grid(row=2, column=0, padx=5, pady=5, sticky="nsew")
    canvas_widget.configure(bg=bg_color)

    init_graph()

    canvas.mpl_connect("button_press_event", on_click)

    root.mainloop()


if __name__ == "__main__":
    main()
