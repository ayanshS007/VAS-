import tkinter as tk
import math
from tkinter import colorchooser, filedialog, simpledialog
from config import *
from geometry import calculate_polygon_area, calculate_polygon_perimeter
from drawing_helpers import get_distance_label
from toolbar import setup_toolbar
from Furniture import Furniture, find_image_path
from PIL import ImageGrab
import os

class CanvasManager:
    def __init__(self, root):
        self.root = root
        self.root.title("Graph Paper Layout Tool")

        self.zoom_level = 1.0
        self.zoom_step = 0.1
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
        self.current_preview = None
        self.current_line_label = None
        self.fill_color = ""
        self.freeform_points = []
        self.fill_mode_enabled = False
        self.temp_direction = None
        self.temp_entry = None
        self.line_by_angle_mode = False
        self.click_callback = None
        self.text_insertion_mode = False

        self.unit_var = tk.StringVar(value=self.unit)
        self.line_style_var = tk.StringVar(value=self.line_style)
        self.line_style_var.set("solid")  # or "bold" or "dashed"
        self.text_insertion_mode = False
        self.text_font_size = 11
        self.selected_text_item = None
        self.fill_color = ""
        self.fill_mode_enabled = False
        self.resizing_room_id = None
        




        # Image furniture system
        self.image_furniture_list = ["double_bed", "single_bed", "dining_table_8_seat","Toilet","sofa","Chair","Bath Tub","Toiler_room1","Bathroom_layout1"]
        self.selected_image_furniture = None
        self.image_furniture_items = []
        self.selected_image_item = None

        # Canvas setup
        self.canvas = tk.Canvas(root, width=self.canvas_width, height=self.canvas_height, bg="white")
        self.canvas.pack(side=tk.RIGHT, expand=True, fill=tk.BOTH)

        left_panel = tk.Frame(self.root)
        left_panel.pack(side=tk.LEFT, fill=tk.Y, padx=5, pady=5)
        setup_toolbar(self, left_panel)

        self.canvas.bind("<MouseWheel>", self.mouse_zoom)
        self.canvas.bind("<Button-1>", self.handle_click)
        self.canvas.bind("<Motion>", self.preview_drawing)
        self.root.bind("<Escape>", lambda e: setattr(self, 'selected_text_item', None))

        self.dragging_item = None
        self.drag_start_pos = None
        self.grid_visible = False
        self.grid_lines = []

        # Sidebar for image furniture
        # self._setup_image_furniture_sidebar(left_panel)

    # def _setup_image_furniture_sidebar(self, parent):
    #     sidebar = tk.Frame(parent, width=200, bg="#f0f0f0")
    #     sidebar.pack(side=tk.LEFT, fill=tk.Y)
    #     # tk.Label(sidebar, text="Image Furniture", bg="#f0f0f0").pack(pady=5)
    #     self.image_thumbnails = {}
    #     for name in self.image_furniture_list:
    #         path = find_image_path(name)
    #         if path:
    #             from PIL import Image, ImageTk
    #             image = Image.open(path).resize((40, 40))
    #             thumb = ImageTk.PhotoImage(image)
    #             self.image_thumbnails[name] = thumb
    #             btn = tk.Button(
    #                 sidebar, image=thumb, text=name.replace("_", " ").title(),
    #                 compound="top", command=lambda n=name: self.set_selected_image_furniture(n)
    #             )
    #             btn.pack(pady=5, padx=10)
    #     # tk.Button(sidebar, text="Rotate", command=self.rotate_selected_image).pack(pady=5)
    #     # tk.Button(sidebar, text="Delete", command=self.delete_selected_image).pack(pady=5)
    #     # tk.Button(sidebar, text="Zoom In", command=lambda: self.zoom_image(1.1)).pack(pady=5)
    #     # tk.Button(sidebar, text="Zoom Out", command=lambda: self.zoom_image(0.9)).pack(pady=5)

    # === Image Furniture System ===
    def set_selected_image_furniture(self, name):
        self.selected_image_furniture = name
    def zoom_in(self):
     self._apply_zoom(1 + self.zoom_step)
    def zoom_out(self):
     self._apply_zoom(1 - self.zoom_step)
    def _apply_zoom(self, scale_factor):
     self.zoom_level *= scale_factor
     self.canvas.scale("all", 0, 0, scale_factor, scale_factor)  # Scale from top-left corner
    #  self.zoom_level *= scale_factor
     self.grid_spacing *= scale_factor  # ✅ Keeps logical scaling consistent

     self._rescale_furniture_labels()
     self._rescale_texts()   

    def handle_click(self, event):
        x, y = event.x, event.y

        if self.drawing_enabled:
            if not self.first_point:
                self.first_point = (x, y)
                # Create point at first click
                point = self.canvas.create_oval(x-0.5, y-0.5, x+0.5, y+0.5, fill="black")
                # Save just the point id to stack for undo
            else:
                x0, y0 = self.first_point
                x1, y1 = event.x, event.y
                dx = x1 - x0
                dy = y1 - y0
                mouse_length = math.hypot(dx, dy)

                # Show distance input like AutoCAD
                if mouse_length > 0:
                    self.temp_direction = (dx / mouse_length, dy / mouse_length)
                    self.temp_origin = (x0, y0)

                    if self.temp_entry:
                       self.temp_entry.destroy()

                    self.temp_entry = tk.Entry(self.root)
                    self.temp_entry.place(x=event.x_root - 30, y=event.y_root - 10, width=60)
                    self.temp_entry.focus()
                    self.temp_entry.bind("<Return>", self.finish_line_with_distance)

                    # Also store freeform points for potential closed shape detection
                    self.freeform_points.append((x0, y0))
                    self.freeform_points.append((x1, y1))

                    # If enough points, check if shape is closed
                    if len(self.freeform_points) >= 3 and math.dist(self.freeform_points[0], self.freeform_points[-1]) < 10:
                                   # At least 3 lines
                        if math.dist(self.freeform_points[0], self.freeform_points[-1]) < 10:
                            polygon_points = [self.freeform_points[0]]
                            for pt in self.freeform_points[1:]:
                                if math.dist(pt, polygon_points[-1]) > 1:
                                    polygon_points.append(pt)

                            flat = [coord for pt in polygon_points for coord in pt]
                            polygon_id = self.canvas.create_polygon(flat, outline=self.line_color, fill=self.fill_color, width=2, tags=("closed_shape",))
                            self.actions_stack.append([polygon_id])
                            self.freeform_points.clear()
                            self.fill_color = ""

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
            point = self.canvas.create_oval(x-0.5, y-0.5, x+0.5, y+0.5, fill="green")
            self.actions_stack.append([point])

        elif self.selected_image_furniture:
            # from Furniture import Furniture
            # image_item = Furniture(self.canvas, self.selected_image_furniture, x, y)
            from Furniture import Furniture, find_image_path
            image_path = find_image_path(self.selected_image_furniture)
            if image_path:
               image_item = Furniture(self.canvas, image_path, x, y, self.select_image_item)
               self.image_furniture_items.append(image_item)
               self.select_image_item(image_item)
               self.selected_image_furniture = None

            self.image_furniture_items.append(image_item)
            self.select_image_item(image_item)
            return

            
        elif self.click_callback:
            self.click_callback(event.x, event.y)
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
                # self.dragging_item = None
                clicked_items = self.canvas.find_overlapping(x-5, y-5, x+5, y+5)
                if clicked_items:
                 top_item = clicked_items[-1]
                 tags = self.canvas.gettags(top_item)

                 if "room_handle" in tags:
                  self.resizing_room_id = top_item
                  self.canvas.bind("<B1-Motion>", self.resize_room_drag)
                  return

                 if "draggable" in tags or "room" in tags:
                  self.dragging_item = top_item
                  self.drag_start_pos = (x, y)
                  self.canvas.bind("<B1-Motion>", self.handle_drag)
                  self.canvas.bind("<ButtonRelease-1>", self.handle_release)
                 return

    def finish_line_with_distance(self, event):
        try:
            dist = float(self.temp_entry.get())
        except:
            self.temp_entry.destroy()
            self.temp_entry = None
            return

        dx, dy = self.temp_direction
        x0, y0 = self.temp_origin
        pixel_length = (dist / self.unit_scale[self.unit]) * self.grid_spacing * self.zoom_level
        x1 = x0 + dx * pixel_length
        y1 = y0 + dy * pixel_length


        width = 4 if self.line_style == "bold" else 2
        dash = (4, 2) if self.line_style == "dashed" else None

        line = self.canvas.create_line(x0, y0, x1, y1, fill=self.line_color, width=width, dash=dash)
        label_text, mid_x, mid_y = get_distance_label(x0, y0, x1, y1, self.unit, self.zoom_level)
        # label_text, mid_x, mid_y = get_distance_label(x0, y0, x1, y1, self.unit)
        label = self.canvas.create_text(mid_x, mid_y - 10, text=label_text, font=("Arial", 8))
        point = self.canvas.create_oval(x1-0.5, y1-0.5, x1+0.5, y1+0.5, fill="black")

        self.actions_stack.append([line, label, point])

        # Clean up
        self.first_point = None
        if self.current_preview:
            self.canvas.delete(self.current_preview)
            self.current_preview = None
        if self.current_line_label:
            self.canvas.delete(self.current_line_label)
            self.current_line_label = None
        self.temp_entry.destroy()
        self.temp_entry = None 


    def select_image_item(self, item):
        if self.selected_image_item:
            self.selected_image_item.delete_handles()
        self.selected_image_item = item
        self.selected_image_item.draw_handles()

    def rotate_selected_image(self):
        if self.selected_image_item:
            self.selected_image_item.rotate()

    def delete_selected_image(self):
        if self.selected_image_item:
            self.selected_image_item.delete()
            if self.selected_image_item in self.image_furniture_items:
                self.image_furniture_items.remove(self.selected_image_item)
            self.selected_image_item = None

    def zoom_image(self, factor):
        for item in self.image_furniture_items:
            item.apply_global_zoom(factor)

    # === Core Canvas Features ===
    def mouse_zoom(self, event):
        scale = 1.1 if event.delta > 0 else 0.9
        self.zoom_level *= scale
        self.canvas.scale("all", event.x, event.y, scale, scale)
        self._rescale_texts()
        for item in self.image_furniture_items:
            item.apply_global_zoom(self.zoom_level)

    def _rescale_texts(self):
        for item in self.canvas.find_all():
            if self.canvas.type(item) == "text":
                self.canvas.itemconfig(item, font=("Arial", 10))

    def draw_grid(self):
        self.clear_grid()
        width = self.canvas.winfo_width()
        height = self.canvas.winfo_height()
        for x in range(0, width, self.grid_spacing):
            line = self.canvas.create_line(x, 0, x, height, fill="#eee")
            self.grid_lines.append(line)
        for y in range(0, height, self.grid_spacing):
            line = self.canvas.create_line(0, y, width, y, fill="#eee")
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

    def change_unit(self, unit):
        self.unit = unit

    def change_line_style(self, style):
        self.line_style = style

    def pick_line_color(self):
        color = colorchooser.askcolor()[1]
        if color:
            self.line_color = color

    def enable_eraser_mode(self):
        self.reset_modes()
        self.eraser_mode = True
        self.canvas.config(cursor="dotbox")
        self.canvas.bind("<Button-1>", self.handle_eraser_click)
        self.canvas.bind("<B1-Motion>", self.handle_eraser_click)

    def handle_eraser_click(self, event):
        x, y = event.x, event.y
        # Find items under cursor (topmost last)
        clicked_items = self.canvas.find_overlapping(x-5, y-5, x+5, y+5)
        if clicked_items:
            item_id = clicked_items[-1]

            # Check if the item has the "grid" tag
            if "grid" in self.canvas.gettags(item_id):
                return  # Don't delete grid items

            self.canvas.delete(item_id)

            # Remove from actions_stack for undo support
            self.actions_stack = [
                [i for i in group if i != item_id]
                for group in self.actions_stack
            ]
            self.actions_stack = [g for g in self.actions_stack if g]  # Remove empty groups

            # Remove from furniture_items if present
            if item_id in self.furniture_items:
                del self.furniture_items[item_id]

        # Optionally, you can turn off eraser mode after one erase:
        # self.reset_modes()
        # self.canvas.config(cursor="")

    def enable_line_drawing(self):
        if self.drawing_enabled:
            self.reset_modes()
        else:
            self.reset_modes()
            self.drawing_enabled = True

    def enable_polygon_mode(self):
        self.reset_modes()
        self.polygon_mode = True
        self.polygon_points = []

    def reset_modes(self): 
        self.drawing_enabled = False
        self.polygon_mode = False
        self.selected_furniture = None
        self.first_point = None
        self.eraser_mode = False  # ✅ reset eraser mode
        self.fill_mode_enabled = False

        self.canvas.config(cursor="")
        # ✅ Unbind eraser-specific mouse events
        self.canvas.unbind("<Button-1>")
        self.canvas.unbind("<B1-Motion>")
    
        # ✅ Rebind default handlers like click and preview
        self.canvas.bind("<Button-1>", self.handle_click)
        self.canvas.bind("<Motion>", self.preview_drawing)

    def finish_polygon(self):
        if len(self.polygon_points) < 3:
            return
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
        self.image_furniture_items.clear()
        self.selected_image_item = None
        self.draw_grid()

    def undo(self):
        if self.actions_stack:
            for item in self.actions_stack.pop():
                self.canvas.delete(item)

    def save_canvas(self):
        filetypes = [
            ("PostScript", "*.ps"),
            ("PNG Image", "*.png"),
            ("JPEG Image", "*.jpg"),
            ("PDF Document", "*.pdf")
        ]
        path = filedialog.asksaveasfilename(
            defaultextension=".ps",
            filetypes=filetypes,
            title="Save As"
        )
        if not path:
            return
        if path.lower().endswith('.ps'):
            self.canvas.postscript(file=path, colormode='color')
        elif path.lower().endswith(('.png', '.jpg', '.jpeg')):
            x = self.root.winfo_rootx() + self.canvas.winfo_x()
            y = self.root.winfo_rooty() + self.canvas.winfo_y()
            x1 = x + self.canvas.winfo_width()
            y1 = y + self.canvas.winfo_height()
            ImageGrab.grab(bbox=(x, y, x1, y1)).save(path)
        elif path.lower().endswith('.pdf'):
            temp_ps = "temp.ps"
            self.canvas.postscript(file=temp_ps, colormode='color')
            try:
                import subprocess
                subprocess.run([
                    'gs',
                    '-q',
                    '-dNOPAUSE',
                    '-dBATCH',
                    '-sDEVICE=pdfwrite',
                    f'-sOutputFile={path}',
                    temp_ps
                ], check=True)
            except Exception as e:
                print(f"PDF conversion failed: {e}")
            finally:
                if os.path.exists(temp_ps):
                    os.remove(temp_ps)

    def preview_drawing(self, event):
        if self.drawing_enabled and self.first_point:
            x0, y0 = self.first_point
            x, y = event.x, event.y
            width = 4 if self.line_style == "bold" else 2
            dash = (4, 2) if self.line_style == "dashed" else None
            if self.current_preview: self.canvas.delete(self.current_preview)
            if self.current_line_label: self.canvas.delete(self.current_line_label)
            self.current_preview = self.canvas.create_line(x0, y0, x, y, fill=self.line_color, width=width, dash=dash)
            label_text, mid_x, mid_y = get_distance_label(x0, y0, x, y, self.unit, self.zoom_level)
            # label_text, mid_x, mid_y = get_distance_label(x0, y0, x, y, self.unit)
            self.current_line_label = self.canvas.create_text(mid_x, mid_y - 10, text=label_text, fill="gray", font=("Arial", 8))

    def pick_fill_color(self):
        color = colorchooser.askcolor()[1]
        if color:
            self.fill_color = color

    def enable_fill_mode(self):
        self.reset_modes()
        self.fill_mode_enabled = True
        self.canvas.config(cursor="dotbox")
        self.canvas.bind("<Button-1>", self.fill_at_point_click)

    def fill_at_point_click(self, event):
        x, y = event.x, event.y
        overlapping = self.canvas.find_overlapping(x-1, y-1, x+1, y+1)
        for item_id in reversed(overlapping):
            item_type = self.canvas.type(item_id)
            tags = self.canvas.gettags(item_id)
            if item_type == "polygon" or "closed_shape" in tags:
                self.canvas.itemconfig(item_id, fill=self.fill_color)
                self.actions_stack.append([item_id])
                break
        self.fill_mode_enabled = False
        self.canvas.config(cursor="")
        self.canvas.bind("<Button-1>", self.handle_click)

    # def enable_text_insertion(self):
    #     self.reset_modes()
    #     self.text_insertion_mode = True
    #     self.canvas.config(cursor="xterm")
    #     self.canvas.bind("<Button-1>", self.handle_click)
    
    def enable_text_insertion(self):
        self.reset_modes()
        self.text_insertion_mode = True
        self.canvas.config(cursor="xterm")
        self.canvas.bind("<Button-1>", self.insert_text_box)

    def insert_text_box(self, event):
        text = simpledialog.askstring("Insert Text", "Enter your text:")
        if text:
            x, y = event.x, event.y
            text_id = self.canvas.create_text(x, y, text=text, font=("Arial", self.text_font_size), anchor="nw")
            self.canvas.tag_bind(text_id, "<Button-1>", self.select_text_item)
            self.canvas.tag_bind(text_id, "<B1-Motion>", self.drag_text)
            self.canvas.tag_bind(text_id, "<Double-Button-1>", self.resize_text_popup)
            self.actions_stack.append([text_id])

    def select_text_item(self, event):
        self.selected_text_item = self.canvas.find_closest(event.x, event.y)[0]

    def drag_text(self, event):
        if self.selected_text_item:
            self.canvas.coords(self.selected_text_item, event.x, event.y)

    def resize_text_popup(self, event):
        if self.selected_text_item:
            size = simpledialog.askinteger("Font Size", "Enter new font size:", initialvalue=self.text_font_size)
            if size:
                self.text_font_size = size
                self.canvas.itemconfig(self.selected_text_item, font=("Arial", self.text_font_size))
            # Add any other advanced features from your previous CanvasManager as needed.
    def insert_room_template(self, name, width_m, height_m):
     x0, y0 = 100 + self.group_id_counter * 20, 100 + self.group_id_counter * 20
     width_px = width_m / self.unit_scale[self.unit] * self.grid_spacing * self.zoom_level
     height_px = height_m / self.unit_scale[self.unit] * self.grid_spacing * self.zoom_level
     x1, y1 = x0 + width_px, y0 + height_px

     # Unique tag for each room
     group_tag = f"room_group_{self.group_id_counter}"
     self.group_id_counter += 1

     # Draw rectangle and label, with same unique tag
     rect = self.canvas.create_rectangle(x0, y0, x1, y1, fill="#d0f0c0", outline="black", tags=(group_tag,))
     label = self.canvas.create_text((x0 + x1) / 2, (y0 + y1) / 2,
                                    text=f"{name}\n{width_m}×{height_m} m", font=("Arial", 10),
                                    tags=(group_tag,))

     # Bind drag events to the unique group tag
     self.canvas.tag_bind(group_tag, "<Button-1>", self.start_drag_room)
     self.canvas.tag_bind(group_tag, "<B1-Motion>", self.drag_room)
     self.canvas.tag_bind(group_tag, "<ButtonRelease-1>", self.end_drag_room)

     # Add to undo stack
     self.actions_stack.append([rect, label])


    def start_drag_room(self, event):
     self.drag_start_pos = (event.x, event.y)
     clicked_item = self.canvas.find_closest(event.x, event.y)[0]
     tags = self.canvas.gettags(clicked_item)
     # Get the room group tag (e.g., "room_0")
     self.drag_group_tag = next((tag for tag in tags if tag.startswith("room_group_")), None)
    def drag_room(self, event):
     if hasattr(self, 'drag_group_tag') and self.drag_group_tag:
        dx = event.x - self.drag_start_pos[0]
        dy = event.y - self.drag_start_pos[1]
        for item in self.canvas.find_withtag(self.drag_group_tag):
            self.canvas.move(item, dx, dy)
        self.drag_start_pos = (event.x, event.y)

    def end_drag_room(self, event):
     self.dragged_items = None


    # def resize_room(self, event, rect_id, label_id, handle_id):
    #  x0, y0, _, _ = self.canvas.coords(rect_id)
    #  x1 = self.canvas.canvasx(event.x)
    #  y1 = self.canvas.canvasy(event.y)

    #  self.canvas.coords(rect_id, x0, y0, x1, y1)
    #  self.canvas.coords(label_id, (x0 + x1) / 2, (y0 + y1) / 2)
    #  self.canvas.coords(handle_id, x1 - 6, y1 - 6, x1 + 6, y1 + 6)




