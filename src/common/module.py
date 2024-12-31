import tkinter as tk
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from common.app import App


class Module(tk.Frame):
    """Base class for all modules"""

    __label__: str
    """Label of the module, used in the menu"""

    app: "App"
    """Static reference to the App instance, set by the App when the module is initialized"""

    def __init__(self) -> None:
        super().__init__()

    @classmethod
    def show(cls) -> None:
        """Show the module"""
        cls.app._show_module(cls)
