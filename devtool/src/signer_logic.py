"""
HubSynk - Signer Logic v2.0
Lógica de assinatura e empacotamento de ferramentas .hubsynk

MELHORIA DE SEGURANÇA v2.0:
  Além de assinar o tool_config.json (metadados), agora também calculamos e incluímos
  o SHA-256 do executável dentro do JSON antes de assinar.
  Isso garante que ninguém possa trocar o .exe dentro do pacote sem invalidar a assinatura.
"""

import os
import json
import hashlib
import zipfile
from cryptography.hazmat.primitives.asymmetric import padding, rsa
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.backends import default_backend


def _sha256_file(path: str) -> str:
    """Calcula o hash SHA-256 de um arquivo em blocos (seguro para arquivos grandes)."""
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()


def generate_keys():
    """Gera um novo par de chaves RSA 4096-bit."""
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=4096,
        backend=default_backend()
    )
    public_key = private_key.public_key()

    private_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption()
    )

    public_pem = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )

    return private_pem, public_pem


def sign_and_package_tool(exe_path, private_key_path, name, version, description, icon_file=None):
    """
    Assina e empacota uma ferramenta no formato .hubsynk.

    Fluxo de segurança (v2.0):
      1. Calcula o SHA-256 do .exe
      2. Monta o tool_config.json incluindo o hash do exe
      3. Assina o conteúdo JSON com RSA-PSS + SHA-256 usando a chave privada
      4. Empacota tudo em um .hubsynk (ZIP): exe + tool_config.json + signature.sig

    Com o hash do exe dentro do JSON assinado, qualquer modificação no binário
    será detectada durante a verificação, pois o hash não vai bater.
    """
    if not os.path.exists(exe_path):
        raise FileNotFoundError(f"Executável não encontrado: {exe_path}")

    if not os.path.exists(private_key_path):
        raise FileNotFoundError(f"Chave privada não encontrada: {private_key_path}")

    # 1. Carregar chave privada
    with open(private_key_path, "rb") as key_file:
        private_key = serialization.load_pem_private_key(
            key_file.read(),
            password=None,
            backend=default_backend()
        )

    # 2. Calcular hash SHA-256 do executável
    exe_hash = _sha256_file(exe_path)
    main_exe_name = os.path.basename(exe_path)

    # 3. Montar tool_config.json com o hash do exe incluído
    tool_config_data = {
        "name": name,
        "exe_file": main_exe_name,
        "exe_sha256": exe_hash,          # NOVO: hash do binário dentro do JSON
        "version": version,
        "description": description,
        "signature_file": "signature.sig"
    }

    if icon_file and os.path.exists(icon_file):
        tool_config_data["icon_file"] = os.path.basename(icon_file)

    # Serialização canônica: keys ordenadas, sem espaços extras — garante que
    # o mesmo JSON seja sempre produzido da mesma forma em qualquer plataforma.
    tool_config_content = json.dumps(tool_config_data, indent=4, sort_keys=True).encode("utf-8")

    # 4. Assinar o conteúdo JSON com RSA-PSS + SHA-256
    signature = private_key.sign(
        tool_config_content,
        padding.PSS(
            mgf=padding.MGF1(hashes.SHA256()),
            salt_length=padding.PSS.MAX_LENGTH
        ),
        hashes.SHA256()
    )

    # 5. Empacotar no arquivo .hubsynk
    base_name = name.replace(" ", "_").lower()
    output_zip = os.path.join(os.path.dirname(exe_path), f"{base_name}.hubsynk")

    with zipfile.ZipFile(output_zip, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.write(exe_path, main_exe_name)
        zf.writestr("tool_config.json", tool_config_content)
        zf.writestr("signature.sig", signature)
        if icon_file and os.path.exists(icon_file):
            zf.write(icon_file, os.path.basename(icon_file))

    return output_zip
