from typing import TYPE_CHECKING
import numpy as np
import tkinter as tk
import tkinter.ttk as ttk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import networkx as nx
import tkinter.messagebox as msgbox
import matplotlib.pyplot as plt

from common.module import Module
from .d_separation import (
    DSeparationGraph,
    find_d_separating_sets,
    GREEN,
    YELLOW,
    BLUE,
    RED,
    get_random_adjacency_matrix,
)

if TYPE_CHECKING:
    from common.app import App

default_adjacency_matrix = """A B
A C
B D
B E
C E
"""


class D_Separation(Module):
    """A module for visualizing and finding d-separation sets in directed acyclic graphs."""

    __label__ = "D-Separation"

    after_id: str | None = None
    G: DSeparationGraph | None = None

    def __init__(self, app: "App"):
        """Initialize the D-Separation module.

        Args:
            app: The main application instance
        """
        self.after_id = None
        super().__init__(app)

        self.active_nodes = []
        self.data = np.array([]).reshape(0, 2)

        self.create_widgets()
        self.init_graph()

    def destroy(self):
        """Clean up resources when the module is destroyed."""
        self.cancel_highlight()
        plt.close()
        self.canvas_widget.destroy()
        super().destroy()

    def create_widgets(self):
        """Create and layout all the GUI widgets for the module."""
        font_style = ("Courier New", 14, "bold")
        input_frame = ttk.Frame(self, padding=5)
        input_frame.grid(row=0, column=0, sticky="ew")

        style = ttk.Style()
        style.configure("Custom.TText", font=font_style)
        self.adj_matrix_input = tk.Text(input_frame, height=5, width=20, font=font_style)
        self.adj_matrix_input.pack(padx=5, pady=5, fill="both", expand=True)
        self.adj_matrix_input.insert(tk.END, default_adjacency_matrix)

        btn_frame = ttk.Frame(self, padding=5)
        btn_frame.grid(row=1, column=0, sticky="ew")

        btn_init_graph = ttk.Button(btn_frame, text="Generate Graph", command=self.init_graph, style="Custom.TButton")
        btn_init_graph.pack(side="left", padx=5, pady=5, fill="x", expand=True)

        btn_randomize = ttk.Button(
            btn_frame, text="Randomize", command=lambda: self.init_graph(randomize=True), style="Custom.TButton"
        )
        btn_randomize.pack(side="left", padx=5, pady=5, fill="x", expand=True)

        btn_d_separation = ttk.Button(
            btn_frame, text="Find D-separating Sets", command=self.d_separation, style="Custom.TButton"
        )
        btn_d_separation.pack(side="left", padx=5, pady=5, fill="x", expand=True)

        self.fig, self.ax = plt.subplots(figsize=(8, 8))
        self.fig.patch.set_facecolor("black")
        self.ax.set_facecolor("black")
        self.canvas = FigureCanvasTkAgg(self.fig, master=self)
        self.canvas_widget = self.canvas.get_tk_widget()
        self.canvas_widget.grid(row=2, column=0, padx=5, pady=5, sticky="nsew")

        self.canvas.mpl_connect("button_press_event", self.on_click)

    def init_graph(self, randomize: bool = False):
        """Initialize the graph from the adjacency matrix input.

        Creates a new directed graph based on the user input and validates that it is acyclic.
        Displays error messages if the input is invalid.
        If randomize is True, the graph is generated randomly instead of using the user input.
        """
        # Stop highlighting
        self.cancel_highlight()

        _G = DSeparationGraph()

        match randomize:
            case True:
                adj_matrix_str = get_random_adjacency_matrix()
                self.adj_matrix_input.delete("1.0", tk.END)
                self.adj_matrix_input.insert(tk.END, adj_matrix_str)
                adj_matrix = self.parse_adjacency_input(adj_matrix_str)
            case False:
                input_text = self.adj_matrix_input.get("1.0", tk.END)
                if not self.validate_input(input_text):
                    msgbox.showerror("Invalid Input", "Please enter a valid adjacency matrix.")
                    return
                adj_matrix = self.parse_adjacency_input(input_text)

        unique_nodes = set()
        for from_node, to_nodes in adj_matrix.items():
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

        self.pos = nx.circular_layout(_G.graph)
        self.G = _G
        self.active_nodes = []

        # Initial graph drawing
        self.draw_graph()

    def validate_input(self, text):
        """Validate the adjacency matrix input text.

        Args:
            text: The input text to validate

        Returns:
            bool: True if input is valid, False otherwise
        """
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

    def parse_adjacency_input(self, input_text):
        """Parse the adjacency matrix input text into a dictionary representation.

        Args:
            input_text: The input text containing the adjacency matrix

        Returns:
            dict: Dictionary mapping source nodes to lists of target nodes
        """
        adjacency_matrix = {}
        for line in input_text.strip().split("\n"):
            from_node, to_node = line.split()
            if from_node in adjacency_matrix:
                adjacency_matrix[from_node].append(to_node)
            else:
                adjacency_matrix[from_node] = [to_node]
        return adjacency_matrix

    def point_inside_circle(self, point, circle_center, radius):
        """Check if a point lies inside a circle.

        Args:
            point: Tuple of (x,y) coordinates of the point
            circle_center: Tuple of (x,y) coordinates of circle center
            radius: Radius of the circle

        Returns:
            bool: True if point is inside circle, False otherwise
        """
        return np.sqrt((point[0] - circle_center[0]) ** 2 + (point[1] - circle_center[1]) ** 2) < radius

    def on_click(self, event):
        """Handle mouse click events on the graph.

        Args:
            event: The mouse click event containing click coordinates
        """
        # Click coordinates
        x, y = event.xdata, event.ydata
        if x is None or y is None:  # Click was outside the axes
            return

        # Check each node to see if it was clicked
        for node, position in self.pos.items():
            if self.point_inside_circle((x, y), position, 0.1):
                current_node = self.G.nodes[node]
                current_node.toggle_color()

                if current_node.color == GREEN:
                    self.active_nodes.append(node)
                else:
                    self.active_nodes.remove(node)

                if len(self.active_nodes) > 2:
                    oldest_active_node = self.active_nodes.pop(0)
                    self.G.nodes[oldest_active_node].toggle_color()

                self.draw_graph()
                break

    def d_separation(self):
        """Find and display d-separating sets for the selected nodes."""
        if len(self.active_nodes) != 2:
            msgbox.showerror("Error", "Please select exactly two nodes")
            return

        node1, node2 = self.active_nodes
        E = find_d_separating_sets(self.G.graph, node1, node2)

        self.highlight_sets_sequentially(list(E))

    def cancel_highlight(self):
        """Cancel any ongoing highlighting animation."""
        if self.after_id:
            self.after_cancel(self.after_id)
            self.after_id = None

    def highlight_sets_sequentially(self, sets, current_index=0, separated_nodes=None):
        """Highlight d-separating sets one at a time in sequence.

        Args:
            sets: List of d-separating sets to highlight
            current_index: Index of current set being highlighted
            separated_nodes: The pair of nodes being d-separated
        """
        self.cancel_highlight()

        sets.sort(key=len)

        if not separated_nodes:
            separated_nodes = self.active_nodes.copy()

        for node in self.G.nodes.values():
            node.color = BLUE
            self.active_nodes.clear()

        if not sets:
            self.draw_graph(d_separating_sets=list(), separated_nodes=separated_nodes)
            return

        current_set = sets[current_index]
        for node_name in current_set:
            if node_name in self.G.nodes:
                self.G.nodes[node_name].color = YELLOW

        # Redraw the graph with updated colors
        self.draw_graph(sets, separated_nodes)

        # Schedule the next set to be highlighted
        next_index = (current_index + 1) % len(sets)
        self.after_id = self.after(2000, lambda: self.highlight_sets_sequentially(sets, next_index, separated_nodes))

    def draw_graph(self, d_separating_sets=None, separated_nodes=None):
        """Draw the graph with current node colors and optional d-separation information.

        Args:
            d_separating_sets: List of d-separating sets to display
            separated_nodes: The pair of nodes being d-separated
        """
        self.ax.clear()

        node_colors = self.G.get_node_colors()

        # Draw the graph using the node colors
        nx.draw(
            self.G.graph,
            self.pos,
            with_labels=False,
            node_color=node_colors,
            edge_color="black",
            node_size=700,
            ax=self.ax,
        )

        # Manually draw labels with specific font colors
        for node, (x, y) in self.pos.items():
            if self.G.nodes[node].color == BLUE:
                font_color = GREEN
            elif self.G.nodes[node].color == GREEN:
                font_color = BLUE
            else:
                font_color = RED

            self.ax.text(
                x,
                y,
                node,
                color=font_color,
                fontsize=10,
                ha="center",
                va="center",
                fontweight="bold",
            )

        self.fig.tight_layout()

        if d_separating_sets is not None:
            d_separating_sets.sort(key=len)
            textstr = "D-Separating Sets of " + separated_nodes[0] + " and " + separated_nodes[1] + ":\n"
            if len(d_separating_sets) == 0:
                textstr += "No D-Separating Sets\n"
            for _, s in enumerate(d_separating_sets):
                if s == set():
                    textstr += "∅\n"
                textstr += "{" + ", ".join(s) + "}\n"

            props = dict(boxstyle="square", facecolor=YELLOW, alpha=0.5)
            self.ax.text(
                0.05,
                0.95,
                textstr,
                transform=self.ax.transAxes,
                fontsize=10,
                color=RED,
                fontweight="bold",
                verticalalignment="top",
                bbox=props,
            )

        self.canvas.draw_idle()
