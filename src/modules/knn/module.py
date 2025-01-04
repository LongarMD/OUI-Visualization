from typing import TYPE_CHECKING, Optional
import tkinter.ttk as ttk
import tkinter as tk
import tkinter.messagebox as msgbox
import matplotlib.pyplot as plt  # type: ignore
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg  # type: ignore
import numpy as np
from sklearn.datasets import load_iris  # type: ignore
from sklearn.decomposition import PCA  # type: ignore
import matplotlib.patches as patches  # type: ignore

from common.module import Module

if TYPE_CHECKING:
    from common.app import App
    from matplotlib.figure import Figure
    from matplotlib.axes import Axes
    from matplotlib.collections import PathCollection

instructions = """# K-Nearest Neighbors (KNN) Visualization

This interactive tool helps you understand how the K-Nearest Neighbors algorithm classifies data points.

How to use:
1. Click anywhere on the plot to place a test point, or manually enter coordinates in the "Enter test point" field
2. Enter a value for K (number of neighbors) in the "Enter K" field
3. Choose classification method:
   - Majority: Assigns the most common class among K neighbors
   - Weighted: Weighs neighbors by distance (closer points have more influence)
4. Click "Show Neighbors" to see:
   - The test point's classification (shown by its color)
   - A circle showing the K nearest neighbors
5. Use "Clear" to reset the visualization

The plot shows the Iris dataset projected into 2D space, with different colors representing different classes."""


