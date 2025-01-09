# OUI Algorithm Visualizations

## Overview

This repository contains a collection of interactive visualizations for various algorithms. Each module is designed to be standalone and can be run independently.

## Modules

- [Nomogram](src/modules/nomogram): Interactive visualization of a nomogram for Naive Bayes classification.
- [D-Separation](src/modules/d_separation): Interactive visualization of d-separation: Graph visualization where you can select two nodes. The program then displays (colors, highlights) all sets of nodes that d-separate these two nodes.
- [AO*](src/modules/ao_star): Interactive visualization of AO* tree search. The computer draws a small search tree and heuristic h, and the user must first select which node to expand and enter the correct values.
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

