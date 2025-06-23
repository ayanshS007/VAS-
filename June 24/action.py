# actions.py

class ActionManager:
    def __init__(self):
        self.undo_stack = []
        self.redo_stack = []

    def log(self, action):
        self.undo_stack.append(action)
        self.redo_stack.clear()

    def undo(self, canvas):
        if self.undo_stack:
            action = self.undo_stack.pop()
            self._reverse_action(canvas, action)
            self.redo_stack.append(action)

    def redo(self, canvas):
        if self.redo_stack:
            action = self.redo_stack.pop()
            self._apply_action(canvas, action)
            self.undo_stack.append(action)

    def _reverse_action(self, canvas, action):
        t = action["type"]

        if t == "create":
            for item in action["items"]:
                canvas.delete(item)

        elif action["type"] == "delete":
            item_type = action["item_type"]
            coords = action["coords"]
            options = action["options"]

            if item_type == "text":
                canvas.create_text(*coords, text=options["text"], fill=options["fill"], font=("Arial", 10))
            elif item_type == "line":
                canvas.create_line(*coords, fill=options["fill"], width=int(float(options["width"])))
            elif item_type == "oval":
                canvas.create_oval(*coords, fill=options["fill"])
            elif item_type == "rectangle":
                canvas.create_rectangle(*coords, fill=options["fill"], outline=options["outline"], width=2)
            elif item_type == "image":
                print("⚠️ Cannot undo image delete directly without full state.")

        elif t == "move":
            item = action["item"]
            dx = action["from"][0] - action["to"][0]
            dy = action["from"][1] - action["to"][1]
            canvas.move(item, dx, dy)

    def _apply_action(self, canvas, action):
        t = action["type"]

        if t == "create":
            # Cannot redo without re-creating items (would need to store parameters for recreation)
            pass

        elif t == "delete":
            for data in action["items"]:
                canvas.delete(data["new_id"])

        elif t == "move":
            item = action["item"]
            dx = action["to"][0] - action["from"][0]
            dy = action["to"][1] - action["from"][1]
            canvas.move(item, dx, dy)
