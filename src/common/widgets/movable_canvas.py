from typing import Optional
import tkinter as tk


class MovableCanvas(tk.Canvas):
    """
    Custom canvas widget that supports panning and zooming.

    The canvas can be:
    - Panned by clicking and dragging
    - Zoomed using the mouse wheel
    """

    def __init__(self, parent: Optional[tk.Widget] = None, **kwargs) -> None:
        tk.Canvas.__init__(self, parent, **kwargs)
        self.bind("<ButtonPress-1>", lambda ev: self.scan_mark(ev.x, ev.y))
        self.bind("<B1-Motion>", lambda ev: self.scan_dragto(ev.x, ev.y, gain=1))
        self.bind("<MouseWheel>", self.zoom)

    def zoom(self, ev: tk.Event) -> None:
        """Handles mouse wheel events to zoom the canvas content"""
        x = self.canvasx(ev.x)
        y = self.canvasx(ev.y)
        scale = 1.001**ev.delta
        self.scale(tk.ALL, x, y, scale, scale)
