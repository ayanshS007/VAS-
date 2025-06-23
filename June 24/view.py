# view.py

import tkinter as tk

class CanvasView:
    def __init__(self, root, model: 'CanvasModel'):
        self.model = model
        self.canvas = tk.Canvas(root, width=1200, height=800, bg="white")
        self.canvas.pack(side=tk.RIGHT, expand=True, fill=tk.BOTH)
        self.grid_lines = []
        self.grid_visible = False

    def draw_grid(self):
        self.clear_grid()

        width = self.canvas.winfo_width()
        height = self.canvas.winfo_height()

        spacing = self.model.grid_spacing
        zoom = self.model.zoom_level
        unit = self.model.unit
        scale = self.model.unit_scale.get(unit, 1.0)

        pixel_interval = spacing * zoom / scale
        if pixel_interval < 20:
            return  # Avoid overly dense grid

        self.grid_lines = []

        # Vertical lines
        for x in range(0, width, int(pixel_interval)):
            line = self.canvas.create_line(x, 0, x, height, fill="#e0e0e0", tags="grid")
            label = self.canvas.create_text(x + 2, 10, text=f"{self.pixel_to_real(x, 0)[0]:.1f}",
                                            font=("Arial", 7), fill="#888888", anchor="nw", tags="grid")
            self.grid_lines.extend([line, label])

        # Horizontal lines
        for y in range(0, height, int(pixel_interval)):
            line = self.canvas.create_line(0, y, width, y, fill="#e0e0e0", tags="grid")
            label = self.canvas.create_text(2, y + 2, text=f"{self.pixel_to_real(0, y)[1]:.1f}",
                                            font=("Arial", 7), fill="#888888", anchor="nw", tags="grid")
            self.grid_lines.extend([line, label])

        self.grid_visible = True

    def clear_grid(self):
        for item in getattr(self, "grid_lines", []):
            self.canvas.delete(item)
        self.grid_lines.clear()
        self.grid_visible = False

    def toggle_grid(self):
        if getattr(self, "grid_visible", False):
            self.clear_grid()
        else:
            self.draw_grid()

    def apply_zoom(self, scale_factor):
        self.model.zoom_level *= scale_factor
        self.canvas.scale("all", 0, 0, scale_factor, scale_factor)

    def real_to_pixel(self, x, y):
        unit_factor = self.model.unit_scale[self.model.unit]
        scale = self.model.grid_spacing * self.model.zoom_level
        return x / unit_factor * scale, y / unit_factor * scale

    def pixel_to_real(self, x, y):
        unit_factor = self.model.unit_scale[self.model.unit]
        scale = self.model.grid_spacing * self.model.zoom_level
        return round(x / scale * unit_factor, 2), round(y / scale * unit_factor, 2)