# Usage in main.py:
# from canvas_manager import CanvasManager
# root = tk.Tk()
# app = CanvasManager(root)
# root.geometry("1200x800")
# root.mainloop()

# main.py (Example Usage)
# if __name__ == "__main__":
#     root = tk.Tk()
#     app = CanvasManager(root)
#     root.geometry("1200x800")
#     root.mainloop()





    
        
    
        
            
# import tkinter as tk
# import math
# from tkinter import colorchooser, filedialog
# from config import *
# from geometry import calculate_polygon_area, calculate_polygon_perimeter
# from drawing_helpers import get_distance_label
# from toolbar import setup_toolbar
# import math
# from Furniture import Furniture
# import os
# from PIL import ImageGrab


# class CanvasManager:
    
#     def __init__(self, root):
#         self.zoom_level = 1.0
#         self.zoom_step = 0.1  # Amount to zoom in/out per click
#         self.icon_font_size = 20  # default emoji size
#         self.emoji_map = {
#          "Bed": "🛏️",
#          "Chair": "🪑",
#          "Table": "🛋️",
#           "Door": "🚪",
#          "Toilet": "🚽",
#           "Shower": "🚿",
#           "Sink": "🧼",
#           "Dining": "🍽️",
#           "Stove": "🔥",
#           "Fridge": "🧊",
#           "Computer": "🖥️",
#            "TV": "📺",
#            "Storage": "📦",
#            "Window": "🪟"
#        }

