import tkinter as tk
from tkinter import simpledialog, colorchooser
import math
import os
from PIL import Image, ImageTk
from Furniture import Furniture, find_image_path
from drawing_helpers import get_distance_label
from geometry import calculate_polygon_area, calculate_polygon_perimeter
import json
from tkinter import messagebox

class CanvasTools:
    def __init__(self, root, model, view, actions):
        self.root = root
        self.model = model
        self.view = view
        self.canvas = view.canvas
        self.actions = actions
        self.first_point = None
        self.current_line_label = None
        self.current_preview = None
        self.polygon_points = []
        self.current_preview = None
        self.fill_color = "#cccccc"
        self.temp_entry = None
        self.unit_scale = model.unit_scale
        self.freeform_points = []
        self.image_furniture_items = []
        self.selected_furniture_obj = None
        self.flooring_enabled = False
        self.flooring_image_path = ""
        self.flooring_type_var = tk.StringVar(value="wood")
        self.room_flooring_images = {}
        self.paste_ready = False
        self.group_id_counter = 1
        self.coord_label = None
        self.canvas_frozen = False
        self.copied_item_data = None
        self.group_id_counter = 1000  # for generating new room group tags


    # === Line Drawing ===
    def start_line(self, event):
        x, y = event.x, event.y

        if not self.first_point:
            self.first_point = (x, y)

            # Create small black point
            point_id = self.canvas.create_oval(x - 0.5, y - 0.5, x + 0.5, y + 0.5, fill="black")
            self.actions.log({"type": "create", "items": [point_id]})
        else:
            x0, y0 = self.first_point
            x1, y1 = x, y
            dx = x1 - x0
            dy = y1 - y0
            mouse_length = math.hypot(dx, dy)

            if mouse_length > 0:
                self.temp_direction = (dx / mouse_length, dy / mouse_length)
                self.temp_origin = (x0, y0)

                if self.temp_entry:
                    self.temp_entry.destroy()

                # Distance entry box
                self.temp_entry = tk.Entry(self.root)
                self.temp_entry.place(x=event.x_root - 30, y=event.y_root - 10, width=60)
                self.temp_entry.focus()
                self.temp_entry.bind("<Return>", self.finish_line_with_distance)

                # Freeform closed-shape support
                self.freeform_points.append((x0, y0))
                self.freeform_points.append((x1, y1))

                if (
                    len(self.freeform_points) >= 3 and
                    math.dist(self.freeform_points[0], self.freeform_points[-1]) < 10
                ):
                    # Build closed polygon
                    polygon_points = [self.freeform_points[0]]
                    for pt in self.freeform_points[1:]:
                        if math.dist(pt, polygon_points[-1]) > 1:
                            polygon_points.append(pt)

                    flat = [coord for pt in polygon_points for coord in pt]
                    polygon_id = self.canvas.create_polygon(flat,
                                                            outline=self.model.line_color,
                                                            fill=self.model.fill_color,
                                                            width=2,
                                                            tags=("closed_shape",))
                    self.actions.log({"type": "create", "items": [polygon_id]})
                    self.freeform_points.clear()
                    self.model.fill_color = ""

            self.first_point = None

            if self.current_preview:
                self.canvas.delete(self.current_preview)
                self.current_preview = None

            if self.current_line_label:
                self.canvas.delete(self.current_line_label)
                self.current_line_label = None
    
    def finish_line_with_distance(self, event):
        try:
            dist = float(self.temp_entry.get())
        except:
            self.temp_entry.destroy()
            self.temp_entry = None
            self.first_point = None
            return

        dx, dy = self.temp_direction
        x0, y0 = self.temp_origin

        unit_scale = self.model.unit_scale[self.model.unit]
        pixel_length = (dist / unit_scale) * self.model.grid_spacing * self.model.zoom_level
        x1 = x0 + dx * pixel_length
        y1 = y0 + dy * pixel_length

        width = 4 if self.model.line_style == "bold" else 2
        dash = (4, 2) if self.model.line_style == "dashed" else None

        line = self.canvas.create_line(x0, y0, x1, y1,
                                    fill=self.model.line_color,
                                    width=width,
                                    dash=dash)
        # Label and point
        label_text, mid_x, mid_y = get_distance_label(x0, y0, x1, y1, self.model.unit, self.model.zoom_level)
        label = self.canvas.create_text(mid_x, mid_y - 10, text=label_text, font=("Arial", 8))
        point = self.canvas.create_oval(x1 - 0.5, y1 - 0.5, x1 + 0.5, y1 + 0.5, fill="black")

        self.actions.log({
            "type": "create",
            "items": [line, label, point]
        })

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

    # === Polygon Drawing ===
    def add_polygon_point(self, event):
        x, y = event.x, event.y

        if self.polygon_points:
            # Close polygon if near first point
            if math.dist((x, y), self.polygon_points[0]) < 10:
                self.finish_polygon()
                return

            # Draw line from last point to current
            x0, y0 = self.polygon_points[-1]
            line = self.canvas.create_line(x0, y0, x, y, fill="green", width=2)
            self.actions.log({"type": "create", "items": [line]})

        # Add point
        self.polygon_points.append((x, y))
        point = self.canvas.create_oval(x - 0.5, y - 0.5, x + 0.5, y + 0.5, fill="green")
        self.actions.log({"type": "create", "items": [point]})

    def _close_to_first(self, event):
        x0, y0 = self.polygon_points[0]
        return abs(event.x - x0) < 10 and abs(event.y - y0) < 10

    def finish_polygon(self):
        if len(self.polygon_points) < 3:
            return

        flat = [coord for pt in self.polygon_points for coord in pt]

        # Draw polygon
        polygon_id = self.canvas.create_polygon(flat,
                                                outline="green",
                                                fill="",
                                                width=2,
                                                tags=("closed_shape",))

        # Area + perimeter (in model.unit)
        area = calculate_polygon_area(self.polygon_points, self.model.unit)
        perimeter = calculate_polygon_perimeter(self.polygon_points, self.model.unit)

        # Center for label
        cx = sum(x for x, _ in self.polygon_points) / len(self.polygon_points)
        cy = sum(y for _, y in self.polygon_points) / len(self.polygon_points)

        label_text = f"Area: {area:.2f} {self.model.unit}²\nPerimeter: {perimeter:.2f} {self.model.unit}"
        label_id = self.canvas.create_text(cx, cy, text=label_text, font=("Arial", 9))

        # Log to undo
        self.actions.log({"type": "create", "items": [polygon_id, label_id]})

        # Reset
        self.polygon_points = []
        self.first_point = None

        if self.current_preview:
            self.canvas.delete(self.current_preview)
            self.current_preview = None

    def _preview_polygon(self):
        if self.current_preview:
            self.canvas.delete(self.current_preview)
        if len(self.polygon_points) >= 2:
            coords = [coord for pt in self.polygon_points for coord in pt]
            self.current_preview = self.canvas.create_line(coords, fill="gray", dash=(4, 2))
                  
