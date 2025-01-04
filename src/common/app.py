import tkinter as tk
import sv_ttk  # type: ignore
from modules.main_menu import MainMenu, MODULES

from common.module import Module

DEFAULT_WINDOW_SIZE = (1000, 600)


class App(tk.Tk):
    """
    The main application window class.

    This class handles the main window creation, positioning, theme management, and module
    switching functionality.

    Attributes:
        _current_module (Module | None): Currently displayed module

    The window uses the system's theme (light/dark) by default and provides options to
    switch between themes via the Options menu.
    """

    _current_module: "Module | None" = None

    def __init__(self) -> None:
        """
        Initialize the main application window.

        Sets up the window title, size, position, theme, and creates the menubar.
        This method is called only once when the singleton instance is created.
        """
        super().__init__()
        self.title("Visualizations")

        self.iconphoto(True, tk.PhotoImage(file="assets/favicon.png"))

        window_width, window_height = DEFAULT_WINDOW_SIZE
        self.geometry(f"{window_width}x{window_height}")
        self.resizable(True, True)

        self._center_window(window_width, window_height)

        sv_ttk.set_theme("light")  # darkdetect.theme()

        self._create_menubar()
        self.show_module(MainMenu)

    def _center_window(self, window_width: int, window_height: int) -> None:
        """
        Center the application window on the screen.

        Args:
            window_width (int): Width of the window in pixels
            window_height (int): Height of the window in pixels
        """
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()

        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2

        self.geometry(f"{window_width}x{window_height}+{x}+{y}")

    def _create_menubar(self) -> None:
        """
        Create and configure the application's menu bar.

        Sets up two main menus:
        - Modules: Contains navigation options to different application modules
        - Options: Contains application settings like theme toggling and exit option
        """
        menubar = tk.Menu(self)

        # "Modules" menu
        modules_menu = tk.Menu(menubar, tearoff=False)
        modules_menu.add_command(label=MainMenu.__label__, command=lambda: self.show_module(MainMenu))
        modules_menu.add_separator()
        for module in MODULES:
            modules_menu.add_command(label=module.__label__, command=lambda m=module: self.show_module(m))
        menubar.add_cascade(label="Menu", menu=modules_menu)

        # Create "Options" menu
        # options_menu = tk.Menu(menubar, tearoff=False)
        # options_menu.add_command(label="Toggle Theme", command=sv_ttk.toggle_theme)
        # options_menu.add_command(label="Exit", command=self.quit)
        # menubar.add_cascade(label="Options", menu=options_menu)

        self.config(menu=menubar)

    def show_module(self, module_class: type["Module"]) -> None:
        """
        Switch the currently displayed module.

        Destroys the current module if it exists and creates an instance of the new module.

        Args:
            module_class (type[Module]): The class of the module to be displayed
        """
        if self._current_module:
            self._current_module.destroy()

        module = module_class(self)
        module.pack(fill="both", expand=True)

        self._current_module = module
