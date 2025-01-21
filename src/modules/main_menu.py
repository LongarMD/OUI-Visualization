from common.module import Module
import tkinter.ttk as ttk
from typing import TYPE_CHECKING, List, Type

from modules.ab_pruning.module import AB_Pruning
from modules.d_separation.module import D_Separation
from modules.knn.module import KNN
from modules.nomogram.module import Nomogram
from modules.lst_scheduling.module import LST_Scheduling

if TYPE_CHECKING:
    from common.app import App


MODULES: List[Type[Module]] = [AB_Pruning, D_Separation, KNN, Nomogram, LST_Scheduling]

category_names = {
    "machine_learning": "Machine Learning",
    "search": "Search",
    "planning": "Planning and Task Scheduling",
    "reasoning": "Reasoning",
}


class MainMenu(Module):
    __label__ = "Main menu"
    __instructions__ = "Select a module to start"

    def __init__(self, app: "App") -> None:
        super().__init__(app)

        self.categories = {m.__category_key__ for m in MODULES}
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
        for category in category_names:
            if category not in self.categories:
                continue
            frame = ttk.Frame(notebook, padding=15)
            frame.grid_columnconfigure(1, weight=1)

            notebook.add(frame, text=category_names[category])
            category_tabs[category] = frame

        # Configure style for large, bold buttons
        style = ttk.Style()
        style.configure(
            "Bold.TButton",
            font=("TkDefaultFont", 15, "bold"),  # Much larger font
            padding=(10, 20),
        )  # Add internal padding (left/right, top/bottom)

        for i, module in enumerate(MODULES):
            frame = category_tabs[module.__category_key__]

            btn = ttk.Button(
                frame,
                text=module.__label__,
                command=lambda m=module: self.app.show_module(m),  # type: ignore
                width=20,
                style="Bold.TButton",
            )
            btn.grid(
                row=i * 2,
                column=0,
                padx=10,
                pady=10,
                sticky="nsew",
                rowspan=2,
            )

            # Create and configure the description label
            description = module.__short_description__
            desc_label = ttk.Label(frame, text=description, wraplength=600, justify="left")
            desc_label.grid(
                row=i * 2,
                column=1,
                padx=10,
                pady=10,
                sticky="nsew",
                rowspan=2,
            )
