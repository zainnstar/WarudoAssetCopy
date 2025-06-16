from src.utils.json_handler import JsonHandler

class SceneData:
    def __init__(self, file_path=None):
        self.file_path = file_path
        self.data = {}
        if file_path:
            self.load()

    def load(self):
        """Load scene data from JSON file"""
        self.data = JsonHandler.load_json(self.file_path)

    def save(self):
        """Save scene data to JSON file"""
        if self.file_path:
             JsonHandler.save_json(self.file_path, self.data)
    def get_asset_list(self):
        """Return list of assets in the scene with hierarchy information"""
        assets = []
        if not self.data or "assets" not in self.data:
            return assets
        
        # Create asset ID to hierarchy mapping
        hierarchy_map = self._build_hierarchy_map()
        
        # Extract assets from the actual Warudo JSON structure  
        for asset in self.data["assets"]:
            asset_name = asset.get("name", "Unknown")
            asset_id = asset.get("id", "")
            asset_type_id = asset.get("typeId", "")
            
            # Determine asset type based on typeId
            if asset_type_id == "6a05ecf3-1501-4cab-b9d7-84131b881a29":
                asset_type = "カメラ"
            elif asset_type_id == "945f0112-8ebe-4c5e-bda2-700925489a57":
                asset_type = "道具"
            else:
                asset_type = "その他"
            
            # Get hierarchy path for this asset
            hierarchy = hierarchy_map.get(asset_id, "")
            
            # Return (type, name, hierarchy) tuple for GUI compatibility
            assets.append((asset_type, asset_name, hierarchy))
        
        return assets

    def _build_hierarchy_map(self):
        """Build a mapping from asset ID to hierarchy path"""
        hierarchy_map = {}
        
        if not self.data or "assetHierarchy" not in self.data:
            return hierarchy_map
        
        def traverse_hierarchy(node, path=""):
            """Recursively traverse hierarchy tree"""
            if not node:
                return
            
            key = node.get("key", "")
            current_path = path
            
            # Add current key to path if it's not empty and not an asset ID
            if key and not self._is_asset_id(key):
                current_path = f"{path}/{key}" if path else key
            elif key and self._is_asset_id(key):
                # This is an asset ID, map it to the current hierarchy path
                hierarchy_map[key] = current_path
            
            # Process children
            children = node.get("children")
            if children:
                for child in children:
                    traverse_hierarchy(child, current_path)
        
        # Start traversal from root
        hierarchy_root = self.data["assetHierarchy"]
        if "children" in hierarchy_root:
            for child in hierarchy_root["children"]:
                traverse_hierarchy(child)
        
        return hierarchy_map
    
    def _is_asset_id(self, key):
        """Check if a key looks like an asset ID (UUID format)"""
        import re
        # UUID pattern: 8-4-4-4-12 hexadecimal characters
        uuid_pattern = r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$'
        return bool(re.match(uuid_pattern, key.lower()))
    def copy_asset(self, asset_name, target_scene):
        """Copy asset from this scene to target scene by asset name, including hierarchy"""
        if not self.data or "assets" not in self.data:
            return False
        
        if not target_scene.data:
            target_scene.data = {}
        if "assets" not in target_scene.data:
            target_scene.data["assets"] = []
        
        # Find the asset to copy
        asset_to_copy = None
        asset_id = None
        for asset in self.data["assets"]:
            if asset.get("name") == asset_name:
                asset_to_copy = asset.copy()
                asset_id = asset.get("id")
                break
        
        if not asset_to_copy:
            return False
        # Check if asset already exists in target and generate unique name
        original_name = asset_to_copy.get("name")
        unique_name = self._generate_unique_name(original_name, target_scene)
        asset_to_copy["name"] = unique_name
        
        # Add the asset to target scene
        target_scene.data["assets"].append(asset_to_copy)
        
        # Copy hierarchy information if it exists
        if asset_id and self.data.get("assetHierarchy"):
            self._copy_asset_hierarchy(asset_id, target_scene)
        
        return True
    
    def _copy_asset_hierarchy(self, asset_id, target_scene):
        """Copy hierarchy path for the specified asset to target scene"""
        if not target_scene.data.get("assetHierarchy"):
            target_scene.data["assetHierarchy"] = {"collapsed": False, "key": "", "children": []}
        
        # Find the hierarchy path for this asset
        hierarchy_path = self._find_asset_hierarchy_path(asset_id)
        if hierarchy_path:
            # Ensure the hierarchy path exists in target scene
            self._ensure_hierarchy_path(hierarchy_path, asset_id, target_scene)
    
    def _find_asset_hierarchy_path(self, asset_id):
        """Find the hierarchy path for a given asset ID"""
        if not self.data or "assetHierarchy" not in self.data:
            return []
        
        def search_in_node(node, path):
            if not node:
                return None
            
            key = node.get("key", "")
            current_path = path[:]
            
            # Add current key to path if it's not an asset ID
            if key and not self._is_asset_id(key):
                current_path.append(key)
            elif key == asset_id:
                # Found the asset
                return current_path
            
            # Search in children
            children = node.get("children")
            if children:
                for child in children:
                    result = search_in_node(child, current_path)
                    if result is not None:
                        return result
            
            return None
        
        # Start search from root
        hierarchy_root = self.data["assetHierarchy"]
        if "children" in hierarchy_root:
            for child in hierarchy_root["children"]:
                result = search_in_node(child, [])
                if result is not None:
                    return result
        
        return []
    
    def _ensure_hierarchy_path(self, path, asset_id, target_scene):
        """Ensure hierarchy path exists in target scene and add asset to it"""
        current_node = target_scene.data["assetHierarchy"]
        
        # Navigate/create the path
        for category in path:
            if not current_node.get("children"):
                current_node["children"] = []
            
            # Find or create the category node
            found_node = None
            for child in current_node["children"]:
                if child.get("key") == category:
                    found_node = child
                    break
            
            if not found_node:
                # Create new category node
                found_node = {
                    "collapsed": False,
                    "key": category,
                    "children": []
                }
                current_node["children"].append(found_node)
            
            current_node = found_node
        
        # Add the asset to the final category
        if not current_node.get("children"):
            current_node["children"] = []
        
        # Check if asset already exists in this hierarchy
        asset_exists = False
        for child in current_node["children"]:
            if child.get("key") == asset_id:
                asset_exists = True
                break
        
        if not asset_exists:
            # Add asset node
            asset_node = {
                "collapsed": False,
                "key": asset_id,
                "children": None
            }
            current_node["children"].append(asset_node)
    
    def _generate_unique_name(self, original_name, target_scene):
        """Generate unique name following Warudo naming convention"""
        if not target_scene.data or "assets" not in target_scene.data:
            return original_name
        
        # Get all existing asset names in target scene
        existing_names = set()
        for asset in target_scene.data["assets"]:
            existing_names.add(asset.get("name", ""))
        
        # If original name doesn't exist, return as is
        if original_name not in existing_names:
            return original_name
          # Generate unique name following Warudo convention
        import re
        
        # Check if original name already follows the pattern "base name + space + number"
        match = re.search(r'^(.+) (\d+)$', original_name)
        
        if match:
            # Name already has "base + space + number" format (e.g., "道具 1")
            base_name = match.group(1)  # "道具"
            start_counter = int(match.group(2)) + 1  # Start from next number
            
            counter = start_counter
            while True:
                new_name = f"{base_name} {counter}"
                if new_name not in existing_names:
                    return new_name
                counter += 1
                
                # Safety check
                if counter > 1000:
                    return f"{base_name} {counter}"
        else:
            # Name doesn't have the space+number format (e.g., "道具", "道具1")
            counter = 1
            while True:
                new_name = f"{original_name} {counter}"
                if new_name not in existing_names:
                    return new_name
                counter += 1
                
                # Safety check
                if counter > 1000:
                    return f"{original_name} {counter}"
