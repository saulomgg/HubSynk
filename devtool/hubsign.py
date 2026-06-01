"""
Saulomgg, StampSynk 1.0
Sistema de Assinatura e Empacotamento HubSynk

Este utilitário permite que desenvolvedores criem suas próprias chaves de segurança,
assinem seus executáveis e os transformem em pacotes .hubsynk compatíveis.

GitHub: https://github.com/saulomgg/
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
import subprocess
import sys
from src.signer_logic import generate_keys, sign_and_package_tool

class StampSynkApp:
    def __init__(self, root):
        self.root = root
        self.root.title("StampSynk v1.0 - HubSynk Developer Tools")
        self.root.geometry("700x600")
        
        self.style = ttk.Style()
        self.style.configure('Header.TLabel', font=('Segoe UI', 12, 'bold'))
        self.style.configure('Action.TButton', font=('Segoe UI', 10, 'bold'))
        
        self._setup_ui()

    def _setup_ui(self):
        notebook = ttk.Notebook(self.root)
        notebook.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Aba 1: Gestão de Chaves
        self.keys_frame = ttk.Frame(notebook, padding=20)
        notebook.add(self.keys_frame, text="1. Security Keys")
        self._setup_keys_tab()
        
        # Aba 2: PyInstaller (Opcional)
        self.build_frame = ttk.Frame(notebook, padding=20)
        notebook.add(self.build_frame, text="2. Build EXE")
        self._setup_build_tab()
        
        # Aba 3: Assinatura e Empacotamento
        self.sign_frame = ttk.Frame(notebook, padding=20)
        notebook.add(self.sign_frame, text="3. Sign & Package")
        self._setup_sign_tab()

    def _setup_keys_tab(self):
        ttk.Label(self.keys_frame, text="Generate your own security keys", style='Header.TLabel').pack(pady=(0, 20))
        
        info_text = ("To distribute tools as 'Official' in your HubSynk, you need a key pair.\n"
                    "1. Generate the keys below.\n"
                    "2. Keep 'private_key.pem' secret (used to sign tools).\n"
                    "3. Copy the content of 'public_key.pem' to your HubSynk code.")
        ttk.Label(self.keys_frame, text=info_text, wraplength=600, justify="left").pack(pady=10)
        
        ttk.Button(self.keys_frame, text="GENERATE NEW KEY PAIR", command=self._generate_keys_action, style='Action.TButton').pack(pady=20)

    def _setup_build_tab(self):
        ttk.Label(self.build_frame, text="Convert Python to EXE (PyInstaller)", style='Header.TLabel').pack(pady=(0, 20))
        
        self.script_path = tk.StringVar()
        ttk.Label(self.build_frame, text="Python Script:").pack(anchor="w")
        entry_frame = ttk.Frame(self.build_frame)
        entry_frame.pack(fill="x", pady=5)
        ttk.Entry(entry_frame, textvariable=self.script_path).pack(side="left", fill="x", expand=True)
        ttk.Button(entry_frame, text="Browse", command=lambda: self._browse_file(self.script_path, [("Python files", "*.py")])).pack(side="right", padx=5)
        
        ttk.Button(self.build_frame, text="BUILD ONEFILE EXE", command=self._build_exe_action, style='Action.TButton').pack(pady=20)
        ttk.Label(self.build_frame, text="Note: Requires 'pyinstaller' installed (pip install pyinstaller)", font=("Segoe UI", 8, "italic")).pack()

    def _setup_sign_tab(self):
        ttk.Label(self.sign_frame, text="Sign and Create .hubsynk Package", style='Header.TLabel').pack(pady=(0, 20))
        
        # EXE Path
        self.exe_path = tk.StringVar()
        self._create_input_field(self.sign_frame, "Executable (.exe):", self.exe_path, [("Executables", "*.exe")])
        
        # Private Key Path
        self.priv_key_path = tk.StringVar(value="private_key.pem")
        self._create_input_field(self.sign_frame, "Private Key (.pem):", self.priv_key_path, [("PEM files", "*.pem")])
        
        # Tool Info
        self.tool_name = tk.StringVar()
        self.tool_version = tk.StringVar(value="1.0.0")
        
        info_frame = ttk.Frame(self.sign_frame)
        info_frame.pack(fill="x", pady=5)
        
        ttk.Label(info_frame, text="Tool Name:").grid(row=0, column=0, sticky="w")
        ttk.Entry(info_frame, textvariable=self.tool_name).grid(row=0, column=1, sticky="ew", padx=5)
        
        ttk.Label(info_frame, text="Version:").grid(row=1, column=0, sticky="w", pady=5)
        ttk.Entry(info_frame, textvariable=self.tool_version).grid(row=1, column=1, sticky="w", padx=5)
        
        info_frame.columnconfigure(1, weight=1)
        
        ttk.Label(self.sign_frame, text="Description:").pack(anchor="w")
        self.desc_text = tk.Text(self.sign_frame, height=4)
        self.desc_text.pack(fill="x", pady=5)
        
        ttk.Button(self.sign_frame, text="SIGN & PACKAGE", command=self._sign_action, style='Action.TButton').pack(pady=20)

    def _create_input_field(self, parent, label, var, filetypes):
        ttk.Label(parent, text=label).pack(anchor="w")
        f = ttk.Frame(parent)
        f.pack(fill="x", pady=(0, 10))
        ttk.Entry(f, textvariable=var).pack(side="left", fill="x", expand=True)
        ttk.Button(f, text="Browse", command=lambda: self._browse_file(var, filetypes)).pack(side="right", padx=5)

    def _browse_file(self, var, filetypes):
        f = filedialog.askopenfilename(filetypes=filetypes)
        if f: var.set(f)

    def _generate_keys_action(self):
        try:
            priv, pub = generate_keys()
            with open("private_key.pem", "wb") as f: f.write(priv)
            with open("public_key.pem", "wb") as f: f.write(pub)
            messagebox.showinfo("Success", "Keys generated: private_key.pem and public_key.pem\n\nKEEP YOUR PRIVATE KEY SAFE!")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def _build_exe_action(self):
        script = self.script_path.get()
        if not script: return
        try:
            messagebox.showinfo("Build", "Starting PyInstaller... This may take a while.")
            subprocess.run(["pyinstaller", "--onefile", "--windowed", script], check=True)
            messagebox.showinfo("Success", "EXE created in 'dist' folder.")
        except Exception as e:
            messagebox.showerror("Error", f"Build failed: {e}")

    def _sign_action(self):
        try:
            res = sign_and_package_tool(
                self.exe_path.get(),
                self.priv_key_path.get(),
                self.tool_name.get(),
                self.tool_version.get(),
                self.desc_text.get("1.0", tk.END).strip()
            )
            messagebox.showinfo("Success", f"Package created: {res}")
        except Exception as e:
            messagebox.showerror("Error", str(e))

if __name__ == "__main__":
    root = tk.Tk()
    app = StampSynkApp(root)
    root.mainloop()
