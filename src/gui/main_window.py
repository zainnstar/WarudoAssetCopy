import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from src.gui.asset_list_frame import AssetListFrame
from src.models.scene_data import SceneData

class MainWindow:
    def __init__(self, root):
        self.root = root
        self.root.title("Warudo Asset Copy Tool")
        self.root.geometry("1200x600")
        
        # Create main container
        main_container = ttk.Frame(root)
        main_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create top frame for buttons
        btn_frame = ttk.Frame(main_container)
        btn_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Create load buttons
        ttk.Button(btn_frame, text="Load Left Scene", command=self.load_left_scene).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Load Right Scene", command=self.load_right_scene).pack(side=tk.LEFT, padx=5)
        
        # Create middle frame for asset lists
        list_frame = ttk.Frame(main_container)
        list_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create left and right asset list frames
        self.left_frame = AssetListFrame(list_frame, "Source Scene")
        self.left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        
        # Create middle buttons frame
        mid_btn_frame = ttk.Frame(list_frame)
        mid_btn_frame.pack(side=tk.LEFT, padx=10)
        
        ttk.Button(mid_btn_frame, text="Copy →", command=self.copy_right).pack(pady=5)
        ttk.Button(mid_btn_frame, text="← Copy", command=self.copy_left).pack(pady=5)
        
        self.right_frame = AssetListFrame(list_frame, "Target Scene")
        self.right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5, 0))
        self.left_scene = None
        self.right_scene = None

    def load_left_scene(self):
        """Load the left scene"""
        file_path = filedialog.askopenfilename(
            filetypes=[("JSON files", "*.json")],
            title="Select Source Scene File"
        )
        if file_path:
            try:
                self.left_scene = SceneData(file_path)
                self.left_frame.set_file_path(file_path)
                self.left_frame.load_assets(self.left_scene)
            except Exception as e:
                messagebox.showerror("Error", str(e))

    def load_right_scene(self):
        """Load the right scene"""
        file_path = filedialog.askopenfilename(
            filetypes=[("JSON files", "*.json")],
            title="Select Target Scene File"
        )
        if file_path:
            try:
                self.right_scene = SceneData(file_path)
                self.right_frame.set_file_path(file_path)
                self.right_frame.load_assets(self.right_scene)
            except Exception as e:
                messagebox.showerror("Error", str(e))

    def copy_right(self):
        """Copy selected assets from left to right"""
        if not self.left_scene or not self.right_scene:
            messagebox.showwarning("Warning", "Please load both scenes first")
            return
            
        selected_assets = self.left_frame.get_selected_assets()
        if not selected_assets:
            messagebox.showinfo("Info", "No assets selected")
            return
            
        success = True
        for asset_path in selected_assets:
            if not self.left_scene.copy_asset(asset_path, self.right_scene):
                success = False
                
        if success:
            self.right_scene.save()
            self.right_frame.load_assets(self.right_scene)
            self.left_frame.clear_selection()
            messagebox.showinfo("Success", "Assets copied successfully")
        else:
            messagebox.showerror("Error", "Some assets could not be copied")

    def copy_left(self):
        """Copy selected assets from right to left"""
        if not self.left_scene or not self.right_scene:
            messagebox.showwarning("Warning", "Please load both scenes first")
            return
            
        selected_assets = self.right_frame.get_selected_assets()
        if not selected_assets:
            messagebox.showinfo("Info", "No assets selected")
            return
            
        success = True
        for asset_path in selected_assets:
            if not self.right_scene.copy_asset(asset_path, self.left_scene):
                success = False
                
        if success:
            self.left_scene.save()
            self.left_frame.load_assets(self.left_scene)
            self.right_frame.clear_selection()
            messagebox.showinfo("Success", "Assets copied successfully")
        else:
            messagebox.showerror("Error", "Some assets could not be copied")
