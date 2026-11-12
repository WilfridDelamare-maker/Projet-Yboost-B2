import pandas as pd

df = pd.read_csv(
    "data/raw/validations/validations_1er_trimestre_2025.csv",
    sep=";"
)

print(df.head()) # affiche les 5 premieres lignes
print(df.columns) # nom des colonnes
print(df.shape) # dimensions du tableau (lignes et colonnes)