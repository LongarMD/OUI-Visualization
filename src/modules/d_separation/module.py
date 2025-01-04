from typing import TYPE_CHECKING, Dict, List, Optional, Set, Tuple, Any
import numpy as np
import tkinter as tk
import tkinter.ttk as ttk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg  # type: ignore
import networkx as nx  # type: ignore
import tkinter.messagebox as msgbox
import matplotlib.pyplot as plt  # type: ignore

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

default_adjacency_matrix: str = """A B
A C
B D
B E
C E"""

instructions: str = """# Instructions
1. Graph Creation
   - Enter edges in the text box using the format: "A B" (one edge per line)
   - Each line represents a directed edge from node A to node B
   - Click "Generate Graph" to create the graph
   - Click "Randomize" to generate a random graph

2. Node Selection
   - Click on nodes to select them (they will turn green)
   - You can select up to 2 nodes at a time
   - Click a selected node again to deselect it

3. Finding D-separating Sets
   - Select exactly 2 nodes
   - Click "Find D-separating Sets" to see all sets that d-separate the selected nodes
   - The d-separating sets will be displayed in yellow
   - Sets will cycle automatically every 2 seconds
   - Empty set (∅) means the nodes are d-separated without conditioning
   - If no sets are found, the nodes cannot be d-separated

Note: The graph must be acyclic (no cycles allowed). If you create a cyclic graph, you'll receive an error message.
"""