#         self.root = root
#         self.root.title("Graph Paper Layout Tool")

#         self.canvas_width = CANVAS_WIDTH
#         self.canvas_height = CANVAS_HEIGHT
#         self.grid_spacing = GRID_SPACING
#         self.unit = DEFAULT_UNIT
#         self.unit_scale = UNIT_SCALE
#         self.line_color = DEFAULT_LINE_COLOR
#         self.line_style = DEFAULT_LINE_STYLE
#         self.group_id_counter = 0

#         self.drawing_enabled = False
#         self.polygon_mode = False
#         self.first_point = None
#         self.polygon_points = []
#         self.actions_stack = []
#         self.selected_furniture = None
#         self.furniture_items = {}

#         self.current_preview = None
#         self.current_line_label = None

#         self.unit_var = tk.StringVar(value=self.unit)
#         self.line_style_var = tk.StringVar(value=self.line_style)
#         self.furniture_var = tk.StringVar(value="Bed")

#         self.canvas = tk.Canvas(root, width=self.canvas_width, height=self.canvas_height, bg="white")
#         self.canvas.pack(side=tk.RIGHT, expand=True, fill=tk.BOTH)
#         self.canvas.bind("<MouseWheel>", self.mouse_zoom)  # Windows
#         # self.canvas.bind("<Button-4>", self.mouse_zoom)    # Linux scroll up
#         # self.canvas.bind("<Button-5>", self.mouse_zoom)    # Linux scroll dow

#         left_panel = tk.Frame(self.root)
#         left_panel.pack(side=tk.LEFT, fill=tk.Y, padx=5, pady=5)

#         setup_toolbar(self, left_panel)
#         self.canvas.bind("<Button-1>", self.handle_click)
#         self.canvas.bind("<Motion>", self.preview_drawing)
#         self.dragging_item = None
#         self.drag_start_pos = None

