import tkinter as tk
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from common.app import App


class Module(tk.Frame):
    """Base class for all modules"""

    __label__: str
    """Label of the module, used in the menu"""

    app: "App"
    """Reference to the App instance"""

    def __init__(self, app: "App") -> None:
        super().__init__()
        self.app = app

    @property
    def window_width(self) -> int:
        return self.app.winfo_width()

    @property
    def window_height(self) -> int:
        return self.app.winfo_height()
