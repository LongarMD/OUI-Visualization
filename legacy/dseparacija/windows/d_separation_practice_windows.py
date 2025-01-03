import random
import networkx as nx
import tkinter as tk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
from d_separation_windows import find_d_separating_sets


after_id = None


class GraphNode:
    def __init__(self, name):
        self.name = name
        self.color = blue

    def toggle_color(self):
        self.color = yellow if self.color == blue else blue


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
    global root, selected_nodes, after_id

    sets.sort(key=len)

    if not separated_nodes:
        separated_nodes = selected_nodes.copy()

    for node in G.nodes.values():
        node.color = blue
        selected_nodes.clear()

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
    global ax, canvas, pos, fig, two_nodes

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
    global G, pos, selected_nodes, root, after_id, two_nodes

    if after_id:
        root.after_cancel(after_id)
        after_id = None

    G = DSeparationGraph()

    num_nodes = random.randint(4, 7)
    for i in range(num_nodes):
        G.add_node(chr(ord("A") + i))

    for node in range(1, num_nodes):
        G.add_edge(chr(ord("A") + random.randint(0, node - 1)), chr(ord("A") + node))

        for potential_parent in range(node):
            if random.random() < 0.4:
                G.add_edge(chr(ord("A") + potential_parent), chr(ord("A") + node))

    pos = nx.circular_layout(G.graph)
    selected_nodes = []

    while True:
        two_nodes = random.sample(list(G.graph.nodes), 2)
        if (
            not G.graph.has_edge(two_nodes[0], two_nodes[1])
            and not G.graph.has_edge(two_nodes[1], two_nodes[0])
            or random.random() < 0.3
        ):
            break

    G.nodes[two_nodes[0]].color = green
    G.nodes[two_nodes[1]].color = green

    draw_graph()


def point_inside_circle(point, circle_center, radius):
    return (
        np.sqrt((point[0] - circle_center[0]) ** 2 + (point[1] - circle_center[1]) ** 2)
        < radius
    )


def on_click(event):
    global pos, G, selected_nodes

    # Click coordinates
    x, y = event.xdata, event.ydata
    if x is None or y is None:  # Click was outside the axes
        return

    # Check each node to see if it was clicked
    for node, position in pos.items():
        if point_inside_circle((x, y), position, 0.1):
            current_node = G.nodes[node]

            if current_node.color == green:
                continue

            current_node.toggle_color()

            if current_node.color == yellow:
                selected_nodes.append(node)
            else:
                selected_nodes.remove(node)

            draw_graph()
            break


def show_custom_messagebox(title, message, color):
    msgbox = tk.Toplevel()
    msgbox.title(title)
    msgbox.configure(bg=color)

    msg_label = tk.Label(msgbox, text=message, font=("Courier New", 12), bg=color)
    msg_label.pack(padx=20, pady=20)

    close_button = tk.Button(
        msgbox, text="Close", command=msgbox.destroy, bg="lightgrey"
    )
    close_button.pack(pady=10)

    # msgbox.eval('tk::PlaceWindow %s center' % msgbox.winfo_pathname(msgbox.winfo_id()))

    msgbox.mainloop()


def check():
    global G, selected_nodes, two_nodes

    node1, node2 = two_nodes
    E = find_d_separating_sets(G.graph, node1, node2)

    # Check if the selected nodes are a d-separating set
    E_as_sets = {frozenset(s) for s in E}

    if E_as_sets == set() and selected_nodes == []:
        show_custom_messagebox(
            "Correct?",
            f"There are no d-separating sets of {node1} and {node2}",
            "lightgreen",
        )
    elif frozenset(selected_nodes) in E_as_sets:
        show_custom_messagebox(
            "Correct!",
            f"The selected set: {set(selected_nodes)} is a d-separating set of {node1} and {node2}",
            "lightgreen",
        )
    else:
        show_custom_messagebox(
            "Incorrect!",
            f"The selected set: {set(selected_nodes)} is not a d-separating set of {node1} and {node2}",
            "red",
        )


def parse_adjacency_input(input_text):
    adjacency_matrix = {}
    for line in input_text.strip().split("\n"):
        from_node, to_node = line.split()
        if from_node in adjacency_matrix:
            adjacency_matrix[from_node].append(to_node)
        else:
            adjacency_matrix[from_node] = [to_node]
    return adjacency_matrix


blue = "#0020A1"
green = "#00FF00"
yellow = "#FFFF00"
red = "#FF1C6F"


def main():
    global data, ax, canvas, selected_nodes, root, fig

    selected_nodes = []
    data = np.array([]).reshape(0, 2)

    bg_color = "#000826"

    root = tk.Tk()
    root.title("D-Separation Visualization")
    root.configure(bg=bg_color)

    font_style = ("Courier New", 14, "bold")

    input_frame = tk.Frame(root, padx=5, pady=5, bg=bg_color)
    input_frame.grid(row=0, column=0, sticky="ew")

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
        btn_frame, text="Check", command=check, font=font_style, bg=blue, fg=green
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
