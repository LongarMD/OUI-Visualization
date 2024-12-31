class TreeNode:
    def __init__(self, is_max):
        self.is_max = is_max
        self.children = []
        self.value = None
        self.alpha = None
        self.beta = None
        self.prev_alpha = None
        self.prev_beta = None

    def is_leaf(self):
        return len(self.children) == 0

    def set_value(self, oth):
        if self.value is not None:
            v1, v2 = self.value, oth.value
            self.value = max(v1, v2) if self.is_max else min(v1, v2)
        else:
            self.value = oth.value

    def alpha_beta_propagate_up(self, child):
        if self.is_max:
            self.prev_alpha = self.alpha
            self.prev_child_beta = child.value
            self.alpha = max(self.alpha, child.value)
        else:
            self.prev_beta = self.beta
            self.prev_child_alpha = child.value
            self.beta = min(self.beta, child.value)

    def alpha_beta_propagate_down(self, parent):
        self.alpha = parent.alpha
        self.beta = parent.beta

        if self.is_leaf():
            if self.is_max:
                self.alpha = self.value
            else:
                self.beta = self.value

    def value_string(self):
        if self.value is not None:
            return str(int(self.value)) if self.value.is_integer() else str(self.value)
        else:
            return ""

    def alpha_beta_string(self, display_eq):
        if self.alpha is None or self.beta is None:
            return ""

        def to_string(f):
            if f.is_integer():
                return str(int(f))
            return str(f)

        if self.is_max and display_eq:
            alpha_string = f"max({to_string(self.prev_alpha)}, {to_string(self.prev_child_beta)}) = {to_string(self.alpha)}"
        else:
            alpha_string = to_string(self.alpha)

        if not self.is_max and display_eq:
            beta_string = f"min({to_string(self.prev_beta)}, {to_string(self.prev_child_alpha)}) = {to_string(self.beta)}"
        else:
            beta_string = to_string(self.beta)

        return f"\u03b1: {alpha_string}\n\u03b2: {beta_string}"

    # creates TreeNode structure from the given structure and leaf values
    def generate_tree(tree_structure_lst, leaf_values):
        root = TreeNode(True)
        prev_layer = [root]

        for layer_degrees in tree_structure_lst:
            curr_layer = []
            for i, degree in enumerate(layer_degrees):
                prev_layer[i].children = [
                    TreeNode(not prev_layer[i].is_max) for d in range(degree)
                ]
                curr_layer.extend(prev_layer[i].children)
            prev_layer = curr_layer

        # set leaf values
        for i, node in enumerate(prev_layer):
            node.value = leaf_values[i]

        return root

    # sets nodes positions (on canvas) recursively
    def set_position(self, curr_x, curr_y, margin_x, margin_y):
        if self.is_leaf():
            self.x = curr_x
            self.y = curr_y
            return curr_x + margin_x

        children_x = 0

        for child in self.children:
            curr_x = child.set_position(curr_x, curr_y + margin_y, margin_x, margin_y)
            children_x += child.x

        # set current's node position
        self.x = children_x / len(self.children)
        self.y = curr_y

        return curr_x

    # sets node positions to match the center of the canvas
    def center_node(self, offset_x, offset_y):
        self.x -= offset_x
        self.y -= offset_y

        for child in self.children:
            child.center_node(offset_x, offset_y)

    # traverses the tree and returns sets of possible x and y
    def get_possible_coords(self, set_x, set_y):
        set_x.add(self.x)
        set_y.add(self.y)

        for child in self.children:
            child.get_possible_coords(set_x, set_y)


