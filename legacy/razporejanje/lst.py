"""
Uporabljene knjižnice:
    - tkinter (from Python 3.12)
    - matplotlib (3.8.2)
    - numpy (1.26.3)

Navodila za uporabo:

    1. Dodaj resurse, ki jih boš uporabljal v simulaciji. (npr. Salica)
    2. Dodaj aktivnosti, kjer ima vsaka aktivnost:
            -> unikaten ID (npr. Večerja)
            -> trajanje    (npr. 30 )
            -> seznam aktivnosti, ki se morajo neposredno izvesti pred to aktivnostjo, ločenih z vejicami (npr. Zajtrk,Kosilo)
            -> seznam resursov, ki jih aktivnost potrebuje, ločenih z vejicami (npr. Salica)
    3. Klikni na gumb "Začni simulacijo"
    4. Klikni na gumb "Naslednji korak" za prikaz naslednje aktivnosti, ki se izvede
"""

import tkinter as tk
import tkinter.messagebox as msgbox
from tkinter import *
from tkinter.ttk import *
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.patches import Rectangle, FancyArrowPatch

import numpy as np


class Aktivnost:
    def __init__(self, id, trajanje, odvisnosti=[], resursi={}, finished=False):
        self.id = id
        self.trajanje = trajanje
        self.odvisnosti = odvisnosti
        self.es = 0  # Najzgodnejši začetek
        self.ls = 0  # Najkasnejši začetek
        self.resursi = resursi
        self.finished = finished


