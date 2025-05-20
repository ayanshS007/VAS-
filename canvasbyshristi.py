import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageDraw, ImageGrab
import os
class AutoCADCanvas:
    def __init__(self, root):
        self.root = root
        self.root.title("AutoCAD Canvas with Grid")

        self.canvas_width = 800
        self.canvas_height = 600
        self.grid_interval = 20

        self.canvas = tk.Canvas(root, bg="white", width=self.canvas_width, height=self.canvas_height)
        self.canvas.pack()

        self.draw_grid()

        self.button_frame = tk.Frame(root)
        self.button_frame.pack()

        tk.Button(self.button_frame, text="Undo", command=self.undo).pack(side=tk.LEFT)
        tk.Button(self.button_frame, text="Redo", command=self.redo).pack(side=tk.LEFT)
        tk.Button(self.button_frame, text="Save Image", command=self.save_image).pack(side=tk.LEFT)
        tk.Button(self.button_frame, text="Clear Canvas", command=self.clear_canvas).pack(side=tk.LEFT)

        self.canvas.bind("<ButtonPress-1>", self.start_draw)
        self.canvas.bind("<B1-Motion>", self.draw)

        self.lines = []  # Stack of tuples: (line_id, x1, y1, x2, y2)
        self.redo_stack = []

    def draw_grid(self):
        for i in range(0, self.canvas_width, self.grid_interval):
            self.canvas.create_line(i, 0, i, self.canvas_height, fill="lightgray", tags="grid")
        for i in range(0, self.canvas_height, self.grid_interval):
            self.canvas.create_line(0, i, self.canvas_width, i, fill="lightgray", tags="grid")

    def start_draw(self, event):
        self.x = event.x
        self.y = event.y

    def draw(self, event):
        line_id = self.canvas.create_line(self.x, self.y, event.x, event.y, fill="black", width=2)
        self.lines.append((line_id, self.x, self.y, event.x, event.y))
        self.redo_stack.clear()
        self.x = event.x
        self.y = event.y

    def undo(self):
        if self.lines:
            line = self.lines.pop()
            self.canvas.delete(line[0])
            self.redo_stack.append(line)

    def redo(self):
        if self.redo_stack:
            _, x1, y1, x2, y2 = self.redo_stack.pop()
            line_id = self.canvas.create_line(x1, y1, x2, y2, fill="black", width=2)
            self.lines.append((line_id, x1, y1, x2, y2))

    def save_image(self):
        filepath = filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("PNG files", "*.png")])
        if filepath:
            # Get canvas position on screen
            x = self.root.winfo_rootx() + self.canvas.winfo_x()
            y = self.root.winfo_rooty() + self.canvas.winfo_y()
            x1 = x + self.canvas.winfo_width()
            y1 = y + self.canvas.winfo_height()

            ImageGrab.grab().crop((x, y, x1, y1)).save(filepath)

    def clear_canvas(self):
        self.canvas.delete("all")
        self.lines.clear()
        self.redo_stack.clear()
        self.draw_grid()


if __name__ == '__main__':
    root = tk.Tk()
    app = AutoCADCanvas(root)
    root.mainloop()