class KNN(Module):
    """A module for visualizing k-nearest neighbors classification algorithm.

    This module provides an interactive visualization of the k-nearest neighbors algorithm,
    allowing users to:
    - View a 2D projection of the Iris dataset
    - Click to place test points
    - Select k value and classification method (majority/weighted)
    - Visualize nearest neighbors and classification results
    """

    __label__: str = "KNN"
    __instructions__: str = instructions

    def __init__(self, app: "App") -> None:
        """Initialize the KNN module.

        Args:
            app: The main application instance
        """
        super().__init__(app)

        self.data: np.ndarray
        self.labels: np.ndarray
        self.fig: "Figure"
        self.ax: "Axes"
        self.canvas: FigureCanvasTkAgg
        self.canvas_widget: tk.Widget
        self.point_entry: ttk.Entry
        self.k_entry: ttk.Entry
        self.classifier_choice: tk.StringVar
        self.weighted_radio: ttk.Radiobutton
        self.btn_next_step: ttk.Button
        self.btn_clear: ttk.Button
        self.prev_point_plot: Optional["PathCollection"] = None

        try:
            self._load_data()
        except FileNotFoundError:
            self._generate_data()

        self.create_widgets()
        self.visualize()

    def _generate_data(self) -> None:
        """Generate the data for the module."""
        iris = load_iris()
        X, y = iris.data, iris.target

        n_components = 2
        pca = PCA(n_components=n_components)
        X_2d = pca.fit_transform(X)

        data = np.array([]).reshape(0, n_components)
        data = np.vstack([data, X_2d])

        np.savetxt("assets/knn/iris_2d.txt", data)
        np.savetxt("assets/knn/iris_labels.txt", y)

        self.data = data
        self.labels = y

    def _load_data(self) -> None:
        """Load the data for the module."""
        self.data = np.loadtxt("assets/knn/iris_2d.txt")
        self.labels = np.loadtxt("assets/knn/iris_labels.txt")

    def destroy(self) -> None:
        """Clean up resources when the module is destroyed."""
        plt.close()
        self.canvas_widget.destroy()
        super().destroy()

    def create_widgets(self) -> None:
        """Create and layout all the GUI widgets for the module."""
        self.fig, self.ax = plt.subplots(figsize=(12, 8))
        self.ax.set_xlim([0, 10])
        self.ax.set_ylim([0, 10])
        self.ax.set_aspect("equal")

        self.canvas = FigureCanvasTkAgg(self.fig, master=self)

        # Configure grid weights
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)  # Make point entry expandable
        self.grid_columnconfigure(3, weight=1)  # Make k entry expandable

        # Canvas setup with padding
        self.canvas_widget = self.canvas.get_tk_widget()
        self.canvas_widget.grid(row=0, column=0, columnspan=8, padx=10, pady=10, sticky="nsew")

        self.canvas.mpl_connect("button_press_event", self.on_click)

        # Bottom controls frame
        controls_frame = ttk.Frame(self)
        controls_frame.grid(row=1, column=0, columnspan=8, padx=10, pady=(0, 10), sticky="ew")

        # Configure controls frame columns
        controls_frame.grid_columnconfigure(1, weight=1)  # point entry
        controls_frame.grid_columnconfigure(3, weight=1)  # k entry

        # Add widgets to controls frame with padding
        lbl1 = ttk.Label(controls_frame, text="Enter test point:")
        lbl1.grid(column=0, row=0, padx=(0, 5), pady=5)

        self.point_entry = ttk.Entry(controls_frame)
        self.point_entry.grid(column=1, row=0, padx=5, pady=5, sticky="ew")

        lbl2 = ttk.Label(controls_frame, text="Enter K:")
        lbl2.grid(column=2, row=0, padx=5, pady=5)

        self.k_entry = ttk.Entry(controls_frame)
        self.k_entry.grid(column=3, row=0, padx=5, pady=5, sticky="ew")

        # Radiobuttons
        self.classifier_choice = tk.StringVar()
        self.classifier_choice.set("Majority")  # Default choice
        majority_radio = ttk.Radiobutton(
            controls_frame, text="Majority", variable=self.classifier_choice, value="Majority"
        )
        majority_radio.grid(column=4, row=0, padx=5, pady=5)

        self.weighted_radio = ttk.Radiobutton(
            controls_frame, text="Weighted", variable=self.classifier_choice, value="Weighted"
        )
        self.weighted_radio.grid(column=5, row=0, padx=5, pady=5)

        # Buttons
        self.btn_next_step = ttk.Button(controls_frame, text="Show Neighbors", command=self.on_show_knn)
        self.btn_next_step.grid(column=6, row=0, padx=5, pady=5)

        self.btn_clear = ttk.Button(controls_frame, text="Clear", command=self.on_clear)
        self.btn_clear.grid(column=7, row=0, padx=(5, 0), pady=5)

    def on_clear(self) -> None:
        """Clear all inputs and reset the visualization."""
        self.point_entry.delete(0, tk.END)
        self.k_entry.delete(0, tk.END)

        self.ax.clear()
        self.ax.set_xlim([0, 10])
        self.ax.set_ylim([0, 10])

        self.visualize(showTestPoint=False)

        self.canvas.draw()

    def on_click(self, event: plt.MouseEvent) -> None:
        """Handle mouse click events to place test points.

        Args:
            event: The mouse click event containing x,y coordinates
        """
        x, y = event.xdata, event.ydata

        if x is not None and y is not None:
            # Clear previous point by redrawing the plot
            self.ax.clear()
            self.visualize()

            # Plot new point
            point_plot = self.ax.scatter(x, y, c="blue", marker="o", s=100, alpha=0.7)
            self.canvas.draw()

            self.point_entry.delete(0, tk.END)
            self.point_entry.insert(0, f"{x:.2f}, {y:.2f}")

            self.prev_point_plot = point_plot

    def on_show_knn(self) -> None:
        """Process the KNN classification for the current test point and k value."""
        try:
            k = int(self.k_entry.get())
            if k <= 0:
                msgbox.showerror("Error", "K should be a positive integer greater than 0")
                return
            if k > self.data.shape[0]:
                msgbox.showerror("Error", "K should be less than or equal to the number of points")
                return
        except ValueError:
            msgbox.showerror("Error", "Please enter a valid number for K")
            return

        try:
            point_coords = [float(coord) for coord in self.point_entry.get().split(",")]
            if len(point_coords) != 2:
                msgbox.showerror("Error", "Please enter valid coordinates (x,y)")
                return
        except ValueError:
            msgbox.showerror("Error", "Please enter valid numerical coordinates (x,y)")
            return

        test_point_class = self.classify_test_point(np.array(point_coords), self.data, self.labels, k)

        self.visualize(True, np.array(point_coords), k, test_point_class)

        self.canvas.draw()

    def classify_test_point(self, test_point: np.ndarray, data: np.ndarray, labels: np.ndarray, k: int) -> int:
        """Classify a test point using k-nearest neighbors.

        Args:
            test_point: The point to classify
            data: Training data points
            labels: Training data labels
            k: Number of neighbors to consider

        Returns:
            The predicted class label for the test point
        """
        distances = np.linalg.norm(data - test_point, axis=1)
        sorted_indices = np.argsort(distances)
        k_nearest_labels = labels[sorted_indices[:k]]

        if self.classifier_choice.get() == "Majority":
            unique_classes, counts = np.unique(k_nearest_labels, return_counts=True)
            majority_class = unique_classes[np.argmax(counts)]

        else:
            # Weighted Voting
            weights = 1 / distances[sorted_indices[:k]]
            weighted_counts = np.bincount(k_nearest_labels, weights=weights)
            majority_class = np.argmax(weighted_counts)

        return int(majority_class)

    def visualize(
        self,
        showTestPoint: bool = False,
        test_point: np.ndarray = np.array([]),
        k: int = 0,
        classified_class: Optional[int] = None,
    ) -> None:
        """Visualize the data points and optionally show test point classification.

        Args:
            showTestPoint: Whether to show the test point
            test_point: Coordinates of the test point
            k: Number of neighbors to show
            classified_class: Predicted class of the test point
        """
        self.ax.clear()
        labels = self.labels.astype(int)
        colors = plt.cm.rainbow(np.linspace(0, 1, len(np.unique(labels))))

        for class_label, color in zip(np.unique(labels), colors):
            class_data = self.data[labels == class_label]
            self.ax.scatter(
                class_data[:, 0],
                class_data[:, 1],
                c=[color],
                label=f"Class {class_label}",
                alpha=0.7,
                edgecolors="w",
                s=100,
            )

        if showTestPoint:
            if classified_class is not None:
                classified_color = colors[classified_class]
                self.ax.scatter(
                    test_point[0],
                    test_point[1],
                    c=[classified_color],
                    marker="o",
                    s=200,
                    alpha=0.7,
                )
            else:
                self.ax.scatter(test_point[0], test_point[1], c="blue", marker="o", s=200, alpha=0.7)

            if k > 0:
                distances = np.linalg.norm(self.data - test_point, axis=1)
                sorted_indices = np.argsort(distances)
                k_nearest_indices = sorted_indices[:k]

                radius = distances[k_nearest_indices[-1]]

                circle = patches.Circle(
                    (test_point[0], test_point[1]),
                    radius,
                    fill=False,
                    color="blue",
                    linestyle="--",
                    linewidth=2,
                )
                self.ax.add_patch(circle)

        self.ax.set_xlim([np.min(self.data[:, 0]), np.max(self.data[:, 0])])
        self.ax.set_ylim([np.min(self.data[:, 1]), np.max(self.data[:, 1])])
        # ax.legend()
