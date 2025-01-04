from common.module import Module
from modules.ao_star.ao_star import AOStarSolver, Node
from typing import TYPE_CHECKING
import tkinter as tk
import tkinter.ttk as ttk
import numpy as np

from modules.ao_star.examples import get_example


if TYPE_CHECKING:
    from common.app import App

instructions = """# AO* Algorithm Simulator Instructions

This simulator helps you understand the AO* algorithm through interactive exploration:

## Interface Elements
- Graph Display: Shows the current state of nodes and connections
- Heuristics Table: Displays initial heuristic values for each node
- Status Bar: Provides real-time guidance and feedback
- Control Panel: Input fields for F and G values

## How to Use
1. Select a Node
   - Click on an unexpanded node to develop it
   - The simulator will confirm if you've chosen correctly

2. Calculate and Enter Values
   - F-value: Total estimated cost (G + H)
   - G-value: Actual cost from start to current node
   - Status bar will guide you if values are incorrect

3. Progress Through the Algorithm
   - Click 'Submit' to confirm your values
   - Watch as the graph updates to show the node's development
   - Solution paths will be highlighted in green

## Additional Features
- Example Graphs: Choose from 5 different preset graphs
- Edit Options: Modify starting graph or heuristics
- Skip Button: Automatically advance to next step
- Node Colors:
  • Gray: Revealed but unexpanded
  • Black: Developed
  • Yellow: Solved
  • Green: Part of final solution

Note: The value 1000 represents infinity in cost calculations."""


