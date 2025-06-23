# toolbar.py
from tkinter import Menu, Menubutton
from Furniture import find_image_path
from PIL import Image, ImageTk
import customtkinter as ctk
import tkinter as tk
from tkinter import Menu, Menubutton
from tkinter import ttk


from layout_serializer import LayoutSerializer






def enable_tool(model, tools, view, mode_key):
    """Helper to activate a drawing/fill/text mode and update cursor."""
    tools.reset_modes()
    model.set(mode_key, True)

    cursor_map = {
        "drawing_enabled": "crosshair",
        "polygon_mode": "crosshair",
        "text_insertion_mode": "xterm",
        "fill_mode_enabled": "dotbox"
    }

    view.canvas.config(cursor=cursor_map.get(mode_key, "arrow"))


def setup_toolbar(root, model, tools, controller, view, actions):
    """Creates a tabbed toolbar on the left with drawing, editing, and view tools."""
    # Left frame
    main_frame = ctk.CTkFrame(root, width=200)
    main_frame.pack(side="left", fill="y", padx=5, pady=5)

    # Tabs using ttk.Notebook
    notebook = ttk.Notebook(main_frame)
    notebook.pack(fill="both", expand=True)

    # === Define Tabs ===
    draw_tab = ctk.CTkFrame(notebook)
    edit_tab = ctk.CTkFrame(notebook)
    view_tab = ctk.CTkFrame(notebook)
    furniture_tab = ctk.CTkFrame(notebook)
    coor_tab= ctk.CTkFrame(notebook)

    # Add tabs to notebook
    notebook.add(draw_tab, text="Draw")
    notebook.add(edit_tab, text="Edit")
    notebook.add(view_tab, text="View")
    notebook.add(furniture_tab, text="Furniture")
    notebook.add(coor_tab, text="Coordinates")

    # === Draw Tab Buttons ===
    ctk.CTkLabel(draw_tab, text="Drawing Tools", font=("Arial", 14)).pack(pady=(10, 5))
    ctk.CTkButton(draw_tab, text="Line", command=lambda: enable_tool(model, tools, view, "drawing_enabled")).pack(pady=4)
    ctk.CTkLabel(draw_tab, text="Line Style").pack(pady=(10, 2))

    line_style_var = ctk.StringVar(value="solid")
    def on_line_style_change(style):
        model.line_style = style
    line_style_menu = ctk.CTkOptionMenu(draw_tab,
                                        variable=line_style_var,
                                        values=["solid", "bold", "dashed"],
                                        command=on_line_style_change)
    line_style_menu.pack(pady=2)
    ctk.CTkButton(edit_tab, text="Eraser Tool",
              command=lambda: tools.enable_eraser_mode()).pack(pady=4)
    ctk.CTkButton(draw_tab, text="Polygon", command=lambda: enable_tool(model, tools, view, "polygon_mode")).pack(pady=4)
    ctk.CTkButton(draw_tab, text="Fill", command=lambda: enable_tool(model, tools, view, "fill_mode_enabled")).pack(pady=4)
    ctk.CTkButton(draw_tab, text="Text", command=lambda: enable_tool(model, tools, view, "text_insertion_mode")).pack(pady=4)

    # === Edit Tab Buttons ===
    ctk.CTkLabel(edit_tab, text="Editing", font=("Arial", 14)).pack(pady=(10, 5))
    ctk.CTkButton(edit_tab, text="Undo", command=lambda: actions.undo(view.canvas)).pack(pady=4)
    ctk.CTkButton(edit_tab, text="Redo", command=lambda: actions.redo(view.canvas)).pack(pady=4)
    freeze_btn_text = tk.StringVar(value="Freeze Canvas")



     # Create serializer instance
    serializer = LayoutSerializer(model, view, tools, actions)
    
    # Add save/load buttons to edit tab
    ctk.CTkLabel(edit_tab, text="").pack(pady=5)
    ctk.CTkLabel(edit_tab, text="Save/Load Layout", font=("Arial", 12, "bold")).pack(pady=5)
    
    ctk.CTkButton(edit_tab, text="Save as JSON", command=serializer.save_to_json).pack(pady=4)
    ctk.CTkButton(edit_tab, text="Load from JSON", command=serializer.load_from_json).pack(pady=4)
    ctk.CTkButton(edit_tab, text="Save as YAML", command=serializer.save_to_yaml).pack(pady=4)
    ctk.CTkButton(edit_tab, text="Load from YAML", command=serializer.load_from_yaml).pack(pady=4)
    ctk.CTkButton(edit_tab, text="Auto Save", command=serializer.auto_save_layout).pack(pady=4)
    
    # Bind Ctrl+S for quick save
    root.bind('<Control-s>', lambda e: serializer.auto_save_layout())
    















    def toggle_freeze():
        tools.toggle_canvas_freeze()
        freeze_btn_text.set("Unfreeze Canvas" if tools.canvas_frozen else "Freeze Canvas")

    ctk.CTkButton(edit_tab, textvariable=freeze_btn_text, command=toggle_freeze).pack(pady=8)

    # === View Tab Buttons ===
    ctk.CTkLabel(view_tab, text="View Options", font=("Arial", 14)).pack(pady=(10, 5))
    ctk.CTkButton(view_tab, text="Toggle Grid", command=view.toggle_grid).pack(pady=4)
    ctk.CTkButton(view_tab, text="Line Color", command=tools.pick_line_color).pack(pady=4)
    ctk.CTkButton(view_tab, text="Fill Color", command=tools.pick_fill_color).pack(pady=4)

    # === Furniture Tab Placeholder ===
    furniture_categories = {
        "Beds": ["double_bed", "single_bed"],
        "Bathroom": ["Toilet", "Bath Tub", "Toiler_room1", "Bathroom_layout1"],
        "Common Furniture": ["dining_table_8_seat", "sofa", "Chair"],
        "Doors": ["doublehand_door", "singlehand_door"]
    }

    # Load images for all furniture items
    image_thumbnails = {}
    for category, items in furniture_categories.items():
        for name in items:
            path = find_image_path(name)
            if path:
                img = Image.open(path).resize((40, 40))
                thumb = ImageTk.PhotoImage(img)
                image_thumbnails[name] = thumb

    # Create dropdown for each category
    for category, items in furniture_categories.items():
        # Create a frame for each category
        category_frame = ctk.CTkFrame(furniture_tab)
        category_frame.pack(pady=5, padx=10, fill="x")
        
        # Category label
        ctk.CTkLabel(category_frame, text=category, font=("Arial", 12, "bold")).pack(pady=(5,0))
        
        # Create menubutton with dropdown
        mbtn = Menubutton(category_frame, text=f"Select {category}", relief=tk.RAISED, 
                        bg="#212121", fg="white", activebackground="#404040")
        menu = Menu(mbtn, tearoff=0, bg="#2b2b2b", fg="white", 
                    activebackground="#404040", activeforeground="white")
        mbtn.config(menu=menu)
        
        # Add items to dropdown with images
        for name in items:
            thumb = image_thumbnails.get(name)
            display_name = name.replace("_", " ").title()
            if thumb:
                menu.add_command(
                    label=display_name,
                    image=thumb,
                    compound="left",
                    command=lambda n=name: tools.select_furniture_item(n)
                )
            else:
                menu.add_command(
                    label=display_name,
                    command=lambda n=name: tools.select_furniture_item(n)
                )
        
        mbtn.pack(pady=5, padx=5, fill="x")

    ctk.CTkButton(furniture_tab, text="Rotate Selected", 
              command=lambda: tools.rotate_selected_furniture()).pack(pady=2)
    ctk.CTkButton(furniture_tab, text="Delete Selected", 
              command=lambda: tools.delete_selected_furniture()).pack(pady=2)







    ctk.CTkButton(edit_tab, text="Reset Modes", command=tools.reset_modes).pack(pady=10)

    #Room formation features
    # Room Name
    ctk.CTkLabel(view_tab, text="Room Name:").pack(pady=2)
    room_name_entry = ctk.CTkEntry(view_tab)
    room_name_entry.pack(pady=2)

    # Length
    ctk.CTkLabel(view_tab, text="Length (ft):").pack(pady=2)
    room_length_entry = ctk.CTkEntry(view_tab)
    room_length_entry.pack(pady=2)

    # Breadth
    ctk.CTkLabel(view_tab, text="Breadth (ft):").pack(pady=2)
    room_breadth_entry = ctk.CTkEntry(view_tab)
    room_breadth_entry.pack(pady=2)

    # Create Room Button
    def create_room_from_sidebar():
        name = room_name_entry.get().strip() or "Room"
        try:
            length = float(room_length_entry.get())
            breadth = float(room_breadth_entry.get())
            tools.insert_room_template(name, length, breadth)
        except ValueError:
            print("⚠️ Please enter valid numbers for length and breadth.")

    ctk.CTkButton(view_tab, text="Create Room", command=create_room_from_sidebar).pack(pady=5)
    ctk.CTkButton(draw_tab, text="Add Flooring", command=tools.enable_flooring_mode).pack(pady=2)

    ctk.CTkLabel(draw_tab, text="Flooring Type:").pack(pady=0)
    flooring_menu = ctk.CTkOptionMenu(
        draw_tab,
        variable=tools.flooring_type_var,
        values=["wood", "tile", "marble", "garden"],
        command=lambda _: tools.enable_flooring_mode()  # Optional auto-trigger
    )
    flooring_menu.pack(pady=2)