#         self.grid_visible = False
#         self.grid_lines = []  # To store line IDs
#     def zoom_in(self):
#      self._apply_zoom(1 + self.zoom_step)
#     def zoom_out(self):
#      self._apply_zoom(1 - self.zoom_step)
#     def _apply_zoom(self, scale_factor):
#      self.zoom_level *= scale_factor
#      self.canvas.scale("all", 0, 0, scale_factor, scale_factor)  # Scale from top-left corner
#      self._rescale_furniture_labels()
#      self._rescale_texts()    
#     def _rescale_texts(self):
#      for item in self.canvas.find_all():
#         if self.canvas.type(item) == "text":
#             # Reset text size to base font size, e.g. 8 or 10
#             self.canvas.itemconfig(item, font=("Arial", 10))
#     def mouse_zoom(self, event):
#     # Determine zoom direction
#      if event.delta > 0 or event.num == 4:
#         scale = 1.1
#      elif event.delta < 0 or event.num == 5:
#         scale = 0.9
#      else:
#         return
#      self.zoom_level *= scale

#       # Get the current mouse position on the canvas
#      mouse_x = self.canvas.canvasx(event.x)
#      mouse_y = self.canvas.canvasy(event.y)

#       #  Scale all canvas items from the mouse position
#      self.canvas.scale("all", mouse_x, mouse_y, scale, scale)

#      # Update all furniture and text sizes
#      self._rescale_furniture_labels()
#      self._rescale_texts()
#     def _rescale_furniture_labels(self):
#      for rect_id, (x, y, label_id) in self.furniture_items.items():
#         self.canvas.coords(label_id, x * self.zoom_level, y * self.zoom_level)
#         self.canvas.itemconfig(label_id, font=("Arial", max(6, int(self.icon_font_size * self.zoom_level))))
#     def draw_grid(self):
#      self.clear_grid()  # Clear existing grid before drawing new

#      for x in range(0, self.canvas_width, self.grid_spacing):
#         line = self.canvas.create_line(x, 0, x, self.canvas_height, fill="#eee")
#         self.grid_lines.append(line)
#      for y in range(0, self.canvas_height, self.grid_spacing):
#         line = self.canvas.create_line(0, y, self.canvas_width, y, fill="#eee")
#         self.grid_lines.append(line)
#      self.grid_visible = True
#     def clear_grid(self):
#      for line_id in self.grid_lines:
#         self.canvas.delete(line_id)
#      self.grid_lines.clear()
#      self.grid_visible = False
#     def toggle_grid(self):
#       if self.grid_visible:
#         self.clear_grid()
#       else:
#         self.draw_grid()

#     def change_unit(self, unit): self.unit = unit
#     def change_line_style(self, style): self.line_style = style
#     def pick_line_color(self):
#         color = colorchooser.askcolor()[1]
#         if color: self.line_color = color
#     def enable_eraser_mode(self):
#       self.reset_modes()
#       self.eraser_mode = True
#       self.canvas.config(cursor="dotbox")

#      # Bind both click and drag to the eraser handler
#       self.canvas.bind("<Button-1>", self.handle_eraser_click)
#       self.canvas.bind("<B1-Motion>", self.handle_eraser_click)

#     def handle_eraser_click(self, event):
#         x, y = event.x, event.y
#     # Find items under cursor (topmost last)
#         clicked_items = self.canvas.find_overlapping(x-5, y-5, x+5, y+5)
#         if clicked_items:
#             item_id = clicked_items[-1]
#             self.canvas.delete(item_id)
#             # Remove from actions_stack for undo support
#             self.actions_stack = [
#                 [i for i in group if i != item_id]
#                 for group in self.actions_stack
#             ]
#             self.actions_stack = [g for g in self.actions_stack if g]  # Remove empty groups

#         # Remove from furniture_items if present
#             if item_id in self.furniture_items:
#                 del self.furniture_items[item_id]
#     # Optionally, you can turn off eraser mode after one erase:
#     # self.reset_modes()
#     # self.canvas.config(cursor="")
#     def enable_line_drawing(self):
#         if self.drawing_enabled:
#             self.reset_modes()
#         else:
#             self.reset_modes()
#             self.drawing_enabled = True

#     def enable_polygon_mode(self):
#         if self.polygon_mode:
#             self.reset_modes()
#         else:
#             self.reset_modes()
#             self.polygon_mode = True
#             self.polygon_points = []

#     def enable_furniture_mode(self):
#         if self.selected_furniture == self.furniture_var.get():
#             self.reset_modes()
#         else:
#             self.reset_modes()
#             self.selected_furniture = self.furniture_var.get()

#     def reset_modes(self): 
#         self.drawing_enabled = False
#         self.polygon_mode = False
#         self.selected_furniture = None
#         self.first_point = None
#         self.eraser_mode = False  # ✅ reset eraser mode
#         self.canvas.config(cursor="")
#         # ✅ Unbind eraser-specific mouse events
#         self.canvas.unbind("<Button-1>")
#         self.canvas.unbind("<B1-Motion>")
    
#         # ✅ Rebind default handlers like click and preview
#         self.canvas.bind("<Button-1>", self.handle_click)
#         self.canvas.bind("<Motion>", self.preview_drawing)

#     def finish_polygon(self):
#         if len(self.polygon_points) < 3: return
#         flat = [coord for pt in self.polygon_points for coord in pt]
#         polygon_id = self.canvas.create_polygon(flat, outline="green", fill="", width=2)
#         area = calculate_polygon_area(self.polygon_points, self.unit)
#         perimeter = calculate_polygon_perimeter(self.polygon_points, self.unit)
#         cx = sum(x for x, _ in self.polygon_points) / len(self.polygon_points)
#         cy = sum(y for _, y in self.polygon_points) / len(self.polygon_points)
#         label = self.canvas.create_text(cx, cy, text=f"Area: {area:.2f} {self.unit}²\nPerimeter: {perimeter:.2f} {self.unit}", font=("Arial", 9))
#         self.actions_stack.append([polygon_id, label])
#         self.polygon_points = []

#     def clear_canvas(self): 
#         self.canvas.delete("all")
#         self.actions_stack.clear()
#         self.furniture_items.clear()
#         self.draw_grid()

#     def undo(self): 
#         if self.actions_stack:
#             for item in self.actions_stack.pop():
#                 self.canvas.delete(item)
#     def save_canvas(self):
#         filetypes = [
#             ("PostScript", "*.ps"),
#             ("PNG Image", "*.png"),
#             ("JPEG Image", "*.jpg"),
#             ("PDF Document", "*.pdf")
#             ]
        
#         path = filedialog.asksaveasfilename(
#             defaultextension=".ps",
#             filetypes=filetypes,
#             title="Save As"
#             )
        
#         if not path:
#             return

#         if path.lower().endswith('.ps'):
#             self.canvas.postscript(file=path, colormode='color')
            
#         elif path.lower().endswith(('.png', '.jpg', '.jpeg')):
#             # Capture visible canvas area using screenshot
#             x = self.root.winfo_rootx() + self.canvas.winfo_x()
#             y = self.root.winfo_rooty() + self.canvas.winfo_y()
#             x1 = x + self.canvas.winfo_width()
#             y1 = y + self.canvas.winfo_height()
            
#             ImageGrab.grab(bbox=(x, y, x1, y1)).save(path)
            
#         elif path.lower().endswith('.pdf'):
#             temp_ps = "temp.ps"
#             self.canvas.postscript(file=temp_ps, colormode='color')
        
#         try:
#             # Use system's ps2pdf command
#             import subprocess
#             subprocess.run([
#                 'gs',
#                 '-q',
#                 '-dNOPAUSE',
#                 '-dBATCH',
#                 '-sDEVICE=pdfwrite',
#                 f'-sOutputFile={path}',
#                 temp_ps
#             ], check=True)
#         except subprocess.CalledProcessError as e:
#             print(f"PDF conversion failed: {e}")
#         finally:
#             if os.path.exists(temp_ps):
#                 os.remove(temp_ps)
#     # def save_canvas(self):
#     #     path = filedialog.asksaveasfilename(defaultextension=".ps", filetypes=[("PostScript", "*.ps")])
#     #     if path: self.canvas.postscript(file=path)

#     def handle_click(self, event):
#         x, y = event.x, event.y

#         if self.drawing_enabled:
#             if not self.first_point:
#                 self.first_point = (x, y)
#                 # Create point at first click
#                 point = self.canvas.create_oval(x-3, y-3, x+3, y+3, fill="red")
#                 # Save just the point id to stack for undo
#                 self.actions_stack.append([point])
#             else:
#                 x0, y0 = self.first_point

