from common.module import Module
import tkinter.ttk as ttk
from modules.ab_pruning.ab_pruning import AB_Pruning


class MainMenu(Module):
    __label__ = "Main menu"

    def __init__(self) -> None:
        super().__init__()

        self.draw()

    def draw(self) -> None:
        ttk.Button(
            self,
            text=AB_Pruning.__label__,
            command=AB_Pruning.show,
        ).pack(pady=10)