#eraser mode
    def enable_eraser_mode(self):
        self.reset_modes()
        self.model.set("eraser_mode", True)
        self.view.canvas.config(cursor="dotbox")

    def handle_eraser_click(self, event):
        x, y = event.x, event.y
        clicked_items = self.canvas.find_overlapping(x - 5, y - 5, x + 5, y + 5)

        for item_id in reversed(clicked_items):
            tags = self.canvas.gettags(item_id)

            if "grid" in tags:
                continue  # ✅ Skip grid lines

            item_type = self.canvas.type(item_id)
            coords = self.canvas.coords(item_id)
            options = {}

            if item_type in ("line", "oval", "rectangle", "polygon"):
                options["fill"] = self.canvas.itemcget(item_id, "fill")
                options["outline"] = self.canvas.itemcget(item_id, "outline")
                options["width"] = self.canvas.itemcget(item_id, "width")
            elif item_type == "text":
                options["text"] = self.canvas.itemcget(item_id, "text")
                options["fill"] = self.canvas.itemcget(item_id, "fill")
            elif item_type == "image":
                options["image"] = "placeholder"

            # ✅ If it's part of a room group — delete all items in the group
            group_tag = next((tag for tag in tags if tag.startswith("room_group_")), None)
            if group_tag:
                group_items = self.canvas.find_withtag(group_tag)
                for gitem in group_items:
                    self.canvas.delete(gitem)
                self.actions.log({
                    "type": "delete_group",
                    "group": group_tag,
                    "items": list(group_items),
                })
            else:
                self.canvas.delete(item_id)
                self.actions.log({
                    "type": "delete",
                    "item_type": item_type,
                    "coords": coords,
                    "options": options,
                })

                # ✅ Clean up furniture tracking if applicable
                if hasattr(self, "image_furniture_items"):
                    self.image_furniture_items = [
                        f for f in self.image_furniture_items if f.image_id != item_id
                    ]

            break  # ✅ Only delete one thing per click
    # === Fill Tool ===
    def fill_shape(self, event):
        overlapping = self.canvas.find_overlapping(event.x - 1, event.y - 1, event.x + 1, event.y + 1)
        for item_id in reversed(overlapping):
            item_type = self.canvas.type(item_id)
            if item_type in ["polygon", "rectangle", "oval"]:
                self.canvas.itemconfig(item_id, fill=self.fill_color)
                self.actions.log({"type": "fill", "item": item_id, "color": self.fill_color})
                break

    # === Text Insertion ===
    def insert_text(self, event):
        text = simpledialog.askstring("Insert Text", "Enter your text:")
        if text:
            x, y = event.x, event.y
            text_id = self.canvas.create_text(x, y, text=text, anchor="nw", font=("Arial", 11))
            self.actions.log({"type": "create", "items": [text_id]})

    # === Color Pickers ===
    def pick_line_color(self):
        color = colorchooser.askcolor()[1]
        if color:
            self.model.line_color = color

    def pick_fill_color(self):
        color = colorchooser.askcolor()[1]
        if color:
            self.fill_color = color

            # === Reset All Drawing Modes ===
    def reset_modes(self):
        # Reset internal flags
        self.drawing_line_mode = False
        self.polygon_mode = False
        self.eraser_mode = False
        self.furniture_mode = False
        self.flooring_enabled = False
        self.paste_ready = False
        self.selected_item = None
        self.selected_image_item = None
        self.freeform_points = []
        self.first_point = None
        self.canvas.config(cursor="arrow")

        # Reset model-level tool modes
        self.model.set("drawing_enabled", False)
        self.model.set("polygon_mode", False)
        self.model.set("fill_mode_enabled", False)
        self.model.set("text_insertion_mode", False)
        self.model.set("furniture_mode", False)
        self.model.set("eraser_mode", False)


