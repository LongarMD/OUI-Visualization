import tkinter as tk
import tkinter.ttk as ttk
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
    _help_window: "tk.Toplevel | None" = None

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

    def _get_window_center(self, window_width: int, window_height: int) -> tuple[int, int]:
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()

        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2

        return x, y

    def _center_window(self, window_width: int, window_height: int) -> None:
        """
        Center the application window on the screen.

        Args:
            window_width (int): Width of the window in pixels
            window_height (int): Height of the window in pixels
        """
        x, y = self._get_window_center(window_width, window_height)

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
            modules_menu.add_command(label=module.__label__, command=lambda m=module: self.show_module(m))  # type: ignore
        menubar.add_cascade(label="Menu", menu=modules_menu)

        # Create "Options" menu
        options_menu = tk.Menu(menubar, tearoff=False)
        # options_menu.add_command(label=Toggle Theme", command=sv_ttk.toggle_theme)
        options_menu.add_command(label="Help", command=self.show_help)
        options_menu.add_command(label="Exit", command=self.quit)
        menubar.add_cascade(label="Options", menu=options_menu)

        # Help menu

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

    def show_help(self) -> None:
        """
        Display a help window with instructions for the current module.

        Creates a new window containing formatted text from the current module's
        __instructions__ attribute. The text supports basic markdown formatting.

        The window includes a scrollbar that appears only when needed. If a help
        window is already open, it will be destroyed and replaced with a new one.

        Returns early if there is no current module or if the current module has
        no instructions.
        """
        if not self._current_module:
            return

        instructions = self._current_module.__instructions__

        if not instructions:
            return

        if self._help_window:
            self._help_window.destroy()

        help_window = tk.Toplevel(self)
        help_window.title("Help for " + self._current_module.__label__)

        w, h = 600, 600
        x, y = self._get_window_center(w, h)

        help_window.geometry(f"{w}x{h}+{x}+{y}")

        help_window.grid_rowconfigure(0, weight=1)
        help_window.grid_columnconfigure(0, weight=1)

        # Create a frame to hold the text widget and scrollbar
        text_frame = ttk.Frame(help_window)
        text_frame.grid(row=0, column=0, pady=10, padx=10, sticky="nsew")

        style = ttk.Style()
        font_name = style.lookup("TLabel", "font")
        font = (font_name, 10)

        # Create text widget and scrollbar
        text_widget = tk.Text(text_frame, wrap="word", width=50, height=10, font=font_name, relief="flat")
        scrollbar = ttk.Scrollbar(text_frame, orient="vertical", command=text_widget.yview)
        text_widget.configure(yscrollcommand=lambda first, last: self._update_scrollbar(scrollbar, first, last))

        # Pack the widgets
        text_widget.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Insert the text
        self._apply_markdown_styling(text_widget, instructions, font)
        text_widget.configure(state="disabled")  # Make it read-only

        self._help_window = help_window

    @staticmethod
    def _apply_markdown_styling(text_widget: tk.Text, content: str, font: tuple[str, int]) -> None:
        """Apply markdown-like styling to text content.

        Applies basic markdown formatting to text content in a tkinter Text widget:
        - Headings (lines starting with # or ##)
        - Bold text (wrapped in **)
        - Italic text (wrapped in _)
        - Horizontal line (---)

        Args:
            text_widget: The tkinter Text widget to apply styling to
            content: The markdown-formatted text content
            font: The font to use for the text
        """

        # Configure tags for styling
        text_widget.tag_configure("bold", font=(font[0], font[1], "bold"))
        text_widget.tag_configure("italic", font=(font[0], font[1], "italic"))
        text_widget.tag_configure("heading1", font=(font[0], font[1] + 3, "bold"))
        text_widget.tag_configure("heading2", font=(font[0], font[1] + 1, "bold"))
        text_widget.tag_configure("hline", relief="sunken", borderwidth=0.5, font=("", 1))

        for line in content.split("\n"):
            # Handle headings
            if line.startswith("## "):
                text_widget.insert("end", line[3:] + "\n", "heading2")
            elif line.startswith("# "):
                text_widget.insert("end", line[2:] + "\n", "heading1")
            # Handle bold text
            elif "**" in line:
                parts = line.split("**")
                for i, part in enumerate(parts):
                    if i % 2 == 1:  # Odd indices are bold
                        text_widget.insert("end", part, "bold")
                    else:
                        text_widget.insert("end", part)
                text_widget.insert("end", "\n")
            # Handle italic text
            elif "_" in line:
                parts = line.split("_")
                for i, part in enumerate(parts):
                    if i % 2 == 1:  # Odd indices are italic
                        text_widget.insert("end", part, "italic")
                    else:
                        text_widget.insert("end", part)
                text_widget.insert("end", "\n")
            elif line.strip() == "---":
                text_widget.insert("end", "\n")
                text_widget.insert("end", "\n", "hline")
                text_widget.insert("end", "\n")
            else:
                text_widget.insert("end", line + "\n")

    @staticmethod
    def _update_scrollbar(scrollbar: ttk.Scrollbar, first: float, last: float) -> None:
        """Update scrollbar visibility based on content"""
        scrollbar.set(first, last)
        if float(last) - float(first) == 1.0:
            scrollbar.pack_forget()
        else:
            scrollbar.pack(side="right", fill="y")
