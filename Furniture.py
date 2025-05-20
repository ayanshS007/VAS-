import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import os

HANDLE_SIZE = 8

class Furniture:
    def __init__(self, canvas, image_path, x, y, select_callback):
        self.canvas = canvas
        self.original_image = Image.open(image_path).convert("RGBA")
        self.angle = 0
        self.scale = 1.0
        self.update_image()
        self.image_id = self.canvas.create_image(x, y, image=self.tk_image, anchor="center")

        self.select_callback = select_callback

        self.canvas.tag_bind(self.image_id, "<ButtonPress-1>", self.start_drag)
        self.canvas.tag_bind(self.image_id, "<B1-Motion>", self.drag)
        self.canvas.tag_bind(self.image_id, "<Button-3>", self.rotate)
        self.canvas.tag_bind(self.image_id, "<Button-1>", self.on_click)

        self.last_mouse = (x, y)
        self.handles = []
        self.handle_dragging = False
        self.handle_index = None

    def update_image(self):
        rotated = self.original_image.rotate(self.angle, expand=True)
        size = (int(rotated.width * self.scale), int(rotated.height * self.scale))
        resized = rotated.resize(size)
        self.tk_image = ImageTk.PhotoImage(resized)
        self.current_size = size

    def start_drag(self, event):
        self.last_mouse = (event.x, event.y)
        self.select_callback(self)

    def drag(self, event):
        dx = event.x - self.last_mouse[0]
        dy = event.y - self.last_mouse[1]
        self.canvas.move(self.image_id, dx, dy)
        self.last_mouse = (event.x, event.y)
        self.update_handles_position()

    def rotate(self, event=None):
        self.angle = (self.angle + 15) % 360
        self.update_image()
        self.canvas.itemconfig(self.image_id, image=self.tk_image)
        self.update_handles_position()

    def resize(self, factor):
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
        self.select_callback(self)

    def draw_handles(self):
        self.delete_handles()
        x, y = self.get_position()
        w, h = self.current_size
        half_w, half_h = w / 2, h / 2
        positions = [(x - half_w, y - half_h), (x + half_w, y - half_h),
                     (x + half_w, y + half_h), (x - half_w, y + half_h)]
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
        positions = [(x - half_w, y - half_h), (x + half_w, y - half_h),
                     (x + half_w, y + half_h), (x - half_w, y + half_h)]
        for i, (hx, hy) in enumerate(positions):
            self.canvas.coords(self.handles[i],
                               hx - HANDLE_SIZE//2, hy - HANDLE_SIZE//2,
                               hx + HANDLE_SIZE//2, hy + HANDLE_SIZE//2)

    def start_handle_drag(self, event, handle_index):
        self.handle_dragging = True
        self.handle_index = handle_index
        self.last_mouse = (event.x, event.y)

    def handle_drag(self, event):
        if not self.handle_dragging:
            return
        x, y = self.get_position()
        dx = event.x - self.last_mouse[0]
        dy = event.y - self.last_mouse[1]
        w, h = self.current_size
        base_img = self.original_image.rotate(self.angle, expand=True)

        scale_x = (w + dx * 2) / base_img.width if self.handle_index in [1, 2] else (w - dx * 2) / base_img.width
        scale_y = (h + dy * 2) / base_img.height if self.handle_index in [2, 3] else (h - dy * 2) / base_img.height
        self.scale = max(0.1, (scale_x + scale_y) / 2)

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


class GraphLayoutApp:
    def __init__(self, root):
        self.root = root
        root.title("2D Home Layout with Furniture")

        self.main_frame = tk.Frame(root)
        self.main_frame.pack(fill="both", expand=True)

        self.sidebar = tk.Frame(self.main_frame, width=200, bg="#f0f0f0")
        self.sidebar.pack(side="left", fill="y")

        self.canvas = tk.Canvas(self.main_frame, bg="white")
        self.canvas.pack(side="right", fill="both", expand=True)
        self.canvas.bind("<Configure>", self.draw_grid)
        self.canvas.bind("<Button-1>", self.canvas_click)

        self.grid_size = 20
        self.furniture_items = []
        self.selected_item = None
        self.selected_furniture_name = "bed"

        self.furniture_list = ["bed", "sofa", "chair", "table", "almirah", "door"]
        self.image_thumbnails = {}

        tk.Label(self.sidebar, text="Select Furniture", bg="#f0f0f0").pack(pady=5)
        for name in self.furniture_list:
            path = f"images/{name}.png"
            if os.path.exists(path):
                image = Image.open(path).resize((40, 40))
                thumb = ImageTk.PhotoImage(image)
                self.image_thumbnails[name] = thumb
                btn = tk.Button(self.sidebar, image=thumb, text=name.capitalize(),
                                compound="top", command=lambda n=name: self.set_selected_furniture(n))
                btn.pack(pady=5, padx=10)

        tk.Button(self.sidebar, text="Rotate", command=self.rotate_selected).pack(pady=10)
        tk.Button(self.sidebar, text="Delete", command=self.delete_selected).pack(pady=5)

    def draw_grid(self, event=None):
        self.canvas.delete("grid_line")
        width = self.canvas.winfo_width()
        height = self.canvas.winfo_height()
        for i in range(0, width, self.grid_size):
            self.canvas.create_line(i, 0, i, height, fill="#e0e0e0", tags="grid_line")
        for i in range(0, height, self.grid_size):
            self.canvas.create_line(0, i, width, i, fill="#e0e0e0", tags="grid_line")

    def set_selected_furniture(self, name):
        self.selected_furniture_name = name

    def canvas_click(self, event):
        path = f"images/{self.selected_furniture_name}.png"
        if os.path.exists(path):
            item = Furniture(self.canvas, path, event.x, event.y, self.select_item)
            self.furniture_items.append(item)
            self.select_item(item)

    def select_item(self, item):
        if self.selected_item:
            self.selected_item.delete_handles()
        self.selected_item = item
        self.selected_item.draw_handles()

    def rotate_selected(self):
        if self.selected_item:
            self.selected_item.rotate()

    def delete_selected(self):
        if self.selected_item:
            self.selected_item.delete()
            self.furniture_items.remove(self.selected_item)
            self.selected_item = None


if __name__ == "__main__":
    root = tk.Tk()
    app = GraphLayoutApp(root)
    root.mainloop()
