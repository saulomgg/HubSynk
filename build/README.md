# Build

Scripts para compilar o HubSynk e gerar o instalador.

## Pré-requisitos

```bash
pip install pyinstaller pillow cryptography requests
```

Inno Setup: https://jrsoftware.org/isinfo.php

## Passo 1 — Gerar o executável

Rodar da **raiz do repositório**:

```bash
pyinstaller build/hubsynk.spec
```

Saída: `dist/HubSynk.exe`

## Passo 2 — Gerar o instalador

Abrir `build/hubsynk_installer_new.iss` no **Inno Setup Compiler** e compilar.

Saída: `Output/HubSynk_Setup_v2.0.exe`

Esse é o arquivo final para distribuição.
