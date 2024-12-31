import tkinter as tk
from common.module import Module


class Module1(Module):
    __label__ = "Alpha-beta pruning"

    def __init__(self) -> None:
        super().__init__()

        # Example label just to show we have some content
        title_label = tk.Label(self, text="Module 1", font=("Helvetica", 16, "bold"))
        title_label.pack(pady=10)

        # Placeholder for any additional widgets
        info_label = tk.Label(
            self, text="This is a placeholder for Module 1 functionality."
        )
        info_label.pack(pady=5)

        # In a real app, you might add buttons, canvases, or other components here
        # to run or display Module 1’s logic.
