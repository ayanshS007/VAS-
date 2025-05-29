import customtkinter as ctk
import tkinter.simpledialog as simpledialog  

def setup_toolbar(app, root):
    main_frame = ctk.CTkFrame(root)
    main_frame.pack(fill="both", expand=True)
    
    from tkinter import ttk
    notebook = ttk.Notebook(main_frame)
    notebook.pack(side="left", fill="y")

    # Create tabs
    draw_tab = ctk.CTkFrame(notebook)
    edit_tab = ctk.CTkFrame(notebook)
    view_tab = ctk.CTkFrame(notebook)
    furniture_tab = ctk.CTkFrame(notebook)  # New furniture controls tab

    notebook.add(draw_tab, text="Draw")
    notebook.add(edit_tab, text="Edit")
    notebook.add(view_tab, text="View")
    notebook.add(furniture_tab, text="Furniture")

    # === Draw Tab ===
    ctk.CTkButton(draw_tab, text="Toggle Grid", command=app.toggle_grid).pack(pady=2)
    ctk.CTkButton(draw_tab, text="Draw Line", command=app.enable_line_drawing).pack(pady=2)
    ctk.CTkButton(draw_tab, text="Draw Polygon", command=app.enable_polygon_mode).pack(pady=2)
    ctk.CTkButton(draw_tab, text="Finish Polygon", command=app.finish_polygon).pack(pady=2)
    ctk.CTkButton(draw_tab, text="Undo", command=app.undo).pack(pady=2)
    import tkinter as tk  # Add at the top if not already imported

    ctk.CTkLabel(draw_tab, text="Line Style").pack(pady=2)
    line_style_menu = ctk.CTkOptionMenu(draw_tab, 
                                    variable=app.line_style_var,
                                    values=["solid", "bold", "dashed"],
                                    command=app.change_line_style)
    line_style_menu.pack(pady=2)

    ctk.CTkButton(draw_tab, text="Pick Line Color", command=app.pick_line_color).pack(pady=2)
    ctk.CTkButton(draw_tab, text="Insert Text", command=app.enable_text_insertion).pack(pady=2)

    def update_font_size(size_str):
        try:
            size = int(size_str)
            app.text_font_size = size
            if app.selected_text_item:
                app.canvas.itemconfig(app.selected_text_item, font=("Arial", size))
        except:
            pass

    ctk.CTkLabel(draw_tab, text="Font Size").pack(pady=2)
    ctk.CTkOptionMenu(draw_tab, values=["8", "10", "12", "16", "20", "24", "32"], command=update_font_size).pack(pady=2)
    ctk.CTkButton(draw_tab, text="Pick Fill Color", command=app.pick_fill_color).pack(pady=2)
    ctk.CTkButton(draw_tab, text="Fill at Point", command=app.enable_fill_mode).pack(pady=2)

   


    # === Edit Tab ===
    ctk.CTkButton(edit_tab, text="Clear Canvas", command=app.clear_canvas).pack(pady=2)
    ctk.CTkButton(edit_tab, text="Eraser Tool", command=app.enable_eraser_mode).pack(pady=2)
    ctk.CTkLabel(edit_tab, text="Unit:").pack()
    ctk.CTkOptionMenu(edit_tab, variable=app.unit_var, 
                     values=list(app.unit_scale.keys()), 
                     command=app.change_unit).pack(pady=2)
    ctk.CTkButton(edit_tab, text="Reset Mode", command=app.reset_modes).pack(pady=2)


    # === Furniture Tab ===
    # ctk.CTkLabel(furniture_tab, text="Furniture Controls").pack(pady=5)
    # Add image buttons for furniture
    from Furniture import find_image_path
    from PIL import Image, ImageTk

    image_thumbnails = {}
    for name in app.image_furniture_list:
     ctk.CTkButton(furniture_tab, text=name.replace("_", " ").title(),
                  command=lambda n=name: app.set_selected_image_furniture(n)).pack(pady=5, padx=10)


    ctk.CTkButton(furniture_tab, text="Rotate Selected", 
                 command=app.rotate_selected_image).pack(pady=2)
    ctk.CTkButton(furniture_tab, text="Delete Selected", 
                 command=app.delete_selected_image).pack(pady=2)
    ctk.CTkButton(furniture_tab, text="Zoom In (+)",
                 command=lambda: app.zoom_image(1.1)).pack(pady=2)
    ctk.CTkButton(furniture_tab, text="Zoom Out (-)", 
                 command=lambda: app.zoom_image(0.9)).pack(pady=2)

    # === View Tab ===
    ctk.CTkButton(view_tab, text="Save Canvas", command=app.save_canvas).pack(pady=2)
    ctk.CTkLabel(view_tab, text="Room Name:").pack(pady=2)
    room_name_entry = ctk.CTkEntry(view_tab)
    room_name_entry.pack(pady=2)

    ctk.CTkLabel(view_tab, text="Length (ft):").pack(pady=2)
    room_length_entry = ctk.CTkEntry(view_tab)
    room_length_entry.pack(pady=2)

    ctk.CTkLabel(view_tab, text="Breadth (ft):").pack(pady=2)
    room_breadth_entry = ctk.CTkEntry(view_tab)
    room_breadth_entry.pack(pady=2)

    def create_room_from_sidebar():
     name = room_name_entry.get().strip() or "Room"
     try:
        length = float(room_length_entry.get())
        breadth = float(room_breadth_entry.get())
        app.insert_room_template(name, length, breadth)
     except ValueError:
        print("⚠️ Please enter valid numbers.")

    ctk.CTkButton(view_tab, text="Create Room", command=create_room_from_sidebar).pack(pady=5)





