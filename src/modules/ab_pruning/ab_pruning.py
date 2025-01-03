import tkinter as tk
from tkinter import ttk
import tkinter.font as tkFont
from common.module import Module

from modules.ab_pruning.ab_simulator import TreeNode, AlphaBetaSimulator


class MovableCanvas(tk.Canvas):
    def __init__(self, master=None, **kwargs):
        tk.Canvas.__init__(self, master, **kwargs)
        self.bind("<ButtonPress-1>", lambda ev: self.scan_mark(ev.x, ev.y))
        self.bind("<B1-Motion>", lambda ev: self.scan_dragto(ev.x, ev.y, gain=1))
        self.bind("<MouseWheel>", self.zoom)

    def zoom(self, ev):
        x = self.canvasx(ev.x)
        y = self.canvasx(ev.y)
        scale = 1.001**ev.delta
        self.scale(tk.ALL, x, y, scale, scale)


class AB_Pruning(Module):
    __label__ = "Alpha-beta pruning"

    node_radius = 30
    tree_structure_lst = None
    leaf_values_lst = None

    def __init__(self) -> None:
        super().__init__()

        self.create_widgets()

    def create_widgets(self):
        self.widget_frame = ttk.Frame(self)
        self.widget_frame.pack(fill=tk.X)

        # tree structure input
        self.tree_structure_label = ttk.Label(
            self.widget_frame, text="Tree structure:", font=tkFont.Font(size=10)
        ).grid(row=0, column=0, padx=10, pady=10, sticky=tk.W)

        self.tree_structure = tk.StringVar()

        self.tree_structure_input = ttk.Entry(
            self.widget_frame,
            textvariable=self.tree_structure,
            font=tkFont.Font(size=10),
            width=40,
        )
        self.tree_structure_input.grid(
            row=0, column=1, padx=(0, 10), pady=10, sticky=tk.EW
        )
        # default value
        self.tree_structure_input.insert(tk.END, "2|2,2|2,2,2,2")

        def_bg = self.tree_structure_input.cget("background")
        self.tree_structure.trace_add(
            "write",
            lambda *args: self.tree_structure_input.configure(background=def_bg),
        )

        # leaf values input
        self.leaf_values_label = ttk.Label(
            self.widget_frame, text="Leafs:", font=tkFont.Font(size=10)
        )
        self.leaf_values_label.grid(row=1, column=0, padx=10, pady=(0, 10), sticky=tk.W)

        self.leaf_values = tk.StringVar()

        self.leaf_values_input = ttk.Entry(
            self.widget_frame,
            textvariable=self.leaf_values,
            font=tkFont.Font(size=10),
            width=40,
        )
        self.leaf_values_input.grid(
            row=1, column=1, padx=(0, 10), pady=(0, 10), sticky=tk.EW
        )
        # default value
        self.leaf_values_input.insert(tk.END, "11,-20,12,-10,-12,-5,-6,2")

        self.leaf_values.trace_add(
            "write", lambda *args: self.leaf_values_input.configure(background=def_bg)
        )

        # generate tree button
        self.generate_tree_btn = ttk.Button(
            self.widget_frame,
            text="Generate",
            command=self.validate_input,
        )
        self.generate_tree_btn.grid(row=0, column=2, padx=5, pady=10, sticky=tk.EW)

        # reset button
        self.reset_btn = ttk.Button(
            self.widget_frame,
            text="Reset",
            command=self.prepare_simulator,
        )
        self.reset_btn.grid(row=1, column=2, padx=5, pady=(0, 10), sticky=tk.EW)

        # canvas
        self.canvas = MovableCanvas(self, bg="white")
        self.canvas.pack(fill=tk.BOTH, expand=True)

        # simulation controls frame
        sim_frame = ttk.Frame(self.widget_frame)
        sim_frame.grid(
            row=0,
            column=3,
            rowspan=2,
            columnspan=3,
            padx=(20, 10),
            pady=10,
            sticky=tk.NSEW,
        )

        # instructions
        self.instruction_btn = ttk.Button(
            sim_frame,
            text="Instructions",
            command=self.show_instructions,
        )
        self.instruction_btn.grid(
            row=0, column=0, columnspan=4, sticky=tk.EW, pady=(0, 5)
        )

        self.all_backward_button = ttk.Button(sim_frame, text="<<")
        self.all_backward_button.grid(row=1, column=0, padx=(0, 5), sticky=tk.EW)

        self.backward_button = ttk.Button(sim_frame, text="<")
        self.backward_button.grid(row=1, column=1, padx=(0, 5), sticky=tk.EW)

        self.forward_button = ttk.Button(sim_frame, text=">")
        self.forward_button.grid(row=1, column=2, padx=(0, 5), sticky=tk.EW)

        self.all_forward_button = ttk.Button(sim_frame, text=">>")
        self.all_forward_button.grid(row=1, column=3, sticky=tk.EW)

        # Configure grid weights for resizing
        self.widget_frame.columnconfigure(1, weight=1)
        self.widget_frame.columnconfigure(3, weight=1)
        sim_frame.columnconfigure((0, 1, 2, 3), weight=1)

    def validate_input(self):
        tree_structure_str = self.tree_structure.get()
        leaf_values_str = self.leaf_values.get()

        is_valid = True

        # validate tree structure input
        tree_structure_lst = []
        layers = tree_structure_str.split("|")
        expected_no_nodes = 1

        for _, layer in enumerate(layers):
            tree_structure_lst.append([])
            layer_degrees = layer.split(",")
            # degree counts from upper layers should match with current layer
            if len(layer_degrees) != expected_no_nodes:
                is_valid = False

            degree_count = 0
            # each degree must be an (positive) integer
            for deg in layer_degrees:
                if deg.isnumeric() and int(deg) > 0:
                    degree_count += int(deg)
                    tree_structure_lst[-1].append(int(deg))
                else:
                    is_valid = False
            expected_no_nodes = degree_count

        tree_str_valid = is_valid

        leaf_values = []
        leafs = leaf_values_str.split(",")
        # number of leafs should match degree count from last layer
        if len(leafs) != expected_no_nodes:
            is_valid = False

        def is_number(s):
            try:
                float(s)
                return True
            except ValueError:
                return False

        for _, leaf in enumerate(leafs):
            if not is_number(leaf):
                is_valid = False
            else:
                leaf_values.append(float(leaf))

        if is_valid:
            print("input is valid!")
            self.tree_structure_lst = tree_structure_lst
            self.leaf_values_lst = leaf_values
            self.prepare_simulator()
        else:
            print("input is not valid!")
            self.invalid_input(tree_str_valid)

    def show_instructions(self):
        instruction = tk.Toplevel(self.app)
        instruction.title("Program Instructions")
        # instruction.geometry("500x400")

        instruction_text = (
            "Generate Tree:\n"
            "To create a tree, provide both the tree structure and leaf values.\n\n"
            "Tree Structure:\n"
            "Define the number of children for nodes in each layer. For instance, use the format\n"
            "'n|m1,m2,m3' where 'n' is the number of children for the app node, and 'm1,m2,m3'\n"
            "represent the number of children for the nodes in the next layer. Example: '3|3,3,3'\n"
            "signifies that the app node has 3 children, and each of those children has 3 children\n"
            "as well.\n\n"
            "Leaf Values:\n"
            "Input a list of numbers (possibly decimals) separated by commas. For the previously\n"
            "mentioned tree structure, an example would be: '-11,4,3,1.5,1,-5.3,7,-10,20'.\n\n"
            "Ensure that the input is semantically valid; otherwise, the tree cannot be generated.\n\n"
            "Alpha Beta Pruning Simulation:\n"
            "After generating a tree, simulate Alpha Beta pruning by clicking on '<<' and '>>'.\n\n"
            "Handling Large Trees:\n"
            "If the input generates a tree that is too large for the canvas, drag the tree around\n"
            "to view different parts of the tree. You can also use mouse-wheel for zooming."
        )

        label = ttk.Label(
            instruction, text=instruction_text, justify="left", padding=10
        )
        label.grid(row=0, column=0, pady=10, padx=10)

    def invalid_input(self, tree_str_valid):
        if not tree_str_valid:
            self.tree_structure_input.configure(style="Invalid.TEntry")
        else:
            self.leaf_values_input.configure(style="Invalid.TEntry")

    def prepare_simulator(self):
        if not self.tree_structure_lst or not self.leaf_values_lst:
            return

        app_node = TreeNode.generate_tree(self.tree_structure_lst, self.leaf_values_lst)

        # fixed margin
        margin_x = 80
        margin_y = 150

        app_node.set_position(margin_x, margin_y, margin_x, margin_y)
        app_node.center_node(app_node.x - self.canvas.winfo_width() / 2, 0)

        self.canvas.xview_moveto(0)
        self.canvas.yview_moveto(0)

        # draw initial tree
        self.draw_tree(app_node, self.node_radius)

        alpha_beta_simulator = AlphaBetaSimulator(self, app_node)

        # set buttons for controlling simulation
        self.backward_button.config(command=alpha_beta_simulator.backward)
        self.forward_button.config(command=alpha_beta_simulator.forward)

        self.all_backward_button.config(command=alpha_beta_simulator.all_backward)
        self.all_forward_button.config(command=alpha_beta_simulator.all_forward)

    # draws tree on canvas
    def draw_tree(
        self,
        app_node,
        radius,
        parent_x=None,
        parent_y=None,
        marked_node=None,
        cutoffs=None,
        cutoff=False,
        is_prop_up=None,
    ):
        # clear canvas
        if parent_x is None and parent_y is None:
            self.canvas.delete("all")

        self.draw_separators(app_node)
        self.draw_nodes(
            app_node,
            radius,
            parent_x,
            parent_y,
            marked_node,
            cutoffs,
            cutoff,
            is_prop_up,
        )

    # draws nodes on canvas
    def draw_nodes(
        self,
        node,
        radius,
        parent_x=None,
        parent_y=None,
        marked_node=None,
        cutoffs=None,
        cutoff=False,
        is_prop_up=None,
    ):
        # connect node with parent
        if parent_x is not None and parent_y is not None:
            self.canvas.create_line(
                parent_x, parent_y, node.x, node.y, width=1, fill="black"
            )

        # draw cutoff line
        if cutoff:
            self.draw_perpendicular_line(parent_x, parent_y, node.x, node.y)

        for i, child in enumerate(node.children):
            # determine if there is a cutoff
            cutoff = False
            for cutoff_pair in cutoffs or []:
                if cutoff_pair[0] == node and cutoff_pair[1] <= i:
                    cutoff = True

            self.draw_nodes(
                child, radius, node.x, node.y, marked_node, cutoffs, cutoff, is_prop_up
            )

        # draw node as triangle
        color = (
            "olivedrab1"
            if node == marked_node
            else ("light sky blue" if node.is_max else "IndianRed1")
        )
        v_max = [
            node.x,
            node.y - 0.866 * radius,
            node.x - radius,
            node.y + radius,
            node.x + radius,
            node.y + radius,
        ]
        v_min = [
            node.x - radius,
            node.y - radius,
            node.x + radius,
            node.y - radius,
            node.x,
            node.y + 0.866 * radius,
        ]
        vertices = v_max if node.is_max else v_min

        self.canvas.create_polygon(vertices, fill=color)

        # draw node value
        text_color = "red" if node == marked_node else "black"
        text_yoffset = (0.2 if node.is_max else -0.2) * radius
        self.canvas.create_text(
            node.x,
            node.y + text_yoffset,
            text=node.value_string(),
            font=("Arial", 10, "bold"),
            fill=text_color,
        )

        # draw alpha beta values
        display_eq = is_prop_up and node == marked_node
        self.canvas.create_text(
            node.x,
            node.y - 1.5 * self.node_radius,
            text=node.alpha_beta_string(display_eq),
            font=("Arial", 10, "bold"),
            fill=text_color,
        )

    def draw_perpendicular_line(self, x1, y1, x2, y2, length=10):
        # direction of the original line
        dx = x2 - x1
        dy = y2 - y1

        # perpendicular direction
        perp_dx = -dy
        perp_dy = dx

        # normalize perpendicular direction
        perp_length = (perp_dx**2 + perp_dy**2) ** 0.5
        perp_dx /= perp_length
        perp_dy /= perp_length

        # calculate endpoints of the perpendicular line
        x_center = x1 + (x2 - x1) / 2
        y_center = y1 + (y2 - y1) / 2

        perp_x1 = x_center + perp_dx * length
        perp_y1 = y_center + perp_dy * length
        perp_x2 = x_center - perp_dx * length
        perp_y2 = y_center - perp_dy * length

        # draw perpendicular line
        self.canvas.create_line(perp_x1, perp_y1, perp_x2, perp_y2, width=4, fill="red")

    # draws dotted separators between tree layers
    def draw_separators(self, app_node):
        padding = 75
        text_padding = 60

        set_x = set()
        set_y = set()
        app_node.get_possible_coords(set_x, set_y)

        min_x, max_x = min(set_x) - padding, max(set_x) + padding
        list_y = sorted(list(set_y))

        # draw separator between each layer
        for i in range(1, len(list_y)):
            y1, y2 = list_y[i - 1], list_y[i]
            y_line = (y1 + y2) / 2
            self.canvas.create_line(
                min_x - padding,
                y_line,
                max_x + padding,
                y_line,
                dash=(4, 2),
                fill="black",
            )

        # draw layer type
        for i, layer_y in enumerate(list_y):
            text = "MAX" if i % 2 == 0 else "MIN"
            self.canvas.create_text(
                max_x + text_padding,
                layer_y,
                text=text,
                font=("Arial", 12, "bold"),
                fill="black",
            )
