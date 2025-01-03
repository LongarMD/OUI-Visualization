from common.module import Module
import tkinter.ttk as ttk
from modules.ab_pruning.module import AB_Pruning
from modules.ao_star.module import AO_Star
from typing import TYPE_CHECKING, List, Type


if TYPE_CHECKING:
    from common.app import App


MODULES: List[Type[Module]] = [AB_Pruning, AO_Star]


class MainMenu(Module):
    __label__ = "Main menu"

    def __init__(self, app: "App") -> None:
        super().__init__(app)

        self.draw()

    def draw(self) -> None:
        for module in MODULES:
            ttk.Button(
                self,
                text=module.__label__,
                command=lambda m=module: self.app.show_module(m),
            ).pack(pady=10)