# def setup_toolbar(app, root):
#     # Create the main frame and pack it
#     main_frame = ttk.Frame(root)
#     main_frame.pack(fill=tk.BOTH, expand=True)

#     # Create a Notebook (tabbed interface)
#     notebook = ttk.Notebook(main_frame)
#     notebook.pack(side=tk.LEFT, fill=tk.Y)

#     # Create individual tabs
#     draw_tab = ttk.Frame(notebook)
#     edit_tab = ttk.Frame(notebook)
#     view_tab = ttk.Frame(notebook)
#     abhishekcrazy_tab = ttk.Frame(notebook)

#     # Add tabs to notebook
#     notebook.add(draw_tab, text="Draw")
#     notebook.add(edit_tab, text="Edit")
#     notebook.add(view_tab, text="View")
#     notebook.add(abhishekcrazy_tab, text="abhishekcrazy")

#     # === DRAW TAB ===
#     tk.Button(draw_tab, text="Toggle Grid", command=app.toggle_grid).pack(pady=2)
#     tk.Button(draw_tab, text="Draw Line", command=app.enable_line_drawing, width=15).pack(pady=2)
#     tk.Button(draw_tab, text="Draw Polygon", command=app.enable_polygon_mode, width=15).pack(pady=2)
#     tk.Button(draw_tab, text="Finish Polygon", command=app.finish_polygon, width=15).pack(pady=2)
#     tk.Button(draw_tab, text="Undo", command=app.undo, width=15).pack(pady=2)
#     tk.Button(draw_tab, text="Draw Wall", command=app.draw_wall).pack(pady=2)

#     #line_button = ttk.Button(draw_tab, text="Line by Length & Angle",
#                             #command=lambda: app.activate_line_by_angle_mode())
#    # line_button.pack(pady=5)
#     tk.Label(draw_tab, text="Line Style:").pack()
#     tk.OptionMenu(draw_tab, app.line_style_var, "solid", "bold", "dashed", command=app.change_line_style).pack(pady=2)
#     tk.Button(draw_tab, text="Pick Line Color", command=app.pick_line_color, width=15).pack(pady=2)
#     # tk.Button(draw_tab, text="Pick Fill Color", command=app.pick_fill_color, width=15).pack(pady=2)
#     # tk.Button(draw_tab, text="Fill at Point", command=app.enable_fill_mode, width=15).pack(pady=2)


#     tk.Button(edit_tab, text="Eraser Tool", command=app.enable_eraser_mode, width=15).pack(pady=2)
    

#     # === EDIT TAB ===
    
#     tk.Button(edit_tab, text="Clear Canvas", command=app.clear_canvas, width=15).pack(pady=2)
#     tk.Label(edit_tab, text="Unit:").pack()
#     tk.OptionMenu(edit_tab, app.unit_var, *app.unit_scale.keys(), command=app.change_unit).pack(pady=2)
#     tk.Button(edit_tab, text="Insert Text", command=app.enable_text_insertion, width=15).pack(pady=2)

