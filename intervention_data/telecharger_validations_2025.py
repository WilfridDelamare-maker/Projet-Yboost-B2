"""
Récupère les validations 2025 du réseau ferré (4 trimestres) depuis l'archive
historique d'Île-de-France Mobilités.

Pourquoi ce script : les jeux "validations-reseau-ferre-nombre-validations-par-jour-1er/2eme-trimestre"
sont remplacés chaque année par l'année en cours. En novembre 2026 ils contiennent 2026,
alors que la météo et les événements du projet portent sur 2025.

Usage (depuis la racine du projet) :
    python intervention_data/telecharger_validations_2025.py

Résultat : data/raw/validations_2025/2025_T1.csv ... 2025_T4.csv
Le contenu est conservé tel quel (seul le format passe de xlsx à csv) ;
le nettoyage est fait dans le notebook.
"""
import csv
import io
import zipfile
from pathlib import Path

import openpyxl
import requests

# Adresse de l'archive 2025, trouvée dans le jeu "histo-validations-reseau-ferre" du portail IDFM
URL_ARCHIVE_2025 = ("https://data.iledefrance-mobilites.fr/api/explore/v2.1/catalog/datasets/"
                    "histo-validations-reseau-ferre/files/f23d8b3b613b51008b8419a33a47e0cf")

# Dossier de destination, créé s'il n'existe pas
SORTIE = Path("data/raw/validations_2025")
SORTIE.mkdir(parents=True, exist_ok=True)

# Téléchargement de l'archive zip ; raise_for_status arrête le script en cas d'erreur HTTP
print("Téléchargement de l'archive 2025 (~80 Mo) ...", flush=True)
r = requests.get(URL_ARCHIVE_2025, timeout=900)
r.raise_for_status()

# L'archive est ouverte directement en mémoire, sans l'écrire sur le disque
archive = zipfile.ZipFile(io.BytesIO(r.content))

# L'archive contient, pour chaque trimestre, un fichier NB_FER (validations par jour)
# et un fichier PROFIL_FER (profils horaires). Seul NB_FER est utilisé ici.
for t in ("T1", "T2", "T3", "T4"):
    nom_xlsx = f"data-rf-2025/{t} FER/2025_{t}_NB_FER.xlsx"
    print(f"Conversion de {nom_xlsx} ...", end=" ", flush=True)

    # read_only=True : lecture ligne par ligne, beaucoup plus rapide et économe en mémoire
    wb = openpyxl.load_workbook(io.BytesIO(archive.read(nom_xlsx)), read_only=True)
    feuille = wb.worksheets[0]

    # Recopie de chaque ligne de la feuille Excel dans un CSV séparé par des points-virgules
    n = 0
    with open(SORTIE / f"2025_{t}.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f, delimiter=";")
        for ligne in feuille.iter_rows(values_only=True):
            w.writerow(ligne)
            n += 1
    print(f"{n - 1} lignes")   # n - 1 : on ne compte pas la ligne d'en-tête
