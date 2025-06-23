import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import os

HANDLE_SIZE = 8

def find_image_path(name):
    """Find the path for the furniture image, supporting .png and .jpeg."""
    base_dir = os.path.dirname(os.path.abspath(__file__))
    for ext in ('png', 'jpeg', 'jpg'):
        path = os.path.join(base_dir, "Images", f"{name}.{ext}")
        if os.path.exists(path):
            return path
    return None

class Furniture:
    def __init__(self, canvas, image_path, x, y, select_callback,scale,angle,get_freeze_state):
        self.image_path = image_path
        self.canvas = canvas
        self.original_image = Image.open(image_path).convert("RGBA")
        self.angle = angle
        self.scale = scale
        self.update_image()
        self.image_id = self.canvas.create_image(x, y, image=self.tk_image, anchor="center",tags=("furniture",))
        self.select_callback = select_callback
        self.canvas.tag_bind(self.image_id, "<ButtonPress-1>", self.start_drag)
        self.canvas.tag_bind(self.image_id, "<B1-Motion>", self.drag)
        self.canvas.tag_bind(self.image_id, "<Double-Button-1>", self.rotate)
        self.canvas.tag_bind(self.image_id, "<Button-1>", self.on_click)
        self.last_mouse = (x, y)
        self.handles = []
        self.handle_dragging = False
        self.handle_index = None
        self.get_freeze_state = get_freeze_state  # function to query freeze state

    def update_image(self):
        rotated = self.original_image.rotate(self.angle, expand=True)
        size = (int(rotated.width * self.scale), int(rotated.height * self.scale))
        resized = rotated.resize(size)
        self.tk_image = ImageTk.PhotoImage(resized)
        self.current_size = size

    def start_drag(self, event):
        if self.get_freeze_state(): return
        self.last_mouse = (event.x, event.y)
        self.select_callback(self)

    def drag(self, event):
        if self.get_freeze_state(): return
        dx = event.x - self.last_mouse[0]
        dy = event.y - self.last_mouse[1]
        self.canvas.move(self.image_id, dx, dy)
        self.last_mouse = (event.x, event.y)
        self.update_handles_position()

    def rotate(self, event=None):
        if self.get_freeze_state(): return
        self.angle = (self.angle + 15) % 360
        self.update_image()
        self.canvas.itemconfig(self.image_id, image=self.tk_image)
        self.update_handles_position()

    def resize(self, factor):
        if self.get_freeze_state(): return
        self.scale *= factor
        self.update_image()
        self.canvas.itemconfig(self.image_id, image=self.tk_image)
        self.update_handles_position()

    def get_position(self):
        coords = self.canvas.coords(self.image_id)
        return coords[0], coords[1] if coords else (0, 0)

    def set_position(self, x, y):
        self.canvas.coords(self.image_id, x, y)
        self.update_handles_position()

    def on_click(self, event):
        if self.get_freeze_state(): return
        self.select_callback(self)

    def draw_handles(self):
        self.delete_handles()
        x, y = self.get_position()
        w, h = self.current_size
        half_w, half_h = w / 2, h / 2
        positions = [
            (x - half_w, y - half_h), (x + half_w, y - half_h),
            (x + half_w, y + half_h), (x - half_w, y + half_h)
        ]
        for i, (hx, hy) in enumerate(positions):
            handle = self.canvas.create_rectangle(
                hx - HANDLE_SIZE//2, hy - HANDLE_SIZE//2,
                hx + HANDLE_SIZE//2, hy + HANDLE_SIZE//2,
                fill="blue", outline="black",
                tags=("handle", f"handle_{id(self)}_{i}")
            )
            self.handles.append(handle)
            self.canvas.tag_bind(handle, "<ButtonPress-1>", lambda e, idx=i: self.start_handle_drag(e, idx))
            self.canvas.tag_bind(handle, "<B1-Motion>", self.handle_drag)
            self.canvas.tag_bind(handle, "<ButtonRelease-1>", self.end_handle_drag)




    def delete_handles(self):
        for h in self.handles:
            self.canvas.delete(h)
        self.handles.clear()

    def update_handles_position(self):
        if not self.handles:
            return
        x, y = self.get_position()
        w, h = self.current_size
        half_w, half_h = w / 2, h / 2
        positions = [
            (x - half_w, y - half_h), (x + half_w, y - half_h),
            (x + half_w, y + half_h), (x - half_w, y + half_h)
        ]
        for i, (hx, hy) in enumerate(positions):
            self.canvas.coords(self.handles[i],
                hx - HANDLE_SIZE//2, hy - HANDLE_SIZE//2,
                hx + HANDLE_SIZE//2, hy + HANDLE_SIZE//2)

    def start_handle_drag(self, event, handle_index):
        if self.get_freeze_state(): return
        self.handle_dragging = True
        self.handle_index = handle_index
        self.last_mouse = (event.x, event.y)

    def handle_drag(self, event):
        if self.get_freeze_state(): return
        if not self.handle_dragging:
            return
        x, y = self.get_position()
        dx = event.x - self.last_mouse[0]
        dy = event.y - self.last_mouse[1]
        w, h = self.current_size
        base_img = self.original_image.rotate(self.angle, expand=True)
        scale_x = (w + dx * 2) / base_img.width if self.handle_index in [1, 2] else (w - dx * 2) / base_img.width
        scale_y = (h + dy * 2) / base_img.height if self.handle_index in [2, 3] else (h - dy * 2) / base_img.height
        self.scale = max(0.05, (scale_x + scale_y) / 2)
        self.update_image()
        self.canvas.itemconfig(self.image_id, image=self.tk_image)
        self.set_position(x + dx / 2, y + dy / 2)
        self.last_mouse = (event.x, event.y)

    def end_handle_drag(self, event):
        self.handle_dragging = False
        self.handle_index = None

    def delete(self):
        self.delete_handles()
        self.canvas.delete(self.image_id)

    def apply_global_zoom(self, zoom_level):
        self.scale = zoom_level
        self.update_image()
        self.canvas.itemconfig(self.image_id, image=self.tk_image)
        self.update_handles_position()
        
    def flip_horizontal(self):
        # Flip the original image left-right and update
        self.original_image = self.original_image.transpose(Image.FLIP_LEFT_RIGHT)
        self.update_image()
        self.canvas.itemconfig(self.image_id, image=self.tk_image)
        self.update_handles_position()

    def flip_vertical(self):
        # Flip the original image top-bottom and update
        self.original_image = self.original_image.transpose(Image.FLIP_TOP_BOTTOM)
        self.update_image()
        self.canvas.itemconfig(self.image_id, image=self.tk_image)
        self.update_handles_position()