#                 width = 4 if self.line_style == "bold" else 2
#                 dash = (4, 2) if self.line_style == "dashed" else None

#                 # Create line
#                 line = self.canvas.create_line(x0, y0, x, y, fill=self.line_color, width=width, dash=dash)
                
#                 # Create label with distance
#                 label_text, mid_x, mid_y = get_distance_label(x0, y0, x, y, self.unit, self.zoom_level)
#                 # label_text, mid_x, mid_y = get_distance_label(x0, y0, x, y, self.unit)
#                 # label = self.canvas.create_text(x, y, text=icon, font=("Arial", self.icon_font_size))

#                 label = self.canvas.create_text(mid_x, mid_y - 10, text=label_text, font=("Arial", 8))
                
#                 # Create second point at end of line
#                 point = self.canvas.create_oval(x-3, y-3, x+3, y+3, fill="red")
                
#                 # Store line + 2 points + label together in actions_stack as one undo unit
#                 self.actions_stack.append([line, label, point])

#                 self.first_point = None
#                 if self.current_preview: 
#                     self.canvas.delete(self.current_preview)
#                     self.current_preview = None
#                 if self.current_line_label: 
#                     self.canvas.delete(self.current_line_label)
#                     self.current_line_label = None
# #                 clicked_items = self.canvas.find_overlapping(x-5, y-5, x+5, y+5)
# #                 if clicked_items:
# #                     self.dragging_item = clicked_items[-1]
# #                     self.selected_icon = self.dragging_item
# #         elif self.polygon_mode:
# #             if self.polygon_points:
# #                 if math.dist((x, y), self.polygon_points[0]) < 10:
# #                     self.finish_polygon()
# #                     return
# #                 x0, y0 = self.polygon_points[-1]
# #                 line = self.canvas.create_line(x0, y0, x, y, fill="green", width=2)
# #                 self.actions_stack.append([line])
# #             self.polygon_points.append((x, y))
# #             point = self.canvas.create_oval(x-3, y-3, x+3, y+3, fill="green")
# #             self.actions_stack.append([point])

# #         elif self.selected_furniture:
# #             for item_id, info in self.furniture_items.items():
# #                 ix, iy, _ = info
# #                 if abs(ix - x) < 20 and abs(iy - y) < 20:
# #                     self.canvas.coords(item_id, x-15, y-15, x+15, y+15)
# #                     self.canvas.coords(info[2], x, y)
# #                     self.furniture_items[item_id] = (x, y, info[2])
# #                     return
# #             icon = self.emoji_map.get(self.selected_furniture, self.selected_furniture)
# #             label = self.canvas.create_text(x, y, text=icon, font=("Arial", 20))
# #             rect = self.canvas.create_rectangle(x-20, y-20, x+20, y+20, outline="gray", dash=(2, 2))
# #             # self.furniture_items[rect] = (x, y, label, self.icon_font_size)
# #             self.furniture_items[rect] = (x, y, label)
# #             self.actions_stack.append([rect, label])
        
# #         else:
# #             # Check if clicked near any canvas item to start dragging
# #             clicked_items = self.canvas.find_overlapping(x-5, y-5, x+5, y+5)
# #             if clicked_items:
# #                 # Pick the topmost item under cursor
# #                 self.dragging_item = clicked_items[-1]
# #                 self.drag_start_pos = (x, y)
# #                 # Bind mouse motion and release for dragging
# #                 self.canvas.bind("<B1-Motion>", self.handle_drag)
# #                 self.canvas.bind("<ButtonRelease-1>", self.handle_release)
# #             else:
# #                 self.dragging_item = None
# #     def preview_drawing(self, event):
# #         if self.drawing_enabled and self.first_point:
# #             x0, y0 = self.first_point
# #             x, y = event.x, event.y
# #             width = 4 if self.line_style == "bold" else 2
# #             dash = (4, 2) if self.line_style == "dashed" else None
# #             if self.current_preview: self.canvas.delete(self.current_preview)
# #             if self.current_line_label: self.canvas.delete(self.current_line_label)
# #             self.current_preview = self.canvas.create_line(x0, y0, x, y, fill=self.line_color, width=width, dash=dash)
# #             label_text, mid_x, mid_y = get_distance_label(x0, y0, x, y, self.unit, self.zoom_level)
# #             # label_text, mid_x, mid_y = get_distance_label(x0, y0, x, y, self.unit)
# #             self.current_line_label = self.canvas.create_text(mid_x, mid_y - 10, text=label_text, fill="gray", font=("Arial", 8))
    
# #     def handle_drag(self, event):
# #         if not self.dragging_item:
# #             return
# #         x, y = event.x, event.y
# #         dx = x - self.drag_start_pos[0]
# #         dy = y - self.drag_start_pos[1]
# #         self.canvas.move(self.dragging_item, dx, dy)

# #         # If dragging furniture, move the label as well
# #         if self.dragging_item in self.furniture_items:
# #             label_id = self.furniture_items[self.dragging_item][2]
# #             self.canvas.move(label_id, dx, dy)
# #             # ix, iy, label_id, font_size = self.furniture_items[self.dragging_item]
# #             ix, iy, _ = self.furniture_items[self.dragging_item]
# #             # self.furniture_items[self.dragging_item] = (ix + dx, iy + dy, label_id, font_size)
# #             self.furniture_items[self.dragging_item] = (ix + dx, iy + dy, label_id)

# #         self.drag_start_pos = (x, y)

# #     def handle_release(self, event):
# #         self.dragging_item = None
# #         self.drag_start_pos = None
# #         # Unbind the drag events to avoid conflicts
# #         self.canvas.unbind("<B1-Motion>")
# #         self.canvas.unbind("<ButtonRelease-1>")
# #     def zoom_in_furniture(self):
# #      self.icon_font_size += 2
# #      self.update_furniture_sizes()
# #     def zoom_out_furniture(self):
# #      if self.icon_font_size > 6:
# #         self.icon_font_size -= 2
# #         self.update_furniture_sizes()
# #     def update_furniture_sizes(self):
# #        for _, (x, y, label_id) in self.furniture_items.items():
# #         icon = self.canvas.itemcget(label_id, "text")
# #         self.canvas.itemconfig(label_id, font=("Arial", self.icon_font_size))
# #         self.canvas.coords(label_id, x, y)
# import tkinter as tk
# import math
# from tkinter import colorchooser, filedialog
# from config import *
# from geometry import calculate_polygon_area, calculate_polygon_perimeter
# from drawing_helpers import get_distance_label
# from toolbar import setup_toolbar
# import math
# from Furniture import Furniture
# import os
# from PIL import ImageGrab
# from tkinter import simpledialog

# class CanvasManager:
    
#     def __init__(self, root):
#         self.zoom_level = 1.0
#         self.zoom_step = 0.1  # Amount to zoom in/out per click
#         self.icon_font_size = 20  # default emoji size
#         self.emoji_map = {
#          "Bed": "🛏️",
#          "Chair": "🪑",
#          "Table": "🛋️",
#           "Door": "🚪",
#          "Toilet": "🚽",
#           "Shower": "🚿",
#           "Sink": "🧼",
#           "Dining": "🍽️",
#           "Stove": "🔥",
#           "Fridge": "🧊",
#           "Computer": "🖥️",
#            "TV": "📺",
#            "Storage": "📦",
#            "Window": "🪟"
#        }
#         self.unit_suffix = {
#             "meters": "m",
#            "feet": "ft",
#           "inches": "in",
#           "centimeters": "cm"
#                }
#         self.root = root
#         self.root.title("Graph Paper Layout Tool")

#         self.canvas_width = CANVAS_WIDTH
#         self.canvas_height = CANVAS_HEIGHT
#         self.grid_spacing = GRID_SPACING
#         self.unit = DEFAULT_UNIT
#         self.unit_scale = UNIT_SCALE
#         self.line_color = DEFAULT_LINE_COLOR
#         self.line_style = DEFAULT_LINE_STYLE
#         self.group_id_counter = 0

