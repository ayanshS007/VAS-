import tkinter as tk
from tkinter import ttk
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import os

from Furniture import Furniture
HANDLE_SIZE = 8
class GraphLayoutApp:
    def __init__(self, root):
        self.root = root
        root.title("2D Home Layout with Furniture")

        self.main_frame = tk.Frame(root)
        self.main_frame.pack(fill="both", expand=True)

        # Sidebar
        self.sidebar = tk.Frame(self.main_frame, width=200, bg="#f0f0f0")
        self.sidebar.pack(side="left", fill="y")

        # Canvas
        self.canvas = tk.Canvas(self.main_frame, bg="white")
        self.canvas.pack(side="right", fill="both", expand=True)
        self.canvas.bind("<Configure>", self.draw_grid)
        self.canvas.bind("<Button-1>", self.canvas_click)

        self.grid_size = 20
        self.furniture_items = []
        self.selected_item = None
        self.selected_furniture_name = "double_bed"

        # Dropdown with thumbnails
        self.furniture_list = ["double_bed", "single_bed", "dining_table_8_seat","chair"]
        self.image_thumbnails = {}

        tk.Label(self.sidebar, text="Select Furniture", bg="#f0f0f0").pack(pady=5)

        for name in self.furniture_list:
            path = f"images/{name}.png"
            if os.path.exists(path):
                image = Image.open(path).resize((40, 40))
                thumb = ImageTk.PhotoImage(image)
                self.image_thumbnails[name] = thumb

                btn = tk.Button(
                    self.sidebar,
                    image=thumb,
                    text=name.capitalize(),
                    compound="top",
                    command=lambda n=name: self.set_selected_furniture(n)
                )
                btn.pack(pady=5, padx=10, fill="x")
            else:
                print(f"Missing image: {path}")

        # Info
        tk.Label(self.sidebar, text="Controls", bg="#f0f0f0", font=("Arial", 10, "bold")).pack(pady=(20, 5))
        tk.Label(self.sidebar, text="Left click = Place & Drag\nRight click = Rotate\n+ / - = Resize\nDel = Delete selected", bg="#f0f0f0", justify="left").pack(pady=5, padx=10)

        # Keyboard shortcuts
        self.root.bind("<KeyPress-plus>", lambda e: self.resize_selected(1.1))
        self.root.bind("<KeyPress-minus>", lambda e: self.resize_selected(0.9))
        self.root.bind("<KeyPress-equal>", lambda e: self.resize_selected(1.1))
        self.root.bind("<Delete>", lambda e: self.delete_selected())

    def draw_grid(self, event=None):
        self.canvas.delete("grid")
        width = self.canvas.winfo_width()
        height = self.canvas.winfo_height()
        for x in range(0, width, self.grid_size):
            self.canvas.create_line(x, 0, x, height, fill="#ddd", tag="grid")
        for y in range(0, height, self.grid_size):
            self.canvas.create_line(0, y, width, y, fill="#ddd", tag="grid")

    def canvas_click(self, event):
        # If clicking empty space, add furniture
        clicked_item = self.canvas.find_closest(event.x, event.y)
        if clicked_item:
            tags = self.canvas.gettags(clicked_item)
            if "handle" in tags:
                # clicked on handle, ignore here (handled in Furniture)
                return

            # Check if clicked on any furniture image
            for furniture in self.furniture_items:
                if furniture.image_id == clicked_item[0]:
                    self.select_item(furniture)
                    return

        # If clicked empty space, add new furniture
        self.add_furniture_at(event.x, event.y)

    def set_selected_furniture(self, name):
        self.selected_furniture_name = name

    def add_furniture_at(self, x, y):
        name = self.selected_furniture_name
        path = f"images/{name}.png"
        if os.path.exists(path):
            item =Furniture(self.canvas, path, x, y, self.select_item)
            self.furniture_items.append(item)
            self.select_item(item)

    def resize_selected(self, factor):
        if self.selected_item:
            self.selected_item.resize(factor)

    def select_item(self, item):
        # Deselect old
        if self.selected_item and self.selected_item != item:
            self.selected_item.delete_handles()

        self.selected_item = item
        item.draw_handles()

    def delete_selected(self):
        if self.selected_item:
            self.selected_item.delete()
            if self.selected_item in self.furniture_items:
                self.furniture_items.remove(self.selected_item)
            self.selected_item = None