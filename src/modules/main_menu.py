from common.module import Module
import tkinter.ttk as ttk
from modules.ab_pruning.module import AB_Pruning
from modules.ao_star.module import AO_Star
from typing import List, Type

MODULES: List[Type[Module]] = [AB_Pruning, AO_Star]


class MainMenu(Module):
    __label__ = "Main menu"

    def __init__(self) -> None:
        super().__init__()

        self.draw()

    def draw(self) -> None:
        for module in MODULES:
            ttk.Button(
                self,
                text=module.__label__,
                command=module.show,
            ).pack(pady=10)