#         self.drawing_enabled = False
#         self.polygon_mode = False
#         self.first_point = None
#         self.polygon_points = []
#         self.actions_stack = []
#         self.selected_furniture = None
#         self.furniture_items = {}

#         self.current_preview = None
#         self.current_line_label = None

#         self.unit_var = tk.StringVar(value=self.unit)
#         self.line_style_var = tk.StringVar(value=self.line_style)
#         self.furniture_var = tk.StringVar(value="Bed")
#         self.text_insertion_mode = False


#         # self.canvas = tk.Canvas(root, width=self.canvas_width, height=self.canvas_height, bg="white")
#         # self.canvas.pack(side=tk.RIGHT, expand=True, fill=tk.BOTH)
#         # Scrollable canvas wrapper
#         canvas_frame = tk.Frame(root)
#         canvas_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

#         # Scrollbars
#         x_scroll = tk.Scrollbar(canvas_frame, orient=tk.HORIZONTAL)
#         y_scroll = tk.Scrollbar(canvas_frame, orient=tk.VERTICAL)

#             # Canvas with scrollbars
#         self.canvas = tk.Canvas(
#          canvas_frame,
#          width=self.canvas_width,
#          height=self.canvas_height,
#          bg="white",
#          xscrollcommand=x_scroll.set,
#          yscrollcommand=y_scroll.set,
#          scrollregion=(0, 0, self.canvas_width * 2, self.canvas_height * 2)  # Adjust as needed
#           )

#         x_scroll.config(command=self.canvas.xview)
#         y_scroll.config(command=self.canvas.yview)

#         x_scroll.pack(side=tk.BOTTOM, fill=tk.X)
#         y_scroll.pack(side=tk.RIGHT, fill=tk.Y)
#         self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

#         self.canvas.bind("<MouseWheel>", self.mouse_zoom)  # Windows
#         # self.canvas.bind("<Button-4>", self.mouse_zoom)    # Linux scroll up
#         # self.canvas.bind("<Button-5>", self.mouse_zoom)    # Linux scroll dow

#         left_panel = tk.Frame(self.root)
#         left_panel.pack(side=tk.LEFT, fill=tk.Y, padx=5, pady=5)

#         setup_toolbar(self, left_panel)
#         self.canvas.bind("<Button-1>", self.handle_click)
#         self.canvas.bind("<Motion>", self.preview_drawing)
#         self.dragging_item = None
#         self.drag_start_pos = None

#         self.grid_visible = False
#         self.grid_lines = []  # To store line IDs
        
#         self.rectangle_width = 0
#         self.rectangle_height = 0
            
#         self.line_by_angle_mode = False
#         self.click_callback = None
#         self.update_scrollregion()

        

#     def zoom_in(self):
#      self._apply_zoom(1 + self.zoom_step)
#     def zoom_out(self):
#      self._apply_zoom(1 - self.zoom_step)
#     def _apply_zoom(self, scale_factor):
#      self.zoom_level *= scale_factor
#      self.canvas.scale("all", 0, 0, scale_factor, scale_factor)  # Scale from top-left corner
#      self._rescale_furniture_labels()
#      self._rescale_texts()    
#      self.update_scrollregion()

#     def update_scrollregion(self):
#      bbox = self.canvas.bbox("all")
#      if bbox:
#         self.canvas.config(scrollregion=bbox)

#     def _rescale_texts(self):
#      for item in self.canvas.find_all():
#         if self.canvas.type(item) == "text":
#             # Reset text size to base font size, e.g. 8 or 10
#             self.canvas.itemconfig(item, font=("Arial", 10))
#     def mouse_zoom(self, event):
#     # Determine zoom direction
#      if event.delta > 0 or event.num == 4:
#         scale = 1.1
#      elif event.delta < 0 or event.num == 5:
#         scale = 0.9
#      else:
#         return
#      self.zoom_level *= scale

#       # Get the current mouse position on the canvas
#      mouse_x = self.canvas.canvasx(event.x)
#      mouse_y = self.canvas.canvasy(event.y)

#       #  Scale all canvas items from the mouse position
#      self.canvas.scale("all", mouse_x, mouse_y, scale, scale)

#      # Update all furniture and text sizes
#      self._rescale_furniture_labels()
#      self._rescale_texts()
#      self.update_scrollregion()

#     def _rescale_furniture_labels(self):
#      for rect_id, (x, y, label_id) in self.furniture_items.items():
#         self.canvas.coords(label_id, x * self.zoom_level, y * self.zoom_level)
#         self.canvas.itemconfig(label_id, font=("Arial", max(6, int(self.icon_font_size * self.zoom_level))))
#     # def draw_grid(self):
#     #  self.clear_grid()  # Clear existing grid before drawing new

#     #  for x in range(0, self.canvas_width, self.grid_spacing):
#     #     line = self.canvas.create_line(x, 0, x, self.canvas_height, fill="#eee")
#     #     self.grid_lines.append(line)
#     #  for y in range(0, self.canvas_height, self.grid_spacing):
#     #     line = self.canvas.create_line(0, y, self.canvas_width, y, fill="#eee")
#     #     self.grid_lines.append(line)
#     #  self.grid_visible = True
#     # def clear_grid(self):
#     #  for line_id in self.grid_lines:
#     #     self.canvas.delete(line_id)
#     #  self.grid_lines.clear()
#     #  self.grid_visible = False
#     # def toggle_grid(self):
#     #   if self.grid_visible:
#     #     self.clear_grid()
#     #   else:
#     #     self.draw_grid()

#     def change_unit(self, unit): self.unit = unit
#     def change_line_style(self, style): self.line_style = style
#     def pick_line_color(self):
#         color = colorchooser.askcolor()[1]
#         if color: self.line_color = color
#     def enable_eraser_mode(self):
#       self.reset_modes()
#       self.eraser_mode = True
#       self.canvas.config(cursor="dotbox")

#      # Bind both click and drag to the eraser handler
#       self.canvas.bind("<Button-1>", self.handle_eraser_click)
#       self.canvas.bind("<B1-Motion>", self.handle_eraser_click)

#     def handle_eraser_click(self, event):
#         x, y = event.x, event.y
#         # Find items under cursor (topmost last)
#         clicked_items = self.canvas.find_overlapping(x-5, y-5, x+5, y+5)
#         if clicked_items:
#             item_id = clicked_items[-1]

#             # Check if the item has the "grid" tag
#             if "grid" in self.canvas.gettags(item_id):
#                 return  # Don't delete grid items

#             self.canvas.delete(item_id)

#             # Remove from actions_stack for undo support
#             self.actions_stack = [
#                 [i for i in group if i != item_id]
#                 for group in self.actions_stack
#             ]
#             self.actions_stack = [g for g in self.actions_stack if g]  # Remove empty groups

#             # Remove from furniture_items if present
#             if item_id in self.furniture_items:
#                 del self.furniture_items[item_id]

#         # Optionally, you can turn off eraser mode after one erase:
#         # self.reset_modes()
#         # self.canvas.config(cursor="")
#     # def enable_line_drawing(self):
#     #     if self.drawing_enabled:
#     #         self.reset_modes()
#     #     else:
#     #         self.reset_modes()
#     #         self.drawing_enabled = True
#     def enable_line_drawing(self):
#      if self.drawing_enabled:
#         self.reset_modes()
#      else:
#         self.reset_modes()
#         self.drawing_enabled = True
#         self.canvas.config(cursor="pencil")  # You can try "crosshair" if "pencil" doesn't work


#     def enable_polygon_mode(self):
#         if self.polygon_mode:
#             self.reset_modes()
#         else:
#             self.reset_modes()
#             self.polygon_mode = True
#             self.polygon_points = []

#     def enable_furniture_mode(self):
#         if self.selected_furniture == self.furniture_var.get():
#             self.reset_modes()
#         else:
#             self.reset_modes()
#             self.selected_furniture = self.furniture_var.get()

#     def reset_modes(self): 
#         self.drawing_enabled = False
#         self.polygon_mode = False
#         self.selected_furniture = None
#         self.first_point = None
#         self.eraser_mode = False  # ✅ reset eraser mode
#         self.canvas.config(cursor="")
#         self.text_insertion_mode = False

#         # ✅ Unbind eraser-specific mouse events
#         self.canvas.unbind("<Button-1>")
#         self.canvas.unbind("<B1-Motion>")
    
