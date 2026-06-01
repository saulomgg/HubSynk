import os
import requests
import zipfile
import io
import shutil
from urllib.parse import urlparse

class GitHubManager:
    def __init__(self, config_manager):
        self.config_manager = config_manager
        # No HubSynkConfig, o atributo é 'app_data_path' (minúsculo)
        self.github_tools_dir = os.path.join(self.config_manager.app_data_path, 'github_tools')
        os.makedirs(self.github_tools_dir, exist_ok=True)

    def download_from_url(self, url):
        """
        Baixa um repositório ou pasta específica do GitHub.
        Suporta links de repositório ou links de subpastas (tree).
        """
        try:
            parsed_url = urlparse(url)
            path_parts = parsed_url.path.strip('/').split('/')
            
            if len(path_parts) < 2:
                return False, "URL do GitHub inválida."

            owner = path_parts[0]
            repo = path_parts[1]
            
            # Caso seja uma subpasta: https://github.com/owner/repo/tree/branch/subfolder
            is_subfolder = "tree" in path_parts
            branch = "main"
            subfolder_path = ""
            
            if is_subfolder:
                tree_idx = path_parts.index("tree")
                branch = path_parts[tree_idx + 1]
                subfolder_path = "/".join(path_parts[tree_idx + 2:])
            
            # API para baixar o ZIP do repositório (infelizmente o GitHub não permite baixar só uma pasta via ZIP direto facilmente sem API complexa)
            # Vamos baixar o repo inteiro e extrair o que precisamos
            zip_url = f"https://github.com/{owner}/{repo}/archive/refs/heads/{branch}.zip"
            
            response = requests.get(zip_url)
            if response.status_code != 200:
                # Tenta 'master' se 'main' falhar
                zip_url = f"https://github.com/{owner}/{repo}/archive/refs/heads/master.zip"
                response = requests.get(zip_url)
                if response.status_code != 200:
                    return False, f"Falha ao baixar repositório: {response.status_code}"

            z = zipfile.ZipFile(io.BytesIO(response.content))
            
            # Nome da pasta raiz dentro do ZIP (geralmente repo-branch)
            zip_root = z.namelist()[0].split('/')[0]
            
            target_name = subfolder_path.split('/')[-1] if subfolder_path else repo
            install_dir = os.path.join(self.github_tools_dir, target_name)
            
            if os.path.exists(install_dir):
                shutil.rmtree(install_dir)
            os.makedirs(install_dir, exist_ok=True)

            # Extrair apenas os arquivos necessários
            prefix = f"{zip_root}/{subfolder_path}" if subfolder_path else zip_root
            
            for member in z.infolist():
                if member.filename.startswith(prefix):
                    # Remove o prefixo para salvar na pasta de destino
                    relative_path = member.filename[len(prefix):].lstrip('/')
                    if not relative_path: continue
                    
                    target_path = os.path.join(install_dir, relative_path)
                    if member.is_dir():
                        os.makedirs(target_path, exist_ok=True)
                    else:
                        os.makedirs(os.path.dirname(target_path), exist_ok=True)
                        with z.open(member) as source, open(target_path, "wb") as target:
                            shutil.copyfileobj(source, target)
            
            return True, install_dir
        except Exception as e:
            return False, str(e)

    def list_local_tools(self):
        """Lista as ferramentas baixadas do GitHub."""
        tools = []
        if not os.path.exists(self.github_tools_dir):
            return tools
            
        for item in os.listdir(self.github_tools_dir):
            item_path = os.path.join(self.github_tools_dir, item)
            if os.path.isdir(item_path):
                tools.append({
                    "name": item,
                    "path": item_path
                })
        return tools