class AlphaBetaSimulator:
    def __init__(self, app, root_node):
        self.app = app
        self.root_node = root_node

        self.curr_node = None
        self.curr_path = []
        self.over = False

        # maps node to index of next unvisited child
        self.next_child = {}

        # stores actions to allow backward steps
        self.action_stack = []

        # stores current cutoffs as (parent, cutoff_idx) pairs
        self.cutoffs = []

    def forward(self, draw=True):
        if self.over:
            return

        if self.curr_node is None:
            self.curr_node = self.root_node
            self.curr_path.append(self.curr_node)

            self.curr_node.alpha = float("-inf")
            self.curr_node.beta = float("inf")

            self.action_stack.append(("INIT",))

        else:
            if self.curr_node.is_leaf():
                prev_node = self.curr_node
                self.curr_node = self.curr_path[-2]
                self.curr_path.pop()

                # save previous values
                prev_value = self.curr_node.value
                prev_alpha = self.curr_node.alpha
                prev_beta = self.curr_node.beta

                # update value, alpha and beta
                self.curr_node.set_value(prev_node)
                self.curr_node.alpha_beta_propagate_up(prev_node)

                self.action_stack.append(
                    ("MOVE_UP", prev_node, prev_value, prev_alpha, prev_beta, False)
                )

            else:
                # determine next child's index
                if self.curr_node not in self.next_child:
                    self.next_child[self.curr_node] = 0
                next_child_idx = self.next_child[self.curr_node]

                # is there a cutoff?
                cutoff = self.curr_node.alpha >= self.curr_node.beta
                if cutoff:
                    self.cutoffs.append((self.curr_node, next_child_idx))

                # is there any unsivised child?
                if next_child_idx < len(self.curr_node.children) and not cutoff:
                    self.next_child[self.curr_node] += 1
                    self.curr_node = self.curr_node.children[next_child_idx]
                    self.curr_path.append(self.curr_node)

                    # save previous alpha and beta
                    prev_alpha = self.curr_node.alpha
                    prev_beta = self.curr_node.beta

                    # propagate alpha and beta
                    self.curr_node.alpha_beta_propagate_down(self.curr_path[-2])

                    self.action_stack.append(
                        ("MOVE_DOWN", self.curr_path[-2], prev_alpha, prev_beta)
                    )

                else:
                    if self.curr_node == self.root_node:
                        self.curr_path.pop()
                        self.curr_node = None
                        self.over = True

                        self.action_stack.append(("END", cutoff))

                    else:
                        prev_node = self.curr_node
                        self.curr_node = self.curr_path[-2]
                        self.curr_path.pop()

                        # save previous values
                        prev_value = self.curr_node.value
                        prev_alpha = self.curr_node.alpha
                        prev_beta = self.curr_node.beta

                        # update value, alpha and beta
                        self.curr_node.set_value(prev_node)
                        self.curr_node.alpha_beta_propagate_up(prev_node)

                        self.action_stack.append(
                            (
                                "MOVE_UP",
                                prev_node,
                                prev_value,
                                prev_alpha,
                                prev_beta,
                                cutoff,
                            )
                        )

        if draw:
            is_prop_up = (
                len(self.action_stack) > 0 and self.action_stack[-1][0] == "MOVE_UP"
            )
            self.app.draw_tree(
                self.root_node,
                self.app.node_radius,
                marked_node=self.curr_node,
                cutoffs=self.cutoffs,
                is_prop_up=is_prop_up,
            )

    def backward(self, draw=True):
        if len(self.action_stack) == 0:
            return

        action = self.action_stack[-1][0]

        if action == "INIT":
            self.curr_node.alpha = None
            self.curr_node.beta = None

            self.curr_node = None
            self.curr_path.pop()

            self.action_stack.pop()

        elif action == "MOVE_DOWN":
            # reconstruct node's alpha and beta
            self.curr_node.alpha = self.action_stack[-1][2]
            self.curr_node.beta = self.action_stack[-1][3]

            # set current node and fix child indexing
            self.curr_node = self.action_stack[-1][1]
            self.next_child[self.curr_node] -= 1
            self.curr_path.pop()

            self.action_stack.pop()

        elif action == "MOVE_UP":
            # reconstruct node's value, alpha and beta
            self.curr_node.value = self.action_stack[-1][2]
            self.curr_node.alpha = self.action_stack[-1][3]
            self.curr_node.beta = self.action_stack[-1][4]

            # set current node
            self.curr_node = self.action_stack[-1][1]
            self.curr_path.append(self.curr_node)

            # remove cutoff (if exists)
            if self.action_stack[-1][5]:
                self.cutoffs.pop()

            self.action_stack.pop()

        elif action == "END":
            self.curr_node = self.root_node
            self.curr_path.append(self.curr_node)
            self.over = False

            # remove cutoff
            if self.action_stack[-1][1]:
                self.cutoffs.pop()

            self.action_stack.pop()

        if draw:
            self.app.draw_tree(
                self.root_node,
                self.app.node_radius,
                marked_node=self.curr_node,
                cutoffs=self.cutoffs,
            )

    def all_backward(self):
        while len(self.action_stack):
            self.backward(draw=False)
        self.app.draw_tree(
            self.root_node,
            self.app.node_radius,
            marked_node=self.curr_node,
            cutoffs=self.cutoffs,
        )

    def all_forward(self):
        while not self.over:
            self.forward(draw=False)
        self.app.draw_tree(
            self.root_node,
            self.app.node_radius,
            marked_node=self.curr_node,
            cutoffs=self.cutoffs,
        )
