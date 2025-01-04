from common.module import Module
import tkinter.ttk as ttk
from typing import TYPE_CHECKING, List, Type

from modules.ab_pruning.module import AB_Pruning
from modules.ao_star.module import AO_Star
from modules.d_separation.module import D_Separation
from modules.knn.module import KNN


if TYPE_CHECKING:
    from common.app import App


MODULES: List[Type[Module]] = [AB_Pruning, AO_Star, D_Separation, KNN]


class MainMenu(Module):
    __label__ = "Main menu"
    __instructions__ = "Select a module to start"

    def __init__(self, app: "App") -> None:
        super().__init__(app)

        self.draw()

    def draw(self) -> None:
        for module in MODULES:
            ttk.Button(
                self,
                text=module.__label__,
                command=lambda m=module: self.app.show_module(m),  # type: ignore
            ).pack(pady=10)