#     # tk.Button(edit_tab, text="Zoom In Canvas", command=app.zoom_in).pack(pady=2)
#     # tk.Button(edit_tab, text="Zoom Out Canvas", command=app.zoom_out).pack(pady=2)


#     # === VIEW TAB ===
#     tk.Label(view_tab, text="Room Templates:").pack(pady=2)
#     # tk.Button(view_tab, text="Bedroom (3x4m)", command=lambda: app.insert_room_template("Bedroom", 3, 4)).pack(pady=2)
#     # tk.Button(view_tab, text="Bathroom (2x2m)", command=lambda: app.insert_room_template("Bathroom", 2, 2)).pack(pady=2)
#     # tk.Button(view_tab, text="Kitchen (3x2.5m)", command=lambda: app.insert_room_template("Kitchen", 3, 2.5)).pack(pady=2)
#     tk.Button(draw_tab, text="Pick Fill Color", command=app.pick_fill_color, width=15).pack(pady=2)
#     tk.Button(draw_tab, text="Fill at Point", command=app.enable_fill_mode, width=15).pack(pady=2)



#     tk.Button(view_tab, text="Save Canvas", command=app.save_canvas, width=15).pack(pady=2)

#     tk.Label(view_tab, text="Furniture:").pack()
#     furniture_options = [
#     "Bed", "Chair", "Table", "Door", "Toilet", "Shower", "Sink",
#     "Dining", "Stove", "Fridge", "Computer", "TV", "Storage", "Window"
#      ]
#     tk.OptionMenu(view_tab, app.furniture_var, *furniture_options).pack(pady=2)
#     # tk.OptionMenu(view_tab, app.furniture_var, "Bed", "Table", "Chair", "Door").pack(pady=2)
#     tk.Button(view_tab, text="Place Furniture", command=app.enable_furniture_mode, width=15).pack(pady=2)
#     # tk.Button(view_tab, text="Increase Icon Size", command=app.increase_selected_icon_size).pack(pady=2)
#     # tk.Button(view_tab, text="Decrease Icon Size", command=app.decrease_selected_icon_size).pack(pady=2)
#     tk.Button(view_tab, text="Zoom In Furniture", command=app.zoom_in_furniture).pack(pady=2)
#     tk.Button(view_tab, text="Zoom Out Furniture", command=app.zoom_out_furniture).pack(pady=2)
#     # tk.Button(view_tab, text="Zoom In Canvas", command=app.zoom_in).pack(pady=2)
#     # tk.Button(view_tab, text="Zoom Out Canvas", command=app.zoom_out).pack(pady=2)
#     # Optional: add some widgets inside the new tab
#     tk.Label(abhishekcrazy_tab, text="Welcome to the abhishekcrazy tab!").pack(pady=10)
#     tk.Button(abhishekcrazy_tab, text="Do Something Crazy", command=lambda: print("Crazy action!")).pack(pady=5)

#     def draw_rectangle_from_ui():
#         try:
#             length = int(length_entry.get())
#             width = int(width_entry.get())
#             app.draw_rectangle(width, length)  # Pass to canvas manager
#         except ValueError:
#             print("Please enter valid integers for length and width.")

#     # UI inputs inside the tab
#     tk.Label(abhishekcrazy_tab, text="Enter length:").pack()
#     length_entry = tk.Entry(abhishekcrazy_tab)
#     length_entry.pack()

#     tk.Label(abhishekcrazy_tab, text="Enter width:").pack()
#     width_entry = tk.Entry(abhishekcrazy_tab)
#     width_entry.pack()

#     draw_button = tk.Button(abhishekcrazy_tab, text="Draw Rectangle", command=draw_rectangle_from_ui)
#     draw_button.pack(pady=10)

# # import tkinter as tk
# from tkinter import ttk#for tabs
# import math
# import tkinter as tk
# from tkinter import ttk

# def setup_toolbar(app, root):
#     # Create the main frame and pack it
#     main_frame = ttk.Frame(root)
#     main_frame.pack(fill=tk.BOTH, expand=True)

