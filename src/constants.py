import os
import hashlib

# --- Windows 11 / Fluent Design Style Constants ---
WIN_BG = '#f3f3f3' # Light background
WIN_FG = '#000000' # Text color
WIN_ACCENT = '#0078D7' # Accent blue
WIN_ACCENT_HOVER = '#005399'
WIN_CARD_BG = '#ffffff'

# --- Support & URLs ---
GITHUB_URL = "https://github.com/saulomgg/"
SUPPORT_URL = f"{GITHUB_URL}hubsynk/issues" # Updated to GitHub
URL_WEBSITE = GITHUB_URL

# --- Support Message ---
SUPPORT_MESSAGE_EN = """HubSynk is a solo project, created by Saulomgg, with the goal of developing fast, practical, and accessible programs.
Currently in version 1.0, the project grows based on community feedback and collaborations.

All support received is directed towards improvements, server creation, and online versions of the tools, allowing you to use them freely.
You can also contribute with services, ideas, or code, directly helping HubSynk's evolution.

Access the GitHub, learn about the tools, and participate in this construction.
"""

# --- Developer Info ---
DEVELOPER_INFO = "Developed by Saulomgg (HubSynk Owner)"

# --- App Data Paths ---
APP_DATA_DIR_NAME = "HubSynk"
if os.name == 'nt':
    APP_DATA_PATH = os.path.join(os.getenv('LOCALAPPDATA', os.path.expanduser('~')), APP_DATA_DIR_NAME)
else:
    APP_DATA_PATH = os.path.join(os.path.expanduser('~'), '.hubsynk')

TOOLS_DIR = os.path.join(APP_DATA_PATH, 'installed_tools')
HUB_CONFIG_FILE = os.path.join(APP_DATA_PATH, 'hub_config.json')

# --- Security ---
# Chave pública oficial HubSynk (RSA 4096)
PUBLIC_KEY = """ -----BEGIN PUBLIC KEY-----
MIICIjANBgkqhkiG9w0BAQEFAAOCAg8AMIICCgKCAgEAv1pGSxsLHyQ0G/G+pvnJ
dXWVFF4u6XVU7ex5/aiwHIWn7vtsbt8gX7dkGPgm4K00OCS9jeW7w5fXTeX6tHJf
xFTvQXFOKYZmDx9SYlR6m2ACT9VOK0yRsGFqdROftmaDUJqvRbQNu93nDyO5czIk
K3nCpS/Qpcko3iIvuLnX5nuzs/bNksdViJPCNOw1C7yGT2WhWx2R/lpk5670XFqj
xfIGylr9kvAlhKu5qtehuFpJzcbYRxPLyhTg9Gy7HaYGAguYrpAp6vT1Don7sIxU
NiWUXFrjrbr7/evjIA1f35N+yP4LV628KDy3nENyAoorDXhGZgcrRuUlKcxJAozE
mGYjRCSHwS3n7Z9RC2qa+5A/cmOcpUIx7KgE0bNrqz5ZnI1QwYqWKWAFGsullTw5
vZ5Q3la2qbD9LWKEHA3REOQUIK6yMvrbOvNgjSZkyKUkddDywYLp9Kb0dPNui9Eg
hHGrB3jL18KniymmO26OouT1wpDhL9td5IzeW98w2QJ1KrbMbotwLPmFe/VEpCQv
fCAlqp0G+AncBtxMDUxkrDAt8pBKV9Xao1fCj+C3IuidwIpXm9HQFK4frfiUSLwS
D4AG6MK5gmy8J9hsY6hhvbjWU7pxP8fAamOyDydKnNOc8c998yznyCve4Q3BASFy
V8vEWlCzSXxxsRFIbPSW5FsCAwEAAQ==
-----END PUBLIC KEY-----"""
