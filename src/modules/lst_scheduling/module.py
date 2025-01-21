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
from .lst import Aktivnost, Planer, find_next_available_time

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
        self.fig = None
        self.ax = None
        self.canvas = None
        self.new_fig = None
        self.new_ax = None
        self.new_canvas = None

        self.create_widgets()

    def destroy(self) -> None:
        """Clean up resources when the module is destroyed."""
        if self.fig:
            plt.close(self.fig)
        if self.new_fig:
            plt.close(self.new_fig)
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
            command=self.dodaj_aktivnost,
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
            command=self.dodaj_resurs,
            width=15,
        )
        self.dodaj_resurs_button.grid(row=1, column=0, columnspan=2, pady=5)

        # Position resource frame
        self.frame_resurs.grid(row=1, column=1, sticky="nsew", padx=5)

        # Start simulation button
        self.zacni_simulacijo_button = tk.Button(
            self,
            text="Start Simulation",
            command=self.simuliraj,
        )
        self.zacni_simulacijo_button.grid(row=2, column=0, columnspan=2)

        # Create activities and resources window
        self.help_window = tk.Toplevel(self)
        self.help_window.title("Activities and Resources")
        self.help_window.geometry("700x300")
        self.help_window.grid_columnconfigure(0, weight=1)
        self.help_window.grid_columnconfigure(1, weight=1)
        self.help_window.grid_rowconfigure(1, weight=1)

        # Create labels
        self.label_activities = tk.Label(self.help_window, text="Activities", font=("Helvetica", 12))
        self.label_resources = tk.Label(self.help_window, text="Resources", font=("Helvetica", 12))

        self.label_activities.grid(row=0, column=0, sticky="nw", padx=10, pady=10)
        self.label_resources.grid(row=0, column=1, sticky="nw", padx=10, pady=10)

        # Create listboxes
        self.listbox_activities = tk.Listbox(self.help_window, font=("Helvetica", 14))
        self.listbox_resources = tk.Listbox(self.help_window, font=("Helvetica", 14))

        self.listbox_activities.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
        self.listbox_resources.grid(row=1, column=1, padx=10, pady=10, sticky="nsew")

    def dodaj_aktivnost(self) -> None:
        try:
            id_aktivnosti = self.id_entry.get()
            trajanje = int(self.trajanje_entry.get())
            odvisnosti_vnos = self.odvisnosti_entry.get()
            odvisnosti = odvisnosti_vnos.split(",") if odvisnosti_vnos else []
            resursi_vnos = self.resursi_entry.get()
            resursi = {}
            if resursi_vnos:
                for resurs in resursi_vnos.split(","):
                    ime_resursa = resurs.strip()
                    if ime_resursa in self.planer.all_resources:
                        resursi[ime_resursa.strip()] = int(1)
                    else:
                        msgbox.showerror("Error", f"Resource {ime_resursa} does not exist")
                        return
            nova_aktivnost = Aktivnost(id_aktivnosti, trajanje, odvisnosti, resursi)
            self.planer.dodaj_aktivnost(nova_aktivnost)
            self.planer.prikazi_urnik(self.ax, self.canvas)

            # počisti vnose
            self.id_entry.delete(0, tk.END)
            self.trajanje_entry.delete(0, tk.END)
            self.odvisnosti_entry.delete(0, tk.END)
            self.resursi_entry.delete(0, tk.END)
            # posodobi listbox
            new_string = (
                nova_aktivnost.id
                + ", "
                + str(nova_aktivnost.trajanje)
                + ", "
                + str(nova_aktivnost.odvisnosti)
                + ", "
                + str(list(nova_aktivnost.resursi.keys()))
            )
            self.listbox_activities.insert(tk.END, new_string)

        except ValueError:
            msgbox.showerror("Error", "Invalid input for activity duration.")

    def dodaj_resurs(self) -> None:
        try:
            resurs_name = self.all_resources_entry.get()

            if resurs_name in self.planer.all_resources:
                msgbox.showerror("Error", f"Resurs with name {resurs_name} already exists")
                return

            if resurs_name:  # and resurs_quantity > 0:
                self.planer.dodaj_resource(resurs_name, 1, False)
            else:
                msgbox.showerror("Error", "Invalid input for resource.")
        except ValueError:
            msgbox.showerror("Error", "Invalid input for resource quantity.")

        self.all_resources_entry.delete(0, tk.END)

        # posodobi listbox
        self.listbox_resources.insert(tk.END, resurs_name)

    def draw_activity_on_canvas(self, ax, activity, start_time, end_time, y_pos):
        def find_connected_activities(activity, connected_set):
            if activity.id in connected_set:
                return
            connected_set.add(activity.id)
            for dep_activity in self.planer.aktivnosti:
                if activity.id in dep_activity.odvisnosti:
                    find_connected_activities(dep_activity, connected_set)

        # Check if the activity is already in the color mapping
        if activity.id not in self.activity_color_mapping:
            connected_activities = set()
            find_connected_activities(activity, connected_activities)
            # Assign a color to all connected activities
            face_color = color_palette[self.current_color_index % len(color_palette)]
            self.current_color_index += 1
            for act_id in connected_activities:
                self.activity_color_mapping[act_id] = face_color
        else:
            face_color = self.activity_color_mapping[activity.id]

        rect_height = 8
        border_color = "black"
        border_width = 2

        rect = Rectangle(
            (start_time, y_pos - rect_height / 2),
            activity.trajanje,
            rect_height,
            facecolor=face_color,
            edgecolor=border_color,
            linewidth=border_width,
        )
        ax.add_patch(rect)

        # Add text inside the rectangle
        text = f"{activity.id}\n[{start_time}, {end_time}]"
        ax.text(
            start_time + activity.trajanje / 2,
            y_pos,
            text,
            ha="center",
            va="center",
            color="black",
        )

        # Adjust the axes limits if necessary
        ax.set_xlim(0, max(end_time + 10, ax.get_xlim()[1]))  # Adjust the x-axis limit
        ax.set_ylim(
            min(y_pos - rect_height, ax.get_ylim()[0]),
            max(y_pos + rect_height, ax.get_ylim()[1]),
        )  # Adjust the y-axis limit

    def simuliraj(self):
        # Kreiraj novo okno
        new_window = tk.Toplevel(self)
        new_window.title("LST Scheduling")
        new_window.geometry("800x650")
        new_window.grid_columnconfigure(0, weight=1)
        new_window.grid_rowconfigure(0, weight=3)
        new_window.grid_rowconfigure(1, weight=1)

        self.new_fig, self.new_ax = plt.subplots()
        self.new_ax.set_xlim(0, 100)
        self.new_ax.set_ylim(0, 100)
        self.new_canvas = FigureCanvasTkAgg(self.new_fig, master=new_window)
        self.new_canvas_widget = self.new_canvas.get_tk_widget()
        self.new_canvas_widget.grid(row=0, column=0, columnspan=2, sticky="nsew")

        # Dodaj gumb next step
        next_step_button = tk.Button(
            new_window,
            text="Next step",
            command=self.next_step,
            font=("Helvetica", 16),
        )
        next_step_button.grid(row=1, column=0, columnspan=1)

        # Dodaj resource ki imajo consumable = False
        resource_names = list([r for r in self.planer.all_resources if not self.planer.all_resources[r]["consumable"]])
        y_positions = [i * 20 for i in range(len(resource_names))]
        self.resource_y_positions = {name: y_pos for name, y_pos in zip(resource_names, y_positions)}

        self.new_ax.set_yticks(y_positions)
        self.new_ax.set_yticklabels(resource_names)
        self.new_ax.set_ylim(min(y_positions) - 20, max(y_positions) + 20)

    def next_step(self) -> None:
        if (
            "resource_availability" not in globals()
        ):  # dict kjer za vsak resurs hranimo tuple (start_time, end_time) ki predstavljajo kdaj je ta resurs zaseden
            resource_availability = {res: [] for res in self.planer.all_resources}

        unfinished_activities = [
            a for a in self.planer.aktivnosti if not a.finished and a.id not in ["start", "finish"]
        ]

        if not unfinished_activities:
            msgbox.showinfo("Info", "All activities are finished.")
            return

        ready_activities = [
            a
            for a in unfinished_activities
            if all(dep.finished for dep in self.planer.aktivnosti if dep.id in a.odvisnosti)
        ]  # aktivnosti ki imajo vse potrebne predhodnike končane

        if not ready_activities:
            return

        available_activities_slack = {
            a: a.ls - a.es for a in ready_activities
        }  # za vse izračunamo slack in vzamemo aktivnost z najmanjšim slackom
        activity_with_smallest_slack = min(available_activities_slack, key=available_activities_slack.get)

        # start time za aktivnost z najmanjšim slackom
        if activity_with_smallest_slack.resursi:
            required_resources = list(
                activity_with_smallest_slack.resursi.keys()
            )  # pogledamo katere vse resurse potrebuje aktivnost
            start_time = find_next_available_time(
                resource_availability,
                required_resources,
                activity_with_smallest_slack.trajanje,
                activity_with_smallest_slack.es,
            )  # poiščemo čas ko so vsi resursi prosti za celotno trajanje aktivnosti
            y_positions = [
                self.resource_y_positions.get(res, 0) for res in required_resources
            ]  # aktivnost bomo narisal k vsakmu resursu ki ga potrebuje
            end_time = start_time + activity_with_smallest_slack.trajanje
            for res in required_resources:  # dict resource_availability posodobimo z novim časom ko so resursi zasedeni
                resource_availability[res].append((start_time, end_time))

        else:  # če ne uporabla resursov jo narišemo k "Brez" in je njen start time enak njenemu ES
            start_time = activity_with_smallest_slack.es
            y_positions = [self.resource_y_positions.get("Brez", 0)]
            self.resource_y_positions["Brez"] -= 10
            end_time = start_time + activity_with_smallest_slack.trajanje

        activity_with_smallest_slack.finished = True

        if (
            start_time > activity_with_smallest_slack.ls
        ):  # posodobimo ES in LS za vse aktivnosti če ES presega pričakovan LS (LS kjer nismo upoštevali resursov)
            msgbox.showinfo("Info", "ES exceeds expected value. Updating ES and LS on the graph.")
            activity_with_smallest_slack.es = activity_with_smallest_slack.ls = start_time
            self.planer.izracunaj_es_naknadno()
            self.planer.izracunaj_ls_naknadno()
            self.planer.prikazi_urnik(self.ax, self.canvas)

        for y_pos in y_positions:  # narišemo na canvas aktivnost k vsem njenim resursom
            self.draw_activity_on_canvas(self.new_ax, activity_with_smallest_slack, start_time, end_time, y_pos)

        self.new_canvas.draw()