#     # Create a Notebook (tabbed interface)
#     notebook = ttk.Notebook(main_frame)
#     notebook.pack(side=tk.LEFT, fill=tk.Y)

#     # Create individual tabs
#     draw_tab = ttk.Frame(notebook)
#     edit_tab = ttk.Frame(notebook)
#     view_tab = ttk.Frame(notebook)

#     # Add tabs to notebook
#     notebook.add(draw_tab, text="Draw")
#     notebook.add(edit_tab, text="Edit")
#     notebook.add(view_tab, text="View")

#     # === DRAW TAB ===
#     tk.Button(draw_tab, text="Toggle Grid", command=app.toggle_grid).pack(pady=2)
#     tk.Button(draw_tab, text="Draw Line", command=app.enable_line_drawing, width=15).pack(pady=2)
#     tk.Button(draw_tab, text="Draw Polygon", command=app.enable_polygon_mode, width=15).pack(pady=2)
#     tk.Button(draw_tab, text="Finish Polygon", command=app.finish_polygon, width=15).pack(pady=2)
#     tk.Button(draw_tab, text="Undo", command=app.undo, width=15).pack(pady=2)

#     tk.Label(draw_tab, text="Line Style:").pack()
#     tk.OptionMenu(draw_tab, app.line_style_var, "solid", "bold", "dashed", command=app.change_line_style).pack(pady=2)
#     tk.Button(draw_tab, text="Pick Line Color", command=app.pick_line_color, width=15).pack(pady=2)
#     tk.Button(edit_tab, text="Eraser Tool", command=app.enable_eraser_mode, width=15).pack(pady=2)


    

#     # === EDIT TAB ===
    
#     tk.Button(edit_tab, text="Clear Canvas", command=app.clear_canvas, width=15).pack(pady=2)
#     tk.Label(edit_tab, text="Unit:").pack()
#     tk.OptionMenu(edit_tab, app.unit_var, *app.unit_scale.keys(), command=app.change_unit).pack(pady=2)

#     # === VIEW TAB ===
#     tk.Button(view_tab, text="Save Canvas", command=app.save_canvas, width=15).pack(pady=2)

#     tk.Label(view_tab, text="Furniture:").pack()
#     furniture_options = [
#     "Bed", "Chair", "Table", "Door", "Toilet", "Shower", "Sink",
#     "Dining", "Stove", "Fridge", "Computer", "TV", "Storage", "Window"
#      ]
#     tk.OptionMenu(view_tab, app.furniture_var, *furniture_options).pack(pady=2)
#     # tk.OptionMenu(view_tab, app.furniture_var, "Bed", "Table", "Chair", "Door").pack(pady=2)
#     tk.Button(view_tab, text="Place Furniture", command=app.enable_furniture_mode, width=15).pack(pady=2)
#     # tk.Button(view_tab, text="Increase Icon Size", command=app.increase_selected_icon_size).pack(pady=2)
#     # tk.Button(view_tab, text="Decrease Icon Size", command=app.decrease_selected_icon_size).pack(pady=2)
#     tk.Button(view_tab, text="Zoom In Furniture", command=app.zoom_in_furniture).pack(pady=2)
#     tk.Button(view_tab, text="Zoom Out Furniture", command=app.zoom_out_furniture).pack(pady=2)

# import tkinter as tk
# from tkinter import ttk#for tabs
# import math
# import tkinter as tk
# from tkinter import ttk
# from config import GRID_SPACING

# def setup_toolbar(app, root):
#     # Create the main frame and pack it
#     main_frame = ttk.Frame(root)
#     main_frame.pack(fill=tk.BOTH, expand=True)

#     # Create a Notebook (tabbed interface)
#     notebook = ttk.Notebook(main_frame)
#     notebook.pack(side=tk.LEFT, fill=tk.Y)

#     # Create individual tabs
#     draw_tab = ttk.Frame(notebook)
#     edit_tab = ttk.Frame(notebook)
#     view_tab = ttk.Frame(notebook)
#     abhishekcrazy_tab = ttk.Frame(notebook)

#     # Add tabs to notebook
#     notebook.add(draw_tab, text="Draw")
#     notebook.add(edit_tab, text="Edit")
#     notebook.add(view_tab, text="View")
#     notebook.add(abhishekcrazy_tab, text="abhishekcrazy")

