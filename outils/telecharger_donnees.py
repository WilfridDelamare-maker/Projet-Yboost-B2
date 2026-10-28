"""
Télécharge directement les 5 fichiers de données du projet dans data/raw/.

Usage (depuis la racine du projet) :
    python telecharger_donnees.py
"""
from pathlib import Path
from urllib.parse import quote

import pandas as pd
import requests

RAW = Path("data/raw")
(RAW / "validations").mkdir(parents=True, exist_ok=True)

PORTAIL = "https://data.iledefrance-mobilites.fr/api/explore/v2.1/catalog/datasets"
TRIMESTRES = ["1er", "2eme", "3eme", "4eme"]          # 4 trimestres de 2025
DEBUT, FIN = "2025-01-01", "2025-12-31"


def telecharger(url: str, destination: Path) -> None:
    print(f"Téléchargement de {destination.name} ...", end=" ", flush=True)
    r = requests.get(url, timeout=600)
    r.raise_for_status()
    destination.write_bytes(r.content)
    print(f"{len(r.content) / 1e6:.1f} Mo")


# 1. Validations par jour, réseau ferré (un fichier par trimestre)
for t in TRIMESTRES:
    jeu = f"validations-reseau-ferre-nombre-validations-par-jour-{t}-trimestre"
    telecharger(f"{PORTAIL}/{jeu}/exports/csv?delimiter=%3B",
                RAW / "validations" / f"validations_{t}_trimestre_2025.csv")

# 2. Météo journalière à Paris (Open-Meteo)
telecharger("https://archive-api.open-meteo.com/v1/archive?latitude=48.86&longitude=2.35"
            f"&start_date={DEBUT}&end_date={FIN}"
            "&daily=temperature_2m_mean,precipitation_sum,wind_speed_10m_max"
            "&timezone=Europe%2FParis&format=csv",
            RAW / "meteo_open_meteo.csv")

# 3. Jours fériés de métropole
telecharger("https://calendrier.api.gouv.fr/jours-feries/metropole.json",
            RAW / "jours_feries.json")

# 4. Calendrier scolaire : vacances de la zone C (académie de Paris) qui touchent 2025
filtre = quote(f"zones='Zone C' AND location='Paris' "
               f"AND end_date >= '{DEBUT}' AND start_date <= '{FIN}'")
telecharger("https://data.education.gouv.fr/api/explore/v2.1/catalog/datasets/"
            f"fr-en-calendrier-scolaire/exports/csv?where={filtre}&delimiter=%3B",
            RAW / "calendrier_scolaire_brut.csv")

# Version lisible : une ligne par période, premier et dernier jour de vacances
cal = pd.read_csv(RAW / "calendrier_scolaire_brut.csv", sep=";")
cal = cal[cal["population"] != "Enseignants"]          # garde le calendrier élèves
for col in ("start_date", "end_date"):
    cal[col] = (pd.to_datetime(cal[col], utc=True)
                .dt.tz_convert("Europe/Paris").dt.tz_localize(None).dt.normalize())
cal["fin"] = cal["end_date"] - pd.Timedelta(days=1)     # end_date = jour de la rentrée
cal = (cal.rename(columns={"description": "vacances", "start_date": "debut"})
          [["vacances", "annee_scolaire", "debut", "fin"]]
          .sort_values("debut"))
cal["debut"] = cal["debut"].dt.date
cal["fin"] = cal["fin"].dt.date
cal.to_csv(RAW / "calendrier_scolaire.csv", sep=";", index=False)
print(f"calendrier_scolaire.csv : {len(cal)} périodes de vacances")