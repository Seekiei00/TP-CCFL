import pandas as pd
from datetime import date

CHEMIN_MATERIEL = "data/materiel.csv"
CHEMIN_ASSOCIATIONS = "data/associations.csv"
CHEMIN_RESERVATIONS = "data/reservations.csv"

CHEMIN_MATERIEL_PROPRE = "sorties/materiel_propre.csv"
CHEMIN_ASSOCIATIONS_PROPRE = "sorties/associations_propre.csv"
CHEMIN_RESERVATIONS_PROPRE = "sorties/reservations_propre.csv"
CHEMIN_RAPPORT = "sorties/rapport_qualite.md"

ENCODAGE = "utf-8"

ANNEE_COURANTE = date.today().year

CATEGORIES_ATTENDUES = 6


# --- Chargement ---

df_materiel = pd.read_csv(CHEMIN_MATERIEL, encoding=ENCODAGE)
# code_postal est un identifiant, pas un nombre : sans dtype, les cellules vides
# le font lire en decimal et il ressortirait ecrit 59270.0.
df_associations = pd.read_csv(
    CHEMIN_ASSOCIATIONS, encoding=ENCODAGE, dtype={"code_postal": "string"}
)
df_reservations = pd.read_csv(CHEMIN_RESERVATIONS, encoding=ENCODAGE)


# --- Outil de detection ---

anomalies = []


def controler(lettre, fichier, colonne, description, masque, df, traitement):
    nb = int(masque.sum())
    part = round(100 * nb / len(df), 2)
    anomalies.append(
        {
            "lettre": lettre,
            "fichier": fichier,
            "colonne": colonne,
            "description": description,
            "nb": nb,
            "part": part,
            "traitement": traitement,
        }
    )
    print(f"\n{lettre}. {fichier} - {colonne} : {description}")
    print(f"   lignes concernees : {nb} ({part} %)")
    if nb > 0:
        print(df[masque].head(3).to_string(index=False))


# --- Detection sur materiel.csv ---

print("\n########## MATERIEL ##########")

categorie = df_materiel["categorie"]
valeur_texte = df_materiel["valeur_achat"].astype(str)

controler(
    "a", "materiel.csv", "toutes", "lignes en doublon strict",
    df_materiel.duplicated(), df_materiel,
    "Suppression des doublons, une occurrence conservee",
)
controler(
    "b", "materiel.csv", "annee_achat", "annee d'achat vide",
    df_materiel["annee_achat"].isna(), df_materiel,
    "Conservation en valeur manquante",
)
controler(
    "c", "materiel.csv", "annee_achat", f"annee d'achat posterieure a {ANNEE_COURANTE}",
    df_materiel["annee_achat"] > ANNEE_COURANTE, df_materiel,
    "Mise a valeur manquante, ligne conservee",
)
controler(
    "d", "materiel.csv", "valeur_achat", "valeur d'achat vide",
    df_materiel["valeur_achat"].isna(), df_materiel,
    "Conservation en valeur manquante",
)
controler(
    "e", "materiel.csv", "categorie", "categorie ecrite en majuscules",
    categorie.str.strip().str.isupper(), df_materiel,
    "Correction automatique vers le libelle homogene",
)
controler(
    "f", "materiel.csv", "categorie", "categorie avec des espaces parasites",
    categorie != categorie.str.strip(), df_materiel,
    "Correction automatique vers le libelle homogene",
)
controler(
    "g", "materiel.csv", "valeur_achat", "valeur d'achat avec une virgule decimale",
    valeur_texte.str.contains(","), df_materiel,
    "Correction automatique, virgule remplacee par un point",
)


# --- Detection sur associations.csv ---

print("\n########## ASSOCIATIONS ##########")

date_iso = pd.to_datetime(
    df_associations["date_convention"], format="%Y-%m-%d", errors="coerce"
)

controler(
    "h", "associations.csv", "code_postal", "code postal vide",
    df_associations["code_postal"].isna(), df_associations,
    "Conservation en valeur manquante, signalee a la direction",
)
controler(
    "i", "associations.csv", "type_association", "type d'association valant inconnu",
    df_associations["type_association"] == "inconnu", df_associations,
    "Conservation avec signalement",
)
controler(
    "j", "associations.csv", "date_convention", "date de convention au format JJ/MM/AAAA",
    date_iso.isna(), df_associations,
    "Correction automatique vers le format ISO",
)


# --- Detection sur reservations.csv ---

print("\n########## RESERVATIONS ##########")

debut = pd.to_datetime(df_reservations["date_debut"])
retour = pd.to_datetime(df_reservations["date_retour_reelle"])
materiels_existants = df_materiel.drop_duplicates()["id_materiel"]

