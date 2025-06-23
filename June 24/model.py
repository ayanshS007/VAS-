# model.py

class CanvasModel:
    def __init__(self):
        self.zoom_level = 1.0
        self.zoom_step = 0.1
        self.grid_spacing = 20
        self.unit = "m"
        self.unit_scale = {"m": 1.0, "cm": 100, "ft": 3.281}
        
        self.line_color = "black"
        self.line_style = "solid"
        self.fill_color = ""
        self.selected_item = None
        self.selected_image_item = None
        self.group_id_counter = 0

        self.state_flags = {
            "drawing_enabled": False,
            "polygon_mode": False,
            "fill_mode_enabled": False,
            "eraser_mode": False,
            "text_insertion_mode": False,
            "furniture_mode": False,
        }

    def toggle(self, key):
        self.state_flags[key] = not self.state_flags[key]

    def set(self, key, value):
        self.state_flags[key] = value

    def get(self, key):
        return self.state_flags.get(key, False)
