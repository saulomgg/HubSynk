# StampSynk v2.0 — HubSynk Developer Tools

Utilitário para desenvolvedores criarem, assinarem e empacotarem ferramentas no formato `.hubsynk`.

## Estrutura de arquivos

```
devtools/
├── private_key.pem        ← SUA CHAVE PRIVADA — NUNCA COMPARTILHE!
├── public_key.pem         ← Chave pública (referência)
├── hubsign.py             ← Interface gráfica (GUI)
└── src/
    └── signer_logic.py    ← Lógica de assinatura (v2.0)
```

## Pré-requisitos


pip install cryptography


## Como usar

cd devtools
python hubsign.py


## O que mudou na v2.0

### Segurança reforçada: Hash do executável

Na v1.0, a assinatura cobria apenas o `tool_config.json` (metadados).
Isso significava que alguém poderia trocar o `.exe` dentro do `.hubsynk`
e a assinatura continuaria válida.

Na **v2.0**, o campo `exe_sha256` é calculado e inserido dentro do
`tool_config.json` **antes** de assinar. Resultado:

- A assinatura RSA agora cobre **metadados + hash do binário**
- Se o `.exe` for modificado, o hash não bate → instalação abortada
- Proteção dupla: integridade dos metadados E do executável

### Formato do tool_config.json (v2.0)

```json
{
    "description": "Descrição da ferramenta",
    "exe_file": "minha_ferramenta.exe",
    "exe_sha256": "abc123...hash do exe...",
    "icon_file": "icon.ico",
    "name": "Nome da Ferramenta",
    "signature_file": "signature.sig",
    "version": "1.0.0"
}
```

> Nota: as chaves são ordenadas alfabeticamente para serialização canônica,
> garantindo que a assinatura seja reproduzível em qualquer plataforma.

## Aba 1 — Security Keys

Gera um novo par de chaves RSA 4096-bit.
- `private_key.pem`: guarde em local seguro, nunca suba pro GitHub
- `public_key.pem`: copie o conteúdo para `src/constants.py` no HubSynk

## Aba 2 — Build EXE (opcional)

Converte um script Python em executável via PyInstaller.
Requer: `pip install pyinstaller`

## Aba 3 — Sign & Package

Assina e empacota o executável em um `.hubsynk`.