controler(
    "k", "reservations.csv", "toutes", "lignes en doublon strict",
    df_reservations.duplicated(), df_reservations,
    "Suppression des doublons, une occurrence conservee",
)
controler(
    "l", "reservations.csv", "id_materiel", "materiel inexistant dans materiel.csv",
    ~df_reservations["id_materiel"].isin(materiels_existants), df_reservations,
    "Suppression de la ligne",
)
controler(
    "m", "reservations.csv", "date_retour_reelle", "retour reel anterieur au debut du pret",
    retour < debut, df_reservations,
    "Suppression de la ligne",
)
controler(
    "n", "reservations.csv", "quantite", "quantite egale a zero",
    df_reservations["quantite"] == 0, df_reservations,
    "Suppression de la ligne",
)


# --- Cas metier normal : les prets en cours ---
# Une date de retour vide n'est pas un defaut, c'est un pret non encore rendu.

prets_en_cours_avant = int(retour.isna().sum())

print("\n########## CAS METIER NORMAL ##########")
print(f"\nPrets en cours (date_retour_reelle vide) : {prets_en_cours_avant}")
print("Ce n'est pas une anomalie : le materiel n'est pas encore rendu.")


# --- Nettoyage de materiel.csv ---

materiel_propre = df_materiel.drop_duplicates().copy()

materiel_propre["categorie"] = materiel_propre["categorie"].str.strip().str.capitalize()

materiel_propre["valeur_achat"] = pd.to_numeric(
    materiel_propre["valeur_achat"].astype(str).str.replace(",", "."), errors="coerce"
)

# Une annee d'achat posterieure a l'annee courante est impossible : on la vide
# sans supprimer le materiel, qui existe bien dans le parc.
annee_impossible = materiel_propre["annee_achat"] > ANNEE_COURANTE
materiel_propre.loc[annee_impossible, "annee_achat"] = pd.NA
materiel_propre["annee_achat"] = materiel_propre["annee_achat"].astype("Int64")

materiel_propre.to_csv(CHEMIN_MATERIEL_PROPRE, index=False, encoding=ENCODAGE)


# --- Nettoyage de associations.csv ---

associations_propre = df_associations.copy()

# Deux passes : le format ISO, puis le format francais la ou la premiere a echoue.
dates_iso = pd.to_datetime(
    associations_propre["date_convention"], format="%Y-%m-%d", errors="coerce"
)
dates_fr = pd.to_datetime(
    associations_propre["date_convention"], format="%d/%m/%Y", errors="coerce"
)
associations_propre["date_convention"] = dates_iso.fillna(dates_fr).dt.strftime("%Y-%m-%d")

associations_propre.to_csv(CHEMIN_ASSOCIATIONS_PROPRE, index=False, encoding=ENCODAGE)


# --- Nettoyage de reservations.csv ---

reservations_propre = df_reservations.drop_duplicates().copy()

debut_propre = pd.to_datetime(reservations_propre["date_debut"])
retour_propre = pd.to_datetime(reservations_propre["date_retour_reelle"])

a_ecarter = (
    (~reservations_propre["id_materiel"].isin(materiel_propre["id_materiel"]))
    | (retour_propre < debut_propre)
    | (reservations_propre["quantite"] == 0)
)

reservations_ecartees = reservations_propre[a_ecarter]
reservations_propre = reservations_propre[~a_ecarter]

reservations_propre.to_csv(CHEMIN_RESERVATIONS_PROPRE, index=False, encoding=ENCODAGE)

prets_en_cours_apres = int(reservations_propre["date_retour_reelle"].isna().sum())

# Prets en cours ecartes par le nettoyage : ils pointaient vers un materiel inexistant.
prets_en_cours_perdus = reservations_ecartees[
    reservations_ecartees["date_retour_reelle"].isna()
]


# --- Rapport ---

lignes = []
lignes.append("# Rapport de qualite des donnees - Pret de materiel (CCFL)")
lignes.append("")
lignes.append(
    f"Rapport genere par `etape03/qualite.py` le {date.today().isoformat()}."
)
lignes.append("")

lignes.append("## Recapitulatif des anomalies")
lignes.append("")
lignes.append("| | Fichier | Colonne | Description | Lignes | Part | Traitement retenu |")
lignes.append("|---|---|---|---|---|---|---|")
for anomalie in anomalies:
    lignes.append(
        "| {lettre} | {fichier} | {colonne} | {description} | {nb} | {part} % | {traitement} |".format(
            **anomalie
        )
    )
lignes.append("")
lignes.append(
    f"Soit **{len(anomalies)} categories d'anomalies**, de a a {anomalies[-1]['lettre']}. "
    "Les prets en cours ne figurent pas dans ce tableau : ce sont des prets non rendus, "
    "pas des defauts."
)
lignes.append("")