class AO_Star(Module):
    __label__ = "AO*"
    __instructions__ = instructions

    solver: AOStarSolver
    canvas: tk.Canvas

    id2name: dict[int, Node] = {}
    iteration: int = 0
    num_iterations: int = 1
    node_entered: bool = False
    selected_node: Node | None = None

    def __init__(self, app: "App") -> None:
        super().__init__(app)
        self.set_example(1)
        self.solver.solve()

        self.draw()

    def reset(self):
        self.iteration = 0
        self.num_iterations = 1

    def draw(self):
        # Create frames
        canvas_frame = ttk.Frame(self)
        canvas_frame.pack(fill=tk.BOTH, expand=True)

        controls_frame = ttk.Frame(self)
        controls_frame.pack(fill=tk.X)

        # Controls frame widgets
        F_label = ttk.Label(controls_frame, text="Enter F cost:")
        F_label.grid(column=3, row=1)
        self.F_entry = ttk.Entry(controls_frame)
        self.F_entry.grid(column=4, row=1)
        self.F_entry.configure(state=tk.DISABLED)

        # G cost
        G_label = ttk.Label(controls_frame, text="Enter G cost:")
        G_label.grid(column=3, row=2)
        self.G_entry = ttk.Entry(controls_frame)
        self.G_entry.grid(column=4, row=2)
        self.G_entry.configure(state=tk.DISABLED)

        # submit F and G
        self.testFG = ttk.Button(controls_frame, text="Submit")  # TODO:, command=test_FG)
        self.testFG.grid(column=4, row=3)
        self.testFG.configure(state=tk.DISABLED)

        # get next step
        self.nextstep = ttk.Button(controls_frame, text="Next step")  # TODO:, command=next_step)
        self.nextstep.grid(column=2, row=3)
        self.nextstep.configure(state=tk.DISABLED)

        # current status
        self.status_text = tk.StringVar()
        self.status_text.set(
            "                                             STATUS:                                             "
        )
        self.status_label = ttk.Label(controls_frame, textvariable=self.status_text, style="Status.TLabel")
        self.status_label.grid(column=2, row=1)

        # current status2
        self.status_text2 = tk.StringVar()
        self.status_text2.set("             	select the first node to start the algorithm                ")
        self.status_label2 = ttk.Label(controls_frame, textvariable=self.status_text2, style="Status.TLabel")
        self.status_label2.grid(column=2, row=2)

        # canvas for trees
        self.canvas = tk.Canvas(canvas_frame)
        self.canvas.pack(fill=tk.BOTH, expand=True)
        self.canvas.bind("<Button-1>", self._on_node_click)

        # draw the trees
        self.draw_tree()

    def set_example(self, n: int):
        graph, H, final_nodes = get_example(n)
        self.solver = AOStarSolver(graph, H, final_nodes)

    def draw_tree(self):
        self.id2name = {}
        start_y = 105
        # legend
        self.canvas.create_text(35, start_y, fill="black", text="Legend:")
        self.canvas.create_oval(20, start_y + 15, 35, start_y + 30, outline="black", fill="gray")
        self.canvas.create_text(85, start_y + 22, fill="black", text="- revealed nodes")
        self.canvas.create_oval(20, start_y + 35, 35, start_y + 50, outline="black", fill="black")
        self.canvas.create_text(91, start_y + 42, fill="black", text="- developed nodes")
        self.canvas.create_oval(20, start_y + 55, 35, start_y + 70, outline="black", fill="goldenrod3")
        self.canvas.create_text(80, start_y + 62, fill="black", text="- solved nodes")
        self.canvas.create_oval(20, start_y + 75, 35, start_y + 90, outline="black", fill="lightgreen")
        self.canvas.create_text(86, start_y + 82, fill="black", text="- solution nodes")
        # different starting trees
        self.canvas.create_text(self.window_width - 50, start_y, fill="black", text="Examples")
        graph_button1 = tk.Button(self, text="Graph 1", command=lambda: self.set_example(1))
        self.canvas.create_window(self.window_width - 50, start_y + 30, window=graph_button1)
        graph_button2 = tk.Button(self, text="Graph 2", command=lambda: self.set_example(2))
        self.canvas.create_window(self.window_width - 50, start_y + 60, window=graph_button2)
        graph_button3 = tk.Button(self, text="Graph 3", command=lambda: self.set_example(3))
        self.canvas.create_window(self.window_width - 50, start_y + 90, window=graph_button3)
        graph_button4 = tk.Button(self, text="Graph 4", command=lambda: self.set_example(4))
        self.canvas.create_window(self.window_width - 50, start_y + 120, window=graph_button4)
        graph_button5 = tk.Button(self, text="Graph 5", command=lambda: self.set_example(5))
        self.canvas.create_window(self.window_width - 50, start_y + 150, window=graph_button5)
        # edit starting graph
        graph_button = tk.Button(self, text="Starting graph")  # TODO:, command=show_graph)
        self.canvas.create_window(self.window_width // 2, start_y, window=graph_button)
        # edit starting heuristics
        heuristics_button = tk.Button(self, text="Starting heuristics")  # TODO:, command=show_heuristics)
        self.canvas.create_window(self.window_width // 2, 25, window=heuristics_button)
        self.canvas.create_line(5, 80, self.window_width - 5, 80, fill="gray")
        node_names = ""
        node_heuristics = ""
        for i, (names, heuristics) in enumerate(self.solver.H.items()):
            if i == self.solver.node_count:
                break
            node_names += str(names).rjust(10, " ")
            node_heuristics += str(heuristics).rjust(10, " ")
        self.canvas.create_text(self.window_width // 2, 50, fill="black", text=node_names)
        self.canvas.create_text(self.window_width // 2, 65, fill="black", text=node_heuristics)

        ##### FIRST TREE #####
        levels = self.solver.get_levels()
        # GET POSITIONS
        positions = {}
        last_y = 0
        scale = 110
        for lvl in levels:
            y_offset = start_y + 30 + lvl * scale // 2
            if y_offset > last_y:
                last_y = y_offset
            level = levels[lvl]
            num_nodes = len(level)
            x_positions = [0]
            if num_nodes > 1:
                step = (2 * lvl * scale) // (num_nodes - 1)
                x_positions = np.arange(-lvl * scale, lvl * scale + 1, step)
            for ix, n in enumerate(level):
                x = self.window_width // 2 + x_positions[ix]
                y = y_offset
                node_type = self.solver.graph[n]
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
            self.canvas.create_oval(x - node_size, y - node_size, x + node_size, y + node_size, outline="black")
            # mark final nodes
            if node in self.solver.final_nodes:
                self.canvas.create_oval(
                    x - node_size + 2,
                    y - node_size + 2,
                    x + node_size - 2,
                    y + node_size - 2,
                    outline="black",
                )
            # node names
            self.canvas.create_text(x, y, fill="black", text=node)
            # node type
            if node_type:
                self.canvas.create_text(x, y + 20, fill="blue", text=node_type)

        # DRAW EDGES WITH WEIGHTS
        for node, edges in self.solver.graph.items():
            if "OR" in self.solver.graph[node]:
                edges = self.solver.graph[node]["OR"]
            elif "AND" in self.solver.graph[node]:
                edges = self.solver.graph[node]["AND"]
            else:
                edges = []
            for edge, weight in edges:
                x1, y1, _ = positions[node]
                x2, y2, _ = positions[edge]
                # create edges
                self.canvas.create_line(x1, y1 + node_size, x2, y2 - node_size, fill="gray")
                # add weight text in the middle of the edges
                self.canvas.create_text(
                    (x1 + x2) / 2 + 5,
                    (y1 + y2) / 2 + 5,
                    text=str(weight),
                    fill="darkblue",
                    font=("Arial", 10),
                )

        ##### SECOND TREE #####
        current_nodes = self.solver.nodes_list_iterations[self.iteration]
        levels = {}
        last_y += 50
        self.canvas.create_line(5, last_y - 15, self.window_width - 5, last_y - 15, fill="gray")
        self.canvas.create_text(self.window_width // 2, last_y + 10, fill="black", text="Simulation graph")

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
        for lvl in levels:
            levels[lvl].sort(key=lambda node: node.parent.name if node.parent else "")
            level = levels[lvl]
            num_nodes = len(level)
            x_positions = [0]
            if num_nodes > 1:
                step = (2 * lvl * scale) // (num_nodes - 1)
                x_positions = np.arange(-lvl * scale, lvl * scale + 1, step)
            for ix, n in enumerate(level):
                x = self.window_width // 2 + x_positions[ix]
                y = 35 + lvl * 50
                positions[n] = (x, y)

        # DRAW EDGES WITH WEIGHTS
        for node, position in positions.items():
            for child_node in node.children:
                if child_node in current_nodes:
                    x1, y1 = position
                    y1 += last_y
                    x2, y2 = positions[child_node]
                    y2 += last_y
                    self.canvas.create_line(x1, y1, x2, y2, fill="gray64")
                    self.canvas.create_text(
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
            if (
                node in self.solver.solution_tree and self.iteration == self.num_iterations - 1
            ):  # solution nodes are green
                node_id = self.canvas.create_oval(x - 10, y - 10, x + 10, y + 10, fill="lightgreen", outline="black")
                self.canvas.create_text(x, y, fill="black", text=node.name)
            elif node in self.solver.nodes_solved[self.iteration]:  # solved nodes are yellow
                node_id = self.canvas.create_oval(x - 10, y - 10, x + 10, y + 10, fill="goldenrod3", outline="black")
                self.canvas.create_text(x, y, fill="black", text=node.name)
            elif node in self.solver.nodes_sequence[: self.iteration]:  # developed nodes are black
                node_id = self.canvas.create_oval(x - 10, y - 10, x + 10, y + 10, fill="black", outline="black")
                self.canvas.create_text(x, y, fill="white", text=node.name)
            else:  # revealed nodes are gray
                node_id = self.canvas.create_oval(x - 10, y - 10, x + 10, y + 10, fill="gray75", outline="black")
                self.canvas.create_text(x, y, fill="black", text=node.name)
            if node in self.solver.nodes_sequence[: self.iteration] and node.type_:  # node type
                self.canvas.create_text(x, y + 20, fill="blue", text=node.type_)
            # show F values
            if node in self.solver.nodes_list_iterations[self.iteration - 1]:
                self.canvas.create_text(x + 40, y, fill="black", text=f"F({node.name})={current_nodes[node]}")
            # save position for node id
            self.id2name[node_id] = node

        # skip next step
        hint_button = tk.Button(self, text="Skip")  # TODO:, command=next_step)
        self.canvas.create_window(25, 50, window=hint_button)

        self.canvas.create_line(5, self.window_height - 10, self.window_width - 5, self.window_height - 10, fill="gray")

    def _on_node_click(self, event: tk.Event):
        item = self.canvas.find_closest(event.x, event.y)
        item_id = item[0]
        node = self.id2name.get(item_id)
        if node:
            # change color of selected node for 1 second to green if correct and red if wrong
            if node.name == self.solver.nodes_sequence[self.iteration].name:
                starting_color = self.canvas.itemcget(item_id, "fill")
                self.toggle_color(item_id, starting_color, "medium sea green")
                self.canvas.unbind("<Button-1>")
                self.node_entered = True
                self.selected_node = node
            else:
                starting_color = self.canvas.itemcget(item_id, "fill")
                self.toggle_color(item_id, starting_color, "firebrick2")
                self.node_entered = False
            self.update_status()

    def toggle_color(self, item_id, starting_color, new_color):
        current_color = self.canvas.itemcget(item_id, "fill")
        next_color = new_color if current_color != new_color else starting_color
        self.canvas.itemconfig(item_id, fill=next_color)
        self.canvas.after(500, self.toggle_color, item_id, starting_color, new_color)

    def update_status(self):
        if not self.node_entered:
            self.canvas.bind("<Button-1>", self._on_node_click)
        if self.node_entered:
            self.G_entry.configure(state=tk.NORMAL)
            self.F_entry.configure(state=tk.NORMAL)
            self.status_text2.set("                     correct node selected, enter F and G                     ")
            self.status_label.configure(bg="lightgreen")
            self.status_label2.configure(bg="lightgreen")
            self.testFG.configure(state=tk.NORMAL)
        else:
            self.G_entry.configure(state=tk.DISABLED)
            self.F_entry.configure(state=tk.DISABLED)
            self.testFG.configure(state=tk.DISABLED)
            self.status_text2.set(
                "                       incorrect node selected, try again                       "
            )  # , bg="red")
            self.status_label.configure(bg="salmon")
            self.status_label2.configure(bg="salmon")
        if self.F_entered and self.G_entered:
            self.F_entered = False
            self.G_entered = False
