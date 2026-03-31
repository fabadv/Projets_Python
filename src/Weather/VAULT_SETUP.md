# Configuration Vault Local pour Weather API

## 🚀 Quick Start (Sans Docker!)

### 1. Installer les dépendances
```bash
pip install -r requirements.txt
```

### 2. Initialiser le Vault local
```bash
python init_vault.py
```

L'app te demandera ta clé API OpenWeatherMap et la stockera dans `.vault_secrets.json`

### 3. Lancer l'application
```bash
python weather.py
```

C'est tout! 🎉

## 🔐 Comment ça fonctionne?

Au lieu d'utiliser Docker/Vault distant:
- ✅ Les secrets sont stockés dans **`.vault_secrets.json`** (fichier local)
- ✅ Les permissions restrictives empêchent l'accès non autorisé
- ✅ Fallback automatique vers `.env` si le vault local n'existe pas
- ✅ **Zéro dépendance externe** (pas de Docker nécessaire!)

## 📂 Structure des secrets

```
.vault_secrets.json (stocké localement)
{
  "weather/openweather": {
    "api_key": "votre_clé_api"
  }
}
```

## 🔒 Sécurité

**IMPORTANT:** Le fichier `.vault_secrets.json` contient vos secrets!

```
✅ FAIRE:
- Ajouter à .gitignore (déjà fait!)
- Garder les permissions restrictives (0600)
- Ne pas le partager ou le committer

❌ NE PAS FAIRE:
- Committer en Git
- Partager le fichier
- Rendre accessible en production
```

## 🛠️ Commandes utiles

### Voir vos secrets stockés
```python
from vault_local import get_vault
vault = get_vault()
secrets = vault.list_secrets('weather')
print(secrets)
```

### Ajouter un nouveau secret
```python
from vault_local import get_vault
vault = get_vault()
vault.set_secret('weather/another', 'secret_key', 'value')
```

### Supprimer un secret
```python
from vault_local import get_vault
vault = get_vault()
vault.delete_secret('weather/openweather')
```

## 🚀 Migrer vers production

Pour passer en production avec un vrai Vault:

```python
# Remplacer vault_local par hvac
import hvac

client = hvac.Client(url='https://vault.example.com', token='real-token')
secret = client.secrets.kv.read_secret_version(path='weather/openweather')
```

Les clés restent les mêmes - juste le backend change!

## 📖 Alternatives

Vous pouvez aussi utiliser:
- **AWS Secrets Manager** (production)
- **Azure Key Vault** (production)
- **Google Cloud Secret Manager** (production)
- **HashiCorp Vault Cloud** (managed)

## ❓ FAQ

**Q: Puis-je committer `.vault_secrets.json`?**
Non! C'est dans .gitignore pour une raison.

**Q: Que se passe-t-il si je supprime `.vault_secrets.json`?**
L'app tombera à `.env` pour la clé API.

**Q: C'est sûr pour la production?**
Non, utilisez un vrai Vault ou un service cloud pour la production.

**Q: Comment à faire un backup des secrets?**
Sauvegardez `.vault_secrets.json` dans un endroit sûr, hors Git.

## ✨ Avantages de cette approche

- 🚀 **Zéro setup** - pas d'installation Docker nécessaire
- 🔒 **Sécurisé** - permissions de fichier restrictives
- 📦 **Transparent** - juste un fichier JSON
- 🔄 **Compatible** - fonctionne avec du vrai Vault aussi
- 💡 **Simple** - du pur Python, facile à comprendre
