from typing import TYPE_CHECKING, Any, Optional
import tkinter.ttk as ttk
import tkinter as tk
import tkinter.messagebox as msgbox
import matplotlib.pyplot as plt  # type: ignore
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg  # type: ignore
import numpy as np
from sklearn.datasets import load_iris  # type: ignore
from sklearn.decomposition import PCA  # type: ignore
import matplotlib.patches as patches  # type: ignore
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.patches import Rectangle, FancyArrowPatch
from tkinter import messagebox as msgbox

from common.module import Module
from .lst import Planer

if TYPE_CHECKING:
    from common.app import App
    from matplotlib.figure import Figure
    from matplotlib.axes import Axes
    from matplotlib.collections import PathCollection


instructions = """
1. Add resources that you will use in the simulation. (e.g. Cup)
2. Add activities, where each activity has:
        -> unique ID (e.g. Dinner)
        -> duration (e.g. 30)
        -> list of activities that must be executed directly before this activity, separated by commas (e.g. Breakfast,Lunch)
        -> list of resources that the activity needs, separated by commas (e.g. Cup)
3. Click on the "Start simulation" button
4. Click on the "Next step" button to show the next activity to be executed"""

color_palette = [
    "skyblue",
    "lightgreen",
    "lightcoral",
    "khaki",
    "lightpink",
    "plum",
]


class LST_Scheduling(Module):
    """A module for visualizing LST scheduling algorithm."""

    __label__: str = "LST Scheduling"
    __instructions__: str = instructions
    __category_key__: str = "planning"
    __short_description__: str = "Visualization of the Least Slack Time scheduling algorithm."

    def __init__(self, app: "App") -> None:
        super().__init__(app)

        self.planer = Planer()
        self.activity_color_mapping = {}
        self.current_color_index = 0

        self.create_widgets()

    def destroy(self) -> None:
        """Clean up resources when the module is destroyed."""
        plt.close(self.fig)
        super().destroy()

    def create_widgets(self) -> None:
        # Create figure and canvas
        self.fig, self.ax = plt.subplots()
        self.ax.axis("off")
        self.canvas = FigureCanvasTkAgg(self.fig, master=self)
        self.canvas_widget = self.canvas.get_tk_widget()
        self.canvas_widget.grid(row=0, column=0, columnspan=2, sticky="nsew")

        # Configure grid weights
        self.grid_rowconfigure(0, weight=3)
        self.grid_rowconfigure(1, weight=2)
        self.grid_rowconfigure(2, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        # Create activity frame
        self.frame_aktivnost = tk.Frame(self, relief=tk.RIDGE, borderwidth=5)
        self.frame_aktivnost.grid_rowconfigure(0, weight=1)
        self.frame_aktivnost.grid_rowconfigure(1, weight=1)
        self.frame_aktivnost.grid_rowconfigure(2, weight=1)
        self.frame_aktivnost.grid_rowconfigure(3, weight=1)
        self.frame_aktivnost.grid_rowconfigure(4, weight=1)
        self.frame_aktivnost.grid_columnconfigure(0, weight=1)
        self.frame_aktivnost.grid_columnconfigure(1, weight=1)

        # Activity ID
        self.id_label = tk.Label(
            master=self.frame_aktivnost,
            text="Activity ID:",
        )
        self.id_label.grid(row=0, column=0, sticky="w")
        self.id_entry = tk.Entry(
            master=self.frame_aktivnost,
        )
        self.id_entry.grid(row=0, column=1, sticky="nsew")

        # Duration
        self.trajanje_label = tk.Label(
            master=self.frame_aktivnost,
            text="Duration (natural number):",
        )
        self.trajanje_label.grid(row=1, column=0, sticky="w")
        self.trajanje_entry = tk.Entry(
            master=self.frame_aktivnost,
        )
        self.trajanje_entry.grid(row=1, column=1, sticky="nsew")

        # Dependencies
        self.odvisnosti_label = tk.Label(
            master=self.frame_aktivnost,
            text="Depends on activities: (ID1,ID2,...)",
        )
        self.odvisnosti_label.grid(row=2, column=0, sticky="w")
        self.odvisnosti_entry = tk.Entry(
            master=self.frame_aktivnost,
        )
        self.odvisnosti_entry.grid(row=2, column=1, sticky="nsew")

        # Resources
        self.resursi_label = tk.Label(
            master=self.frame_aktivnost,
            text="Resources (format: Resource1,Resource2,...):",
        )
        self.resursi_label.grid(row=3, column=0, sticky="w")
        self.resursi_entry = tk.Entry(
            master=self.frame_aktivnost,
        )
        self.resursi_entry.grid(row=3, column=1, sticky="nsew")

        # Add activity button
        self.dodaj_button = tk.Button(
            master=self.frame_aktivnost,
            text="Add Activity",
            # command=self.dodaj_aktivnost,  # TODO
        )
        self.dodaj_button.grid(row=4, column=0, columnspan=2)
        self.frame_aktivnost.grid(row=1, column=0, sticky="nsew")

        # Create resource frame
        # Create resource frame
        self.frame_resurs = tk.Frame(self, relief=tk.RIDGE, borderwidth=5)
        self.frame_resurs.grid_rowconfigure(0, weight=1)
        self.frame_resurs.grid_rowconfigure(1, weight=1)
        self.frame_resurs.grid_columnconfigure(0, weight=1)
        self.frame_resurs.grid_columnconfigure(1, weight=1)

        # Resource ID input
        self.all_resources_label = tk.Label(
            self.frame_resurs,
            text="Resource ID:",
            anchor="w",
            padx=5,
        )
        self.all_resources_label.grid(row=0, column=0, sticky="w")

        self.all_resources_entry = tk.Entry(self.frame_resurs, width=20)
        self.all_resources_entry.grid(row=0, column=1, sticky="ew", padx=5)

        # Add resource button
        self.dodaj_resurs_button = tk.Button(
            self.frame_resurs,
            text="Add Resource",
            # command=self.dodaj_resurs,  # TODO
            width=15,
        )
        self.dodaj_resurs_button.grid(row=1, column=0, columnspan=2, pady=5)

        # Position resource frame
        self.frame_resurs.grid(row=1, column=1, sticky="nsew", padx=5)

        # Start simulation button
        self.zacni_simulacijo_button = tk.Button(
            self,
            text="Start Simulation",
            bg="#007bff",
            fg="white",
            # command=self.simuliraj,  # TODO
        )
        self.zacni_simulacijo_button.grid(row=2, column=0, columnspan=2)
