"""
Saulomgg, hubsynk1.0
HubSynk - Your Essential Windows Productivity Hub

Este é um projeto open source. Sinta-se à vontade para usar, modificar e distribuir.
Acompanhe o desenvolvimento e apoie o projeto no GitHub: https://github.com/saulomgg/
Siga nas redes sociais para atualizações e dicas!

GitHub: https://github.com/saulomgg/
Comunidade: Acesse via GitHub Issues/Discussions
"""

import tkinter as tk
import multiprocessing
import sys
from src.config_manager import HubSynkConfig
from src.tool_processor import ToolProcessor
from src.tool_launcher import ToolLauncher
from src.ui import HubSynkApp

def main():
    # Suporte para multiprocessing quando compilado com PyInstaller
    if getattr(sys, 'frozen', False):
        multiprocessing.freeze_support()
        
    root = tk.Tk()
    
    # Initialize components
    config_manager = HubSynkConfig()
    tool_processor = ToolProcessor(config_manager)
    tool_launcher = ToolLauncher()
    
    # Initialize UI
    app = HubSynkApp(root, config_manager, tool_processor, tool_launcher)
    
    root.mainloop()

if __name__ == "__main__":
    main()
