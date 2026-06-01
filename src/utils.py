import hashlib
import os
from functools import lru_cache
from PIL import Image, ImageTk

def calculate_file_hash(file_path, hash_algorithm=hashlib.sha256):
    h = hash_algorithm()
    try:
        with open(file_path, 'rb') as f:
            while chunk := f.read(4096):
                h.update(chunk)
        return h.hexdigest()
    except Exception:
        return None

class IconCache:
    """Caches tool icons to improve performance."""
    def __init__(self, max_size=100):
        self.cache = {}
        self.max_size = max_size
        self.access_order = []

    @lru_cache(maxsize=100)
    def _load_and_resize_image(self, path, size=(48, 48)):
        """Loads and resizes an image with LRU caching."""
        try:
            img = Image.open(path)
            img = img.resize(size, Image.Resampling.LANCZOS)
            return ImageTk.PhotoImage(img)
        except Exception:
            return None

    def get_icon(self, tool_info, size=(48, 48)):
        """Gets a tool's icon from the cache or loads it if necessary."""
        cache_key_part = tool_info.get('exe_path')
        if not cache_key_part: 
            return None
        
        cache_key = f"{cache_key_part}_{size}"

        if cache_key in self.cache:
            self.access_order.remove(cache_key)
            self.access_order.append(cache_key)
            return self.cache[cache_key]

        tool_icon_path = None
        if tool_info.get("is_official", False):
            if tool_info.get("icon_file") and tool_info.get("folder_path"):
                potential_icon_path = os.path.join(tool_info["folder_path"], tool_info["icon_file"])
                if os.path.exists(potential_icon_path):
                    tool_icon_path = potential_icon_path
        
        path_to_load = tool_icon_path
        photo_image = self._load_and_resize_image(path_to_load, size)

        if photo_image:
            self.cache[cache_key] = photo_image
            self.access_order.append(cache_key)
            if len(self.cache) > self.max_size:
                oldest_key = self.access_order.pop(0)
                del self.cache[oldest_key]
            return photo_image

        return None

    def clear(self):
        """Clears the icon cache."""
        self.cache.clear()
        self.access_order.clear()
