"""
READ ME

difference between weighted and majority classifier
can be seen, for example, in point (1.60, 0.27) with k=3

"""

import tkinter as tk
from tkinter import StringVar
import tkinter.messagebox as msgbox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
from sklearn.datasets import load_iris
from sklearn.decomposition import PCA
import matplotlib.patches as patches


def visualize(
    data, labels, ax, showTestPoint=False, test_point=[], k=0, classified_class=None
):
    ax.clear()
    labels = labels.astype(int)
    colors = plt.cm.rainbow(np.linspace(0, 1, len(np.unique(labels))))

    for class_label, color in zip(np.unique(labels), colors):
        class_data = data[labels == class_label]
        ax.scatter(
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
            ax.scatter(
                test_point[0],
                test_point[1],
                c=[classified_color],
                marker="o",
                s=200,
                alpha=0.7,
            )
        else:
            ax.scatter(
                test_point[0], test_point[1], c="blue", marker="o", s=200, alpha=0.7
            )

        if k > 0:
            distances = np.linalg.norm(data - test_point, axis=1)
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
            ax.add_patch(circle)

    ax.set_xlim([np.min(data[:, 0]), np.max(data[:, 0])])
    ax.set_ylim([np.min(data[:, 1]), np.max(data[:, 1])])
    # ax.legend()


def classify_test_point(test_point, data, labels, k):
    distances = np.linalg.norm(data - test_point, axis=1)
    sorted_indices = np.argsort(distances)
    k_nearest_labels = labels[sorted_indices[:k]]

    if classifier_choice.get() == "Majority":
        unique_classes, counts = np.unique(k_nearest_labels, return_counts=True)
        majority_class = unique_classes[np.argmax(counts)]

    else:
        # Weighted Voting
        weights = 1 / distances[sorted_indices[:k]]
        weighted_counts = np.bincount(k_nearest_labels, weights=weights)
        majority_class = np.argmax(weighted_counts)

    return majority_class


def on_show_knn():
    global labels, data, ax

    try:
        k = int(k_entry.get())
        if k <= 0:
            msgbox.showerror("Error", "K should be a positive integer greater than 0")
            return
        if k > data.shape[0]:
            msgbox.showerror(
                "Error", "K should be less than or equal to the number of points"
            )
            return
    except ValueError:
        msgbox.showerror("Error", "Please enter a valid number for K")
        return

    try:
        point_coords = [float(coord) for coord in point_entry.get().split(",")]
        if len(point_coords) != 2:
            msgbox.showerror("Error", "Please enter valid coordinates (x,y)")
            return
    except ValueError:
        msgbox.showerror("Error", "Please enter valid numerical coordinates (x,y)")
        return

    test_point_class = classify_test_point(np.array(point_coords), data, labels, k)
    msgbox.showinfo(
        "Test Point Classification",
        f"The test point belongs to class {test_point_class}",
    )

    visualize(data, labels, ax, True, np.array(point_coords), k, test_point_class)

    canvas.draw()


def on_click(event):
    global data, point_entry, prev_point_plot
    x, y = event.xdata, event.ydata

    if not hasattr(on_click, "prev_point_plot"):
        on_click.prev_point_plot = None

    if on_click.prev_point_plot:
        on_click.prev_point_plot.remove()

    if x is not None and y is not None:
        point_plot = ax.scatter(x, y, c="blue", marker="o", s=100, alpha=0.7)
        canvas.draw()

        point_entry.delete(0, tk.END)
        point_entry.insert(0, f"{x:.2f}, {y:.2f}")

        on_click.prev_point_plot = point_plot


def on_clear():
    global data, labels, point_entry, k_entry

    point_entry.delete(0, tk.END)
    k_entry.delete(0, tk.END)

    ax.clear()
    ax.set_xlim([0, 10])
    ax.set_ylim([0, 10])

    visualize(data, labels, ax, showTestPoint=False)

    canvas.draw()


def main():
    global data, ax, canvas, point_entry, k_entry, labels, classifier_choice

    # LOAD SAMPLE DATA
    iris = load_iris()
    X, y = iris.data, iris.target

    n_components = 2
    pca = PCA(n_components=n_components)
    X_2d = pca.fit_transform(X)

    data = np.array([]).reshape(0, n_components)
    data = np.vstack([data, X_2d])

    labels = y

    root = tk.Tk()
    root.title("KNN Visualization")
    # root.geometry("800x700")

    fig, ax = plt.subplots(figsize=(12, 8))
    ax.set_xlim([0, 10])
    ax.set_ylim([0, 10])
    ax.set_aspect("equal")

    canvas = FigureCanvasTkAgg(fig, master=root)
    canvas_widget = canvas.get_tk_widget()
    canvas_widget.grid(row=0, column=0, columnspan=8)

    canvas.mpl_connect("button_press_event", on_click)

    ######################display
    lbl1 = tk.Label(root, text="Enter test point:")
    lbl1.grid(column=0, row=1)

    point_entry = tk.Entry(root)
    point_entry.grid(column=1, row=1)

    lbl2 = tk.Label(root, text="Enter K:")
    lbl2.grid(column=2, row=1)

    k_entry = tk.Entry(root)
    k_entry.grid(column=3, row=1)

    # Radiobuttons for classifier choice
    classifier_choice = StringVar()
    classifier_choice.set("Majority")  # Default choice
    majority_radio = tk.Radiobutton(
        root, text="Majority", variable=classifier_choice, value="Majority"
    )
    majority_radio.grid(column=4, row=1)

    weighted_radio = tk.Radiobutton(
        root, text="Weighted", variable=classifier_choice, value="Weighted"
    )
    weighted_radio.grid(column=5, row=1)

    btn_next_step = tk.Button(root, text="Show Neighbors", command=on_show_knn)
    btn_next_step.grid(column=6, row=1)

    btn_clear = tk.Button(root, text="Clear", command=on_clear)
    btn_clear.grid(column=7, row=1)

    visualize(data, labels, ax)

    root.mainloop()


if __name__ == "__main__":
    main()