#         # ✅ Rebind default handlers like click and preview
#         self.canvas.bind("<Button-1>", self.handle_click)
#         self.canvas.bind("<Motion>", self.preview_drawing)

#     def finish_polygon(self):
#         if len(self.polygon_points) < 3: return
#         flat = [coord for pt in self.polygon_points for coord in pt]
#         polygon_id = self.canvas.create_polygon(flat, outline="green", fill="", width=2)
#         area = calculate_polygon_area(self.polygon_points, self.unit)
#         perimeter = calculate_polygon_perimeter(self.polygon_points, self.unit)
#         cx = sum(x for x, _ in self.polygon_points) / len(self.polygon_points)
#         cy = sum(y for _, y in self.polygon_points) / len(self.polygon_points)
#         label = self.canvas.create_text(cx, cy, text=f"Area: {area:.2f} {self.unit}²\nPerimeter: {perimeter:.2f} {self.unit}", font=("Arial", 9))
#         self.actions_stack.append([polygon_id, label])
#         self.polygon_points = []

#     def clear_canvas(self): 
#         self.canvas.delete("all")
#         self.actions_stack.clear()
#         self.furniture_items.clear()
#         self.draw_grid()

#     def undo(self): 
#         if self.actions_stack:
#             for item in self.actions_stack.pop():
#                 self.canvas.delete(item)
#     def save_canvas(self):
#         filetypes = [
#             ("PostScript", "*.ps"),
#             ("PNG Image", "*.png"),
#             ("JPEG Image", "*.jpg"),
#             ("PDF Document", "*.pdf")
#             ]
        
#         path = filedialog.asksaveasfilename(
#             defaultextension=".ps",
#             filetypes=filetypes,
#             title="Save As"
#             )
        
#         if not path:
#             return

#         if path.lower().endswith('.ps'):
#             self.canvas.postscript(file=path, colormode='color')
            
#         elif path.lower().endswith(('.png', '.jpg', '.jpeg')):
#             # Capture visible canvas area using screenshot
#             x = self.root.winfo_rootx() + self.canvas.winfo_x()
#             y = self.root.winfo_rooty() + self.canvas.winfo_y()
#             x1 = x + self.canvas.winfo_width()
#             y1 = y + self.canvas.winfo_height()
            
#             ImageGrab.grab(bbox=(x, y, x1, y1)).save(path)
            
#         elif path.lower().endswith('.pdf'):
#             temp_ps = "temp.ps"
#             self.canvas.postscript(file=temp_ps, colormode='color')
        
#         try:
#             # Use system's ps2pdf command
#             import subprocess
#             subprocess.run([
#                 'gs',
#                 '-q',
#                 '-dNOPAUSE',
#                 '-dBATCH',
#                 '-sDEVICE=pdfwrite',
#                 f'-sOutputFile={path}',
#                 temp_ps
#             ], check=True)
#         except subprocess.CalledProcessError as e:
#             print(f"PDF conversion failed: {e}")
#         finally:
#             if os.path.exists(temp_ps):
#                 os.remove(temp_ps)
#     # def save_canvas(self):
#     #     path = filedialog.asksaveasfilename(defaultextension=".ps", filetypes=[("PostScript", "*.ps")])
#     #     if path: self.canvas.postscript(file=path)

#     def handle_click(self, event):
#         x, y = event.x, event.y

#         if self.drawing_enabled:
#             if not self.first_point:
#                 self.first_point = (x, y)
#                 # Create point at first click
#                 point = self.canvas.create_oval(x-0.5, y-0.5, x+0.5, y+0.5, fill="black")
#                 # Save just the point id to stack for undo
#                 self.actions_stack.append([point])
#             else:
#                 x0, y0 = self.first_point

#                 width = 4 if self.line_style == "bold" else 2
#                 dash = (4, 2) if self.line_style == "dashed" else None

#                 # Create line
#                 line = self.canvas.create_line(x0, y0, x, y, fill=self.line_color, width=width, dash=dash)
                
#                 # Create label with distance
#                 # label_text, mid_x, mid_y = get_distance_label(x0, y0, x, y, self.unit, self.zoom_level)
#                 label_text, mid_x, mid_y = get_distance_label(x0, y0, x, y, self.unit, self.zoom_level)
#                 suffix = self.unit_suffix.get(self.unit, self.unit)
#                 label_text = f"{label_text} {suffix}"

#                 # # label_text, mid_x, mid_y = get_distance_label(x0, y0, x, y, self.unit)
#                 # # label = self.canvas.create_text(x, y, text=icon, font=("Arial", self.icon_font_size))

#                 label = self.canvas.create_text(mid_x, mid_y - 10, text=label_text, font=("Arial", 8))
#                 # label_text, mid_x, mid_y, angle_deg = get_distance_label(x0, y0, x, y, self.unit, self.zoom_level)

#                 #   # Directional hint based on angle
#                 # if -45 <= angle_deg <= 45:
#                 #        arrow = "→"
#                 # elif 45 < angle_deg <= 135:
#                 #        arrow = "↓"
#                 # elif angle_deg > 135 or angle_deg < -135:
#                 #        arrow = "←"
#                 # else:
#                 #      arrow = "↑"

#                 # text = f"{arrow} {label_text}"
#                 # label = self.canvas.create_text(mid_x, mid_y, text=text, font=("Arial", 8))

                
#                 # Create second point at end of line
#                 point = self.canvas.create_oval(x-0.5, y-0.5, x+0.5, y+0.5, fill="black")
                
#                 # Store line + 2 points + label together in actions_stack as one undo unit
#                 self.actions_stack.append([line, label, point])

#                 self.first_point = None
#                 if self.current_preview: 
#                     self.canvas.delete(self.current_preview)
#                     self.current_preview = None
#                 if self.current_line_label: 
#                     self.canvas.delete(self.current_line_label)
#                     self.current_line_label = None
#                 clicked_items = self.canvas.find_overlapping(x-5, y-5, x+5, y+5)
#                 if clicked_items:
#                     self.dragging_item = clicked_items[-1]
#                     self.selected_icon = self.dragging_item
#         elif self.polygon_mode:
#             if self.polygon_points:
#                 if math.dist((x, y), self.polygon_points[0]) < 10:
#                     self.finish_polygon()
#                     return
#                 x0, y0 = self.polygon_points[-1]
#                 line = self.canvas.create_line(x0, y0, x, y, fill="green", width=2)
#                 self.actions_stack.append([line])
#             self.polygon_points.append((x, y))
#             point = self.canvas.create_oval(x-3, y-3, x+3, y+3, fill="green")
#             self.actions_stack.append([point])

#         elif self.selected_furniture:
#             for item_id, info in self.furniture_items.items():
#                 ix, iy, _ = info
#                 if abs(ix - x) < 20 and abs(iy - y) < 20:
#                     self.canvas.coords(item_id, x-15, y-15, x+15, y+15)
#                     self.canvas.coords(info[2], x, y)
#                     self.furniture_items[item_id] = (x, y, info[2])
#                     return
#             icon = self.emoji_map.get(self.selected_furniture, self.selected_furniture)
#             label = self.canvas.create_text(x, y, text=icon, font=("Arial", 20))
#             rect = self.canvas.create_rectangle(x-20, y-20, x+20, y+20, outline="gray", dash=(2, 2))
#             # self.furniture_items[rect] = (x, y, label, self.icon_font_size)
#             self.furniture_items[rect] = (x, y, label)
#             self.actions_stack.append([rect, label])
#         elif self.text_insertion_mode:
#           user_text = simpledialog.askstring("Insert Text", "Enter text:")
#           if user_text:
#              text_id = self.canvas.create_text(x, y, text=user_text, font=("Arial", 12), fill="black")
#              self.actions_stack.append([text_id])

            
#         elif self.click_callback:
#             self.click_callback(event.x, event.y)
#         else:
#             # Check if clicked near any canvas item to start dragging
#             clicked_items = self.canvas.find_overlapping(x-5, y-5, x+5, y+5)
#             if clicked_items:
#                 # Pick the topmost item under cursor
#                 self.dragging_item = clicked_items[-1]
#                 self.drag_start_pos = (x, y)
#                 # Bind mouse motion and release for dragging
#                 self.canvas.bind("<B1-Motion>", self.handle_drag)
#                 self.canvas.bind("<ButtonRelease-1>", self.handle_release)
#             else:
#                 self.dragging_item = None
#     def finish_line_with_distance(self, event):
#         try:
#             dist = float(self.temp_entry.get())
#         except:
#             self.temp_entry.destroy()
#             self.temp_entry = None
#             return

