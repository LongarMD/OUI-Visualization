from common.module import Module
import tkinter.ttk as ttk
from typing import TYPE_CHECKING, List, Type

from modules.ab_pruning.module import AB_Pruning
from modules.ao_star.module import AO_Star
from modules.d_separation.module import D_Separation
from modules.knn.module import KNN
from modules.nomogram.module import Nomogram


if TYPE_CHECKING:
    from common.app import App


MODULES: List[Type[Module]] = [AB_Pruning, AO_Star, D_Separation, KNN, Nomogram]

category_names = {
    "machine_learning": "Machine Learning",
    "search": "Search",
    "planning": "Planning and Task Scheduling",
    "deduction": "Deduction",
}


class MainMenu(Module):
    __label__ = "Main menu"
    __instructions__ = "Select a module to start"

    def __init__(self, app: "App") -> None:
        super().__init__(app)

        self.categories = [m.__category_key__ for m in MODULES]
        for c in self.categories:
            if c not in category_names:
                raise ValueError(f"Category {c} not found in category_names")

        self.draw()

    def draw(self) -> None:
        # Create notebook (tab container)
        notebook = ttk.Notebook(self)
        notebook.pack(expand=True, fill="both")

        # Create a tab for each category
        category_tabs = {}
        for category in set(m.__category_key__ for m in MODULES):
            frame = ttk.Frame(notebook)
            notebook.add(frame, text=category_names[category])
            category_tabs[category] = frame

        # Add buttons to their respective category tabs
        for module in MODULES:
            ttk.Button(
                category_tabs[module.__category_key__],
                text=module.__label__,
                command=lambda m=module: self.app.show_module(m),  # type: ignore
            ).pack(pady=10)