#     # === DRAW TAB ===
#     # tk.Button(draw_tab, text="Toggle Grid", command=app.toggle_grid).pack(pady=2)
#     # tk.Button(draw_tab, text="Draw Line", command=app.enable_line_drawing, width=15).pack(pady=2)
#     tk.Button(draw_tab, text="🖊️ Line", command=app.enable_line_drawing, width=15).pack(pady=2)
#     tk.Button(draw_tab, text="Draw Polygon", command=app.enable_polygon_mode, width=15).pack(pady=2)
#     tk.Button(draw_tab, text="Finish Polygon", command=app.finish_polygon, width=15).pack(pady=2)
#     tk.Button(draw_tab, text="Undo", command=app.undo, width=15).pack(pady=2)
#     line_button = ttk.Button(draw_tab, text="Line by Length & Angle",
#                             command=lambda: app.activate_line_by_angle_mode())
#     line_button.pack(pady=5)
#     tk.Label(draw_tab, text="Line Style:").pack()
#     tk.OptionMenu(draw_tab, app.line_style_var, "solid", "bold", "dashed", command=app.change_line_style).pack(pady=2)
#     tk.Button(draw_tab, text="Pick Line Color", command=app.pick_line_color, width=15).pack(pady=2)
#     tk.Button(edit_tab, text="Eraser Tool", command=app.enable_eraser_mode, width=15).pack(pady=2)
    

#     # === EDIT TAB ===
    
#     tk.Button(edit_tab, text="Clear Canvas", command=app.clear_canvas, width=15).pack(pady=2)
#     tk.Label(edit_tab, text="Unit:").pack()
#     tk.OptionMenu(edit_tab, app.unit_var, *app.unit_scale.keys(), command=app.change_unit).pack(pady=2)
#     tk.Button(edit_tab, text="Insert Text", command=app.enable_text_insertion, width=15).pack(pady=2)

#     # tk.Button(edit_tab, text="Zoom In Canvas", command=app.zoom_in).pack(pady=2)
#     # tk.Button(edit_tab, text="Zoom Out Canvas", command=app.zoom_out).pack(pady=2)


#     # === VIEW TAB ===
#     tk.Button(view_tab, text="Save Canvas", command=app.save_canvas, width=15).pack(pady=2)

#     tk.Label(view_tab, text="Furniture:").pack()
#     furniture_options = [
#     "Bed", "Chair", "Table", "Door", "Toilet", "Shower", "Sink",
#     "Dining", "Stove", "Fridge", "Computer", "TV", "Storage", "Window"
#      ]
#     tk.OptionMenu(view_tab, app.furniture_var, *furniture_options).pack(pady=2)
#     # tk.OptionMenu(view_tab, app.furniture_var, "Bed", "Table", "Chair", "Door").pack(pady=2)
#     tk.Button(view_tab, text="Place Furniture", command=app.enable_furniture_mode, width=15).pack(pady=2)
#     # tk.Button(view_tab, text="Increase Icon Size", command=app.increase_selected_icon_size).pack(pady=2)
#     # tk.Button(view_tab, text="Decrease Icon Size", command=app.decrease_selected_icon_size).pack(pady=2)
#     tk.Button(view_tab, text="Zoom In Furniture", command=app.zoom_in_furniture).pack(pady=2)
#     tk.Button(view_tab, text="Zoom Out Furniture", command=app.zoom_out_furniture).pack(pady=2)
#     # tk.Button(view_tab, text="Zoom In Canvas", command=app.zoom_in).pack(pady=2)
#     # tk.Button(view_tab, text="Zoom Out Canvas", command=app.zoom_out).pack(pady=2)
#     # Optional: add some widgets inside the new tab
#     tk.Label(abhishekcrazy_tab, text="Welcome to the abhishekcrazy tab!").pack(pady=10)
#     tk.Button(abhishekcrazy_tab, text="Do Something Crazy", command=lambda: print("Crazy action!")).pack(pady=5)

#     def draw_rectangle_from_ui():
#         try:
#             length = int(length_entry.get())
#             width = int(width_entry.get())
#             app.draw_rectangle(width, length)  # Pass to canvas manager
#         except ValueError:
#             print("Please enter valid integers for length and width.")

