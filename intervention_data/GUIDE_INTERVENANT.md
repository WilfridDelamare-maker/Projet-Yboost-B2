# Groupe 1 : guide d'intervention, traitement et analyse des données

**Sujet :** prédire l'affluence des gares d'Île-de-France en fonction de la météo et des événements locaux.

## 1. État du projet

| Élément | État |
|---|---|
| Script de collecte (`outils/telecharger_donnees.py`) | Fonctionnel : validations IDFM, météo, jours fériés, vacances scolaires |
| Fichier d'événements (`evenements_2025.csv`) | 191 événements saisis manuellement, incomplet |
| Nettoyage, jointures, analyse | Non commencés |
| `readme.md`, `requirements.txt` | Vides ou à reprendre |

## 2. Points bloquants et corrections

| Problème | Conséquence | Correction |
|---|---|---|
| Les fichiers T1 et T2 « 2025 » contiennent des données 2026 (jeux IDFM remplacés chaque année) | Moitié de l'année impossible à joindre à la météo et aux événements | `telecharger_validations_2025.py` récupère l'archive historique 2025 |
| Formats différents entre trimestres (nom et format de la date, casse, ordre des colonnes) | Dates erronées sans message d'erreur | Fonction de lecture unique avec conversions explicites |
| Une gare porte plusieurs libellés (La Défense : 3) | Gares fragmentées, trafic sous-estimé | Agrégation par `id_zdc` |
| Catégorie de titre écrite avec et sans accent | Catégorie comptée deux fois | Normalisation des accents |
| 1 738 gare-jours à zéro (fermetures pour travaux) | Bruit pour le modèle | Variable `gare_fermee` |
| Fichier d'événements incomplet | Pics d'affluence inexpliqués | Liste des dates à vérifier produite par le notebook |

## 3. Résultats d'analyse

| Facteur | Effet mesuré | Interprétation |
|---|---|---|
| Jour de la semaine | samedi -25 %, dimanche -47 % | Facteur principal ; mardi le plus chargé (effet télétravail lundi et vendredi) |
| Vacances scolaires | -22 % (août : environ -45 %) | Indispensable dans le modèle |
| Jours fériés | -42 % | Indispensable dans le modèle |
| Météo | moins de 2 % d'écart, corrélations proches de 0 | Les déplacements contraints ne dépendent pas du temps ; hypothèse non confirmée au niveau réseau |
| Événements | x1,6 en médiane ; x2 à x2,5 Stade de France ; x8 Villepinte ; nul à La Défense | Effet fort mais local, proportionnel au rapport taille de l'événement / trafic habituel de la gare |

Méthode utilisée : chaque jour est comparé à une affluence attendue (médiane des jours comparables : même gare,
même jour de semaine, même statut vacances). Sans cette normalisation, les effets sont masqués par le calendrier.

## 4. Déroulé proposé (environ 1 h 30)

1. Vérification des sources : montrer le problème des fichiers 2026 (10 min).
2. Harmonisation et contrôle qualité : formats, accents, identifiants de gare (20 min).
3. Agrégation et enrichissement : calendrier, météo, rattachement des événements aux gares (20 min).
4. Analyse : calendrier, météo, événements, avec interprétation de chaque résultat (30 min).
5. Anomalies et suite du projet (10 min).

## 5. Recommandations pour la suite

1. Compléter le fichier d'événements à partir des pics non expliqués.
2. Recentrer la cible sur les gares proches de lieux d'événements, plus pertinentes au regard du sujet.
3. Définir une référence simple à battre (valeur du même jour la semaine précédente).
4. Découper les données dans le temps (janvier-octobre / novembre-décembre), jamais aléatoirement.
5. Exclure ou signaler les jours de fermeture.
6. Compléter `requirements.txt` : pandas, numpy, matplotlib, requests, openpyxl, jupyter.

## 6. Fichiers

| Fichier | Contenu |
|---|---|
| `intervention_data/telecharger_validations_2025.py` | Récupération des validations 2025 (environ 1 min) |
| `intervention_data/preparation_analyse_donnees.ipynb` | Notebook exécuté, avec graphiques et interprétations |
| `data/processed/affluence_gare_jour_2025.csv.gz` | 626 gares x 365 jours avec variables calendrier, météo, événements |
| `data/processed/affluence_reseau_jour_2025.csv` | Total réseau par jour avec variables calendrier et météo |
