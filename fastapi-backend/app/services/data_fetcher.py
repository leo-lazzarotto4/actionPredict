import requests
import datetime
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import StockData
from apscheduler.schedulers.background import BackgroundScheduler

# 🔑 Variables API
API_KEY = "X3S3EO6wapebnQrkwKuEbe1GT6WAm7yp"
TICKER = "AAPL"
BASE_URL = "https://api.polygon.io/v2/aggs/ticker/{ticker}/range/1/minute/{start_date}/{end_date}?apiKey={apiKey}"

# 📅 Gestion des dates
END_DATE = datetime.datetime.today().date()  # Aujourd'hui
START_DATE = END_DATE - datetime.timedelta(days=3)  # 3 jours avant
ITERATIONS = 0
MAX_ITERATIONS = 40  # Stop après 40 itérations

def fetch_data(ticker: str, start_date: str, end_date: str, db: Session):
    """Récupère les données de Polygon.io et les stocke en base."""
    url = BASE_URL.format(ticker=ticker, start_date=start_date, end_date=end_date, apiKey=API_KEY)
    try:
        response = requests.get(url)
        response.raise_for_status()  # Lève une exception pour les codes d'erreur HTTP
    except requests.exceptions.RequestException as e:
        print(f"❌ Erreur de connexion ou d'API: {e}")
        return

    data = response.json()
    if 'results' in data and data['results']:
        try:
            for entry in data['results']:
                stock_entry = StockData(
                    volume=entry.get("v", 0),
                    vw=entry.get("vw", None),
                    open=entry.get("o", 0.0),
                    close=entry.get("c", 0.0),
                    high=entry.get("h", 0.0),
                    low=entry.get("l", 0.0),
                    timestamp=datetime.datetime.fromtimestamp(entry["t"] / 1000),  # Conversion timestamp
                )
                db.add(stock_entry)
            db.commit()
            print(f"✅ {len(data['results'])} lignes insérées pour {start_date} → {end_date}.")
        except Exception as e:
            db.rollback()
            print(f"❌ Erreur d'insertion en BDD : {e}")
    else:
        print(f"⚠️ Aucune donnée trouvée entre {start_date} et {end_date}.")


def scheduled_task():
    """Tâche planifiée pour récupérer les données et reculer dans le temps."""
    global START_DATE, END_DATE, ITERATIONS
    db = next(get_db())  # Obtenir la session DB

    if ITERATIONS >= MAX_ITERATIONS:
        print("🚀 Fin du processus après 40 itérations.")
        return
    
    print(f"📊 Récupération des données de {START_DATE} à {END_DATE} (Itération {ITERATIONS+1}/{MAX_ITERATIONS})")
    fetch_data(TICKER, START_DATE.strftime("%Y-%m-%d"), END_DATE.strftime("%Y-%m-%d"), db)

    # Mise à jour des dates (on recule de 3 jours)
    END_DATE = START_DATE
    START_DATE = END_DATE - datetime.timedelta(days=3)
    ITERATIONS += 1

# 🔄 Lancement du scheduler
def start_scheduler():
    from apscheduler.schedulers.background import BackgroundScheduler
    scheduler = BackgroundScheduler()
    scheduler.add_job(scheduled_task, 'interval', seconds=30)
    scheduler.start()
    return scheduler
