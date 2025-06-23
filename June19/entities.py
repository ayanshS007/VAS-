# entities.py

from PIL import Image, ImageTk

class RoomEntity:
    def __init__(self, canvas, model, name, width_m, height_m, group_id):
        self.canvas = canvas
        self.model = model
        self.name = name
        self.group_tag = f"room_group_{group_id}"
        self.unit_scale = model.unit_scale[model.unit]
        self.grid_spacing = model.grid_spacing
        self.zoom_level = model.zoom_level
        self.wlabel=width_m
        self.hlabel=height_m
        self.width_px = width_m / self.unit_scale * self.grid_spacing * self.zoom_level
        self.height_px = height_m / self.unit_scale * self.grid_spacing * self.zoom_level
        self.x0 = 100 + group_id * 20
        self.y0 = 100 + group_id * 20
        self.x1 = self.x0 + self.width_px
        self.y1 = self.y0 + self.height_px

        self.fill_color = "#d0f0c0"  # default
        if "shaft" in name.lower():
            self.fill_color = "#808080"
        elif "cupboard" in name.lower():
            self.fill_color = "#663300"

        self.create()

    def create(self):
        self.items = []

        self.rect_id = self.canvas.create_rectangle(
            self.x0, self.y0, self.x1, self.y1,
            fill=self.fill_color, outline="black",
            tags=("room", self.group_tag)
        )
        self.items.append(self.rect_id)

        if "shaft" in self.name.lower():
            line1 = self.canvas.create_line(self.x0, self.y0, self.x1, self.y1, fill="black", tags=(self.group_tag,))
            line2 = self.canvas.create_line(self.x0, self.y1, self.x1, self.y0, fill="black", tags=(self.group_tag,))
            self.items.extend([line1, line2])
        else:
            text = f"{self.name}\n{round(self.wlabel,1)}×{round(self.hlabel, 1)} {self.model.unit}"
            self.label_id = self.canvas.create_text(
                (self.x0 + self.x1) / 2,
                (self.y0 + self.y1) / 2,
                text=text,
                font=("Arial", 10),
                tags=(self.group_tag,)
            )
            self.items.append(self.label_id)

        # ✅ Add both to group tag
        self.canvas.addtag_withtag(self.group_tag, self.rect_id)
        if hasattr(self, 'label_id'):
            self.canvas.addtag_withtag(self.group_tag, self.label_id)

        # Bind drag to the group
        self.canvas.tag_bind(self.group_tag, "<Button-1>", self.start_drag)
        self.canvas.tag_bind(self.group_tag, "<B1-Motion>", self.drag)
        self.canvas.tag_bind(self.group_tag, "<ButtonRelease-1>", self.end_drag)

        def start_drag(self, event):
            self.drag_start = (event.x, event.y)

        def drag(self, event):
            dx = event.x - self.drag_start[0]
            dy = event.y - self.drag_start[1]
            for item in self.canvas.find_withtag(self.group_tag):
                self.canvas.move(item, dx, dy)
            self.drag_start = (event.x, event.y)

        def end_drag(self, event):
            pass

    # def start_drag(self, event):
    #     self.drag_start = (event.x, event.y)

    # def drag(self, event):
    #     dx = event.x - self.drag_start[0]
    #     dy = event.y - self.drag_start[1]
    #     for item in self.canvas.find_withtag(self.group_tag):
    #         self.canvas.move(item, dx, dy)
    #     self.drag_start = (event.x, event.y)

    # def end_drag(self, event):
    #     pass  # Optionally log action for undo


class FurnitureEntity:
    def __init__(self, canvas, image_path, x, y, scale=0.25, angle=0):
        self.canvas = canvas
        self.image_path = image_path
        self.x = x
        self.y = y
        self.scale = scale
        self.angle = angle

        self.load_image()
        self.image_id = self.canvas.create_image(
            self.x, self.y, image=self.tk_img, anchor="center", tags=("furniture",)
        )

    def load_image(self):
        img = Image.open(self.image_path)
        size = (int(img.width * self.scale), int(img.height * self.scale))
        img = img.resize(size, Image.Resampling.LANCZOS)
        self.tk_img = ImageTk.PhotoImage(img)

    def rotate(self):
        self.angle = (self.angle + 90) % 360
        img = Image.open(self.image_path)
        img = img.resize((int(img.width * self.scale), int(img.height * self.scale)))
        img = img.rotate(self.angle, expand=True)
        self.tk_img = ImageTk.PhotoImage(img)
        self.canvas.itemconfig(self.image_id, image=self.tk_img)

    def flip_horizontal(self):
        img = Image.open(self.image_path)
        img = img.resize((int(img.width * self.scale), int(img.height * self.scale)))
        img = img.transpose(Image.FLIP_LEFT_RIGHT)
        self.tk_img = ImageTk.PhotoImage(img)
        self.canvas.itemconfig(self.image_id, image=self.tk_img)

    def flip_vertical(self):
        img = Image.open(self.image_path)
        img = img.resize((int(img.width * self.scale), int(img.height * self.scale)))
        img = img.transpose(Image.FLIP_TOP_BOTTOM)
        self.tk_img = ImageTk.PhotoImage(img)
        self.canvas.itemconfig(self.image_id, image=self.tk_img)

    def delete(self):
        self.canvas.delete(self.image_id)
