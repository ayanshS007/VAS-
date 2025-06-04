    # Layer Management Methods
    def assign_layer(self, object_id, layer=None):
        """Assign a layer to an object"""
        if layer is None:
            layer = self.current_layer
        
        self.layer_manager[object_id] = layer
        if layer > self.max_layer:
            self.max_layer = layer
        
        self.update_visual_stacking()

    def assign_layer_to_group(self, object_ids, layer=None):
        """Assign the same layer to multiple objects (like grouped items)"""
        if layer is None:
            layer = self.current_layer
        
        for obj_id in object_ids:
            self.layer_manager[obj_id] = layer
        
        if layer > self.max_layer:
            self.max_layer = layer
        
        self.update_visual_stacking()

    def update_visual_stacking(self):
        """Update the visual stacking order based on layer assignments"""
        if not self.layer_manager:
            return
        
        # Get all objects and their layers, sorted by layer number
        objects_by_layer = []
        for obj_id, layer in self.layer_manager.items():
            try:
                # Check if object still exists on canvas
                if self.canvas.type(obj_id):
                    objects_by_layer.append((layer, obj_id))
            except:
                # Object was deleted, remove from layer manager
                continue
        
        # Sort by layer (lowest first) and update stacking
        objects_by_layer.sort(key=lambda x: x[0])
        
        # Apply stacking order - lower layers first, higher layers on top
        for i, (layer, obj_id) in enumerate(objects_by_layer):
            try:
                # Move to bottom first, then raise to proper level
                self.canvas.tag_lower(obj_id)
            except:
                continue
        
        # Now raise objects in order from lowest to highest layer
        for layer, obj_id in objects_by_layer:
            try:
                self.canvas.tag_raise(obj_id)
            except:
                continue
        
        # Keep selection outline on top if it exists
        if self.selection_outline:
            self.canvas.tag_raise(self.selection_outline)


    def select_object(self, object_id):
        """Select an object for layer operations"""
        if object_id == self.selected_object:
            return
        
        # Clear previous selection
        self.clear_selection()
        
        # Set new selection
        self.selected_object = object_id
        self.show_selection_feedback(object_id)

    def clear_selection(self):
        """Clear current selection"""
        self.selected_object = None
        self.hide_selection_feedback()

    def show_selection_feedback(self, object_id):
        """Show visual feedback for selected object"""
        try:
            # Get object bounds
            bbox = self.canvas.bbox(object_id)
            if bbox:
                x1, y1, x2, y2 = bbox
                # Create selection outline
                self.selection_outline = self.canvas.create_rectangle(
                    x1-2, y1-2, x2+2, y2+2,
                    outline="red", width=2, dash=(5, 5),
                    tags=("selection_outline",)
                )
                # Ensure selection outline is on top
                self.canvas.tag_raise(self.selection_outline)
        except:
            pass

    def hide_selection_feedback(self):
        """Hide selection visual feedback"""
        if self.selection_outline:
            self.canvas.delete(self.selection_outline)
            self.selection_outline = None
        
        for handle in self.selection_handles:
            self.canvas.delete(handle)
        self.selection_handles.clear()

    
    def bring_forward(self):
        """Bring selected object one layer forward"""
        if not self.selected_object or self.selected_object not in self.layer_manager:
            print("No object selected for layer operation")
            return
        
        current_layer = self.layer_manager[self.selected_object]


         # Find next occupied layer above current
        layers_above = [l for l in self.layer_manager.values() if l > current_layer]
        new_layer = current_layer + 1 if not layers_above else min(layers_above) + 1

        # Update layer tracking
        self.max_layer = max(self.max_layer, new_layer)
        self._update_object_layer(new_layer)

            new_layer = current_layer + 1
        
        # Update max_layer
        if new_layer > self.max_layer:
            self.max_layer = new_layer

        else:
            # Find next available layer within existing range
            while new_layer <= self.max_layer and any(v == new_layer for v in self.layer_manager.values()):
                new_layer += 1
            self.max_layer = max(self.max_layer, new_layer)
        
        # Update layer for selected object
        self.layer_manager[self.selected_object] = new_layer
        
        # Handle grouped objects
        if self.selected_object in self.object_metadata:
            metadata = self.object_metadata[self.selected_object]
            if "group" in metadata and metadata["group"]:
                for group_obj in metadata["group"]:
                    if group_obj != self.selected_object and group_obj in self.layer_manager:
                        self.layer_manager[group_obj] = new_layer
        
        # CRITICAL: Force immediate visual update
        self.update_visual_stacking()
        self.show_selection_feedback(self.selected_object)
        print(f"Brought object {self.selected_object} forward to layer {new_layer}")

    def send_back(self):
        """Send selected object one layer back"""
        if not self.selected_object or self.selected_object not in self.layer_manager:
            print("No object selected for layer operation")
            return
        
        current_layer = self.layer_manager[self.selected_object]
        new_layer = max(0, current_layer - 1)  # Don't go below 0
        
        # Update layer for selected object
        self.layer_manager[self.selected_object] = new_layer
        
        # Handle grouped objects
        if self.selected_object in self.object_metadata:
            metadata = self.object_metadata[self.selected_object]
            if "group" in metadata and metadata["group"]:
                for group_obj in metadata["group"]:
                    if group_obj != self.selected_object and group_obj in self.layer_manager:
                        self.layer_manager[group_obj] = new_layer
        
        # CRITICAL: Force immediate visual update
        self.update_visual_stacking()
        self.show_selection_feedback(self.selected_object)
        print(f"Sent object {self.selected_object} back to layer {new_layer}")


    def get_object_layer(self, object_id):
        """Get the layer number of an object"""
        return self.layer_manager.get(object_id, 0)

    def get_selected_object_info(self):
        """Get information about the currently selected object"""
        if not self.selected_object:
            return None
        
        layer = self.get_object_layer(self.selected_object)
        obj_type = "unknown"
        
        if self.selected_object in self.object_metadata:
            obj_type = self.object_metadata[self.selected_object].get("type", "unknown")
        
        return {
            "id": self.selected_object,
            "layer": layer,
            "type": obj_type
        }

    def debug_layers(self):
        """Debug method to check layer assignments"""
        print("=== LAYER DEBUG ===")
        print(f"Selected object: {self.selected_object}")
        print(f"Layer manager entries: {len(self.layer_manager)}")
        
        for obj_id, layer in sorted(self.layer_manager.items(), key=lambda x: x[1]):
            try:
                obj_type = self.canvas.type(obj_id)
                metadata = self.object_metadata.get(obj_id, {}).get("type", "unknown")
                print(f"ID {obj_id}: Layer {layer}, Type: {obj_type}, Meta: {metadata}")
            except:
                print(f"ID {obj_id}: Layer {layer}, DELETED/INVALID")
        print("==================")
        


        # Sidebar for image furniture
        # self._setup_image_furniture_sidebar(left_panel)
