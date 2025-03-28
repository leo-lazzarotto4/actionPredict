from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from app.routes import users, auth
from app.services.data_fetcher import start_scheduler
from dotenv import load_dotenv
from sqlalchemy.orm import Session
from app.database import get_db, engine
from app.models import StockData
from app.schemas import DateRangeRequest
import uvicorn


# Charger les variables d'environnement
load_dotenv()

StockData.metadata.create_all(bind=engine)

app = FastAPI(title="Projet Actions", description="API pour prédire les actions avec IA")

# 🔥 Configuration CORS pour Vue.js
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Remplace "*" par les domaines autorisés
    allow_credentials=True,
    allow_methods=["*"],  # Autorise toutes les méthodes (GET, POST, etc.)
    allow_headers=["*"],  # Autorise tous les headers
)

# 📌 Inclusion des routes
app.include_router(auth.router, prefix="/auth", tags=["Authentification"])
app.include_router(users.router, prefix="/users", tags=["Utilisateurs"])

@app.get("/")
def read_root():
    return {"message": "Bienvenue sur l'API de prédiction des actions"}

# 🚀 Démarrage du scheduler au lancement du serveur
@app.on_event("startup")
def startup_event():
    print("🎯 Démarrage du scheduler pour récupérer les données...")
    start_scheduler()

@app.post("/get-data-between-dates/")
def get_data_between_dates(date_range: DateRangeRequest, db: Session = Depends(get_db)):
    """ Récupère les données entre deux dates """
    start_date = date_range.start_date
    end_date = date_range.end_date

    # Query SQLAlchemy pour récupérer les données entre start_date et end_date
    data = db.query(StockData).filter(StockData.timestamp >= start_date, StockData.timestamp <= end_date).all()

    # Si aucune donnée n'est trouvée
    if not data:
        return {"message": "Aucune donnée trouvée pour cette période"}

    # Si des données sont trouvées, renvoie-les
    return {"data": data}

# 🚀 Lancement du serveur
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))  
    uvicorn.run(app, host="0.0.0.0", port=port, reload=True)
