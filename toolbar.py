import tkinter as tk
from tkinter import ttk#for tabs
import math
import tkinter as tk
from tkinter import ttk

def setup_toolbar(app, root):
    # Create the main frame and pack it
    main_frame = ttk.Frame(root)
    main_frame.pack(fill=tk.BOTH, expand=True)

    # Create a Notebook (tabbed interface)
    notebook = ttk.Notebook(main_frame)
    notebook.pack(side=tk.LEFT, fill=tk.Y)

    # Create individual tabs
    draw_tab = ttk.Frame(notebook)
    edit_tab = ttk.Frame(notebook)
    view_tab = ttk.Frame(notebook)

    # Add tabs to notebook
    notebook.add(draw_tab, text="Draw")
    notebook.add(edit_tab, text="Edit")
    notebook.add(view_tab, text="View")

    # === DRAW TAB ===
    tk.Button(draw_tab, text="Toggle Grid", command=app.toggle_grid).pack(pady=2)
    tk.Button(draw_tab, text="Draw Line", command=app.enable_line_drawing, width=15).pack(pady=2)
    tk.Button(draw_tab, text="Draw Polygon", command=app.enable_polygon_mode, width=15).pack(pady=2)
    tk.Button(draw_tab, text="Finish Polygon", command=app.finish_polygon, width=15).pack(pady=2)
    tk.Button(draw_tab, text="Undo", command=app.undo, width=15).pack(pady=2)

    tk.Label(draw_tab, text="Line Style:").pack()
    tk.OptionMenu(draw_tab, app.line_style_var, "solid", "bold", "dashed", command=app.change_line_style).pack(pady=2)
    tk.Button(draw_tab, text="Pick Line Color", command=app.pick_line_color, width=15).pack(pady=2)
    tk.Button(edit_tab, text="Eraser Tool", command=app.enable_eraser_mode, width=15).pack(pady=2)


    

    # === EDIT TAB ===
    
    tk.Button(edit_tab, text="Clear Canvas", command=app.clear_canvas, width=15).pack(pady=2)
    tk.Label(edit_tab, text="Unit:").pack()
    tk.OptionMenu(edit_tab, app.unit_var, *app.unit_scale.keys(), command=app.change_unit).pack(pady=2)

    # === VIEW TAB ===
    tk.Button(view_tab, text="Save Canvas", command=app.save_canvas, width=15).pack(pady=2)

    tk.Label(view_tab, text="Furniture:").pack()
    furniture_options = [
    "Bed", "Chair", "Table", "Door", "Toilet", "Shower", "Sink",
    "Dining", "Stove", "Fridge", "Computer", "TV", "Storage", "Window"
     ]
    tk.OptionMenu(view_tab, app.furniture_var, *furniture_options).pack(pady=2)
    # tk.OptionMenu(view_tab, app.furniture_var, "Bed", "Table", "Chair", "Door").pack(pady=2)
    tk.Button(view_tab, text="Place Furniture", command=app.enable_furniture_mode, width=15).pack(pady=2)
    # tk.Button(view_tab, text="Increase Icon Size", command=app.increase_selected_icon_size).pack(pady=2)
    # tk.Button(view_tab, text="Decrease Icon Size", command=app.decrease_selected_icon_size).pack(pady=2)
    tk.Button(view_tab, text="Zoom In Furniture", command=app.zoom_in_furniture).pack(pady=2)
    tk.Button(view_tab, text="Zoom Out Furniture", command=app.zoom_out_furniture).pack(pady=2)
