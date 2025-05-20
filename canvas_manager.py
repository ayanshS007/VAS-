import tkinter as tk
import math
from tkinter import colorchooser, filedialog
from config import *
from geometry import calculate_polygon_area, calculate_polygon_perimeter
from drawing_helpers import get_distance_label
from toolbar import setup_toolbar
import math
from Furniture import Furniture
class CanvasManager:
    def __init__(self, root):
        self.root = root
        self.root.title("Graph Paper Layout Tool")

        self.canvas_width = CANVAS_WIDTH
        self.canvas_height = CANVAS_HEIGHT
        self.grid_spacing = GRID_SPACING
        self.unit = DEFAULT_UNIT
        self.unit_scale = UNIT_SCALE
        self.line_color = DEFAULT_LINE_COLOR
        self.line_style = DEFAULT_LINE_STYLE
        self.group_id_counter = 0

        self.drawing_enabled = False
        self.polygon_mode = False
        self.first_point = None
        self.polygon_points = []
        self.actions_stack = []
        self.selected_furniture = None
        self.furniture_items = {}

        self.current_preview = None
        self.current_line_label = None

        self.unit_var = tk.StringVar(value=self.unit)
        self.line_style_var = tk.StringVar(value=self.line_style)
        self.furniture_var = tk.StringVar(value="Bed")

        self.canvas = tk.Canvas(root, width=self.canvas_width, height=self.canvas_height, bg="white")
        self.canvas.pack(side=tk.RIGHT, expand=True, fill=tk.BOTH)

        left_panel = tk.Frame(self.root)
        left_panel.pack(side=tk.LEFT, fill=tk.Y, padx=5, pady=5)

        setup_toolbar(self, left_panel)
        self.canvas.bind("<Button-1>", self.handle_click)
        self.canvas.bind("<Motion>", self.preview_drawing)
        self.dragging_item = None
        self.drag_start_pos = None

        self.grid_visible = False
        self.grid_lines = []  # To store line IDs


    def draw_grid(self):
     self.clear_grid()  # Clear existing grid before drawing new

     for x in range(0, self.canvas_width, self.grid_spacing):
        line = self.canvas.create_line(x, 0, x, self.canvas_height, fill="#eee")
        self.grid_lines.append(line)
     for y in range(0, self.canvas_height, self.grid_spacing):
        line = self.canvas.create_line(0, y, self.canvas_width, y, fill="#eee")
        self.grid_lines.append(line)
     self.grid_visible = True
    def clear_grid(self):
     for line_id in self.grid_lines:
        self.canvas.delete(line_id)
     self.grid_lines.clear()
     self.grid_visible = False
    def toggle_grid(self):
      if self.grid_visible:
        self.clear_grid()
      else:
        self.draw_grid()

    def change_unit(self, unit): self.unit = unit
    def change_line_style(self, style): self.line_style = style
    def pick_line_color(self):
        color = colorchooser.askcolor()[1]
        if color: self.line_color = color

    def enable_line_drawing(self):
        if self.drawing_enabled:
            self.reset_modes()
        else:
            self.reset_modes()
            self.drawing_enabled = True

    def enable_polygon_mode(self):
        if self.polygon_mode:
            self.reset_modes()
        else:
            self.reset_modes()
            self.polygon_mode = True
            self.polygon_points = []

    def enable_furniture_mode(self):
        if self.selected_furniture == self.furniture_var.get():
            self.reset_modes()
        else:
            self.reset_modes()
            self.selected_furniture = self.furniture_var.get()

    def reset_modes(self): 
        self.drawing_enabled = False
        self.polygon_mode = False
        self.selected_furniture = None
        self.first_point = None

    def finish_polygon(self):
        if len(self.polygon_points) < 3: return
        flat = [coord for pt in self.polygon_points for coord in pt]
        polygon_id = self.canvas.create_polygon(flat, outline="green", fill="", width=2)
        area = calculate_polygon_area(self.polygon_points, self.unit)
        perimeter = calculate_polygon_perimeter(self.polygon_points, self.unit)
        cx = sum(x for x, _ in self.polygon_points) / len(self.polygon_points)
        cy = sum(y for _, y in self.polygon_points) / len(self.polygon_points)
        label = self.canvas.create_text(cx, cy, text=f"Area: {area:.2f} {self.unit}²\nPerimeter: {perimeter:.2f} {self.unit}", font=("Arial", 9))
        self.actions_stack.append([polygon_id, label])
        self.polygon_points = []

    def clear_canvas(self): 
        self.canvas.delete("all")
        self.actions_stack.clear()
        self.furniture_items.clear()
        self.draw_grid()

    def undo(self): 
        if self.actions_stack:
            for item in self.actions_stack.pop():
                self.canvas.delete(item)

    def save_canvas(self):
        path = filedialog.asksaveasfilename(defaultextension=".ps", filetypes=[("PostScript", "*.ps")])
        if path: self.canvas.postscript(file=path)

    def handle_click(self, event):
        x, y = event.x, event.y

        if self.drawing_enabled:
            if not self.first_point:
                self.first_point = (x, y)
                # Create point at first click
                point = self.canvas.create_oval(x-3, y-3, x+3, y+3, fill="red")
                # Save just the point id to stack for undo
                self.actions_stack.append([point])
            else:
                x0, y0 = self.first_point

                width = 4 if self.line_style == "bold" else 2
                dash = (4, 2) if self.line_style == "dashed" else None

                # Create line
                line = self.canvas.create_line(x0, y0, x, y, fill=self.line_color, width=width, dash=dash)
                
                # Create label with distance
                label_text, mid_x, mid_y = get_distance_label(x0, y0, x, y, self.unit)
                label = self.canvas.create_text(mid_x, mid_y - 10, text=label_text, font=("Arial", 8))
                
                # Create second point at end of line
                point = self.canvas.create_oval(x-3, y-3, x+3, y+3, fill="red")
                
                # Store line + 2 points + label together in actions_stack as one undo unit
                self.actions_stack.append([line, label, point])

                self.first_point = None
                if self.current_preview: 
                    self.canvas.delete(self.current_preview)
                    self.current_preview = None
                if self.current_line_label: 
                    self.canvas.delete(self.current_line_label)
                    self.current_line_label = None

        elif self.polygon_mode:
            if self.polygon_points:
                if math.dist((x, y), self.polygon_points[0]) < 10:
                    self.finish_polygon()
                    return
                x0, y0 = self.polygon_points[-1]
                line = self.canvas.create_line(x0, y0, x, y, fill="green", width=2)
                self.actions_stack.append([line])
            self.polygon_points.append((x, y))
            point = self.canvas.create_oval(x-3, y-3, x+3, y+3, fill="green")
            self.actions_stack.append([point])

        elif self.selected_furniture:
            for item_id, info in self.furniture_items.items():
                ix, iy, _ = info
                if abs(ix - x) < 20 and abs(iy - y) < 20:
                    self.canvas.coords(item_id, x-15, y-15, x+15, y+15)
                    self.canvas.coords(info[2], x, y)
                    self.furniture_items[item_id] = (x, y, info[2])
                    return
            rect = self.canvas.create_rectangle(x-15, y-15, x+15, y+15, fill="orange")
            label = self.canvas.create_text(x, y, text=self.selected_furniture, font=("Arial", 7))
            self.furniture_items[rect] = (x, y, label)
            self.actions_stack.append([rect, label])
        
        else:
            # Check if clicked near any canvas item to start dragging
            clicked_items = self.canvas.find_overlapping(x-5, y-5, x+5, y+5)
            if clicked_items:
                # Pick the topmost item under cursor
                self.dragging_item = clicked_items[-1]
                self.drag_start_pos = (x, y)
                # Bind mouse motion and release for dragging
                self.canvas.bind("<B1-Motion>", self.handle_drag)
                self.canvas.bind("<ButtonRelease-1>", self.handle_release)
            else:
                self.dragging_item = None

    def preview_drawing(self, event):
        if self.drawing_enabled and self.first_point:
            x0, y0 = self.first_point
            x, y = event.x, event.y
            width = 4 if self.line_style == "bold" else 2
            dash = (4, 2) if self.line_style == "dashed" else None
            if self.current_preview: self.canvas.delete(self.current_preview)
            if self.current_line_label: self.canvas.delete(self.current_line_label)
            self.current_preview = self.canvas.create_line(x0, y0, x, y, fill=self.line_color, width=width, dash=dash)
            label_text, mid_x, mid_y = get_distance_label(x0, y0, x, y, self.unit)
            self.current_line_label = self.canvas.create_text(mid_x, mid_y - 10, text=label_text, fill="gray", font=("Arial", 8))
    
    def handle_drag(self, event):
        if not self.dragging_item:
            return
        x, y = event.x, event.y
        dx = x - self.drag_start_pos[0]
        dy = y - self.drag_start_pos[1]
        self.canvas.move(self.dragging_item, dx, dy)

        # If dragging furniture, move the label as well
        if self.dragging_item in self.furniture_items:
            label_id = self.furniture_items[self.dragging_item][2]
            self.canvas.move(label_id, dx, dy)
            ix, iy, _ = self.furniture_items[self.dragging_item]
            self.furniture_items[self.dragging_item] = (ix + dx, iy + dy, label_id)

        self.drag_start_pos = (x, y)

    def handle_release(self, event):
        self.dragging_item = None
        self.drag_start_pos = None
        # Unbind the drag events to avoid conflicts
        self.canvas.unbind("<B1-Motion>")
        self.canvas.unbind("<ButtonRelease-1>")
