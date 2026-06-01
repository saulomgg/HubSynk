import os
import json
import shutil
from tkinter import messagebox
from .constants import APP_DATA_PATH, TOOLS_DIR, HUB_CONFIG_FILE

class HubSynkConfig:
    """Manages HubSynk's configuration and tool list."""

    def __init__(self):
        self.app_data_path = APP_DATA_PATH
        self.tools_path = TOOLS_DIR
        self.config_file = HUB_CONFIG_FILE
        self.logs_path = os.path.join(self.app_data_path, "logs")
        self._create_directory_structure()
        self.config = self._load_config()

    def _create_directory_structure(self):
        for directory in [self.app_data_path, self.tools_path, self.logs_path]:
            os.makedirs(directory, exist_ok=True)

    def _load_config(self):
        default_config = {"version": "1.0", "tools": []}
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                messagebox.showwarning("Corrupt Configuration", "HubSynk's configuration file is corrupt and will be reset.")
                self._save_config(default_config)
                return default_config
        else:
            self._save_config(default_config)
            return default_config

    def _save_config(self, config=None):
        if config is None:
            config = self.config
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
        except IOError as e:
            messagebox.showerror("Save Error", f"Could not save HubSynk configuration: {e}")

    def add_tool(self, tool_info):
        tool_id = tool_info.get('exe_path')
        
        existing_tool_index = -1
        for i, tool in enumerate(self.config["tools"]):
            if tool.get('exe_path') == tool_id:
                existing_tool_index = i
                break

        if existing_tool_index == -1:
            self.config["tools"].append(tool_info)
        else:
            self.config["tools"][existing_tool_index].update(tool_info)
        
        self._save_config()

    def remove_tool(self, tool_info_to_remove):
        tool_id_to_remove = tool_info_to_remove.get('exe_path')
        
        original_tool_count = len(self.config["tools"])
        self.config["tools"] = [t for t in self.config["tools"] if t.get('exe_path') != tool_id_to_remove]

        if len(self.config["tools"]) < original_tool_count:
            self._save_config()
            
            folder_to_delete = tool_info_to_remove.get("folder_path")
            if tool_info_to_remove.get("is_official") and folder_to_delete and os.path.exists(folder_to_delete):
                if os.path.commonpath([self.tools_path, os.path.abspath(folder_to_delete)]) == os.path.abspath(self.tools_path):
                    try:
                        shutil.rmtree(folder_to_delete)
                        messagebox.showinfo("Tool Removed", f"The tool '{tool_info_to_remove['name']}' and its files have been removed.")
                    except Exception as e:
                        messagebox.showwarning("Removal Error", f"Could not remove the tool's folder '{tool_info_to_remove['name']}': {e}")
                else:
                    messagebox.showwarning("Security Warning", "Attempted to remove a folder outside of the HubSynk directory. Operation cancelled.")
            else:
                 messagebox.showinfo("Tool Removed", f"The tool '{tool_info_to_remove['name']}' has been removed from the list.")
        else:
            messagebox.showwarning("Removal Error", "Tool not found in configuration.")

    def get_tools(self):
        return self.config.get("tools", [])

    def update_favorite_status(self, tool_info, is_favorite):
        tool_id = tool_info.get('exe_path')
        for tool in self.config["tools"]:
            if tool.get('exe_path') == tool_id:
                tool['is_favorite'] = is_favorite
                self._save_config()
                return
        messagebox.showerror("Error", "Tool not found in configuration to update favorite status.")
