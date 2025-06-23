import json
import yaml
import os
import datetime
from tkinter import filedialog, messagebox
import tkinter as tk
from pathlib import Path

class LayoutSerializer:
    def __init__(self, model, view, tools, actions):
        self.model = model
        self.view = view
        self.canvas = view.canvas
        self.tools = tools
        self.actions = actions
        
        # Set up default save directory
        self.default_save_dir = os.path.join(os.getcwd(), "saved_layouts")
        self.ensure_save_directory()
        
        # Auto-save settings
        self.auto_save_enabled = True
        self.current_layout_file = None

    def ensure_save_directory(self):
        # """Create the default save directory if it doesn't exist."""
        Path(self.default_save_dir).mkdir(parents=True, exist_ok=True)

    def serialize_layout(self):
        # """Convert the current canvas layout to a dictionary."""
        layout = {
            "version": "1.0",
            "metadata": self._serialize_metadata(),
            "rooms": self._serialize_rooms(),
            "furniture": self._serialize_furniture(),
            "shapes": self._serialize_shapes(),
            "text": self._serialize_text()
        }
        return layout




    def save_to_json(self):
    # """Save the current layout to a JSON file."""
        layout = self.serialize_layout()
        print("Layout data to save:", layout)  # Debug print
        
        file_path = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            title="Save Layout as JSON"
        )
        
        if file_path:
            try:
                with open(file_path, 'w') as f:
                    json.dump(layout, f, indent=2)
                print(f"File saved successfully to: {file_path}")  # Debug print
                self.current_layout_file = file_path
                messagebox.showinfo("Success", f"Layout saved to {file_path}")
                return True
            except Exception as e:
                print(f"Save error: {e}")  # Debug print
                messagebox.showerror("Error", f"Failed to save layout: {str(e)}")
                return False
        return False













        




    def deserialize_layout(self, layout_data):
    # """Convert a layout dictionary back to canvas objects."""
        from Furniture import Furniture, find_image_path
        
        # Clear the canvas first (except for grid)
        self._clear_canvas()
        
        # Apply metadata if available
        if "metadata" in layout_data:
            self._deserialize_metadata(layout_data["metadata"])
        
        # Recreate rooms
        if "rooms" in layout_data:
            for room_data in layout_data["rooms"]:
                self._recreate_room(room_data)
        
        # Recreate furniture
        if "furniture" in layout_data:
            for furniture_data in layout_data["furniture"]:
                self._recreate_furniture(furniture_data)
        
        # Recreate shapes
        if "shapes" in layout_data:
            for shape_data in layout_data["shapes"]:
                self._recreate_shape(shape_data)
        
        # Recreate text
        if "text" in layout_data:
            for text_data in layout_data["text"]:
                self._recreate_text(text_data)
        
        print("Layout loaded successfully")

    def _recreate_room(self, room_data):
        # """Recreate a room from serialized data."""
        # room_id = self.canvas.create_rectangle(
        #     room_data["x"], room_data["y"],
        #     room_data["x"] + room_data["width"], 
        #     room_data["y"] + room_data["height"],
        #     fill=room_data["fill_color"],
        #     outline=room_data["outline_color"],
        #     tags=("room", room_data["group_tag"])
        # )
        room_id = self.canvas.create_rectangle(
        room_data["x"], room_data["y"],
        room_data["x"] + room_data["width"],
        room_data["y"] + room_data["height"],
        fill=room_data["fill_color"],
        outline=room_data["outline_color"],
        tags=("room", room_data["group_tag"])
    )
    
        # Recreate flooring if it exists
        if room_data.get("flooring", {}).get("has_flooring", False):
            flooring_info = room_data["flooring"]
            self._recreate_room_flooring(room_id, room_data, flooring_info)
    
    def _recreate_room_flooring(self, room_id, room_data, flooring_info):
        # """Recreate flooring for a room."""
        from PIL import Image, ImageTk
        import os
        
        flooring_path = flooring_info.get("image_path", "")
        
        # Try to find the flooring image
        if not os.path.exists(flooring_path):
            # Try to find in Images directory
            base_dir = os.path.dirname(os.path.abspath(__file__))
            flooring_type = flooring_info.get("flooring_type", "wood")
            
            for ext in ('png', 'jpeg', 'jpg'):
                alt_path = os.path.join(base_dir, "Images", f"{flooring_type}.{ext}")
                if os.path.exists(alt_path):
                    flooring_path = alt_path
                    break
        
        if not os.path.exists(flooring_path):
            print(f"Warning: Flooring image not found: {flooring_path}")
            return
        
        try:
            # Calculate room dimensions
            x0, y0 = room_data["x"], room_data["y"]
            x1, y1 = x0 + room_data["width"], y0 + room_data["height"]
            
            # Load and resize flooring image
            img = Image.open(flooring_path)
            img = img.resize((int(room_data["width"]), int(room_data["height"])), Image.Resampling.LANCZOS)
            tk_img = ImageTk.PhotoImage(img, master=self.canvas)
            
            # Create flooring image
            image_id = self.canvas.create_image(
                x0, y0,
                image=tk_img,
                anchor="nw",
                tags=("flooring", room_data["group_tag"])
            )
            
            # Create border
            border_id = self.canvas.create_rectangle(
                x0, y0, x1, y1,
                outline="black",
                width=2,
                tags=("flooring_border", room_data["group_tag"])
            )
            
            # Store flooring data in tools for future operations
            if not hasattr(self.tools, 'room_flooring_images'):
                self.tools.room_flooring_images = {}
                
            self.tools.room_flooring_images[room_id] = {
                'image_id': image_id,
                'tk_img': tk_img,
                'border_id': border_id,
                'image_path': flooring_path
            }
            
            # Manage z-order
            self.canvas.tag_raise(border_id, image_id)
            
        except Exception as e:
            print(f"Error recreating flooring: {e}")


    def _recreate_furniture(self, furniture_data):
        # """Recreate furniture from serialized data."""
        from Furniture import Furniture, find_image_path
        image_path = None
        # Method 1: Try the stored full path
        if os.path.exists(furniture_data["image_path"]):
            image_path = furniture_data["image_path"]
        
        # Method 2: Try using the image name with find_image_path function
        elif "image_name" in furniture_data:
            image_path = find_image_path(furniture_data["image_name"])
        
        # Method 3: Try using the filename in local Images directory
        elif "image_filename" in furniture_data:
            base_dir = os.path.dirname(os.path.abspath(__file__))
            local_path = os.path.join(base_dir, "Images", furniture_data["image_filename"])
            if os.path.exists(local_path):
                image_path = local_path
        # Method 4: Extract name from original path and search
        else:
            original_name = os.path.splitext(os.path.basename(furniture_data["image_path"]))[0]
            image_path = find_image_path(original_name)
        
        if not image_path:
            print(f"Warning: Could not locate furniture image: {furniture_data.get('image_filename', furniture_data['image_path'])}")
            return
        
        try:
            furniture_item = Furniture(
                canvas=self.canvas,
                image_path=image_path,
                x=furniture_data["x"],
                y=furniture_data["y"],
                select_callback=self.tools.select_image_item,
                scale=furniture_data["scale"],
                angle=furniture_data["angle"],
                get_freeze_state=lambda: self.tools.canvas_frozen
            )
            
            self.tools.image_furniture_items.append(furniture_item)
            print(f"Successfully recreated furniture: {os.path.basename(image_path)}")
            
        except Exception as e:
            print(f"Error recreating furniture: {e}")








        path = find_image_path(furniture_data["image_path"].split("/")[-1].split(".")[0])
        if path:
            furniture_item = Furniture(
                canvas=self.canvas,
                image_path=path,
                x=furniture_data["x"],
                y=furniture_data["y"],
                select_callback=self.tools.select_image_item,
                scale=furniture_data["scale"],
                angle=furniture_data["angle"],
                get_freeze_state=lambda: self.tools.canvas_frozen
            )
            self.tools.image_furniture_items.append(furniture_item)

    def _recreate_shape(self, shape_data):
        # """Recreate shapes from serialized data."""
        coords = [coord for point in shape_data["points"] for coord in point]
        
        if shape_data["type"] == "line":
            self.canvas.create_line(
                *coords,
                fill=shape_data["outline_color"],
                width=shape_data["width"]
            )
        elif shape_data["type"] == "rectangle":
            self.canvas.create_rectangle(
                *coords,
                fill=shape_data["fill_color"],
                outline=shape_data["outline_color"],
                width=shape_data["width"]
            )
        elif shape_data["type"] == "oval":
            self.canvas.create_oval(
                *coords,
                fill=shape_data["fill_color"],
                outline=shape_data["outline_color"],
                width=shape_data["width"]
            )

    def _recreate_text(self, text_data):
        # """Recreate text from serialized data."""
        self.canvas.create_text(
            text_data["x"], text_data["y"],
            text=text_data["content"],
            font=text_data["font"],
            fill=text_data["color"],
            anchor="nw"
        )


    def load_from_json(self):
    # """Load a layout from a JSON file."""
        file_path = filedialog.askopenfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            title="Load Layout from JSON"
        )
        
        if file_path:
            try:
                with open(file_path, 'r') as f:
                    layout_data = json.load(f)
                self.deserialize_layout(layout_data)
                self.current_layout_file = file_path
                messagebox.showinfo("Success", f"Layout loaded from {file_path}")
                return True
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load layout: {str(e)}")
                return False
        return False

    # def load_from_json(self):
    #     """Load a layout from a JSON file."""
    #     file_path = filedialog.askopenfilename(
    #         defaultextension=".json",
    #         filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
    #         title="Load Layout from JSON"
    #     )
        
    #     if file_path:
    #         try:
    #             with open(file_path, 'r') as f:
    #                 layout_data = json.load(f)
    #         self.deserialize_layout(layout_data)
    #         self.current_layout_file = file_path
   
    #     return False

    def save_to_yaml(self):
        # """Save the current layout to a YAML file."""
        layout = self.serialize_layout()
        
        file_path = filedialog.asksaveasfilename(
            defaultextension=".yaml",
            filetypes=[("YAML files", "*.yaml"), ("All files", "*.*")],
            title="Save Layout as YAML"
        )
        
        if file_path:
            try:
                with open(file_path, 'w') as f:
                    yaml.safe_dump(layout, f, indent=2)
                self.current_layout_file = file_path
                messagebox.showinfo("Success", f"Layout saved to {file_path}")
                return True
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save layout: {str(e)}")
                return False
        return False

    def load_from_yaml(self):
        # """Load a layout from a YAML file."""
        file_path = filedialog.askopenfilename(
            defaultextension=".yaml",
            filetypes=[("YAML files", "*.yaml"), ("All files", "*.*")],
            title="Load Layout from YAML"
        )
        
        if file_path:
            try:
                with open(file_path, 'r') as f:
                    layout_data = yaml.safe_load(f)
                self.deserialize_layout(layout_data)
                self.current_layout_file = file_path
                messagebox.showinfo("Success", f"Layout loaded from {file_path}")
                return True
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load layout: {str(e)}")
                return False
        return False

    def auto_save_layout(self):
        # """Auto-save the current layout."""
        if not self.auto_save_enabled:
            return False
        
        # Generate timestamp filename
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"autosave_{timestamp}.json"
        file_path = os.path.join(self.default_save_dir, filename)
        
        layout = self.serialize_layout()
        try:
            with open(file_path, 'w') as f:
                json.dump(layout, f, indent=2)
            print(f"Auto-saved to: {file_path}")
            messagebox.showinfo("Auto-Save", f"Layout auto-saved to {filename}")
            return True
        except Exception as e:
            print(f"Auto-save error: {e}")
            return False

    def _serialize_metadata(self):
        # """Serialize canvas metadata."""
        return {
            "project_name": "Floor Plan",
            "description": "Auto-generated layout",
            "created": datetime.datetime.now().isoformat(),
            "modified": datetime.datetime.now().isoformat(),
            "unit": getattr(self.model, 'unit', 'm'),
            "grid_spacing": getattr(self.model, 'grid_spacing', 20),
            "canvas_width": self.canvas.winfo_width(),
            "canvas_height": self.canvas.winfo_height(),
            "zoom_level": getattr(self.model, 'zoom_level', 1.0)
        }

    def _serialize_rooms(self):
    # """Serialize room data including flooring information."""
        rooms = []
        for item in self.canvas.find_withtag("room"):
            coords = self.canvas.coords(item)
            if len(coords) >= 4:
                # Build base room dict
                room_data = {
                    "id":     f"room_{item}",
                    "name":   "Room",
                    "x":      coords[0],
                    "y":      coords[1],
                    "width":  coords[2] - coords[0],
                    "height": coords[3] - coords[1],
                    "fill_color":    self.canvas.itemcget(item, "fill"),
                    "outline_color": self.canvas.itemcget(item, "outline"),
                    "group_tag":     "room_group"
                }
                # Attach flooring info if present
                if hasattr(self.tools, 'room_flooring_images') \
                and item in self.tools.room_flooring_images:
                    fd = self.tools.room_flooring_images[item]
                    room_data["flooring"] = {
                        "image_path":   fd.get('image_path', ''),
                        "has_flooring": True,
                        "flooring_type": self._get_flooring_type_from_path(
                            fd.get('image_path', '')
                        )
                    }
                else:
                    room_data["flooring"] = {"has_flooring": False}
                rooms.append(room_data)
        return rooms



    # def _get_flooring_type_from_path(self, image_path):
    # # """Extract flooring type from image path."""
    #     if not image_path:
    #         return "none"
        
    #     filename = os.path.basename(image_path).lower()
    #     if "wood" in filename:
    #         return "wood"
    #     elif "tile" in filename:
    #         return "tile"
    #     elif "marble" in filename:
    #         return "marble"
    #     elif "garden" in filename:
    #         return "garden"
    #     else:
    #         return "unknown"
    def _get_flooring_type_from_path(self, image_path):
    # """Extract flooring type from image path."""
        import os
        if not image_path:
            return "none"
        fname = os.path.basename(image_path).lower()
        if "wood"   in fname: return "wood"
        if "tile"   in fname: return "tile"
        if "marble" in fname: return "marble"
        if "garden" in fname: return "garden"
        return "unknown"







    def _serialize_furniture(self):
        furniture = []
        for idx, f in enumerate(self.tools.image_furniture_items):
            x, y = self.canvas.coords(f.image_id)
            
            # Extract just the filename for portability
            image_filename = os.path.basename(f.image_path)
            image_name = os.path.splitext(image_filename)[0]
            
            furniture_data = {
                "id": f"furniture_{idx}",
                "image_path": f.image_path,  # Keep full path for backward compatibility
                "image_filename": image_filename,  # Add filename
                "image_name": image_name,  # Add base name without extension
                "x": x,
                "y": y,
                "scale": f.scale,
                "angle": f.angle
            }
            furniture.append(furniture_data)
        return furniture

    def _serialize_shapes(self):
    # """Serialize shape data."""
        shapes = []
        for item in self.canvas.find_all():
            tags = self.canvas.gettags(item)
            if "grid" not in tags and "room" not in tags and "furniture" not in tags:
                item_type = self.canvas.type(item)
                coords = self.canvas.coords(item)
                if coords:
                    points = [[coords[i], coords[i+1]] for i in range(0, len(coords), 2)]
                    
                    # Safely get width
                    try:
                        width_str = self.canvas.itemcget(item, "width")
                        width = float(width_str) if width_str else 1.0
                    except (ValueError, TypeError, tk.TclError):
                        width = 1.0
                    
                    # Safely get colors based on item type
                    outline_color = ""
                    fill_color = ""
                    
                    try:
                        if item_type in ["line", "rectangle", "oval", "polygon"]:
                            outline_color = self.canvas.itemcget(item, "outline")
                        elif item_type == "text":
                            outline_color = self.canvas.itemcget(item, "fill")
                    except tk.TclError:
                        outline_color = "black"
                    
                    try:
                        if item_type in ["rectangle", "oval", "polygon"]:
                            fill_color = self.canvas.itemcget(item, "fill")
                    except tk.TclError:
                        fill_color = ""
                    
                    # Use fill color as outline for items that don't have outline
                    if not outline_color and fill_color:
                        outline_color = fill_color
                    elif not outline_color:
                        outline_color = "black"
                    
                    shapes.append({
                        "id": f"shape_{item}",
                        "type": item_type,
                        "points": points,
                        "outline_color": outline_color,
                        "fill_color": fill_color,
                        "width": width,
                        "style": "solid"
                    })
        return shapes



    def _serialize_text(self):
    # """Serialize text data."""
        texts = []
        for item in self.canvas.find_all():
            if self.canvas.type(item) == "text":
                coords = self.canvas.coords(item)
                
                # Safely get text properties
                try:
                    content = self.canvas.itemcget(item, "text")
                except tk.TclError:
                    content = ""
                
                try:
                    font = self.canvas.itemcget(item, "font")
                except tk.TclError:
                    font = "Arial 10"
                
                try:
                    color = self.canvas.itemcget(item, "fill")
                except tk.TclError:
                    color = "black"
                
                if coords and content:
                    texts.append({
                        "id": f"text_{item}",
                        "content": content,
                        "x": coords[0],
                        "y": coords[1],
                        "font": font,
                        "color": color
                    })
        return texts


    def _clear_canvas(self):
        # """Clear all canvas items except grid."""
        for item in self.canvas.find_all():
            if "grid" not in self.canvas.gettags(item):
                self.canvas.delete(item)
        # Clear furniture list
        self.tools.image_furniture_items.clear()

    def _deserialize_metadata(self, metadata):
        # """Apply metadata to the model."""
        if hasattr(self.model, 'unit'):
            self.model.unit = metadata.get("unit", "m")
        if hasattr(self.model, 'grid_spacing'):
            self.model.grid_spacing = metadata.get("grid_spacing", 20)
        if hasattr(self.model, 'zoom_level'):
            self.model.zoom_level = metadata.get("zoom_level", 1.0)























        