#=== Furniture Placement ===
    def select_furniture_item(self, name):
        self.reset_modes()
        self.model.set("furniture_mode", True)
        self.selected_furniture = name
        self.canvas.config(cursor="hand2")

    def place_furniture(self, event):
        from Furniture import Furniture, find_image_path

        name = self.selected_furniture
        if not name:
            return

        path = find_image_path(name)
        if not path:
            return

        furniture_item = Furniture(
            canvas=self.canvas,
            image_path=path,
            x=event.x,
            y=event.y,
            select_callback=self.select_image_item,
            scale=0.25,
            angle=0,
            get_freeze_state=lambda: self.canvas_frozen
        )

        self.image_furniture_items.append(furniture_item)
        self.select_image_item(furniture_item)

        self.canvas.itemconfig(furniture_item.image_id, tags=("furniture",))

        self.selected_furniture = None
        self.model.set("furniture_mode", False)
        self.canvas.config(cursor="arrow")

    def select_image_item(self, furniture_item):
        if self.selected_furniture_obj and self.selected_furniture_obj != furniture_item:
            self.selected_furniture_obj.delete_handles()

        self.selected_furniture_obj = furniture_item
        furniture_item.draw_handles()
        
    def delete_selected_furniture(self):
        if self.selected_furniture_obj:
            self.selected_furniture_obj.delete()
            self.image_furniture_items.remove(self.selected_furniture_obj)
            self.selected_furniture_obj = None
        
        #=== Room formation===#
    def insert_room_template(self, name, width, height):
        from entities import RoomEntity
        group_id = getattr(self.model, "room_counter", 0)
        setattr(self.model, "room_counter", group_id + 1)

        room = RoomEntity(self.canvas, self.model, name, width, height, group_id)
        self.actions.log({"type": "create", "items": room.items})
        
    def enable_flooring_mode(self):
        import os
        self.paste_ready = False
        self.reset_modes()
        self.flooring_enabled = True

        selected_type = self.flooring_type_var.get()
        base_dir = os.path.dirname(os.path.abspath(__file__))
        for ext in ('png', 'jpeg', 'jpg'):
            path = os.path.join(base_dir, "Images", f"{selected_type}.{ext}")
            
            self.flooring_image_path=path
        # if selected_type == "wood":
        #     self.flooring_image_path = "E:\\VAS Intern\\Anvicodebroken\\June11\\Image\\wood.jpg"
        # elif selected_type == "tile":
        #     self.flooring_image_path = "E:\\VAS Intern\\Anvicodebroken\\June11\\Image\\tile.jpg"
        # elif selected_type == "marble":
        #     self.flooring_image_path = "E:\\VAS Intern\\Anvicodebroken\\June11\\Image\\marble.jpeg"
        # elif selected_type == "garden":
        #     self.flooring_image_path = "E:\\VAS Intern\\Anvicodebroken\\June11\\Image\\garden.jpeg"
        # else:
        #     self.flooring_image_path = "E:\\VAS Intern\\Anvicodebroken\\June11\\Image\\wood.jpg"

        # if not os.path.exists(self.flooring_image_path):
        #     self.flooring_image_path ="E:\\VAS Intern\\Anvicodebroken\\June11\\Image\\wood.jpg"

        self.canvas.config(cursor="crosshair")
        
    def apply_flooring_to_room(self, event):
        from tkinter import messagebox
        from PIL import Image, ImageTk

        x, y = event.x, event.y
        overlapping = self.canvas.find_overlapping(x-1, y-1, x+1, y+1)

        for item_id in reversed(overlapping):
            tags = self.canvas.gettags(item_id)
            if "room" in tags:
                coords = self.canvas.coords(item_id)
                x0, y0, x1, y1 = map(int, coords)

                group_tag = next((tag for tag in tags if tag.startswith("room_group_")), None)

                if not os.path.exists(self.flooring_image_path):
                    messagebox.showerror("Missing Image", f"Could not find {self.flooring_image_path}")
                    return

                if item_id in self.room_flooring_images:
                    old_data = self.room_flooring_images[item_id]
                    self.canvas.delete(old_data['image_id'])
                    self.canvas.delete(old_data['border_id'])

                img = Image.open(self.flooring_image_path)
                img = img.resize((abs(x1 - x0), abs(y1 - y0)), Image.Resampling.LANCZOS)
                tk_img = ImageTk.PhotoImage(img, master=self.canvas)

                image_id = self.canvas.create_image(
                    x0, y0,
                    image=tk_img,
                    anchor="nw",
                    tags=("flooring", group_tag) if group_tag else ("flooring",)
                )
                border_id = self.canvas.create_rectangle(
                    x0, y0, x1, y1,
                    outline="black",
                    width=2,
                    tags=("flooring_border", group_tag) if group_tag else ("flooring_border",)
                )

                # Z-order
                self.canvas.tag_raise(border_id, image_id)
                if group_tag:
                    group_items = self.canvas.find_withtag(group_tag)
                    for item in group_items:
                        if self.canvas.type(item) == "text":
                            self.canvas.tag_raise(item, image_id)
                            self.canvas.tag_raise(item, border_id)

                self.room_flooring_images[item_id] = {
                    'image_id': image_id,
                    'tk_img': tk_img,
                    'border_id': border_id,
                    'image_path': self.flooring_image_path
                }
                break

        self.flooring_enabled = False
        self.canvas.config(cursor="arrow")

    def _rescale_flooring_images(self):
        from PIL import Image, ImageTk

        for room_id, flooring_data in self.room_flooring_images.items():
            current_coords = self.canvas.coords(flooring_data['border_id'])
            x0, y0, x1, y1 = current_coords
            new_width = int(abs(x1 - x0))
            new_height = int(abs(y1 - y0))

            img = Image.open(flooring_data['image_path'])
            img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
            new_tk_img = ImageTk.PhotoImage(img, master=self.canvas)

            old_tags = self.canvas.gettags(flooring_data['image_id'])
            group_tag = next((tag for tag in old_tags if tag.startswith("room_group_")), None)

            self.canvas.delete(flooring_data['image_id'])
            new_image_id = self.canvas.create_image(
                x0, y0,
                image=new_tk_img,
                anchor="nw",
                tags=("flooring", group_tag) if group_tag else ("flooring",)
            )

            flooring_data['image_id'] = new_image_id
            flooring_data['tk_img'] = new_tk_img

            self.canvas.tag_raise(flooring_data['border_id'], new_image_id)

            if group_tag:
                group_items = self.canvas.find_withtag(group_tag)
                for item in group_items:
                    if self.canvas.type(item) == "text":
                        self.canvas.tag_raise(item, new_image_id)
                        self.canvas.tag_raise(item, flooring_data['border_id'])
                for furniture_item in self.image_furniture_items:
                    if hasattr(furniture_item, 'image_id'):
                        self.canvas.tag_raise(furniture_item.image_id, new_image_id)
                        self.canvas.tag_raise(furniture_item.image_id, flooring_data['border_id'])

    #===copy paste===#
    def copy_selected_item(self):
        # ✅ First, try to copy selected furniture object
        if hasattr(self, 'selected_furniture_obj') and self.selected_furniture_obj:
            furniture = self.selected_furniture_obj
            self.copied_item_data = {
                "type": "furniture_image",
                "image_path": furniture.image_path,
                "scale": furniture.scale,
                "angle": furniture.angle
            }
            print("📋 Copied furniture image.")
            return

        # ✅ Otherwise, fallback to canvas shape
        if not hasattr(self, 'selected_item') or not self.selected_item:
            print("⚠️ No item selected to copy.")
            return

        item = self.selected_item
        item_type = self.canvas.type(item)
        coords = self.canvas.coords(item)
        tags = self.canvas.gettags(item)
        options = {}

        if item_type == "line":
            options["fill"] = self.canvas.itemcget(item, "fill")
            options["width"] = self.canvas.itemcget(item, "width")
        elif item_type in ("oval", "rectangle", "polygon"):
            options["fill"] = self.canvas.itemcget(item, "fill")
            options["outline"] = self.canvas.itemcget(item, "outline")
            options["width"] = self.canvas.itemcget(item, "width")
        elif item_type == "text":
            options["text"] = self.canvas.itemcget(item, "text")
            options["fill"] = self.canvas.itemcget(item, "fill")

        self.copied_item_data = {
            "type": item_type,
            "coords": coords,
            "options": options,
            "tags": tags
        }

        print("📋 Copied canvas shape:", self.copied_item_data)


    def prepare_to_paste_item(self):
        if not self.copied_item_data:
            print("⚠️ Nothing copied.")
            return
        print("🖱️ Click to paste item.")
        self.paste_ready = True
        self.canvas.bind("<Button-1>", self.paste_item_at_click)


    def paste_item_at_click(self, event):
        if not self.paste_ready or not self.copied_item_data:
            return

        paste_x, paste_y = event.x, event.y
        data = self.copied_item_data

        # Furniture paste
        if data["type"] == "furniture_image":
            from Furniture import Furniture
            image_item = Furniture(
                self.canvas, data["image_path"], paste_x, paste_y,
                self.select_image_item, data["scale"], data["angle"],
                get_freeze_state=lambda: self.canvas_frozen
            )
            self.image_furniture_items.append(image_item)
            self.select_image_item(image_item)
            print("✅ Pasted furniture.")
            self._finish_paste()
            return

        # Geometry paste
        coords = data["coords"]
        cx = sum(coords[::2]) / (len(coords)//2)
        cy = sum(coords[1::2]) / (len(coords)//2)
        dx, dy = paste_x - cx, paste_y - cy
        new_coords = [c + dx if i % 2 == 0 else c + dy for i, c in enumerate(coords)]

        # Handle group tag (for room items)
        original_tags = data["tags"]
        new_tags = []
        old_group_tag = None

        for tag in original_tags:
            if tag.startswith("room_group_"):
                old_group_tag = tag
            else:
                new_tags.append(tag)

        if old_group_tag and "room" in original_tags:
            new_group_tag = f"room_group_{self.group_id_counter}"
            self.group_id_counter += 1
            new_tags.append(new_group_tag)
        else:
            new_tags = original_tags

        new_id = None
        if data["type"] == "line":
            new_id = self.canvas.create_line(*new_coords, **data["options"], tags=new_tags)
        elif data["type"] == "oval":
            new_id = self.canvas.create_oval(*new_coords, **data["options"], tags=new_tags)
        elif data["type"] == "rectangle":
            new_id = self.canvas.create_rectangle(*new_coords, **data["options"], tags=new_tags)
        elif data["type"] == "polygon":
            new_id = self.canvas.create_polygon(*new_coords, **data["options"], tags=new_tags)
        elif data["type"] == "text":
            new_id = self.canvas.create_text(*new_coords, **data["options"], tags=new_tags)

        # If it was a group (like a room), re-bind drag
        if old_group_tag and new_group_tag:
            self.canvas.tag_bind(new_group_tag, "<Button-1>", self.start_drag_room)
            self.canvas.tag_bind(new_group_tag, "<B1-Motion>", self.drag_room)
            self.canvas.tag_bind(new_group_tag, "<ButtonRelease-1>", self.end_drag_room)

        if new_id:
            self.selected_item = new_id
            print("✅ Pasted item.")
        
        self._finish_paste()

    def _finish_paste(self):
        self.paste_ready = False
        self.canvas.unbind("<Button-1>")

    def select_shape(self, event):
        item = self.canvas.find_closest(event.x, event.y)[0]
        self.selected_item = item
        print("Selected:", item)

#== coordinate system ===#
    def draw_line_by_coords(self, x1, y1, x2, y2):
        px1, py1 = self.view.real_to_pixel(x1, y1)
        px2, py2 = self.view.real_to_pixel(x2, y2)

        line_id = self.canvas.create_line(px1, py1, px2, py2, fill=self.model.line_color, width=2)
        self.actions.log({"type": "create", "items": [line_id]})
        self.canvas.tag_raise(line_id)

    def draw_rectangle_by_coords(self, x1, y1, x2, y2):
        px1, py1 = self.view.real_to_pixel(x1, y1)
        px2, py2 = self.view.real_to_pixel(x2, y2)

        rect_id = self.canvas.create_rectangle(
            px1, py1, px2, py2,
            fill=self.model.fill_color or "#d0f0c0",
            outline=self.model.line_color,
            width=2
        )
        self.actions.log({"type": "create", "items": [rect_id]})
        self.canvas.tag_raise(rect_id)

    def draw_circle_by_coords(self, x, y, radius):
        px, py = self.view.real_to_pixel(x, y)
        pixel_radius = radius / self.model.unit_scale[self.model.unit] * self.model.grid_spacing * self.model.zoom_level

        oval_id = self.canvas.create_oval(
            px - pixel_radius, py - pixel_radius,
            px + pixel_radius, py + pixel_radius,
            fill=self.model.fill_color or "#d0f0c0",
            outline=self.model.line_color,
            width=2
        )
        self.actions.log({"type": "create", "items": [oval_id]})
        self.canvas.tag_raise(oval_id)
    def set_coord_label(self, label):
        self.coord_label = label

    def update_coord_label(self, event):
        if self.coord_label:
            real_x, real_y = self.view.pixel_to_real(event.x, event.y)
            self.coord_label.configure(text=f"Coordinates: ({real_x:.2f}, {real_y:.2f})")

    def toggle_canvas_freeze(self):
        self.canvas_frozen = not self.canvas_frozen
        state = "frozen" if self.canvas_frozen else "active"
        print(f"🧊 Canvas is now {state}.")

        # Optional visual cue
        if self.canvas_frozen:
            self.canvas.config(cursor="X_cursor")  # Freeze look
        else:
            self.canvas.config(cursor="arrow")     # Back to normal



    def rotate_selected_furniture(self):
        
        if hasattr(self, 'selected_furniture_obj') and self.selected_furniture_obj:
            self.selected_furniture_obj.rotate()
            print("Rotated selected furniture")
        else:
            print("No furniture selected for rotation")

    def delete_selected_furniture(self):
        """Delete the currently selected furniture item."""
        if hasattr(self, 'selected_furniture_obj') and self.selected_furniture_obj:
            # Remove from canvas
            self.canvas.delete(self.selected_furniture_obj.image_id)
            # Remove from list
            if self.selected_furniture_obj in self.image_furniture_items:
                self.image_furniture_items.remove(self.selected_furniture_obj)
            self.selected_furniture_obj = None
            print("Deleted selected furniture")
        else:
            print("No furniture selected for deletion")