#         dx, dy = self.temp_direction
#         x0, y0 = self.temp_origin
#         x1 = x0 + dx * (dist / self.unit_scale[self.unit]) * self.grid_spacing
#         y1 = y0 + dy * (dist / self.unit_scale[self.unit]) * self.grid_spacing

#         width = 4 if self.line_style == "bold" else 2
#         dash = (4, 2) if self.line_style == "dashed" else None

#         line = self.canvas.create_line(x0, y0, x1, y1, fill=self.line_color, width=width, dash=dash)
#         label_text, mid_x, mid_y = get_distance_label(x0, y0, x1, y1, self.unit)
#         label = self.canvas.create_text(mid_x, mid_y - 10, text=label_text, font=("Arial", 8))
#         point = self.canvas.create_oval(x1-3, y1-3, x1+3, y1+3, fill="red")

#         self.actions_stack.append([line, label, point])

#         # Clean up
#         self.first_point = None
#         if self.current_preview:
#             self.canvas.delete(self.current_preview)
#             self.current_preview = None
#         if self.current_line_label:
#             self.canvas.delete(self.current_line_label)
#             self.current_line_label = None
#         self.temp_entry.destroy()
#         self.temp_entry = None   
#     def preview_drawing(self, event):
#         if self.drawing_enabled and self.first_point:
#             x0, y0 = self.first_point
#             x, y = event.x, event.y
#             width = 4 if self.line_style == "bold" else 2
#             dash = (4, 2) if self.line_style == "dashed" else None
#             if self.current_preview: self.canvas.delete(self.current_preview)
#             if self.current_line_label: self.canvas.delete(self.current_line_label)
#             self.current_preview = self.canvas.create_line(x0, y0, x, y, fill=self.line_color, width=width, dash=dash)
#             # label_text, mid_x, mid_y = get_distance_label(x0, y0, x, y, self.unit, self.zoom_level)
#             label_text, mid_x, mid_y = get_distance_label(x0, y0, x, y, self.unit, self.zoom_level)
#             suffix = self.unit_suffix.get(self.unit, self.unit)
#             label_text = f"{label_text} {suffix}"

#             # label_text, mid_x, mid_y = get_distance_label(x0, y0, x, y, self.unit)
#             self.current_line_label = self.canvas.create_text(mid_x, mid_y - 10, text=label_text, fill="gray", font=("Arial", 8))
    
#     def handle_drag(self, event):
#         if not self.dragging_item:
#             return
#         x, y = event.x, event.y
#         dx = x - self.drag_start_pos[0]
#         dy = y - self.drag_start_pos[1]
#         self.canvas.move(self.dragging_item, dx, dy)

#         # If dragging furniture, move the label as well
#         if self.dragging_item in self.furniture_items:
#             label_id = self.furniture_items[self.dragging_item][2]
#             self.canvas.move(label_id, dx, dy)
#             # ix, iy, label_id, font_size = self.furniture_items[self.dragging_item]
#             ix, iy, _ = self.furniture_items[self.dragging_item]
#             # self.furniture_items[self.dragging_item] = (ix + dx, iy + dy, label_id, font_size)
#             self.furniture_items[self.dragging_item] = (ix + dx, iy + dy, label_id)

#         self.drag_start_pos = (x, y)

#     def handle_release(self, event):
#         self.dragging_item = None
#         self.drag_start_pos = None
#         # Unbind the drag events to avoid conflicts
#         self.canvas.unbind("<B1-Motion>")
#         self.canvas.unbind("<ButtonRelease-1>")
#     def zoom_in_furniture(self):
#      self.icon_font_size += 2
#      self.update_furniture_sizes()
#     def zoom_out_furniture(self):
#      if self.icon_font_size > 6:
#         self.icon_font_size -= 2
#         self.update_furniture_sizes()
#     def update_furniture_sizes(self):
#        for _, (x, y, label_id) in self.furniture_items.items():
#         icon = self.canvas.itemcget(label_id, "text")
#         self.canvas.itemconfig(label_id, font=("Arial", self.icon_font_size))
#         self.canvas.coords(label_id, x, y)

#     def draw_rectangle(self, width, height, with_grid=True):
#      self.rectangle_width = width * GRID_SPACING * self.unit_scale[self.unit]
#      self.rectangle_height = height * GRID_SPACING * self.unit_scale[self.unit]

#      x0, y0 = 50, 50
#      x1, y1 = x0 + self.rectangle_width, y0 + self.rectangle_height

#       # Store IDs to delete later
#      self.rectangle_grid_items = []

#       # Draw rectangle border
#      rect_id = self.canvas.create_rectangle(x0, y0, x1, y1, outline="blue", tags="grid")
#      self.rectangle_grid_items.append(rect_id)

#      if with_grid:
#         for x in range(int(x0), int(x1) + 1, int(GRID_SPACING * self.unit_scale[self.unit])):
#             line = self.canvas.create_line(x, y0, x, y1, fill="#aaa", dash=(2, 2), tags="grid")
#             self.rectangle_grid_items.append(line)
#             label = self.canvas.create_text(x, y0 - 10, text=f"{(x - x0) // int(GRID_SPACING * self.unit_scale[self.unit])}", fill="gray", font=("Arial", 8), tags="grid")
#             self.rectangle_grid_items.append(label)

#         for y in range(int(y0), int(y1) + 1, int(GRID_SPACING * self.unit_scale[self.unit])):
#             line = self.canvas.create_line(x0, y, x1, y, fill="#aaa", dash=(2, 2), tags="grid")
#             self.rectangle_grid_items.append(line)
#             label = self.canvas.create_text(x0 - 15, y, text=f"{(y - y0) // int(GRID_SPACING * self.unit_scale[self.unit])}", fill="gray", font=("Arial", 8), tags="grid")
#             self.rectangle_grid_items.append(label)

#      self.grid_visible = with_grid

#     def toggle_rectangle_grid(self):
#      if self.grid_visible:
#         for item_id in getattr(self, "rectangle_grid_items", []):
#             self.canvas.delete(item_id)
#         self.rectangle_grid_items = []
#         self.grid_visible = False
#      else:
#         width_units = int(self.rectangle_width / (GRID_SPACING * self.unit_scale[self.unit]))
#         height_units = int(self.rectangle_height / (GRID_SPACING * self.unit_scale[self.unit]))
#         self.draw_rectangle(width_units, height_units, with_grid=True)

#     def activate_line_by_angle_mode(self):
#         self.line_by_angle_mode = True
#         self.set_click_callback(self.handle_line_start_point)

#     def handle_line_start_point(self, x, y):
#         if self.line_by_angle_mode:
#             # Ask for length and angle
#             length = simpledialog.askfloat("Length", "Enter line length:")
#             angle = simpledialog.askfloat("Angle", "Enter angle (in degrees):")

#             if length is not None and angle is not None:
#                 self.draw_line_from_point(x, y, length, angle)

#             self.line_by_angle_mode = False  # Turn off mode
        
#     def set_click_callback(self, callback):
#         self.click_callback = callback
    
#     def draw_line_from_point(self, x0, y0, length, angle):
#         theta = math.radians(angle)
#         x1 = x0 + length * math.cos(theta)*GRID_SPACING * self.unit_scale[self.unit]
#         y1 = y0 - length * math.sin(theta)*GRID_SPACING * self.unit_scale[self.unit]  # Y-axis inverted in canvas
#         width = 4 if self.line_style == "bold" else 2
#         dash = (4, 2) if self.line_style == "dashed" else None
#         line =self.canvas.create_line(x0, y0, x1, y1, fill=self.line_color, width=width, dash=dash)
#         self.actions_stack.append([line])
#     def enable_text_insertion(self):
#            self.reset_modes()
#            self.text_insertion_mode = True
#            self.canvas.config(cursor="xterm")

