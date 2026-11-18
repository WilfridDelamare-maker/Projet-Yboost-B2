import pandas as pd
from pathlib import Path
import json

# ajout des trimestres de validation 

dossier = Path("data/raw/validations") # recupere le chemin du dossier et ses fichiers
dataframes: list[pd.DataFrame] = []

for fichier in dossier.glob("*.csv"): # recupere les fichiers à l'intérieur
    f = pd.read_csv(fichier, sep=';')
    if f["jour"].min().startswith("2025") and f["jour"].max().startswith("2025"):
        dataframes.append(f)

res: pd.DataFrame = pd.concat(dataframes, ignore_index=True)


frequentation = res.groupby(["id_zdc", "jour"])["nb_vald"].sum().reset_index()
frequentation["jour"] = pd.to_datetime(frequentation["jour"])

frequentation["jour_semaine"] = frequentation["jour"].dt.dayofweek


# ajout de meteo 
meteo = pd.read_csv("data/raw/meteo_open_meteo.csv", skiprows=3)
print(meteo.head())
print(meteo.columns)
meteo = meteo.rename(columns={
    "time": "jour",
    "temperature_2m_mean (°C)": "temperature",
    "precipitation_sum (mm)": "pluie",
    "wind_speed_10m_max (km/h)": "vent"
})

meteo["jour"] = pd.to_datetime(meteo["jour"])
print(meteo.head())

frequentation = frequentation.merge(
    meteo,
    on="jour",
    how="left",
    validate="many_to_one"
)

# 5. Ajout des jours fériés

with open("data/raw/jours_feries.json", encoding="utf-8") as f:
    feries = json.load(f)

frequentation["ferie"] = (
    frequentation["jour"]
    .dt.strftime("%Y-%m-%d")
    .isin(feries.keys())
    .astype(int)
)

# 6. Ajout des vacances scolaires

periodes = [
    ("2024-12-21", "2025-01-06"),
    ("2025-02-15", "2025-03-03"),
    ("2025-04-12", "2025-04-28"),
    ("2025-05-29", "2025-06-02"),
    ("2025-07-05", "2025-09-01"),
    ("2025-10-18", "2025-11-03"),
    ("2025-12-20", "2026-01-05")
]

frequentation["vacances"] = 0

for debut, fin in periodes:
    masque = (
        (frequentation["jour"] >= debut)
        & (frequentation["jour"] < fin)
    )

    frequentation.loc[masque, "vacances"] = 1

# 7. Ajout des événements

evenements = pd.read_csv(
    "data/raw/evenements_2025.csv",
    sep=";"
)

evenements["jour"] = pd.to_datetime(evenements["date"])

evenements = evenements.groupby("jour").size().reset_index(
    name="nb_evenements"
)

frequentation = frequentation.merge(
    evenements,
    on="jour",
    how="left"
)

frequentation["nb_evenements"] = (
    frequentation["nb_evenements"].fillna(0).astype(int)
)

frequentation["evenement"] = (
    frequentation["nb_evenements"] > 0
).astype(int)

# 8. Export du tableau final
Path("data/processed").mkdir(parents=True, exist_ok=True)

frequentation.to_csv(
    "data/processed/table.csv",
    index=False
)

print(frequentation.columns)
print(frequentation.shape)
print("Export terminé !")


















'''
print(df.head()) # affiche les 5 premieres lignes
print(df.columns) # nom des colonnes
print(df.shape) # dimensions du tableau (lignes et colonnes)
print(df["jour"].min())
print(df["jour"].max())
'''