#     # UI inputs inside the tab
#     tk.Label(abhishekcrazy_tab, text="Enter length:").pack()
#     length_entry = tk.Entry(abhishekcrazy_tab)
#     length_entry.pack()

#     tk.Label(abhishekcrazy_tab, text="Enter width:").pack()
#     width_entry = tk.Entry(abhishekcrazy_tab)
#     width_entry.pack()

#     draw_button = tk.Button(abhishekcrazy_tab, text="Draw Rectangle", command=draw_rectangle_from_ui)
#     draw_button.pack(pady=10)
#     tk.Button(abhishekcrazy_tab, text="Toggle Rectangle Grid", command=app.toggle_rectangle_grid).pack(pady=5)

# import tkinter as tk
# from tkinter import ttk#for tabs
# import math
# import tkinter as tk
# from tkinter import ttk

# def setup_toolbar(app, root):
#     # Create the main frame and pack it
#     main_frame = ttk.Frame(root)
#     main_frame.pack(fill=tk.BOTH, expand=True)

#     # Create a Notebook (tabbed interface)
#     notebook = ttk.Notebook(main_frame)
#     notebook.pack(side=tk.LEFT, fill=tk.Y)

#     # Create individual tabs
#     draw_tab = ttk.Frame(notebook)
#     edit_tab = ttk.Frame(notebook)
#     view_tab = ttk.Frame(notebook)

#     # Add tabs to notebook
#     notebook.add(draw_tab, text="Draw")
#     notebook.add(edit_tab, text="Edit")
#     notebook.add(view_tab, text="View")

#     # === DRAW TAB ===
#     tk.Button(draw_tab, text="Toggle Grid", command=app.toggle_grid).pack(pady=2)
#     tk.Button(draw_tab, text="Draw Line", command=app.enable_line_drawing, width=15).pack(pady=2)
#     tk.Button(draw_tab, text="Draw Polygon", command=app.enable_polygon_mode, width=15).pack(pady=2)
#     tk.Button(draw_tab, text="Finish Polygon", command=app.finish_polygon, width=15).pack(pady=2)
#     tk.Button(draw_tab, text="Undo", command=app.undo, width=15).pack(pady=2)

#     tk.Label(draw_tab, text="Line Style:").pack()
#     tk.OptionMenu(draw_tab, app.line_style_var, "solid", "bold", "dashed", command=app.change_line_style).pack(pady=2)
#     tk.Button(draw_tab, text="Pick Line Color", command=app.pick_line_color, width=15).pack(pady=2)
#     tk.Button(edit_tab, text="Eraser Tool", command=app.enable_eraser_mode, width=15).pack(pady=2)
    

#     # === EDIT TAB ===
    
#     tk.Button(edit_tab, text="Clear Canvas", command=app.clear_canvas, width=15).pack(pady=2)
#     tk.Label(edit_tab, text="Unit:").pack()
#     tk.OptionMenu(edit_tab, app.unit_var, *app.unit_scale.keys(), command=app.change_unit).pack(pady=2)
#     # tk.Button(edit_tab, text="Zoom In Canvas", command=app.zoom_in).pack(pady=2)
#     # tk.Button(edit_tab, text="Zoom Out Canvas", command=app.zoom_out).pack(pady=2)


#     # === VIEW TAB ===
#     tk.Button(view_tab, text="Save Canvas", command=app.save_canvas, width=15).pack(pady=2)

#     tk.Label(view_tab, text="Furniture:").pack()
#     furniture_options = [
#     "Bed", "Chair", "Table", "Door", "Toilet", "Shower", "Sink",
#     "Dining", "Stove", "Fridge", "Computer", "TV", "Storage", "Window"
#      ]
#     tk.OptionMenu(view_tab, app.furniture_var, *furniture_options).pack(pady=2)
#     # tk.OptionMenu(view_tab, app.furniture_var, "Bed", "Table", "Chair", "Door").pack(pady=2)
#     tk.Button(view_tab, text="Place Furniture", command=app.enable_furniture_mode, width=15).pack(pady=2)
#     # tk.Button(view_tab, text="Increase Icon Size", command=app.increase_selected_icon_size).pack(pady=2)
#     # tk.Button(view_tab, text="Decrease Icon Size", command=app.decrease_selected_icon_size).pack(pady=2)
#     tk.Button(view_tab, text="Zoom In Furniture", command=app.zoom_in_furniture).pack(pady=2)
#     tk.Button(view_tab, text="Zoom Out Furniture", command=app.zoom_out_furniture).pack(pady=2)
#     # tk.Button(view_tab, text="Zoom In Canvas", command=app.zoom_in).pack(pady=2)
#     # tk.Button(view_tab, text="Zoom Out Canvas", command=app.zoom_out).pack(pady=2)

