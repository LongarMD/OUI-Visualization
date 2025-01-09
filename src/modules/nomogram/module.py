from typing import TYPE_CHECKING
import numpy as np
import tkinter as tk
import tkinter.ttk as ttk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
from common.module import Module
from .nomogram import calculate_df, calculate_points, generate_random

if TYPE_CHECKING:
    from common.app import App

instructions = """# Instructions
1. Generate Training Data
   - Enter a number to specify the size of the training dataset
   - Click "Generate" to create a random dataset
   - The nomogram will be displayed automatically

2. Using the Nomogram
   - The nomogram shows the relationship between different features
   - Each line represents a feature (Outlook, Temperature, Humidity, Windy)
   - Points on each line show the contribution of each feature value

3. Making Predictions
   - Select current conditions using the dropdown menus
   - Click "Calculate" to see the probability of playing golf
   - The probability is based on the learned patterns in the data

Note: The nomogram visualizes how each feature contributes to the final prediction.
"""


class Nomogram(Module):
    """A module for visualizing and using Naive Bayes classification through nomograms."""

    __label__ = "Nomogram"
    __instructions__ = instructions
    __category_key__ = "machine_learning"
    __short_description__ = "Interactive visualization of a nomogram for Naive Bayes classification. Shows how each feature contributes to the probability of playing golf based on weather conditions."

    def __init__(self, app: "App"):
        """Initialize the Naive Bayes module.

        Args:
            app: The main application instance
        """
        super().__init__(app)

        self.points = None
        self.aprior = None
        self.fig = None
        self.ax = None
        self.canvas = None

        self.create_widgets()
        self.generate_data()
        self.calculate_probability()

    def destroy(self) -> None:
        """Clean up resources when the module is destroyed."""
        plt.close(self.fig)
        super().destroy()

    def create_widgets(self) -> None:
        """Create and layout all GUI widgets for the module."""
        # Configure grid weights
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # Create input frame
        input_frame = ttk.Frame(self, padding=5)
        input_frame.grid(row=0, column=0, sticky="ew")
        input_frame.grid_columnconfigure(1, weight=1)

        # Add size input
        ttk.Label(input_frame, text="Dataset size:").grid(row=0, column=0, padx=5)
        self.size_var = tk.StringVar(value="100")
        size_entry = ttk.Entry(input_frame, textvariable=self.size_var, width=10)
        size_entry.grid(row=0, column=1, sticky="w", padx=5)

        # Add generate button
        generate_btn = ttk.Button(input_frame, text="Generate", command=self.generate_data)
        generate_btn.grid(row=0, column=2, padx=5)

        # Create plot frame
        plot_frame = ttk.Frame(self, padding=5)
        plot_frame.grid(row=1, column=0, sticky="nsew")
        plot_frame.grid_rowconfigure(0, weight=1)
        plot_frame.grid_columnconfigure(0, weight=1)

        # Create prediction frame
        pred_frame = ttk.Frame(self, padding=5)
        pred_frame.grid(row=2, column=0, sticky="ew")

        # Add prediction controls
        self.create_prediction_widgets(pred_frame)

        result_frame = ttk.Frame(self, padding=10)
        result_frame.grid(row=3, column=0, sticky="ew")
        result_frame.grid_columnconfigure(0, weight=1)  # Configure left spacing
        result_frame.grid_columnconfigure(2, weight=0)  # Center column (label)
        result_frame.grid_columnconfigure(3, weight=1)  # Configure right spacing

        self.result_var = tk.StringVar()
        style = ttk.Style()
        font_name = style.lookup("TLabel", "font")
        font = (font_name, 12, "bold")
        result_label = ttk.Label(result_frame, textvariable=self.result_var, font=font)
        result_label.grid(row=0, column=1, padx=5)

        # Initialize matplotlib figure
        self.fig, self.ax = plt.subplots(figsize=(8, 6))
        self.canvas = FigureCanvasTkAgg(self.fig, master=plot_frame)
        self.canvas.get_tk_widget().grid(row=0, column=0, sticky="nsew")

    def create_prediction_widgets(self, parent: ttk.Frame) -> None:
        """Create widgets for making predictions.

        Args:
            parent: Parent frame to place widgets in
        """
        for i in range(8):
            parent.grid_columnconfigure(i, weight=1)

        # Create dropdown menus
        choices_outlook = ["Sunny", "Overcast", "Rainy"]
        choices_temp = ["Hot", "Cool", "Mild"]
        choices_humidity = ["High", "Normal"]
        choices_windy = ["True", "False"]

        self.outlook_var = tk.StringVar(value=choices_outlook[0])
        self.temp_var = tk.StringVar(value=choices_temp[0])
        self.humidity_var = tk.StringVar(value=choices_humidity[0])
        self.windy_var = tk.StringVar(value=choices_windy[0])

        self.outlook_var.trace_add("write", lambda *args: self.calculate_probability())
        self.temp_var.trace_add("write", lambda *args: self.calculate_probability())
        self.humidity_var.trace_add("write", lambda *args: self.calculate_probability())
        self.windy_var.trace_add("write", lambda *args: self.calculate_probability())

        # Layout dropdowns
        ttk.Label(parent, text="Outlook:", justify="right").grid(row=0, column=0, padx=5, sticky="e")
        ttk.Combobox(parent, textvariable=self.outlook_var, values=choices_outlook, state="readonly", width=10).grid(
            row=0, column=1, padx=5
        )

        ttk.Label(parent, text="Temperature:", justify="right").grid(row=0, column=2, padx=5, sticky="e")
        ttk.Combobox(parent, textvariable=self.temp_var, values=choices_temp, state="readonly", width=10).grid(
            row=0, column=3, padx=5
        )

        ttk.Label(parent, text="Humidity:", justify="right").grid(row=0, column=4, padx=5, sticky="e")
        ttk.Combobox(parent, textvariable=self.humidity_var, values=choices_humidity, state="readonly", width=10).grid(
            row=0, column=5, padx=5
        )

        ttk.Label(parent, text="Windy:", justify="right").grid(row=0, column=6, padx=5, sticky="e")
        ttk.Combobox(parent, textvariable=self.windy_var, values=choices_windy, state="readonly", width=10).grid(
            row=0, column=7, padx=5
        )

    def generate_data(self) -> None:
        """Generate random training data and update the nomogram."""
        try:
            size = int(self.size_var.get())
        except ValueError:
            size = 20

        data = generate_random(size)
        dfs, apriori = calculate_df(data)

        self.points = [calculate_points(df) for df in dfs]
        self.aprior = apriori

        self.plot_nomogram()
        self.calculate_probability()

    def plot_nomogram(self) -> None:
        """Plot the nomogram visualization."""
        self.ax.clear()
        classes = ["Outlook", "Temperature", "Humidity", "Windy"]

        for i, current in enumerate(self.points):
            categories, values = zip(*current)
            # Sort values and categories
            sorted_indices = sorted(range(len(values)), key=lambda k: values[k])
            sorted_values = [values[ix] for ix in sorted_indices]
            sorted_categories = [categories[ix] for ix in sorted_indices]

            self.ax.plot(sorted_values, [i] * len(current), marker="o", label=classes[i])

            for value, category in zip(sorted_values, sorted_categories):
                if i == 0:
                    self.ax.text(value, i + 0.1, category, ha="center", va="bottom", fontsize=8)
                else:
                    self.ax.text(value, i - 0.1, category, ha="center", va="top", fontsize=8)

        self.ax.set_yticks(range(len(self.points)))
        self.ax.set_yticklabels(classes)
        self.ax.set_xlabel("Points")
        self.ax.legend()
        self.ax.axvline(x=0, linestyle="--", color="gray")
        self.ax.set_title("Nomogram")

        self.canvas.draw()

    def calculate_probability(self) -> None:
        """Calculate probability of playing golf based on current conditions."""
        if not self.points:
            return

        values = [self.outlook_var.get(), self.temp_var.get(), self.humidity_var.get(), self.windy_var.get()]

        sum_val = 0
        for value, point_set in zip(values, self.points):
            for category, points in point_set:
                if category == value:
                    sum_val += points
                    break

        odds = np.exp(sum_val)
        probability = odds / (1 + odds)

        self.result_var.set(f"Probability of playing golf: {probability:.2%}")