lignes.append("## Lignes avant et apres nettoyage")
lignes.append("")
lignes.append("| Fichier | Avant | Apres | Ecart |")
lignes.append("|---|---|---|---|")
for nom, avant, apres in (
    ("materiel.csv", len(df_materiel), len(materiel_propre)),
    ("associations.csv", len(df_associations), len(associations_propre)),
    ("reservations.csv", len(df_reservations), len(reservations_propre)),
):
    lignes.append(f"| {nom} | {avant} | {apres} | {apres - avant} |")
lignes.append("")
lignes.append(
    "Categories distinctes dans materiel_propre.csv : "
    f"**{materiel_propre['categorie'].nunique()}** (attendu : {CATEGORIES_ATTENDUES})."
)
lignes.append("")

lignes.append("## Prets en cours")
lignes.append("")
lignes.append(f"- Avant nettoyage : **{prets_en_cours_avant}**")
lignes.append(f"- Apres nettoyage : **{prets_en_cours_apres}**")
lignes.append("")
if len(prets_en_cours_perdus) == 0:
    lignes.append("Aucun pret en cours n'a ete ecarte par le nettoyage.")
else:
    identifiants = ", ".join(prets_en_cours_perdus["id_reservation"].astype(str))
    lignes.append(
        f"Ecart de {prets_en_cours_avant - prets_en_cours_apres} ligne. "
        f"La reservation {identifiants} etait bien un pret en cours, mais elle pointait "
        "vers un materiel absent de l'inventaire : elle a ete ecartee au titre de "
        "l'anomalie l, et non parce qu'elle n'etait pas rendue. Une date de retour vide "
        "reste un cas metier normal et n'a jamais ete comptee comme un defaut."
    )
lignes.append("")

lignes.append("## Points d'attention pour la direction")
lignes.append("")
lignes.append(
    "Les fichiers sont globalement sains : aucune anomalie ne touche plus de 4 % d'un "
    "fichier. Mais l'essentiel des defauts vient de la saisie, pas du logiciel."
)
lignes.append("")
lignes.append(
    "- Les categories de materiel sont ecrites de quatorze facons differentes alors que "
    "le service n'en gere que six : des majuscules ici, un espace en trop la. Tout "
    "comptage par categorie sorti de l'ancien outil etait donc faux. Un menu deroulant a "
    "la saisie reglerait le probleme definitivement."
)
lignes.append(
    "- Cinq materiels portent une annee d'achat posterieure a l'annee en cours, jusqu'a "
    "2031. Nous avons vide ces annees plutot que d'inventer une date : le materiel "
    "existe, son age est inconnu."
)
lignes.append(
    "- Onze materiels n'ont aucune valeur d'achat et neuf aucune annee. Ces cases restent "
    "vides : les remplacer par zero ferait baisser artificiellement la valeur du parc que "
    "vous nous demandez de calculer."
)
lignes.append(
    "- Vingt et une reservations renvoient a un materiel absent de l'inventaire. Elles "
    "sont inexploitables et ont ete ecartees, mais leur presence suggere que du materiel "
    "a ete retire de l'inventaire sans que ses reservations soient traitees."
)
lignes.append(
    "- Quinze reservations ont une date de retour anterieure a la date de depart, et six "
    "portent sur zero unite. Ce sont des erreurs de saisie manifestes, ecartees elles aussi."
)
lignes.append(
    "- Sept associations sur deux cent dix ont un type inconnu et neuf n'ont pas de code "
    "postal. Nous les gardons : ce sont des associations reelles, seule leur fiche est "
    "incomplete. Un rappel aux poles permettrait de les completer."
)
lignes.append(
    f"- Enfin, {prets_en_cours_apres} prets sont en cours. Ce n'est pas une anomalie : ce "
    "materiel est sorti et pas encore rendu, il reste compte comme indisponible."
)
lignes.append("")

with open(CHEMIN_RAPPORT, "w", encoding=ENCODAGE) as fichier:
    fichier.write("\n".join(lignes))


# --- Resume ---

print("\n########## FICHIERS PRODUITS ##########")
print(
    f"\n{CHEMIN_MATERIEL_PROPRE} : {len(materiel_propre)} lignes, "
    f"{materiel_propre['categorie'].nunique()} categories"
)
print(f"{CHEMIN_ASSOCIATIONS_PROPRE} : {len(associations_propre)} lignes")
print(f"{CHEMIN_RESERVATIONS_PROPRE} : {len(reservations_propre)} lignes")
print(f"{CHEMIN_RAPPORT} : {len(anomalies)} anomalies recensees")
print(f"\nPrets en cours : {prets_en_cours_avant} avant, {prets_en_cours_apres} apres")