# # import tkinter as tk
# # from tkinter import ttk#for tabs
# # import math
# # import tkinter as tk
# # from tkinter import ttk

# # def setup_toolbar(app, root):
# #     # Create the main frame and pack it
# #     main_frame = ttk.Frame(root)
# #     main_frame.pack(fill=tk.BOTH, expand=True)

# #     # Create a Notebook (tabbed interface)
# #     notebook = ttk.Notebook(main_frame)
# #     notebook.pack(side=tk.LEFT, fill=tk.Y)

# #     # Create individual tabs
# #     draw_tab = ttk.Frame(notebook)
# #     edit_tab = ttk.Frame(notebook)
# #     view_tab = ttk.Frame(notebook)

# #     # Add tabs to notebook
# #     notebook.add(draw_tab, text="Draw")
# #     notebook.add(edit_tab, text="Edit")
# #     notebook.add(view_tab, text="View")

# #     # === DRAW TAB ===
# #     tk.Button(draw_tab, text="Toggle Grid", command=app.toggle_grid).pack(pady=2)
# #     tk.Button(draw_tab, text="Draw Line", command=app.enable_line_drawing, width=15).pack(pady=2)
# #     tk.Button(draw_tab, text="Draw Polygon", command=app.enable_polygon_mode, width=15).pack(pady=2)
# #     tk.Button(draw_tab, text="Finish Polygon", command=app.finish_polygon, width=15).pack(pady=2)
# #     tk.Button(draw_tab, text="Undo", command=app.undo, width=15).pack(pady=2)

# #     tk.Label(draw_tab, text="Line Style:").pack()
# #     tk.OptionMenu(draw_tab, app.line_style_var, "solid", "bold", "dashed", command=app.change_line_style).pack(pady=2)
# #     tk.Button(draw_tab, text="Pick Line Color", command=app.pick_line_color, width=15).pack(pady=2)
# #     tk.Button(edit_tab, text="Eraser Tool", command=app.enable_eraser_mode, width=15).pack(pady=2)


    

# #     # === EDIT TAB ===
    
# #     tk.Button(edit_tab, text="Clear Canvas", command=app.clear_canvas, width=15).pack(pady=2)
# #     tk.Label(edit_tab, text="Unit:").pack()
# #     tk.OptionMenu(edit_tab, app.unit_var, *app.unit_scale.keys(), command=app.change_unit).pack(pady=2)

# #     # === VIEW TAB ===
# #     tk.Button(view_tab, text="Save Canvas", command=app.save_canvas, width=15).pack(pady=2)

# #     tk.Label(view_tab, text="Furniture:").pack()
# #     furniture_options = [
# #     "Bed", "Chair", "Table", "Door", "Toilet", "Shower", "Sink",
# #     "Dining", "Stove", "Fridge", "Computer", "TV", "Storage", "Window"
# #      ]
# #     tk.OptionMenu(view_tab, app.furniture_var, *furniture_options).pack(pady=2)
# #     # tk.OptionMenu(view_tab, app.furniture_var, "Bed", "Table", "Chair", "Door").pack(pady=2)
# #     tk.Button(view_tab, text="Place Furniture", command=app.enable_furniture_mode, width=15).pack(pady=2)
# #     # tk.Button(view_tab, text="Increase Icon Size", command=app.increase_selected_icon_size).pack(pady=2)
# #     # tk.Button(view_tab, text="Decrease Icon Size", command=app.decrease_selected_icon_size).pack(pady=2)
# #     tk.Button(view_tab, text="Zoom In Furniture", command=app.zoom_in_furniture).pack(pady=2)
# #     tk.Button(view_tab, text="Zoom Out Furniture", command=app.zoom_out_furniture).pack(pady=2)
