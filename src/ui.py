import tkinter as tk
from tkinter import ttk, filedialog, messagebox, Menu
import webbrowser
from datetime import datetime
import os
from .constants import *
from .utils import IconCache
from .github_manager import GitHubManager

class HubSynkApp:
    def __init__(self, root, config_manager, tool_processor, tool_launcher):
        # Esconde a janela durante a configuração para evitar o "pulo" de tamanho
        root.withdraw()
        
        self.github_manager = GitHubManager(config_manager)
        self.root = root
        self.config_manager = config_manager
        self.tool_processor = tool_processor
        self.tool_launcher = tool_launcher
        self.icon_cache = IconCache()
        
        # --- CORREÇÃO DO ÍCONE (Substitui a pena do Python) ---
        self._set_window_icon()
        
        self.root.title(f"HubSynk v1.0 - {DEVELOPER_INFO}")
        
        # Configura o tamanho e posição antes de mostrar
        self.root.geometry("900x700")
        self.root.configure(bg=WIN_BG)
        
        # Centraliza a janela na tela (opcional, mas recomendado para evitar o pulo)
        self.root.update_idletasks()
        
        self._setup_styles()
        self._setup_menu()
        self._setup_main_ui()
        
        self.show_all_tools_view()
        
        # Mostra a janela já configurada e no tamanho correto
        self.root.deiconify()

    def _set_window_icon(self):
        """Define o ícone da barra de título com suporte a PyInstaller."""
        try:
            import sys
            from PIL import Image, ImageTk
            
            # Caminho base para PyInstaller ou Script
            if getattr(sys, 'frozen', False):
                base_path = sys._MEIPASS
            else:
                base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            
            # Tentativas para o arquivo .ico
            ico_paths = [
                os.path.join(base_path, 'app_logo.ico'),
                os.path.join(base_path, 'assets', 'app_logo.ico'),
                'assets/app_logo.ico'
            ]
            
            for path in ico_paths:
                if os.path.exists(path):
                    try:
                        self.root.iconbitmap(path)
                        return
                    except:
                        continue
            
            # Fallback para .png via iconphoto (mais compatível)
            png_paths = [
                os.path.join(base_path, 'app_icon.png'),
                os.path.join(base_path, 'assets', 'app_icon.png'),
                'assets/app_icon.png'
            ]
            
            for path in png_paths:
                if os.path.exists(path):
                    try:
                        img = Image.open(path)
                        self._icon_photo = ImageTk.PhotoImage(img) # Mantém ref
                        self.root.iconphoto(True, self._icon_photo)
                        return
                    except:
                        continue
        except:
            pass

    def _setup_styles(self):
        self.style = ttk.Style()
        self.style.theme_use('clam')
        
        self.style.configure('TFrame', background=WIN_BG)
        self.style.configure('TLabel', background=WIN_BG, foreground=WIN_FG, font=('Segoe UI', 10))
        
        self.style.configure('Accent.TButton', background=WIN_ACCENT, foreground='white', font=('Segoe UI', 10, 'bold'))
        self.style.map('Accent.TButton', background=[('active', WIN_ACCENT_HOVER)])
        
        self.style.configure('Action.TButton', foreground=WIN_ACCENT, background=WIN_BG, font=('Segoe UI', 10))
        self.style.map('Action.TButton', foreground=[('active', WIN_ACCENT_HOVER)], background=[('active', WIN_BG)])
        
        self.style.configure('TNotebook', background=WIN_BG, borderwidth=0)
        self.style.configure('TNotebook.Tab', padding=[15, 8], font=('Segoe UI', 10), background=WIN_BG, foreground=WIN_FG)
        self.style.map('TNotebook.Tab', background=[('selected', WIN_CARD_BG)], foreground=[('selected', WIN_ACCENT)])
        
        self.style.configure('ToolBox.TFrame', background=WIN_CARD_BG, borderwidth=1, relief='flat')
        self.style.configure('ToolBox.Bold.TLabel', background=WIN_CARD_BG, font=('Segoe UI', 12, 'bold'), foreground=WIN_FG)
        self.style.configure('ToolBox.Label', background=WIN_CARD_BG, foreground=WIN_FG, font=('Segoe UI', 10))
        
        self.style.configure('Launch.TButton', background=WIN_ACCENT, foreground='white', font=('Segoe UI', 10, 'bold'), borderwidth=0)
        self.style.map('Launch.TButton', background=[('active', WIN_ACCENT_HOVER)])
        
        self.style.configure('CloseButton.TButton', font=('Segoe UI', 9), background=WIN_BG, foreground='#D70000', relief='flat', padding=[5, 2])
        self.style.map('CloseButton.TButton', background=[('active', '#f0d0d0')])

    def _setup_menu(self):
        menubar = Menu(self.root)
        self.root.config(menu=menubar)

        file_menu = Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Add Official Tool (ZIP)", command=self._add_official_tool)
        file_menu.add_command(label="Add Custom Tool (EXE)", command=self._add_custom_tool)
        file_menu.add_command(label="Add Python Script (PY)", command=self._add_python_tool)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)

        help_menu = Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="Open GitHub", command=self._open_marketplace)
        help_menu.add_command(label="About HubSynk", command=self._show_about)
        help_menu.add_command(label="Support", command=lambda: messagebox.showinfo("Support", SUPPORT_MESSAGE_EN))

    def _setup_main_ui(self):
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill="both", expand=True)

        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill="both", expand=True)
        
        self.all_tools_tab = ttk.Frame(self.notebook, padding="10")
        self.official_tools_tab = ttk.Frame(self.notebook, padding="10")
        self.my_favorite_tools_tab = ttk.Frame(self.notebook, padding="10")
        self.python_tools_tab = ttk.Frame(self.notebook, padding="10")
        self.github_tab = ttk.Frame(self.notebook, padding="10")
        
        self.notebook.add(self.all_tools_tab, text="All Tools")
        self.notebook.add(self.official_tools_tab, text="Official Tools")
        self.notebook.add(self.my_favorite_tools_tab, text="My Favorite Tools")
        self.notebook.add(self.python_tools_tab, text="Python")
        self.notebook.add(self.github_tab, text="GitHub")
        
        self._setup_tab_content(self.all_tools_tab, "all")
        self._setup_tab_content(self.official_tools_tab, "official")
        self._setup_tab_content(self.my_favorite_tools_tab, "fav")
        self._setup_tab_content(self.python_tools_tab, "python")
        self._setup_github_tab()
        
        self.notebook.bind("<<NotebookTabChanged>>", self._on_tab_change)
        
        bottom_frame = ttk.Frame(main_frame, padding="5 0 5 5")
        bottom_frame.pack(fill="x", side="bottom")
        
        ttk.Button(bottom_frame, text="➕ Add Official Tool", command=self._add_official_tool, style='Accent.TButton').pack(side="left", padx=(0, 5))
        ttk.Button(bottom_frame, text="➕ Add Tool", command=self._add_custom_tool, style='Accent.TButton').pack(side="left", padx=(0, 5))
        ttk.Button(bottom_frame, text="🐍 Add Python", command=self._add_python_tool, style='Accent.TButton').pack(side="left", padx=(0, 5))
        ttk.Button(bottom_frame, text="❓ Support", command=self._open_support_url, style='Action.TButton').pack(side="left", padx=(0, 5))
        ttk.Button(bottom_frame, text="🔧 GitHub", command=self._open_marketplace, style='Action.TButton').pack(side="right")

    def _setup_tab_content(self, tab, tab_id):
        search_frame = ttk.Frame(tab)
        search_frame.pack(fill="x", pady=(0, 10))
        
        ttk.Label(search_frame, text="🔍 Search:").pack(side="left", padx=(0, 5))
        search_var = tk.StringVar()
        
        if tab_id == "all":
            self.all_search_var = search_var
            scroll_attr = "all_tools_scrollable_frame"
            canvas_attr = "all_tools_canvas"
        elif tab_id == "official":
            self.official_search_var = search_var
            scroll_attr = "official_tools_scrollable_frame"
            canvas_attr = "official_tools_canvas"
        elif tab_id == "python":
            self.python_search_var = search_var
            scroll_attr = "python_tools_scrollable_frame"
            canvas_attr = "python_tools_canvas"
        else:
            self.fav_search_var = search_var
            scroll_attr = "my_favorite_tools_scrollable_frame"
            canvas_attr = "my_favorite_tools_canvas"

        search_var.trace_add("write", lambda *args: self._on_search_change(tab_id))
        entry = ttk.Entry(search_frame, textvariable=search_var, font=("Segoe UI", 10))
        entry.pack(side="left", fill="x", expand=True, padx=(0, 10))
        ttk.Button(search_frame, text="✕", command=lambda: search_var.set(""), style='Action.TButton').pack(side="right")

        canvas = tk.Canvas(tab, bg=WIN_BG, highlightthickness=0)
        vsb = ttk.Scrollbar(tab, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        canvas.configure(yscrollcommand=vsb.set)

        vsb.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw", tags="scrollable_frame")

        scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.bind("<Configure>", lambda e: canvas.itemconfig("scrollable_frame", width=e.width))
        canvas.bind_all("<MouseWheel>", self._on_mousewheel)
        
        setattr(self, scroll_attr, scrollable_frame)
        setattr(self, canvas_attr, canvas)

    def _on_search_change(self, tab_id):
        if tab_id == "all":
            self._load_tools(self.all_tools_scrollable_frame, filter_favorites=False, filter_official=None, search_query=self.all_search_var.get())
        elif tab_id == "official":
            self._load_tools(self.official_tools_scrollable_frame, filter_favorites=False, filter_official=True, search_query=self.official_search_var.get())
        elif tab_id == "python":
            self._load_tools(self.python_tools_scrollable_frame, filter_favorites=False, filter_official=None, filter_python=True, search_query=self.python_search_var.get())
        else:
            self._load_tools(self.my_favorite_tools_scrollable_frame, filter_favorites=True, filter_official=None, search_query=self.fav_search_var.get())

    def _on_tab_change(self, event):
        selected_tab_text = self.notebook.tab(self.notebook.select(), "text")
        if selected_tab_text == "All Tools":
            self._load_tools(self.all_tools_scrollable_frame, filter_favorites=False, filter_official=None, search_query=self.all_search_var.get())
        elif selected_tab_text == "Official Tools":
            self._load_tools(self.official_tools_scrollable_frame, filter_favorites=False, filter_official=True, search_query=self.official_search_var.get())
        elif selected_tab_text == "My Favorite Tools":
            self._load_tools(self.my_favorite_tools_scrollable_frame, filter_favorites=True, filter_official=None, search_query=self.fav_search_var.get())
        elif selected_tab_text == "Python":
            self._load_tools(self.python_tools_scrollable_frame, filter_favorites=False, filter_official=None, filter_python=True, search_query=self.python_search_var.get())
        elif selected_tab_text == "GitHub":
            self._load_github_tools()

    def _on_mousewheel(self, event):
        selected_tab_text = self.notebook.tab(self.notebook.select(), "text")
        if selected_tab_text == "All Tools":
            canvas = self.all_tools_canvas
        elif selected_tab_text == "Official Tools":
            canvas = self.official_tools_canvas
        elif selected_tab_text == "My Favorite Tools":
            canvas = self.my_favorite_tools_canvas
        elif selected_tab_text == "Python":
            canvas = self.python_tools_canvas
        else:
            return
        
        if event.num == 5 or event.delta < 0:
            canvas.yview_scroll(1, "unit")
        elif event.num == 4 or event.delta > 0:
            canvas.yview_scroll(-1, "unit")

    def show_all_tools_view(self):
        self.notebook.select(self.all_tools_tab)
        self._load_tools(self.all_tools_scrollable_frame, filter_favorites=False, filter_official=None)

    def _load_tools(self, target_frame, filter_favorites=False, filter_official=None, filter_python=False, search_query=""):
        for widget in target_frame.winfo_children():
            widget.destroy()

        tools = self.config_manager.get_tools()
        
        if filter_favorites:
            tools = [t for t in tools if t.get('is_favorite', False)]
        
        if filter_official is not None:
            tools = [t for t in tools if t.get('is_official', False) == filter_official]
            
        if filter_python:
            tools = [t for t in tools if t.get('is_python', False)]
        else:
            if filter_official is None and not filter_favorites:
                tools = [t for t in tools if not t.get('is_python', False)]
            
        def sort_key(tool):
            date_str = tool.get('added_date', '1970-01-01T00:00:00')
            try:
                return datetime.fromisoformat(date_str)
            except ValueError:
                return datetime(1970, 1, 1)
                
        tools.sort(key=sort_key, reverse=True)
        
        if search_query:
            query = search_query.lower()
            tools = [t for t in tools if query in t.get('name', '').lower() or query in t.get('description', '').lower()]
        
        if not tools:
            message = "No tools found."
            no_tools_label = ttk.Label(target_frame, text=message, font=("Segoe UI", 10), background=WIN_BG, foreground="#666666")
            no_tools_label.grid(row=0, column=0, columnspan=3, pady=50, padx=50, sticky="nsew")
            target_frame.grid_columnconfigure(0, weight=1)
            return

        num_cols = 3
        for i, tool_info in enumerate(tools):
            row, col = divmod(i, num_cols)
            card = self._create_tool_card(target_frame, tool_info)
            card.grid(row=row, column=col, padx=10, pady=10, sticky="nsew")
            
        for col in range(num_cols):
            target_frame.grid_columnconfigure(col, weight=1)

    def _create_tool_card(self, parent_frame, tool_info):
        is_official = tool_info.get('is_official', False)
        card_frame = ttk.Frame(parent_frame, style='ToolBox.TFrame', padding="10")
        
        top_frame = ttk.Frame(card_frame, style='ToolBox.TFrame')
        top_frame.pack(fill="x", pady=(0, 5))
        
        name_frame = ttk.Frame(top_frame, style='ToolBox.TFrame')
        name_frame.pack(side="left", fill="x", expand=True)
        
        tool_name_label = ttk.Label(name_frame, text=tool_info["name"], style='ToolBox.Bold.TLabel', anchor="w", wraplength=150) 
        tool_name_label.pack(fill="x", expand=True)

        is_fav = tool_info.get("is_favorite", False)
        fav_text = "★"
        fav_color = "gold" if is_fav else "#cccccc"

        fav_button = tk.Button(top_frame, text=fav_text, command=lambda t=tool_info: self._toggle_favorite(t), 
                               fg=fav_color, bg=WIN_CARD_BG, bd=0, relief="flat", font=("Segoe UI", 12),
                               activebackground=WIN_CARD_BG, activeforeground=fav_color)
        fav_button.pack(side="right")
        
        type_text = "Official" if is_official else "Custom"
        type_color = WIN_ACCENT if is_official else "#107C10"
        type_label = ttk.Label(card_frame, text=f"Type: {type_text}", font=("Segoe UI", 9, "italic"), foreground=type_color, background=WIN_CARD_BG, anchor="w")
        type_label.pack(fill="x", pady=(5, 10))
        
        action_frame = ttk.Frame(card_frame, style='ToolBox.TFrame')
        action_frame.pack(fill="x", pady=(5, 0))
        
        launch_button = ttk.Button(action_frame, text="Launch", command=lambda t=tool_info: self.tool_launcher.launch_tool(t), style='Launch.TButton')
        launch_button.pack(side="left", fill="x", expand=True, padx=(0, 5))
        
        remove_button = ttk.Button(action_frame, text="✕", command=lambda t=tool_info: self._remove_tool(t), style='CloseButton.TButton')
        remove_button.pack(side="right", padx=(5, 0))
            
        return card_frame

    def _toggle_favorite(self, tool_info):
        new_status = not tool_info.get('is_favorite', False)
        self.config_manager.update_favorite_status(tool_info, new_status)
        self._on_tab_change(None)

    def _remove_tool(self, tool_info):
        if messagebox.askyesno("Confirm Removal", f"Are you sure you want to remove the tool '{tool_info['name']}'?"):
            self.config_manager.remove_tool(tool_info)
            self._on_tab_change(None)

    def _add_official_tool(self):
        zip_path = filedialog.askopenfilename(title="Select Official Tool Package", filetypes=[("HubSynk Package", "*.hubsynk"), ("All files", "*.*")])
        if zip_path:
            tool_info = self.tool_processor.process_official_tool(zip_path)
            if tool_info:
                messagebox.showinfo("Success", f"Tool '{tool_info['name']}' has been successfully added!")
                self._on_tab_change(None)

    def _add_custom_tool(self):
        exe_path = filedialog.askopenfilename(title="Select Custom Executable", filetypes=[("Executable files", "*.exe"), ("All files", "*.*")])
        if exe_path:
            tool_info = self.tool_processor.process_custom_tool(exe_path)
            if tool_info:
                messagebox.showinfo("Success", f"Custom tool '{tool_info['name']}' has been added!")
                self._on_tab_change(None)

    def _add_python_tool(self):
        py_path = filedialog.askopenfilename(title="Select Python Script", filetypes=[("Python files", "*.py"), ("All files", "*.*")])
        if py_path:
            tool_info = self.tool_processor.process_python_tool(py_path)
            if tool_info:
                messagebox.showinfo("Success", f"Python script '{tool_info['name']}' has been added!")
                self._on_tab_change(None)

    def _open_marketplace(self):
        webbrowser.open_new_tab(URL_WEBSITE)

    def _open_support_url(self):
        webbrowser.open_new_tab(SUPPORT_URL)

    def _show_about(self):
        about_text = f"HubSynk v1.0\nYour Essential Windows Productivity Hub\n\n{DEVELOPER_INFO}\n\nWebsite: {URL_WEBSITE}\n\n© {datetime.now().year} All rights reserved."
        messagebox.showinfo("About HubSynk", about_text)

    def _setup_github_tab(self):
        input_frame = ttk.Frame(self.github_tab)
        input_frame.pack(fill="x", pady=(0, 10))
        
        ttk.Label(input_frame, text="GitHub URL:").pack(side="left", padx=(0, 5))
        self.github_url_var = tk.StringVar()
        entry = ttk.Entry(input_frame, textvariable=self.github_url_var, font=("Segoe UI", 10))
        entry.pack(side="left", fill="x", expand=True, padx=(0, 10))
        
        download_btn = ttk.Button(input_frame, text="⬇ Download", command=self._download_github_tool, style='Accent.TButton')
        download_btn.pack(side="right")

        self.github_canvas = tk.Canvas(self.github_tab, bg=WIN_BG, highlightthickness=0)
        vsb = ttk.Scrollbar(self.github_tab, orient="vertical", command=self.github_canvas.yview)
        self.github_scrollable_frame = ttk.Frame(self.github_canvas)
        self.github_canvas.configure(yscrollcommand=vsb.set)

        vsb.pack(side="right", fill="y")
        self.github_canvas.pack(side="left", fill="both", expand=True)
        self.github_canvas.create_window((0, 0), window=self.github_scrollable_frame, anchor="nw", tags="scrollable_frame")

        self.github_scrollable_frame.bind("<Configure>", lambda e: self.github_canvas.configure(scrollregion=self.github_canvas.bbox("all")))
        self.github_canvas.bind("<Configure>", lambda e: self.github_canvas.itemconfig("scrollable_frame", width=e.width))

    def _download_github_tool(self):
        url = self.github_url_var.get().strip()
        if not url:
            messagebox.showwarning("Warning", "Please enter a GitHub URL.")
            return
            
        try:
            success, result = self.github_manager.download_from_url(url)
        except Exception as e:
            success, result = False, str(e)
            
        if success:
            tool_name = os.path.basename(result)
            tool_info = {
                "name": tool_name,
                "exe_path": result,
                "version": "GitHub",
                "description": f"Downloaded from: {url}",
                "is_official": False,
                "is_favorite": False,
                "added_date": datetime.now().isoformat()
            }
            self.config_manager.add_tool(tool_info)
            messagebox.showinfo("Success", f"Tool '{tool_name}' has been successfully added!")
            self._load_github_tools()
            self.github_url_var.set("")
        else:
            messagebox.showerror("Error", f"Failed to download: {result}")

    def _load_github_tools(self):
        for widget in self.github_scrollable_frame.winfo_children():
            widget.destroy()
            
        tools = self.github_manager.list_local_tools()
        if not tools:
            ttk.Label(self.github_scrollable_frame, text="No GitHub tools downloaded yet.", foreground="#666666").pack(pady=20)
            return
            
        num_cols = 3
        for i, tool in enumerate(tools):
            row, col = divmod(i, num_cols)
            card = self._create_github_tool_card(self.github_scrollable_frame, tool)
            card.grid(row=row, column=col, padx=10, pady=10, sticky="nsew")
            
        for col in range(num_cols):
            self.github_scrollable_frame.grid_columnconfigure(col, weight=1)

    def _create_github_tool_card(self, parent, tool):
        card_frame = ttk.Frame(parent, style='ToolBox.TFrame', padding="10")
        ttk.Label(card_frame, text=tool["name"], style='ToolBox.Bold.TLabel', wraplength=150).pack(fill="x", pady=(0, 5))
        
        files_frame = ttk.Frame(card_frame, style='ToolBox.TFrame')
        files_frame.pack(fill="both", expand=True, pady=5)
        
        tree = ttk.Treeview(files_frame, height=5, show="tree")
        tree.pack(fill="both", expand=True)
        self._populate_tree(tree, "", tool["path"])
        
        btn_frame = ttk.Frame(card_frame, style='ToolBox.TFrame')
        btn_frame.pack(fill="x", pady=(5, 0))
        
        launch_btn = ttk.Button(btn_frame, text="🚀 Run", command=lambda: self.tool_launcher.launch_tool({"exe_path": tool["path"]}), style='Launch.TButton')
        launch_btn.pack(side="left", fill="x", expand=True, padx=(0, 2))
        
        delete_btn = ttk.Button(btn_frame, text="✕", width=3, command=lambda: self._delete_github_tool(tool), style='CloseButton.TButton')
        delete_btn.pack(side="right", padx=(2, 0))
        
        return card_frame

    def _populate_tree(self, tree, parent, path):
        try:
            for item in os.listdir(path):
                if item.startswith('.') or item == "__pycache__": continue
                abspath = os.path.join(path, item)
                node = tree.insert(parent, "end", text=item, open=False)
                if os.path.isdir(abspath):
                    self._populate_tree(tree, node, abspath)
        except Exception:
            pass

    def _delete_github_tool(self, tool):
        if messagebox.askyesno("Confirm", f"Delete {tool['name']}?"):
            import shutil
            if os.path.exists(tool["path"]):
                shutil.rmtree(tool["path"])
            tools = self.config_manager.get_tools()
            for t in tools:
                if t.get('exe_path') == tool["path"]:
                    self.config_manager.remove_tool(t)
                    break
            self._load_github_tools()
            self._on_tab_change(None)