class D_Separation(Module):
    """A module for visualizing and finding d-separation sets in directed acyclic graphs."""

    __label__: str = "D-Separation"
    __instructions__: str = instructions

    after_id: str | None = None
    G: DSeparationGraph

    def __init__(self, app: "App"):
        """Initialize the D-Separation module.

        Args:
            app: The main application instance
        """
        self.after_id: Optional[str] = None
        super().__init__(app)

        self.active_nodes: List[str] = []
        self.data: np.ndarray = np.array([]).reshape(0, 2)
        self.pos: Dict[str, Tuple[float, float]] = {}
        self.fig: plt.Figure
        self.ax: plt.Axes
        self.canvas: FigureCanvasTkAgg
        self.canvas_widget: tk.Widget
        self.adj_matrix_input: tk.Text

        self.create_widgets()
        self.init_graph()

    def destroy(self) -> None:
        """Clean up resources when the module is destroyed."""
        self.cancel_highlight()
        plt.close()
        self.canvas_widget.destroy()
        super().destroy()

    def create_widgets(self) -> None:
        """Create and layout all the GUI widgets for the module."""
        # Configure grid weights for the main module frame
        self.grid_rowconfigure(2, weight=1)  # Make the graph row expandable
        self.grid_columnconfigure(0, weight=1)  # Make the column expandable

        font_style: Tuple[str, int, str] = ("Courier New", 14, "bold")

        # Configure input frame
        input_frame: ttk.Frame = ttk.Frame(self, padding=5)
        input_frame.grid(row=0, column=0, sticky="nsew")  # Changed sticky to nsew
        input_frame.grid_columnconfigure(0, weight=1)  # Make the text widget expand horizontally

        style: ttk.Style = ttk.Style()
        style.configure("Custom.TText", font=font_style)
        self.adj_matrix_input = tk.Text(input_frame, height=5, width=20, font=font_style)
        self.adj_matrix_input.pack(padx=5, pady=5, fill="both", expand=True)
        self.adj_matrix_input.insert(tk.END, default_adjacency_matrix)

        # Configure button frame
        btn_frame: ttk.Frame = ttk.Frame(self, padding=5)
        btn_frame.grid(row=1, column=0, sticky="nsew")  # Changed sticky to nsew
        btn_frame.grid_columnconfigure((0, 1, 2), weight=1)  # Give equal weight to all button columns

        # Update button configurations to use grid instead of pack
        btn_init_graph: ttk.Button = ttk.Button(
            btn_frame, text="Generate Graph", command=self.init_graph, style="Custom.TButton"
        )
        btn_init_graph.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")

        btn_randomize: ttk.Button = ttk.Button(
            btn_frame, text="Randomize", command=lambda: self.init_graph(randomize=True), style="Custom.TButton"
        )
        btn_randomize.grid(row=0, column=1, padx=5, pady=5, sticky="nsew")

        btn_d_separation: ttk.Button = ttk.Button(
            btn_frame, text="Find D-separating Sets", command=self.d_separation, style="Custom.TButton"
        )
        btn_d_separation.grid(row=0, column=2, padx=5, pady=5, sticky="nsew")

        self.fig, self.ax = plt.subplots(figsize=(8, 8))
        self.fig.patch.set_facecolor("black")
        self.ax.set_facecolor("black")
        self.canvas = FigureCanvasTkAgg(self.fig, master=self)
        self.canvas_widget = self.canvas.get_tk_widget()
        self.canvas_widget.grid(row=2, column=0, padx=5, pady=5, sticky="nsew")

        self.canvas.mpl_connect("button_press_event", self.on_click)

    def init_graph(self, randomize: bool = False) -> None:
        """Initialize the graph from the adjacency matrix input.

        Creates a new directed graph based on the user input and validates that it is acyclic.
        Displays error messages if the input is invalid.
        If randomize is True, the graph is generated randomly instead of using the user input.
        """
        # Stop highlighting
        self.cancel_highlight()

        _G: DSeparationGraph = DSeparationGraph()

        match randomize:
            case True:
                adj_matrix_str: str = get_random_adjacency_matrix()
                self.adj_matrix_input.delete("1.0", tk.END)
                self.adj_matrix_input.insert(tk.END, adj_matrix_str)
                adj_matrix: Dict[str, List[str]] = self.parse_adjacency_input(adj_matrix_str)
            case False:
                input_text: str = self.adj_matrix_input.get("1.0", tk.END)
                if not self.validate_input(input_text):
                    msgbox.showerror("Invalid Input", "Please enter a valid adjacency matrix.")
                    return
                adj_matrix = self.parse_adjacency_input(input_text)

        unique_nodes: Set[str] = set()
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

    def validate_input(self, text: str) -> bool:
        """Validate the adjacency matrix input text.

        Args:
            text: The input text to validate

        Returns:
            bool: True if input is valid, False otherwise
        """
        valid_chars: Set[str] = set("ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz1234567890 ")
        for line in text.strip().split("\n"):
            if not set(line).issubset(valid_chars):
                return False

            parts: List[str] = line.split()
            if len(parts) != 2:
                return False

            from_node, to_node = parts
            if not from_node or not to_node:
                return False

        return True

    def parse_adjacency_input(self, input_text: str) -> Dict[str, List[str]]:
        """Parse the adjacency matrix input text into a dictionary representation.

        Args:
            input_text: The input text containing the adjacency matrix

        Returns:
            dict: Dictionary mapping source nodes to lists of target nodes
        """
        adjacency_matrix: Dict[str, List[str]] = {}
        for line in input_text.strip().split("\n"):
            from_node, to_node = line.split()
            if from_node in adjacency_matrix:
                adjacency_matrix[from_node].append(to_node)
            else:
                adjacency_matrix[from_node] = [to_node]
        return adjacency_matrix

    def point_inside_circle(
        self, point: Tuple[float, float], circle_center: Tuple[float, float], radius: float
    ) -> bool:
        """Check if a point lies inside a circle.

        Args:
            point: Tuple of (x,y) coordinates of the point
            circle_center: Tuple of (x,y) coordinates of circle center
            radius: Radius of the circle

        Returns:
            bool: True if point is inside circle, False otherwise
        """
        return np.sqrt((point[0] - circle_center[0]) ** 2 + (point[1] - circle_center[1]) ** 2) < radius

    def on_click(self, event: Any) -> None:
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

    def d_separation(self) -> None:
        """Find and display d-separating sets for the selected nodes."""
        if len(self.active_nodes) != 2:
            msgbox.showerror("Error", "Please select exactly two nodes")
            return

        node1, node2 = self.active_nodes
        E: Set[Tuple[str, ...]] = find_d_separating_sets(self.G.graph, node1, node2)

        self.highlight_sets_sequentially(list(E))

    def cancel_highlight(self) -> None:
        """Cancel any ongoing highlighting animation."""
        if self.after_id:
            self.after_cancel(self.after_id)
            self.after_id = None

    def highlight_sets_sequentially(
        self, sets: List[Tuple[str, ...]], current_index: int = 0, separated_nodes: Optional[List[str]] = None
    ) -> None:
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

    def draw_graph(
        self, d_separating_sets: Optional[List[Tuple[str, ...]]] = None, separated_nodes: Optional[List[str]] = None
    ) -> None:
        """Draw the graph with current node colors and optional d-separation information.

        Args:
            d_separating_sets: List of d-separating sets to display
            separated_nodes: The pair of nodes being d-separated
        """
        self.ax.clear()

        node_colors: List[str] = self.G.get_node_colors()

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
            textstr: str = "D-Separating Sets of " + separated_nodes[0] + " and " + separated_nodes[1] + ":\n"
            if len(d_separating_sets) == 0:
                textstr += "No D-Separating Sets\n"
            for _, s in enumerate(d_separating_sets):
                if s == tuple():
                    textstr += "∅\n"
                textstr += "{" + ", ".join(s) + "}\n"

            props: Dict[str, Any] = dict(boxstyle="square", facecolor=YELLOW, alpha=0.5)
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
