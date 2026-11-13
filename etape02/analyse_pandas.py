import pandas as pd


CHEMIN_SITES = "data/sites.csv"
CHEMIN_MATERIEL = "data/materiel.csv"
CHEMIN_ASSOCIATIONS = "data/associations.csv"
CHEMIN_RESERVATIONS = "data/reservations.csv"

CHEMIN_TOP10 = "sorties/top10_materiel.csv"

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


# --- Les 10 materiels les plus chers ---

top10_chers = df_materiel.sort_values("valeur_achat", ascending=False).head(10)

print("\n=== Les 10 materiels les plus chers ===")
print(top10_chers[["reference", "designation", "categorie", "valeur_achat"]].to_string(index=False))


# --- Nombre de materiels par categorie ---

materiels_par_categorie = df_materiel["categorie"].value_counts()

print("\n=== Nombre de materiels par categorie ===")
print(materiels_par_categorie.to_string())


# --- Reservations et quantite par pole, en un seul groupby ---

par_site = df_reservations.groupby("code_site").agg(
    nb_reservations=("id_reservation", "size"),
    quantite_totale=("quantite", "sum"),
).sort_values("nb_reservations", ascending=False)

print("\n=== Reservations et quantite par pole ===")
print(par_site.to_string())


# --- Fusion des trois tables ---

# materiel.csv contient des lignes en double : sans drop_duplicates la fusion
# dupliquerait les reservations correspondantes.
df_materiel_unique = df_materiel.drop_duplicates()

print("\n=== Fusion ===")
print("Lignes de df_materiel :", len(df_materiel))
print("Lignes de df_materiel sans doublon :", len(df_materiel_unique))

df_complet = df_reservations.merge(df_materiel_unique, on="id_materiel", how="left")
df_complet = df_complet.merge(df_associations, on="id_association", how="left")

print("Lignes de df_reservations :", len(df_reservations))
print("Lignes de df_complet :", len(df_complet))
print("Lignes sans materiel correspondant :", df_complet["designation"].isna().sum())


# --- Top 10 des materiels les plus reserves ---

top10_reserves = (
    df_complet.groupby(["id_materiel", "designation"])
    .size()
    .reset_index(name="nb_reservations")
    .sort_values("nb_reservations", ascending=False)
    .head(10)
)

print("\n=== Top 10 des materiels les plus reserves ===")
print(top10_reserves.to_string(index=False))

top10_reserves.to_csv(CHEMIN_TOP10, index=False, encoding=ENCODAGE)
print("\nExporte dans", CHEMIN_TOP10)
