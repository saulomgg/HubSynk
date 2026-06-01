import subprocess
import os
import sys
from tkinter import messagebox

class ToolLauncher:
    """Handles the launching of tools."""

    def launch_tool(self, tool_info):
        exe_path = tool_info.get('exe_path')
        
        # Se for um diretório (do GitHub), precisamos encontrar o que rodar
        if exe_path and os.path.isdir(exe_path):
            exe_path = self._find_runnable(exe_path)

        if not exe_path or not os.path.exists(exe_path):
            messagebox.showerror("Launch Error", f"Executable or script not found: {exe_path}")
            return

        # Flag para ocultar o console no Windows (CREATE_NO_WINDOW = 0x08000000)
        creation_flags = 0x08000000 if os.name == 'nt' else 0

        try:
            if exe_path.lower().endswith('.py'):
                # Determina qual interpretador Python usar
                python_exe = sys.executable
                if getattr(sys, 'frozen', False):
                    # No Windows, quando congelado, tentamos usar o interpretador do sistema
                    # 'pythonw' seria ideal para scripts GUI, mas 'python' com a flag CREATE_NO_WINDOW é robusto.
                    python_exe = "python" 
                
                process = subprocess.Popen(
                    [python_exe, exe_path], 
                    cwd=os.path.dirname(exe_path),
                    stderr=subprocess.PIPE,
                    stdout=subprocess.PIPE,
                    text=True,
                    creationflags=creation_flags
                )
                
                # Pequena espera para ver se o processo crasha no início
                try:
                    outs, errs = process.communicate(timeout=1)
                    if process.returncode != 0:
                        self._handle_python_error(errs)
                except subprocess.TimeoutExpired:
                    # O processo ainda está rodando (comum para apps GUI), o que é bom
                    pass
            else:
                # Para outros executáveis (.exe, etc)
                subprocess.Popen(
                    [exe_path], 
                    cwd=os.path.dirname(exe_path), 
                    creationflags=creation_flags
                )
        except Exception as e:
            messagebox.showerror("Launch Error", f"Could not launch tool: {e}")

    def _handle_python_error(self, error_msg):
        """Trata erros específicos do Python."""
        if "ModuleNotFoundError: No module named 'audioop'" in error_msg:
            msg = ("Erro de Compatibilidade (Python 3.13+):\n\n"
                   "O módulo 'audioop' foi removido no Python 3.13. \n"
                   "Para corrigir este erro na ferramenta baixada, execute:\n"
                   "pip install audioop-lts\n\n"
                   "Ou use uma versão do Python anterior à 3.13 (ex: 3.12).")
            messagebox.showerror("Python 3.13 Compatibility", msg)
        else:
            messagebox.showerror("Python Script Error", f"O script encontrou um erro:\n\n{error_msg[:500]}")

    def _find_runnable(self, directory):
        """Tenta encontrar um arquivo executável ou script principal em um diretório."""
        if not os.path.isdir(directory):
            return None
            
        # Prioridade para arquivos comuns de entrada
        priority_files = ['main.py', 'app.py', 'run.py', 'index.py', 'gui.py']
        for pf in priority_files:
            full_path = os.path.join(directory, pf)
            if os.path.exists(full_path):
                return full_path
        
        # Se não achar, procura qualquer .py na raiz
        try:
            files = os.listdir(directory)
            py_files = [f for f in files if f.lower().endswith('.py')]
            if py_files:
                # Se houver apenas um, ou um que contenha o nome da pasta
                if len(py_files) == 1:
                    return os.path.join(directory, py_files[0])
                
                folder_name = os.path.basename(directory).lower().replace('-', '_')
                # Tenta encontrar um arquivo que comece com o nome da pasta ou contenha ele
                for f in py_files:
                    f_lower = f.lower()
                    if f_lower.startswith(folder_name) or folder_name in f_lower:
                        return os.path.join(directory, f)
                
                # Se ainda não achou, pega o que não seja 'setup.py' ou algo assim
                filtered_py = [f for f in py_files if f.lower() not in ['setup.py', '__init__.py']]
                if filtered_py:
                    return os.path.join(directory, filtered_py[0])
                    
                return os.path.join(directory, py_files[0])
        except Exception:
            pass
        
        return None
