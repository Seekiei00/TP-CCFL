import pandas as pd


CHEMIN_SITES = "data/sites.csv"
CHEMIN_MATERIEL = "data/materiel.csv"
CHEMIN_ASSOCIATIONS = "data/associations.csv"
CHEMIN_RESERVATIONS = "data/reservations.csv"

ENCODAGE = "utf-8"


# --- Chargement des 4 fichiers ---

df_sites = pd.read_csv(CHEMIN_SITES, encoding=ENCODAGE)
df_materiel = pd.read_csv(CHEMIN_MATERIEL, encoding=ENCODAGE)
df_associations = pd.read_csv(CHEMIN_ASSOCIATIONS, encoding=ENCODAGE)
df_reservations = pd.read_csv(CHEMIN_RESERVATIONS, encoding=ENCODAGE)

# Conversion des 3 colonnes de dates des reservations
df_reservations["date_debut"] = pd.to_datetime(df_reservations["date_debut"])
df_reservations["date_fin_prevue"] = pd.to_datetime(df_reservations["date_fin_prevue"])
df_reservations["date_retour_reelle"] = pd.to_datetime(df_reservations["date_retour_reelle"])

print("Nombre de lignes par fichier :")
print("df_sites :", df_sites.shape[0])
print("df_materiel :", df_materiel.shape[0])
print("df_associations :", df_associations.shape[0])
print("df_reservations :", df_reservations.shape[0])


# --- df_materiel ---

print("\n=== df_materiel ===")

print("\nForme (lignes, colonnes) :", df_materiel.shape)

print("\nInfo :")
df_materiel.info()

print("\nValeurs manquantes par colonne :")
print(df_materiel.isna().sum())


# --- df_reservations ---

print("\n=== df_reservations ===")

print("\nForme (lignes, colonnes) :", df_reservations.shape)

print("\nInfo :")
df_reservations.info()

print("\nValeurs manquantes par colonne :")
print(df_reservations.isna().sum())


# --- Conversion de valeur_achat ---

print("\n=== valeur_achat ===")

print("\nType avant conversion :", df_materiel["valeur_achat"].dtype)

print("\nValeurs qui empechent la conversion :")
print(df_materiel["valeur_achat"][df_materiel["valeur_achat"].str.contains(",", na=False)])

# Cause : quelques valeurs sont saisies avec une virgule decimale au lieu d'un point.
df_materiel["valeur_achat"] = pd.to_numeric(
    df_materiel["valeur_achat"].str.replace(",", "."), errors="coerce"
)

print("\nType apres conversion :", df_materiel["valeur_achat"].dtype)
print("Valeurs manquantes apres conversion :", df_materiel["valeur_achat"].isna().sum())
