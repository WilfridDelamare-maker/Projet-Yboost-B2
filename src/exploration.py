import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

# 1. Chargement du tableau du J1

df = pd.read_csv(
    "data/processed/table.csv",
    parse_dates=["jour"]
)

Path("rapports/figures").mkdir(
    parents=True,
    exist_ok=True
)

# 2. Découpage temporel

DEBUT_TEST = "2025-10-01"

train = df[df["jour"] < DEBUT_TEST].copy()

# 3. Fonction de création des graphiques

def graphique(data, colonne, titre):
    moyennes = data.groupby(colonne)["nb_vald"].mean()

    print(titre)
    print(moyennes)

    moyennes.plot(kind="bar")

    plt.title(titre)
    plt.ylabel("Validations moyennes")
    plt.tight_layout()

    plt.savefig(f"rapports/figures/{colonne}.png")
    plt.close()

# 4. Analyse exploratoire

graphique(
    train,
    "jour_semaine",
    "Influence du jour de la semaine"
)

graphique(
    train,
    "vacances",
    "Influence des vacances scolaires"
)

graphique(
    train,
    "ferie",
    "Influence des jours fériés"
)

# Analyse de la pluie

train["jour_pluvieux"] = (
    train["pluie"] > 0
).astype(int)

graphique(
    train.dropna(subset=["pluie"]),
    "jour_pluvieux",
    "Influence de la pluie"
)

# Analyse de la température

train["classe_temperature"] = pd.cut(
    train["temperature"],
    bins=[-float("inf"), 15, 25, float("inf")],
    labels=["Froid", "Tempéré", "Chaud"]
)

graphique(
    train,
    "classe_temperature",
    "Influence de la température"
)

# Analyse des événements

graphique(
    train,
    "evenement",
    "Fréquentation avec ou sans événement régional"
)

# 5. Référence naïve J-7

historique = df[["id_zdc", "jour", "nb_vald"]].copy()

historique["jour"] += pd.Timedelta(days=7)

historique = historique.rename(columns={
    "nb_vald": "prediction_j7"
})

df = df.merge(
    historique,
    on=["id_zdc", "jour"],
    how="left",
    validate="one_to_one"
)

# 6. Évaluation sur la période de test

test = df[df["jour"] >= DEBUT_TEST].copy()

test = test.dropna(
    subset=["nb_vald", "prediction_j7"]
)

# Exclure les fermetures connues, si disponibles

if "fermeture" in test.columns:
    test = test[test["fermeture"] == 0]

# 7. Calcul des erreurs

test["erreur"] = abs(
    test["nb_vald"] - test["prediction_j7"]
)

mae = test["erreur"].mean()

wape = (
    test["erreur"].sum()
    / test["nb_vald"].sum()
) * 100

print("MAE :", round(mae, 2))
print("WAPE :", round(wape, 2), "%")

# 8. Graphique réalité / prédiction

id_gare = train.groupby("id_zdc")["nb_vald"].sum().idxmax()

gare = test[test["id_zdc"] == id_gare]
gare = gare.sort_values("jour")

plt.plot(
    gare["jour"],
    gare["nb_vald"],
    label="Réalité"
)

plt.plot(
    gare["jour"],
    gare["prediction_j7"],
    label="Prédiction J-7"
)

plt.title(f"Prédictions pour la gare {id_gare}")
plt.ylabel("Validations")
plt.legend()
plt.xticks(rotation=45)
plt.tight_layout()

plt.savefig("rapports/figures/prediction_j7.png")
plt.close()

# 9. Enregistrement des résultats

scores = pd.DataFrame({
    "modele": ["Reference J-7"],
    "MAE": [mae],
    "WAPE": [wape]
})

scores.to_csv(
    "rapports/scores.csv",
    index=False
)

test.to_csv(
    "data/processed/predictions_j7.csv",
    index=False
)

print("J2 : exploration terminée")