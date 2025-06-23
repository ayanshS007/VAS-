# controller.py

import tkinter as tk

class CanvasController:
    def __init__(self, root, model, view, tools, actions):
        self.root = root
        self.model = model
        self.view = view
        self.canvas = view.canvas
        self.tools = tools
        self.actions = actions

        self.dragging_item = None
        self.drag_start_pos = None

        # Bind events
        self.canvas.bind("<Button-1>", self.on_click)
        self.canvas.bind("<B1-Motion>", self.on_drag)        
        self.canvas.bind("<ButtonRelease-1>", self.on_release)
        self.canvas.bind("<MouseWheel>", self.on_mousewheel)
        root.bind("<Control-z>", lambda e: self.actions.undo(self.canvas))
        root.bind("<Control-y>", lambda e: self.actions.redo(self.canvas))
        root.bind("<Key>", self.on_key_press)
        self.canvas.bind("<Motion>", self.on_mouse_move)
        
    def on_click(self, event):
        x, y = event.x, event.y
        if self.tools.canvas_frozen:
            print("Canvas is frozen — click ignored.")
            return
        # Active tools like drawing, filling, text, etc.
        elif self.model.get("drawing_enabled"):
            self.tools.start_line(event)
        elif self.model.get("polygon_mode"):
            self.tools.add_polygon_point(event)
        elif self.model.get("fill_mode_enabled"):
            self.tools.fill_shape(event)
        elif self.model.get("text_insertion_mode"):
            self.tools.insert_text(event)
        elif self.model.get("furniture_mode"):
            self.tools.place_furniture(event)
            return
        elif self.model.get("eraser_mode"):
            self.tools.handle_eraser_click(event)
            return
        elif self.tools.flooring_enabled:
            self.tools.apply_flooring_to_room(event)
            return
        else:
            self.select_item(event)

    def on_drag(self, event):
        if self.drag_start_pos is None:
            return  # 🛑 No drag start position set
        dx = event.x - self.drag_start_pos[0]
        dy = event.y - self.drag_start_pos[1]
        if self.tools.canvas_frozen:
            return
        elif hasattr(self, 'dragging_group') and self.dragging_group:
            items = self.canvas.find_withtag(self.dragging_group)   
            for item in items:
                self.canvas.move(item, dx, dy)
            self.drag_start_pos = (event.x, event.y)

        elif self.dragging_item is not None:
            if "grid" in self.canvas.gettags(self.dragging_item):
                return  # Prevent moving grid lines
            self.canvas.move(self.dragging_item, dx, dy)
            self.drag_start_pos = (event.x, event.y)

        elif self.model.get("eraser_mode"):
            items = self.canvas.find_overlapping(event.x - 5, event.y - 5, event.x + 5, event.y + 5)
            for item in items:
                if "grid" in self.canvas.gettags(item):
                    continue  # Skip grid lines
                self.canvas.delete(item)
                self.actions.log({"type": "delete", "items": [item]})

    def on_release(self, event):
        if self.dragging_item:
            self.actions.log({
                "type": "move",
                "item": self.dragging_item,
                "from": self.drag_start_pos,
                "to": (event.x, event.y)
            })
        elif hasattr(self, 'dragging_group') and self.dragging_group:
            self.actions.log({
                "type": "move_group",
                "tag": self.dragging_group,
                "to": (event.x, event.y)
            })
        self.dragging_item = None
        self.dragging_group = None
        self.drag_start_pos = None

    def on_mousewheel(self, event):
        scale = 1.1 if event.delta > 0 else 0.9
        self.view.apply_zoom(scale)

    def select_item(self, event):
        items = self.canvas.find_overlapping(event.x - 5, event.y - 5, event.x + 5, event.y + 5)
        if not items:
            return

        top_item = items[-1]
        tags = self.canvas.gettags(top_item)

        # Check if it's part of a group (room)
        group_tag = next((tag for tag in tags if tag.startswith("room_group_")), None)
        if group_tag:
            self.dragging_item = None
            self.dragging_group = group_tag
        else:
            self.dragging_item = top_item
            self.dragging_group = None

        self.drag_start_pos = (event.x, event.y)

        # ✅ Check if it's a furniture image
        for furniture in self.tools.image_furniture_items:
            if hasattr(furniture, 'image_id') and furniture.image_id == top_item:
                self.tools.selected_furniture_obj = furniture
                furniture.draw_handles()  # Optional: highlight
                print("🪑 Furniture selected.")
                return

        # Otherwise, reset selected furniture
        self.tools.selected_furniture_obj = None
    
    def on_key_press(self, event):
        obj = self.tools.selected_furniture_obj

        # Furniture controls (rotate, resize, flip)
        if obj:
            if event.char == "r":
                obj.rotate()
            elif event.char == "f":
                obj.flip_horizontal()
            elif event.char == "v":
                obj.flip_vertical()
            elif event.char == "+":
                obj.resize(1.1)
            elif event.char == "-":
                obj.resize(0.9)
            elif event.keysym == "Delete":
                obj.delete()
                self.tools.image_furniture_items.remove(obj)
                self.tools.selected_furniture_obj = None
                return  # Exit here to avoid running Ctrl keys on deleted obj

        # Global shortcuts (independent of selection)
        if event.keysym == "Escape":
            self.tools.reset_modes()
        elif event.state & 0x4:  # Ctrl key held
            if event.keysym.lower() == "c":
                self.tools.copy_selected_item()
            elif event.keysym.lower() == "v":
                self.tools.prepare_to_paste_item()
        
    def on_mouse_move(self, event):
        self.tools.update_coord_label(event)