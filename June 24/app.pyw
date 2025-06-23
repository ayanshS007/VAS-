import tkinter as tk
from model import CanvasModel
from view import CanvasView
from tools import CanvasTools
from controller import CanvasController
from action import ActionManager
from toolbar import setup_toolbar  # your toolbar.py

def launch_app():
    root = tk.Tk()
    root.title("Mini AutoCAD")
    root.geometry("1400x800")

    # Main frame to contain both toolbar and canvas
    main_frame = tk.Frame(root)
    main_frame.pack(fill="both", expand=True)

    # Step 1: Core app objects
    model = CanvasModel()
    actions = ActionManager()

    # Step 2: Setup canvas first (RIGHT side)
    view = CanvasView(main_frame, model)  # contains .canvas
    tools = CanvasTools(root, model, view, actions)
    controller = CanvasController(root, model, view, tools, actions)

    # Step 3: Setup toolbar (LEFT side)
    toolbar_frame, tabs = setup_toolbar(main_frame, model, tools, controller, view, actions)
    toolbar_frame.pack(side="left", fill="y")

    # Step 4: Draw grid after everything is ready
    view.draw_grid()
    root.mainloop()
if __name__ == "__main__":
    launch_app()