#== Coordinate Tab ===
# Coordinate label (optional real-time tracking)
    coord_label = ctk.CTkLabel(coor_tab, text="Coordinates: (0.0, 0.0)")
    coord_label.pack(pady=5, anchor="w")
    tools.set_coord_label(coord_label)  # Pass label to tools
    # -------- Line by Coordinates --------
    line_entry = ctk.CTkEntry(coor_tab, placeholder_text="x1,y1,x2,y2")
    line_entry.pack()

    def parse_and_draw_line():
        try:
            parts = list(map(float, line_entry.get().split(',')))
            if len(parts) == 4:
                tools.draw_line_by_coords(*parts)
        except Exception as e:
            print("Invalid input:", e)

    ctk.CTkButton(coor_tab, text="Draw Line", command=parse_and_draw_line).pack(pady=5)

    # -------- Rectangle by Coordinates --------
    rect_entry = ctk.CTkEntry(coor_tab, placeholder_text="x1,y1,x2,y2")
    rect_entry.pack()

    def parse_and_draw_rectangle():
        try:
            parts = list(map(float, rect_entry.get().split(',')))
            if len(parts) == 4:
                tools.draw_rectangle_by_coords(*parts)
        except Exception as e:
            print("Invalid input:", e)

    ctk.CTkButton(coor_tab, text="Draw Rectangle", command=parse_and_draw_rectangle).pack(pady=5)

    # -------- Circle by Coordinates --------
    circle_entry = ctk.CTkEntry(coor_tab, placeholder_text="cx,cy,r")
    circle_entry.pack()

    def parse_and_draw_circle():
        try:
            parts = list(map(float, circle_entry.get().split(',')))
            if len(parts) == 3:
                tools.draw_circle_by_coords(*parts)
        except Exception as e:
            print("Invalid input:", e)

    ctk.CTkButton(coor_tab, text="Draw Circle", command=parse_and_draw_circle).pack(pady=5)


    return main_frame, {
        "draw": draw_tab,
        "edit": edit_tab,
        "view": view_tab,
        "furniture": furniture_tab,
        "coordinate": coor_tab
    }
