from matplotlib.patches import Rectangle, FancyArrowPatch
from tkinter import messagebox as msgbox
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
            msgbox.showerror("Error", "Aktivnost z ID-jem {} že obstaja".format(aktivnost.id))
            return

        if not aktivnost.odvisnosti:
            aktivnost.odvisnosti = np.array(["start"])

        # Preveri, ali vse navedene odvisnosti obstajajo
        neobstojece_odvisnosti = [odv for odv in aktivnost.odvisnosti if not any(a.id == odv for a in self.aktivnosti)]
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

        seznam_neodvisnih = [a.id for a in self.aktivnosti if a.id not in seznam_vseh_odvisnih]
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
                    calculate_es(dep) + next(a for a in self.aktivnosti if a.id == dep).trajanje
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
        ls_values = {"finish": total_project_duration}  # Initialize LS for 'finish' activity

        # Function to recursively calculate LS
        def calculate_ls(aktivnost_id):
            if aktivnost_id in ls_values:
                return ls_values[aktivnost_id]

            aktivnost = next((a for a in self.aktivnosti if a.id == aktivnost_id), None)
            if aktivnost is None:
                return total_project_duration

            dependent_activities = [a for a in self.aktivnosti if aktivnost_id in a.odvisnosti]
            if not dependent_activities:
                ls_values[aktivnost_id] = total_project_duration - aktivnost.trajanje
            else:
                min_ls = min(calculate_ls(dep.id) - aktivnost.trajanje for dep in dependent_activities)
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
                    update_es(dep) + next(a for a in self.aktivnosti if a.id == dep).trajanje
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

            dependent_activities = [a for a in self.aktivnosti if aktivnost.id in a.odvisnosti]
            if not dependent_activities:
                aktivnost.ls = max(a.ls for a in self.aktivnosti) - aktivnost.trajanje
            else:
                min_ls = min(update_ls(dep) - aktivnost.trajanje for dep in dependent_activities)
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
        y_positions = [15 * i for i in range(-dependent_count // 2 + 1, dependent_count // 2 + 1)]
        return start_dependets, dependent_count, y_positions

    def prikazi_urnik(self, ax, canvas):
        ax.cla()
        rect_width, rect_height = 20, 10

        start_x, start_y = 0, 0  # Starting point for the 'Start' rectangle

        # Dictionary to store position of each activity
        positions = {}
        used_positions = set()
        # Preštejmo koliko aktivnosti je odvisnih od začetne aktivnosti
        start_dependents, dependent_count, start_dependets_y_positions = self.prestej_odvisnosti_od_starta()

        # Calculate positions of other activities
        for i, aktivnost in enumerate(self.aktivnosti):
            if aktivnost.id == "start":
                x = start_x
                y = start_y

            elif aktivnost.id == "finish":
                x = max(positions.values(), key=lambda x: x[0])[0] + rect_width * 1.5  # finish je vedno najbolj desno
                y = start_y

            else:
                # če je aktivnost odvisna od starta je njena y koordinata odvisna od tega koliko aktivnosti je odvisnih od starta
                # tu je pogoj da če je aktivnost odvisna od starta je odvisna LE od starta
                if "start" in aktivnost.odvisnosti:
                    y_index = start_dependents.index(aktivnost.id)
                    y = start_dependets_y_positions[y_index]
                    x = start_x + rect_width * 1.5
                else:
                    x = max(positions[odvisnost][0] + rect_width * 1.5 for odvisnost in aktivnost.odvisnosti)
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


def find_next_available_time(resource_availability, required_resources, duration, es):
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
                    print("Resource {} is busy in the time slot [{}, {}]".format(res, start, end))
                    # The resource is busy in this slot, move to the end of this busy period
                    earliest_start_time = end
                    resource_free = False
                    break
                elif earliest_start_time < start and earliest_start_time + duration > start:
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
