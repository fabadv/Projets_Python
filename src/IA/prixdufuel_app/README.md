# Prix du Diesel - Application FastAPI

Une application web pour rechercher les prix du diesel par ville en France.

## Installation

1. **Créer un environnement virtuel:**
```bash
python -m venv venv
venv\Scripts\activate  # Windows
# ou source venv/bin/activate  # Linux/Mac
```

2. **Installer les dépendances:**
```bash
pip install -r requirements.txt
```

## Lancer l'application

```bash
uvicorn main:app --reload
```

L'application sera accessible à: `http://127.0.0.1:8000`

API endpoints:
- `GET /` - Interface web
- `GET /api/prix/{ville}` - Récupère les prix du diesel pour une ville
- `GET /health` - Vérifier l'état de l'application

## Structure

```
prixdufuel_app/
├── main.py              # Application FastAPI
├── requirements.txt     # Dépendances Python
├── static/
│   ├── index.html      # Interface web
│   ├── style.css       # Styles
│   └── script.js       # Logique frontend
└── README.md
```

## Utilisation

1. Entrez le nom d'une ville
2. Cliquez sur "Rechercher"
3. Les prix du diesel et SP95 s'affichent pour les stations d'essence disponibles

## API Utilisée

Données provenant de l'API officielle du gouvernement français:
- https://donnees.roulez-eco.fr/

## Améliorations possibles

- [ ] Ajouter une géolocalisation
- [ ] Sauvegarder les recherches récentes
- [ ] Ajouter un graphique de l'historique des prix
- [ ] Intégrer une carte interactive
- [ ] Notifier l'utilisateur si les prix changent
