# OUI Algorithm Visualizations

This repository contains a collection of interactive visualizations for various algorithms. Each module is designed to be standalone and can be run independently.

## Modules

- [Nomogram](src/modules/nomogram): Interactive visualization of a nomogram for Naive Bayes classification.
- [D-Separation](src/modules/d_separation): Interactive visualization of d-separation: Graph visualization where you can select two nodes. The program then displays (colors, highlights) all sets of nodes that d-separate these two nodes.
- [AO\*](src/modules/ao_star): Interactive visualization of AO\* tree search. The computer draws a small search tree and heuristic h, and the user must first select which node to expand and enter the correct values.
- [KNN](src/modules/knn): KNN visualization that plots data in 2D (point cloud) and for a selected test case and k parameter value shows the nearest neighbors and predicted class.
- [Alpha-Beta Pruning](src/modules/ab_pruning): Visualize the alpha-beta pruning algorithm on a game tree.

## Setup

1. Install the [uv](https://docs.astral.sh/uv/) package manager

2. Create a virtual environment and install the dependencies:

```bash
uv venv
uv sync
```

3. Run the application:

```bash
uv run python src/main.py
```

## Development

The core of the application is in the [common](src/common) directory:

- The [App](src/common/app.py) class is the main entry point for the application. It handles the main window, module switching, and help window.
- The [Module](src/common/module.py) class is the base class for all modules. It derives from tkinter.Frame and provides a common interface for all modules.

The modules are in the [modules](src/modules) directory, including the

- [MainMenu](src/common/main_menu.py) class is the main menu for the application.

### Adding a new module

1. Create a new directory in the [modules](src/modules) directory.
2. Create a new module.py file in the new directory.
3. Create a new class that derives from [Module](src/common/module.py). The class must define:
   - The **init** method, which takes a single argument, the App instance.
   - The **label** attribute, which is the name of the module that will be displayed in the menu.
   - The **instructions** attribute, which is the instructions for the module that will be displayed in the help window.
   - The **short_description** attribute, which is the short description of the module that will be displayed in the menu.
   - The **category_key** attribute, which is the category key of the module. Module keys are defined in [Module](src/common/module.py), and used in the main menu to group modules.
4. Add the new module to the [MainMenu](src/common/main_menu.py)'s MODULES list.

### Code standard

- Follow the structure of the existing modules.
- Use the `ruff` formatter and linter:
  ```bash
  uvx ruff check src
  uvx ruff format src
  ```
- Use type hints

## Build

Make sure you have the development dependencies installed.
Run the following command to build the application:

```bash
uv run pyinstaller build_exe.spec
```
