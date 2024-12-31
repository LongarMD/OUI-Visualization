from common.module import Module
import tkinter.ttk as ttk
from modules.module1 import Module1


class MainMenu(Module):
    __label__ = "Main menu"

    def __init__(self) -> None:
        super().__init__()

        self.draw()

    def draw(self) -> None:
        ttk.Button(
            self,
            text=Module1.__label__,
            command=Module1.show,
        ).pack(pady=10)