class Planer:
    def __init__(self):
        self.aktivnosti = [
            Aktivnost("start", 0, [], finished=True),
            Aktivnost("finish", 0, []),
        ]

        self.all_resources = {"Brez": {"kolicina": 1, "consumable": False}}

    # Dodajanje aktivnosti
    def dodaj_aktivnost(self, aktivnost):
        # Preveri, ali aktivnost z istim ID-jem že obstaja
        if any(a.id == aktivnost.id for a in self.aktivnosti):
            msgbox.showerror(
                "Error", "Aktivnost z ID-jem {} že obstaja".format(aktivnost.id)
            )
            return

        if not aktivnost.odvisnosti:
            aktivnost.odvisnosti = np.array(["start"])

        # Preveri, ali vse navedene odvisnosti obstajajo
        neobstojece_odvisnosti = [
            odv
            for odv in aktivnost.odvisnosti
            if not any(a.id == odv for a in self.aktivnosti)
        ]
        if neobstojece_odvisnosti:
            msgbox.showerror(
                "Error",
                "Aktivnost z ID-jem {} je odvisna od neobstoječih aktivnosti: {}".format(
                    aktivnost.id, neobstojece_odvisnosti
                ),
            )
            return

        # Dodaj novo aktivnost v seznam
        self.aktivnosti.append(aktivnost)
        self.posodobi_odvisnosti_finish()
        self.izracunaj_es()
        self.izracunaj_ls()

    # Dodajanje resursov
    def dodaj_resource(self, ime_resursa, kolicina, consumable=False):
        self.all_resources[ime_resursa] = {
            "kolicina": kolicina,
            "consumable": consumable,
        }

    # Posobobi odvisnosti finisha in postavi finish na konec seznama
    def posodobi_odvisnosti_finish(self):
        seznam_vseh_odvisnih = ["finish"]

        for a in self.aktivnosti:
            if a.id == "finish":
                a.odvisnosti = []
                break

        for a in self.aktivnosti:
            seznam_vseh_odvisnih.extend(a.odvisnosti)
            seznam_vseh_odvisnih = list(set(seznam_vseh_odvisnih))

        seznam_neodvisnih = [
            a.id for a in self.aktivnosti if a.id not in seznam_vseh_odvisnih
        ]
        for a in self.aktivnosti:
            if a.id == "finish":
                a.odvisnosti = seznam_neodvisnih
                # finish na konec seznama
                self.aktivnosti.remove(a)
                self.aktivnosti.append(a)
                break

    # Izračun ES za vse aktivnosti v self.aktivnosti
    def izracunaj_es(self):
        es_values = {"start": 0}

        def calculate_es(aktivnost_id):
            if aktivnost_id in es_values:
                return es_values[aktivnost_id]

            aktivnost = next((a for a in self.aktivnosti if a.id == aktivnost_id), None)
            if aktivnost is None:
                return 0
            if "start" in aktivnost.odvisnosti:
                es_values[aktivnost_id] = 0
            else:
                max_es = max(
                    calculate_es(dep)
                    + next(a for a in self.aktivnosti if a.id == dep).trajanje
                    for dep in aktivnost.odvisnosti
                )
                es_values[aktivnost_id] = max_es

            return es_values[aktivnost_id]

        for aktivnost in self.aktivnosti:
            aktivnost.es = calculate_es(aktivnost.id)

        for a in self.aktivnosti:
            a.es = es_values[a.id]

    # Izračun LS za vse aktivnosti v self.aktivnosti
    def izracunaj_ls(self):
        # Assuming that ES times are already calculated and a total project duration is set
        total_project_duration = max(
            a.es for a in self.aktivnosti
        )  # Assuming 'finish' activity represents the project end
        ls_values = {
            "finish": total_project_duration
        }  # Initialize LS for 'finish' activity

        # Function to recursively calculate LS
        def calculate_ls(aktivnost_id):
            if aktivnost_id in ls_values:
                return ls_values[aktivnost_id]

            aktivnost = next((a for a in self.aktivnosti if a.id == aktivnost_id), None)
            if aktivnost is None:
                return total_project_duration

            dependent_activities = [
                a for a in self.aktivnosti if aktivnost_id in a.odvisnosti
            ]
            if not dependent_activities:
                ls_values[aktivnost_id] = total_project_duration - aktivnost.trajanje
            else:
                min_ls = min(
                    calculate_ls(dep.id) - aktivnost.trajanje
                    for dep in dependent_activities
                )
                ls_values[aktivnost_id] = min_ls

            return ls_values[aktivnost_id]

        # Calculate LS for all activities in reverse order
        for aktivnost in reversed(self.aktivnosti):
            aktivnost.ls = calculate_ls(aktivnost.id)

        for a in self.aktivnosti:
            a.ls = ls_values[a.id]  # Return the calculated LS values

    def izracunaj_es_naknadno(self):
        # Assuming that ES times are already calculated, recalculate ES for all activities that are unfinished, but do not change the ES of finished activities

        def update_es(aktivnost_id):
            aktivnost = next((a for a in self.aktivnosti if a.id == aktivnost_id), None)
            if aktivnost is None:
                return 0

            if aktivnost.finished:
                return aktivnost.es

            if "start" in aktivnost.odvisnosti:
                aktivnost.es = 0
            else:
                max_es = max(
                    update_es(dep)
                    + next(a for a in self.aktivnosti if a.id == dep).trajanje
                    for dep in aktivnost.odvisnosti
                )
                aktivnost.es = max_es

            return aktivnost.es

        for aktivnost in self.aktivnosti:
            if not aktivnost.finished:
                update_es(aktivnost.id)

    def izracunaj_ls_naknadno(self):
        # Assuming that LS times are already calculated, recalculate LS for all activities that are unfinished, but do not change the LS of finished activities

        def update_ls(aktivnost):
            if aktivnost.finished:
                return aktivnost.ls

            dependent_activities = [
                a for a in self.aktivnosti if aktivnost.id in a.odvisnosti
            ]
            if not dependent_activities:
                aktivnost.ls = max(a.ls for a in self.aktivnosti) - aktivnost.trajanje
            else:
                min_ls = min(
                    update_ls(dep) - aktivnost.trajanje for dep in dependent_activities
                )
                aktivnost.ls = min_ls

            return aktivnost.ls

        self.aktivnosti[-1].ls = self.aktivnosti[-1].es

        for aktivnost in reversed(self.aktivnosti):
            if not aktivnost.finished and aktivnost.id != "finish":
                update_ls(aktivnost)

    # Prestej koliko aktivnosti ni odvisnih od nobene aktivnosti, zgolj za boljšo vizualizacijo
    def prestej_odvisnosti_od_starta(self):
        start_dependets = [a.id for a in self.aktivnosti if "start" in a.odvisnosti]
        dependent_count = len(start_dependets)
        y_positions = [
            15 * i for i in range(-dependent_count // 2 + 1, dependent_count // 2 + 1)
        ]
        return start_dependets, dependent_count, y_positions

    def prikazi_urnik(self, ax, canvas):
        ax.cla()
        rect_width, rect_height = 20, 10

        start_x, start_y = 0, 0  # Starting point for the 'Start' rectangle

        # Dictionary to store position of each activity
        positions = {}
        used_positions = set()
        # Preštejmo koliko aktivnosti je odvisnih od začetne aktivnosti
        start_dependents, dependent_count, start_dependets_y_positions = (
            self.prestej_odvisnosti_od_starta()
        )

        # Calculate positions of other activities
        for i, aktivnost in enumerate(self.aktivnosti):
            if aktivnost.id == "start":
                x = start_x
                y = start_y

            elif aktivnost.id == "finish":
                x = (
                    max(positions.values(), key=lambda x: x[0])[0] + rect_width * 1.5
                )  # finish je vedno najbolj desno
                y = start_y

            else:
                # če je aktivnost odvisna od starta je njena y koordinata odvisna od tega koliko aktivnosti je odvisnih od starta
                # tu je pogoj da če je aktivnost odvisna od starta je odvisna LE od starta
                if "start" in aktivnost.odvisnosti:
                    y_index = start_dependents.index(aktivnost.id)
                    y = start_dependets_y_positions[y_index]
                    x = start_x + rect_width * 1.5
                else:
                    x = max(
                        positions[odvisnost][0] + rect_width * 1.5
                        for odvisnost in aktivnost.odvisnosti
                    )
                    y = None

                    # try to align with one of the dependencies
                    for odvisnost in aktivnost.odvisnosti:
                        potential_y = positions[odvisnost][1]
                        if (x, potential_y) not in used_positions:
                            y = potential_y
                            break

                    if y is None:
                        y_offset = 0
                        while True:
                            potential_y_up = y_offset
                            potential_y_down = -y_offset
                            if (x, potential_y_up) not in used_positions:
                                y = potential_y_up
                                break
                            elif (x, potential_y_down) not in used_positions:
                                y = potential_y_down
                                break
                            y_offset += rect_height * 1.5

            positions[aktivnost.id] = (x, y)
            used_positions.add((x, y))

            # Draw the activity rectangle
            rect = Rectangle((x, y), rect_width, rect_height, facecolor="skyblue")
            ax.add_patch(rect)
            ax.text(
                x + rect_width / 2,
                y + rect_height / 2,
                f"{aktivnost.id}\n[{aktivnost.es}, {aktivnost.ls}]\nt: {aktivnost.trajanje}",
                horizontalalignment="center",
                verticalalignment="center",
            )

        # Draw arrows for dependencies
        for aktivnost in self.aktivnosti:
            if aktivnost.odvisnosti:
                for odvisnost in aktivnost.odvisnosti:
                    start_pos = positions[odvisnost]
                    end_pos = positions[aktivnost.id]
                    arrow = FancyArrowPatch(
                        (start_pos[0] + rect_width, start_pos[1] + rect_height / 2),
                        (end_pos[0], end_pos[1] + rect_height / 2),
                        arrowstyle="simple",
                        color="red",
                    )
                    ax.add_patch(arrow)

        # Adjust the chart
        ax.set_xlim(0, max(positions.values(), key=lambda x: x[0])[0] + rect_width * 2)
        ax.set_ylim(
            min(positions.values(), key=lambda x: x[1])[1] - rect_height * 2,
            max(positions.values(), key=lambda x: x[1])[1] + rect_height * 2,
        )
        ax.axis("off")  # Turn off the axis
        ax.set_title("Vizualizacija urnika z minimalno časovno rezervo")
        canvas.draw()


def dodaj_aktivnost():
    global \
        id_entry, \
        trajanje_entry, \
        odvisnosti_entry, \
        resursi_entry, \
        planer, \
        ax, \
        canvas, \
        listbox_activities
    try:
        id_aktivnosti = id_entry.get()
        trajanje = int(trajanje_entry.get())
        odvisnosti_vnos = odvisnosti_entry.get()
        odvisnosti = odvisnosti_vnos.split(",") if odvisnosti_vnos else []
        resursi_vnos = resursi_entry.get()
        resursi = {}
        if resursi_vnos:
            for resurs in resursi_vnos.split(","):
                ime_resursa = resurs.strip()
                if ime_resursa in planer.all_resources:
                    resursi[ime_resursa.strip()] = int(1)
                else:
                    msgbox.showerror(
                        "Error", "Resurs {} ne obstaja".format(ime_resursa)
                    )
                    return
        nova_aktivnost = Aktivnost(id_aktivnosti, trajanje, odvisnosti, resursi)
        planer.dodaj_aktivnost(nova_aktivnost)
        planer.prikazi_urnik(ax, canvas)

        # počisti vnose
        id_entry.delete(0, tk.END)
        trajanje_entry.delete(0, tk.END)
        odvisnosti_entry.delete(0, tk.END)
        resursi_entry.delete(0, tk.END)
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
        listbox_activities.insert(tk.END, new_string)

    except ValueError:
        msgbox.showerror("Error", "Napačen vnos za trajanje aktivnosti.")


def dodaj_resurs():
    global all_resources_entry, planer, listbox_resources

    try:
        resurs_name = all_resources_entry.get()

        if resurs_name in planer.all_resources:
            msgbox.showerror(
                "Error", "Resurs z imenom {} že obstaja".format(resurs_name)
            )
            return

        if resurs_name:  # and resurs_quantity > 0:
            planer.dodaj_resource(resurs_name, 1, False)
        else:
            msgbox.showerror("Error", "Napačen vnos za resurs.")
    except ValueError:
        msgbox.showerror("Error", "Napačen vnos za količino resursa.")

    all_resources_entry.delete(0, tk.END)

    # posodobi listbox
    listbox_resources.insert(tk.END, resurs_name)


def simuliraj():
    global planer, ax, canvas, new_ax, new_canvas, resource_y_positions

    # Kreiraj novo okno
    new_window = tk.Toplevel()
    new_window.title("Razporejanje opravil z uporabo algoritma najmanjše rezerve")
    new_window.geometry("800x650")
    new_window.grid_columnconfigure(0, weight=1)
    new_window.grid_rowconfigure(0, weight=3)
    new_window.grid_rowconfigure(1, weight=1)

    new_fig, new_ax = plt.subplots()
    new_ax.set_xlim(0, 100)
    new_ax.set_ylim(0, 100)
    new_canvas = FigureCanvasTkAgg(new_fig, master=new_window)
    new_canvas_widget = new_canvas.get_tk_widget()
    new_canvas_widget.grid(row=0, column=0, columnspan=2, sticky="nsew")

    # Dodaj gumb next step
    next_step_button = tk.Button(
        new_window,
        text="Naslednji korak",
        bg="green",
        fg="white",
        command=next_step,
        font=("Helvetica", 16),
    )
    next_step_button.grid(row=1, column=0, columnspan=1)

    # Dodaj resource ki imajo consumable = False
    resource_names = list(
        [r for r in planer.all_resources if not planer.all_resources[r]["consumable"]]
    )
    y_positions = [i * 20 for i in range(len(resource_names))]
    resource_y_positions = {
        name: y_pos for name, y_pos in zip(resource_names, y_positions)
    }

    new_ax.set_yticks(y_positions)
    new_ax.set_yticklabels(resource_names)
    new_ax.set_ylim(min(y_positions) - 20, max(y_positions) + 20)


def next_step():
    global \
        planer, \
        ax, \
        canvas, \
        new_ax, \
        new_canvas, \
        resource_y_positions, \
        resource_availability

    if (
        "resource_availability" not in globals()
    ):  # dict kjer za vsak resurs hranimo tuple (start_time, end_time) ki predstavljajo kdaj je ta resurs zaseden
        resource_availability = {res: [] for res in planer.all_resources}

    unfinished_activities = [
        a
        for a in planer.aktivnosti
        if not a.finished and a.id not in ["start", "finish"]
    ]

    if not unfinished_activities:
        msgbox.showinfo("Info", "Vse aktivnosti so končane.")
        return

    ready_activities = [
        a
        for a in unfinished_activities
        if all(dep.finished for dep in planer.aktivnosti if dep.id in a.odvisnosti)
    ]  # aktivnosti ki imajo vse potrebne predhodnike končane

    if not ready_activities:
        return

    available_activities_slack = {
        a: a.ls - a.es for a in ready_activities
    }  # za vse izračunamo slack in vzamemo aktivnost z najmanjšim slackom
    activity_with_smallest_slack = min(
        available_activities_slack, key=available_activities_slack.get
    )

    # start time za aktivnost z najmanjšim slackom
    if activity_with_smallest_slack.resursi:
        required_resources = list(
            activity_with_smallest_slack.resursi.keys()
        )  # pogledamo katere vse resurse potrebuje aktivnost
        start_time = find_next_available_time(
            required_resources,
            activity_with_smallest_slack.trajanje,
            activity_with_smallest_slack.es,
        )  # poiščemo čas ko so vsi resursi prosti za celotno trajanje aktivnosti
        y_positions = [
            resource_y_positions.get(res, 0) for res in required_resources
        ]  # aktivnost bomo narisal k vsakmu resursu ki ga potrebuje
        end_time = start_time + activity_with_smallest_slack.trajanje
        for res in (
            required_resources
        ):  # dict resource_availability posodobimo z novim časom ko so resursi zasedeni
            resource_availability[res].append((start_time, end_time))

    else:  # če ne uporabla resursov jo narišemo k "Brez" in je njen start time enak njenemu ES
        start_time = activity_with_smallest_slack.es
        y_positions = [resource_y_positions.get("Brez", 0)]
        resource_y_positions["Brez"] -= 10
        end_time = start_time + activity_with_smallest_slack.trajanje

    activity_with_smallest_slack.finished = True

    if (
        start_time > activity_with_smallest_slack.ls
    ):  # posodobimo ES in LS za vse aktivnosti če ES presega pričakovan LS (LS kjer nismo upoštevali resursov)
        msgbox.showinfo(
            "Info", "ES presega pričakovano vrednost. Posodobimo ES ter LS na grafu."
        )
        activity_with_smallest_slack.es = activity_with_smallest_slack.ls = start_time
        planer.izracunaj_es_naknadno()
        planer.izracunaj_ls_naknadno()
        planer.prikazi_urnik(ax, canvas)

    for y_pos in y_positions:  # narišemo na canvas aktivnost k vsem njenim resursom
        draw_activity_on_canvas(
            new_ax, activity_with_smallest_slack, start_time, end_time, y_pos
        )

    new_canvas.draw()


def find_next_available_time(required_resources, duration, es):
    global resource_availability
    earliest_start_time = es

    while True:
        all_resources_available = True

        # Check availability for each resource
        for res in required_resources:
            intervals = resource_availability[res]
            # Sort intervals by start time
            intervals.sort(key=lambda x: x[0])

            resource_free = True

            # Check if the resource is free in the current time slot
            for start, end in intervals:
                if start <= earliest_start_time < end:
                    print(
                        "Resource {} is busy in the time slot [{}, {}]".format(
                            res, start, end
                        )
                    )
                    # The resource is busy in this slot, move to the end of this busy period
                    earliest_start_time = end
                    resource_free = False
                    break
                elif (
                    earliest_start_time < start
                    and earliest_start_time + duration > start
                ):
                    # The current slot is free, but the activity will overlap with the next busy period
                    earliest_start_time = end
                    resource_free = False
                    break

            if not resource_free:
                all_resources_available = False
                break

        # If all resources are available, return this time slot
        if all_resources_available:
            return earliest_start_time


def draw_activity_on_canvas(ax, activity, start_time, end_time, y_pos):
    global activity_color_mapping, color_palette, current_color_index
    # Draw a rectangle for the activity

    def find_connected_activities(activity, connected_set):
        if activity.id in connected_set:
            return
        connected_set.add(activity.id)
        for dep_activity in planer.aktivnosti:
            if activity.id in dep_activity.odvisnosti:
                find_connected_activities(dep_activity, connected_set)

    # Check if the activity is already in the color mapping
    if activity.id not in activity_color_mapping:
        connected_activities = set()
        find_connected_activities(activity, connected_activities)
        # Assign a color to all connected activities
        face_color = color_palette[current_color_index % len(color_palette)]
        current_color_index += 1
        for act_id in connected_activities:
            activity_color_mapping[act_id] = face_color
    else:
        face_color = activity_color_mapping[activity.id]

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


def activities_resources():
    global listbox_activities, listbox_resources

    help_window = tk.Toplevel()
    help_window.title("Activities and Resources")
    help_window.geometry("700x300")
    help_window.grid_columnconfigure(0, weight=1)
    help_window.grid_columnconfigure(1, weight=1)
    help_window.grid_rowconfigure(1, weight=1)

    label_activities = tk.Label(help_window, text="Aktivnosti", font=("Helvetica", 12))
    label_resources = tk.Label(help_window, text="Resursi", font=("Helvetica", 12))

    label_activities.grid(row=0, column=0, sticky="nw", padx=10, pady=10)
    label_resources.grid(row=0, column=1, sticky="nw", padx=10, pady=10)

    listbox_activities = tk.Listbox(help_window, font=("Helvetica", 14))
    listbox_resources = tk.Listbox(help_window, font=("Helvetica", 14))

    listbox_activities.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
    listbox_resources.grid(row=1, column=1, padx=10, pady=10, sticky="nsew")


def main():
    global \
        id_entry, \
        trajanje_entry, \
        odvisnosti_entry, \
        resursi_entry, \
        all_resources_entry, \
        planer, \
        ax, \
        canvas, \
        activity_color_mapping, \
        color_palette, \
        current_color_index

    planer = Planer()

    activity_color_mapping = {}  # global dictionary to map activities to colors
    color_palette = [
        "skyblue",
        "lightgreen",
        "lightcoral",
        "khaki",
        "lightpink",
        "plum",
    ]  # list of colors to use
    current_color_index = 0  # to keep track of which color to use next

    root = tk.Tk()
    root.geometry("1000x650")
    root.title("Razporejanje opravil brez upoštevanja resursov")

    fig, ax = plt.subplots()
    ax.axis("off")
    canvas = FigureCanvasTkAgg(fig, master=root)
    canvas_widget = canvas.get_tk_widget()
    canvas_widget.grid(row=0, column=0, columnspan=2, sticky="nsew")

    root.grid_rowconfigure(0, weight=3)
    root.grid_rowconfigure(1, weight=2)
    root.grid_rowconfigure(2, weight=1)
    root.grid_columnconfigure(0, weight=1)
    root.grid_columnconfigure(1, weight=1)

    frame_aktivnost = tk.Frame(root, relief=tk.RIDGE, borderwidth=5)
    frame_aktivnost.grid_rowconfigure(0, weight=1)
    frame_aktivnost.grid_rowconfigure(1, weight=1)
    frame_aktivnost.grid_rowconfigure(2, weight=1)
    frame_aktivnost.grid_rowconfigure(3, weight=1)
    frame_aktivnost.grid_rowconfigure(4, weight=1)
    frame_aktivnost.grid_columnconfigure(0, weight=1)
    frame_aktivnost.grid_columnconfigure(1, weight=1)

    id_label = tk.Label(
        master=frame_aktivnost, text="ID aktivnosti:", font=("Helvetica", 16)
    )
    id_label.grid(row=0, column=0, sticky="nsew")
    id_entry = tk.Entry(master=frame_aktivnost, font=("Helvetica", 16))
    id_entry.grid(row=0, column=1, sticky="nsew")

    trajanje_label = tk.Label(
        master=frame_aktivnost,
        text="Trajanje (naravno število):",
        font=("Helvetica", 16),
    )
    trajanje_label.grid(row=1, column=0, sticky="nsew")
    trajanje_entry = tk.Entry(master=frame_aktivnost, font=("Helvetica", 16))
    trajanje_entry.grid(row=1, column=1, sticky="nsew")

    odvisnosti_label = tk.Label(
        master=frame_aktivnost,
        text="Odvisna od aktivnosti: (ID1,ID2,...)",
        font=("Helvetica", 16),
    )
    odvisnosti_label.grid(row=2, column=0, sticky="nsew")
    odvisnosti_entry = tk.Entry(master=frame_aktivnost, font=("Helvetica", 16))
    odvisnosti_entry.grid(row=2, column=1, sticky="nsew")

    resursi_label = tk.Label(
        master=frame_aktivnost,
        text="Resursi (format: Resurs1,Resurs2,...):",
        font=("Helvetica", 16),
    )
    resursi_label.grid(row=3, column=0, sticky="nsew")
    resursi_entry = tk.Entry(master=frame_aktivnost, font=("Helvetica", 16))
    resursi_entry.grid(row=3, column=1, sticky="nsew")

    dodaj_button = tk.Button(
        master=frame_aktivnost,
        text="Dodaj aktivnost",
        command=dodaj_aktivnost,
        font=("Helvetica", 16),
    )
    dodaj_button.grid(row=4, column=0, columnspan=2)
    frame_aktivnost.grid(row=1, column=0, sticky="nsew")

    frame_resurs = tk.Frame(root, relief=tk.RIDGE, borderwidth=5)
    frame_resurs.grid_rowconfigure(0, weight=1)
    frame_resurs.grid_rowconfigure(1, weight=1)
    frame_resurs.grid_columnconfigure(0, weight=1)
    frame_resurs.grid_columnconfigure(1, weight=1)

    all_resources_label = tk.Label(
        frame_resurs, text="ID resursa:", font=("Helvetica", 16)
    )
    all_resources_label.grid(row=0, column=0, sticky="nsew")
    all_resources_entry = tk.Entry(frame_resurs, font=("Helvetica", 16))
    all_resources_entry.grid(row=0, column=1, sticky="nsew")

    dodaj_resurs_button = tk.Button(
        frame_resurs, text="Dodaj resurs", command=dodaj_resurs, font=("Helvetica", 16)
    )
    dodaj_resurs_button.grid(row=1, column=0, columnspan=2)
    frame_resurs.grid(row=1, column=1, sticky="nsew")

    zacni_simulacijo_button = tk.Button(
        root,
        text="Začni simulacijo",
        bg="blue",
        fg="white",
        command=simuliraj,
        font=("Helvetica", 16),
    )
    zacni_simulacijo_button.grid(row=2, column=0, columnspan=2)

    activities_resources()

    root.mainloop()


if __name__ == "__main__":
    main()
