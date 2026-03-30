import fastapi
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import httpx
from typing import Optional

app = fastapi.FastAPI(title="Prix du Diesel")

# Servir les fichiers statiques
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
async def read_root():
    return FileResponse("static/index.html")

@app.get("/api/prix/{ville}")
async def get_prix_diesel(ville: str):
    """
    Récupère les prix du diesel pour une ville donnée
    Utilise l'API data.economie.gouv.fr
    """
    try:
        async with httpx.AsyncClient() as client:
            # Récupérer toutes les stations et filtrer par ville
            response = await client.get(
                "https://data.economie.gouv.fr/api/explore/v2.1/catalog/datasets/prix-des-carburants-en-france-flux-instantane-v2/records",
                params={
                    "limit": 100,
                    "where": f'ville like "{ville}"',
                    "order_by": "gazole_prix"
                },
                timeout=10.0
            )
            
            if response.status_code == 200:
                data = response.json()
                stations = data.get("results", [])
                
                if not stations:
                    raise fastapi.HTTPException(
                        status_code=404,
                        detail=f"Aucune station trouvée pour '{ville}'"
                    )
                
                # Formater les résultats - filtrer celles avec un prix de diesel
                resultats = []
                for station in stations:
                    if station.get("gazole_prix") is not None:
                        resultats.append({
                            "nom": f"Station {station.get('id', 'N/A')}",
                            "adresse": station.get("adresse", "N/A"),
                            "ville": station.get("ville", "N/A"),
                            "prix_diesel": station.get("gazole_prix"),
                            "prix_sp95": station.get("sp95_prix"),
                            "prix_sp98": station.get("sp98_prix"),
                            "prix_e85": station.get("e85_prix"),
                            "prix_e10": station.get("e10_prix"),
                            "prix_gplc": station.get("gplc_prix"),
                            "derniere_maj_diesel": station.get("gazole_maj"),
                            "derniere_maj_sp95": station.get("sp95_maj"),
                            "latitude": station.get("geom", {}).get("lat"),
                            "longitude": station.get("geom", {}).get("lon"),
                            "services": station.get("services_service", [])
                        })
                
                if not resultats:
                    raise fastapi.HTTPException(
                        status_code=404,
                        detail=f"Aucune station avec prix du diesel trouvée pour '{ville}'"
                    )
                
                return {
                    "ville": ville,
                    "stations": resultats[:10],  # Top 10 stations avec prix
                    "nombre": len(resultats)
                }
            else:
                raise fastapi.HTTPException(
                    status_code=500,
                    detail="Erreur lors de la connexion à l'API"
                )
    
    except httpx.TimeoutException:
        raise fastapi.HTTPException(
            status_code=504,
            detail="Délai d'attente dépassé"
        )
    except Exception as e:
        raise fastapi.HTTPException(
            status_code=500,
            detail=f"Erreur: {str(e)}"
        )

@app.get("/health")
async def health():
    return {"status": "ok"}
