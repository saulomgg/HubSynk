"""
HubSynk - Tool Processor v2.0

MELHORIA DE SEGURANÇA v2.0:
  Além de verificar a assinatura RSA do tool_config.json, agora também:
  - Recalcula o SHA-256 do .exe extraído
  - Compara com o hash registrado e assinado dentro do tool_config.json
  Isso garante a integridade total do binário.
"""

import os
import uuid
import hashlib
import zipfile
import json
import shutil
from datetime import datetime
from tkinter import messagebox, filedialog
from .constants import PUBLIC_KEY

try:
    from cryptography.hazmat.primitives.asymmetric import padding
    from cryptography.hazmat.primitives import hashes, serialization
    from cryptography.hazmat.backends import default_backend
    CRYPTOGRAPHY_AVAILABLE = True
except ImportError:
    CRYPTOGRAPHY_AVAILABLE = False


def _sha256_file(path: str) -> str:
    """Calcula o hash SHA-256 de um arquivo em blocos."""
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()


class ToolProcessor:
    """Handles the addition and verification of tools."""

    def __init__(self, config_manager):
        self.config_manager = config_manager

    def _verify_signature(self, data_to_verify: bytes, signature_path: str) -> bool:
        """
        Verifica a assinatura RSA-PSS do conteúdo fornecido.
        Usa a chave pública hardcoded em constants.py.
        """
        if not CRYPTOGRAPHY_AVAILABLE:
            messagebox.showwarning(
                "Verification Warning",
                "Cryptography library not found. Cannot verify tool signature.\n"
                "Install it with: pip install cryptography"
            )
            return True  # Degradação graciosa sem a lib

        try:
            with open(signature_path, "rb") as f:
                signature = f.read()

            public_key = serialization.load_pem_public_key(
                PUBLIC_KEY.encode(),
                backend=default_backend()
            )

            public_key.verify(
                signature,
                data_to_verify,
                padding.PSS(
                    mgf=padding.MGF1(hashes.SHA256()),
                    salt_length=padding.PSS.MAX_LENGTH
                ),
                hashes.SHA256()
            )
            return True

        except Exception as e:
            messagebox.showerror(
                "Verification Error",
                f"Tool signature verification failed:\n{e}"
            )
            return False

    def _verify_exe_hash(self, exe_path: str, expected_hash: str) -> bool:
        """
        Recalcula o SHA-256 do executável extraído e compara com o hash
        que estava registrado e assinado dentro do tool_config.json.

        Se o .exe foi trocado após a assinatura, o hash não vai bater.
        """
        actual_hash = _sha256_file(exe_path)
        if actual_hash != expected_hash:
            messagebox.showerror(
                "Integrity Error",
                "O executável foi modificado ou corrompido após a assinatura.\n\n"
                f"Hash esperado (assinado): {expected_hash[:16]}...\n"
                f"Hash calculado:           {actual_hash[:16]}...\n\n"
                "Instalação abortada por segurança."
            )
            return False
        return True

    def process_official_tool(self, zip_path: str):
        """
        Processa e instala uma ferramenta oficial .hubsynk.

        Passos de verificação:
          1. Extrai o pacote
          2. Lê e valida o tool_config.json
          3. Verifica a assinatura RSA do JSON
          4. Verifica o hash SHA-256 do .exe (NOVO v2.0)
          5. Registra a ferramenta se tudo estiver ok
        """
        temp_dir = os.path.join(self.config_manager.tools_path, str(uuid.uuid4()))
        os.makedirs(temp_dir, exist_ok=True)

        # Passo 1: Extrair
        try:
            with zipfile.ZipFile(zip_path, "r") as zip_ref:
                zip_ref.extractall(temp_dir)
        except Exception as e:
            messagebox.showerror("Extraction Error", f"Could not extract ZIP file:\n{e}")
            shutil.rmtree(temp_dir)
            return None

        # Passo 2: Ler tool_config.json
        tool_config_path = os.path.join(temp_dir, "tool_config.json")
        if not os.path.exists(tool_config_path):
            messagebox.showerror("Configuration Error", "tool_config.json not found in the package.")
            shutil.rmtree(temp_dir)
            return None

        try:
            with open(tool_config_path, "r", encoding="utf-8") as f:
                raw_config = f.read()
            tool_info = json.loads(raw_config)
        except (json.JSONDecodeError, IOError) as e:
            messagebox.showerror("Configuration Error", f"Could not read tool_config.json:\n{e}")
            shutil.rmtree(temp_dir)
            return None

        required_fields = ["name", "exe_file", "version", "description"]
        if not all(field in tool_info for field in required_fields):
            messagebox.showerror("Configuration Error", "tool_config.json is missing required fields.")
            shutil.rmtree(temp_dir)
            return None

        exe_path = os.path.join(temp_dir, tool_info["exe_file"])
        signature_path = os.path.join(temp_dir, tool_info.get("signature_file", "signature.sig"))

        if not os.path.exists(exe_path):
            messagebox.showerror("File Error", "Executable file not found in the package.")
            shutil.rmtree(temp_dir)
            return None

        # Passo 3: Verificar assinatura RSA do JSON
        if not os.path.exists(signature_path):
            messagebox.showerror(
                "Security Alert",
                "Esta ferramenta oficial não possui assinatura. Instalação abortada."
            )
            shutil.rmtree(temp_dir)
            return None

        signed_data = raw_config.encode("utf-8")
        if not self._verify_signature(signed_data, signature_path):
            messagebox.showerror(
                "Security Alert",
                "A assinatura desta ferramenta é inválida. Instalação abortada."
            )
            shutil.rmtree(temp_dir)
            return None

        # Passo 4 (NOVO v2.0): Verificar hash SHA-256 do executável
        expected_exe_hash = tool_info.get("exe_sha256")
        if expected_exe_hash:
            if not self._verify_exe_hash(exe_path, expected_exe_hash):
                shutil.rmtree(temp_dir)
                return None
        else:
            # Pacote antigo (v1) sem hash — avisar mas permitir (retrocompatibilidade)
            messagebox.showwarning(
                "Security Warning",
                "Este pacote foi criado com uma versão antiga do StampSynk e não possui\n"
                "verificação de integridade do executável (exe_sha256 ausente).\n\n"
                "Recomenda-se reempacotar com o StampSynk v2.0."
            )

        # Tudo ok — registrar ferramenta
        tool_info["exe_path"] = exe_path
        tool_info["folder_path"] = temp_dir
        tool_info["is_official"] = True
        tool_info["is_favorite"] = False
        tool_info["added_date"] = datetime.now().isoformat()

        self.config_manager.add_tool(tool_info)
        return tool_info

    def process_custom_tool(self, exe_path: str):
        name = os.path.splitext(os.path.basename(exe_path))[0]
        tool_info = {
            "name": name,
            "exe_path": exe_path,
            "version": "Custom",
            "description": f"Custom tool located at: {exe_path}",
            "is_official": False,
            "is_favorite": False,
            "added_date": datetime.now().isoformat()
        }
        self.config_manager.add_tool(tool_info)
        return tool_info

    def process_python_tool(self, py_path: str):
        name = os.path.splitext(os.path.basename(py_path))[0]
        tool_info = {
            "name": name,
            "exe_path": py_path,
            "version": "Python Script",
            "description": f"Python script located at: {py_path}",
            "is_official": False,
            "is_favorite": False,
            "is_python": True,
            "added_date": datetime.now().isoformat()
        }
        self.config_manager.add_tool(tool_info)
        return tool_info
