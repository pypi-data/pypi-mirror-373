# INSEE MCP Server

Serveur MCP (Model Context Protocol) pour accéder aux données de l'INSEE via l'API SIRENE, BDM et les nomenclatures officielles.

## ⚡ Installation en une ligne

### Avec uv (recommandé)
```bash
# Installation et lancement direct
API_KEY="your_insee_api_key" uv run --with insee-mcp insee-mcp
```

### Configuration MCP standard
Ajoutez ceci à votre configuration MCP (ex: Claude Desktop) :

```json
{
  "mcpServers": {
    "insee": {
      "command": "uv",
      "args": ["run", "--with", "insee-mcp", "insee-mcp"],
      "env": {
        "API_KEY": "votre_clé_api_insee"
      }
    }
  }
}
```

### Avec pipx
```bash
API_KEY="your_insee_api_key" pipx run --spec git+https://github.com/KerryanOPMace/mcp-insee.git insee-mcp
```

## 🚀 Installation rapide

### Installation directe (recommandée)

```bash
# Installation directe depuis GitHub
pip install git+https://github.com/KerryanOPMace/mcp-insee.git

# Configurer votre clé API INSEE
export API_KEY="votre_clé_api_insee"

# Lancer le serveur
insee-mcp
```

### Installation avec pipx (isolée)

```bash
# Installation avec pipx (environnement isolé)
pipx install git+https://github.com/KerryanOPMace/mcp-insee.git

# Configurer la clé API
export API_KEY="votre_clé_api_insee"

# Lancer le serveur
insee-mcp
```

### Installation pour développeurs

```bash
# Cloner le repository
git clone https://github.com/KerryanOPMace/mcp-insee.git
cd mcp-insee

# Installer en mode développement
pip install -e .
```

## 🔑 Configuration

### Clé API INSEE

Vous devez obtenir une clé API sur le [portail API de l'INSEE](https://api.insee.fr/) et la configurer :

**Linux/Mac :**
```bash
export API_KEY="votre_clé_api_insee"
```

**Windows (PowerShell) :**
```powershell
$env:API_KEY="votre_clé_api_insee"
```

**Windows (CMD) :**
```cmd
set API_KEY=votre_clé_api_insee
```

## 🛠️ Outils disponibles

- `search_company` : Recherche d'entreprises dans la base SIRENE
  - Par SIREN, SIRET ou nom d'entreprise
  - Recherche approximative disponible

## 🌐 Accès au serveur

Une fois lancé, le serveur MCP est accessible à :
- **URL** : `http://127.0.0.1:8000/mcp`
- **Transport** : Streamable HTTP

## 🧪 Test du client

```python
from fastmcp import Client
import asyncio

async def test():
    client = Client("http://127.0.0.1:8000/mcp")
    async with client:
        # Lister les outils
        tools = await client.list_tools()
        print(tools)
        
        # Rechercher une entreprise
        result = await client.call_tool("search_company", {
            "siret": "44302124100072"
        })
        print(result)

asyncio.run(test())
```

## 📋 Prérequis

- Python 3.8+
- Clé API INSEE valide
- Accès internet pour les requêtes API

## 📄 Licence

MIT License
