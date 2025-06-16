import tkinter as tk
from tkinter import ttk

class AssetListFrame(ttk.Frame):
    def __init__(self, parent, title, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        
        # Create title label
        title_label = ttk.Label(self, text=title)
        title_label.pack(pady=5)
        
        # Create file path label
        self.file_path_label = ttk.Label(self, text="No file selected", wraplength=250)
        self.file_path_label.pack(pady=5)
          # Create treeview
        self.tree = ttk.Treeview(self, selectmode='extended')
        self.tree.pack(pady=5, fill=tk.BOTH, expand=True)
          # Configure treeview columns
        self.tree["columns"] = ("selected", "type", "path", "hierarchy")
        self.tree.column("#0", width=0, stretch=False)  # Hide default column
        self.tree.column("selected", width=50, stretch=False)
        self.tree.column("type", width=100)
        self.tree.column("path", width=200)
        self.tree.column("hierarchy", width=150)
        
        # Configure treeview headings
        self.tree.heading("#0", text="")
        self.tree.heading("selected", text="Select")
        self.tree.heading("type", text="Type")
        self.tree.heading("path", text="AssetName")
        self.tree.heading("hierarchy", text="Group")
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.tree.yview)
        scrollbar.pack(side="right", fill="y")
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        # Variables to store data
        self.scene_data = None
        self.selected_items = set()
        # Bind events
        self.tree.bind('<Button-1>', self.on_click)

    def set_file_path(self, path):
        """Update the displayed file path"""
        if path:
            self.file_path_label.config(text=path)
        else:
            self.file_path_label.config(text="No file selected")
    def load_assets(self, scene_data):
        """Load assets from scene data into the treeview"""
        self.scene_data = scene_data
        self.tree.delete(*self.tree.get_children())
        self.selected_items.clear()
        
        if not scene_data:
            return
            
        for asset_type, asset_path, hierarchy in scene_data.get_asset_list():
            self.tree.insert("", "end", values=("[ ]", asset_type, asset_path, hierarchy))

    def on_click(self, event):
        """Handle click events on the treeview"""
        region = self.tree.identify_region(event.x, event.y)
        if region == "cell":
            item = self.tree.identify_row(event.y)
            if item:
                values = list(self.tree.item(item)["values"])
                if item in self.selected_items:
                    # Unselect
                    values[0] = "[ ]"
                    self.tree.item(item, values=values)
                    self.selected_items.remove(item)
                else:
                    # Select
                    values[0] = "[X]"
                    self.tree.item(item, values=values)
                    self.selected_items.add(item)

    def get_selected_assets(self):
        """Return list of selected asset paths"""
        selected_assets = []
        for item in self.selected_items:
            values = self.tree.item(item)["values"]
            if values and len(values) >= 3:
                selected_assets.append(values[2])  # Get the asset path (third column)
        return selected_assets

    def clear_selection(self):
        """Clear all selections"""
        for item in self.selected_items:
            values = list(self.tree.item(item)["values"])
            if values:
                values[0] = "[ ]"
                self.tree.item(item, values=values)
        self.selected_items.clear()
