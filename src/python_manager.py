import subprocess
import sys
import os
import threading

class PythonManager:
    """Handles Python environment tasks like installing libraries and requirements."""

    def __init__(self, ui_callback=None):
        self.ui_callback = ui_callback

    def _run_command(self, command, description):
        """Runs a shell command and reports progress via callback."""
        if self.ui_callback:
            self.ui_callback(f"Iniciando: {description}...\n")

        try:
            # Usa 'python' se estiver congelado, senão sys.executable
            python_exe = "python" if getattr(sys, 'frozen', False) else sys.executable
            
            full_command = [python_exe, "-m", "pip"] + command
            
            process = subprocess.Popen(
                full_command,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                universal_newlines=True,
                creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
            )

            for line in process.stdout:
                if self.ui_callback:
                    self.ui_callback(line)
            
            process.wait()
            
            if process.returncode == 0:
                if self.ui_callback:
                    self.ui_callback(f"\n✅ {description} concluído com sucesso!\n")
            else:
                if self.ui_callback:
                    self.ui_callback(f"\n❌ Erro em {description}. Código: {process.returncode}\n")
        
        except Exception as e:
            if self.ui_callback:
                self.ui_callback(f"\n❌ Erro inesperado: {str(e)}\n")

    def install_library(self, lib_name):
        """Installs a single library via pip."""
        if not lib_name.strip():
            return
        
        thread = threading.Thread(
            target=self._run_command, 
            args=(["install", lib_name], f"Instalação de '{lib_name}'")
        )
        thread.start()

    def install_requirements(self, file_path):
        """Installs libraries from a requirements.txt file."""
        if not os.path.exists(file_path):
            if self.ui_callback:
                self.ui_callback(f"Erro: Arquivo não encontrado: {file_path}\n")
            return
        
        thread = threading.Thread(
            target=self._run_command, 
            args=(["install", "-r", file_path], f"Instalação de requirements de {os.path.basename(file_path)}")
        )
        thread.start()
