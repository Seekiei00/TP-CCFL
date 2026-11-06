import csv
from collections import Counter

CHEMIN_SITES = "data/sites.csv"
CHEMIN_MATERIEL = "data/materiel.csv"
CHEMIN_ASSOCIATIONS = "data/associations.csv"
CHEMIN_RESERVATIONS = "data/reservations.csv"

ENCODAGE = "utf-8"

ANNEE_REFERENCE = 2026


def lire_csv(chemin):
    with open(chemin, encoding=ENCODAGE, newline="") as fichier:
        return list(csv.DictReader(fichier))

def compter_par(lignes, colonne):
    return dict(Counter(ligne[colonne] for ligne in lignes))

def total_par(lignes, colonne_groupe, colonne_valeur):
    totaux = {}
    for ligne in lignes:
        groupe = ligne[colonne_groupe]
        valeur = entier_ou_none(ligne[colonne_valeur])
        if valeur is None:
            continue
        totaux[groupe] = totaux.get(groupe, 0) + valeur
    return totaux

def entier_ou_none(valeur):
    try:
        return int(str(valeur).strip())
    except (TypeError, ValueError):
        return None

def trier_decroissant(dictionnaire):
    return sorted(dictionnaire.items(), key=lambda paire: paire[1], reverse=True)

class Site:
    def __init__(self, code_site, nom, commune, annee_ouverture, surface_m2):
        self.code_site = code_site
        self.nom = nom
        self.commune = commune
        self.annee_ouverture = int(annee_ouverture)
        self.surface_m2 = int(surface_m2)

    def anciennete(self, annee_reference):
        return annee_reference - self.annee_ouverture

    def __str__(self):
        return (
            f"{self.code_site} - {self.nom} ({self.commune}), "
            f"{self.surface_m2} m2"
        )

def construire_sites(lignes):
    return [
        Site(
            ligne["code_site"],
            ligne["nom"],
            ligne["commune"],
            ligne["annee_ouverture"],
            ligne["surface_m2"],
        )
        for ligne in lignes
    ]

def reservations_en_cours(reservations):
    return [
        ligne
        for ligne in reservations
        if not ligne["date_retour_reelle"].strip()
    ]

def afficher_titre(titre):
    print()
    print(titre)
    print("-" * len(titre))

def main():
    sites = lire_csv(CHEMIN_SITES)
    materiel = lire_csv(CHEMIN_MATERIEL)
    associations = lire_csv(CHEMIN_ASSOCIATIONS)
    reservations = lire_csv(CHEMIN_RESERVATIONS)

    afficher_titre("1. Nombre de lignes par fichier")
    for chemin, lignes in (
        (CHEMIN_SITES, sites),
        (CHEMIN_MATERIEL, materiel),
        (CHEMIN_ASSOCIATIONS, associations),
        (CHEMIN_RESERVATIONS, reservations),
    ):
        print(f"{chemin} : {len(lignes)} lignes")

    afficher_titre(f"2. Les poles de retrait et leur anciennete en {ANNEE_REFERENCE}")
    for site in construire_sites(sites):
        print(f"{site} - anciennete : {site.anciennete(ANNEE_REFERENCE)} ans")

    afficher_titre("3. Nombre de reservations par pole (du plus grand au plus petit)")
    reservations_par_site = compter_par(reservations, "code_site")
    for code_site, nombre in trier_decroissant(reservations_par_site):
        print(f"{code_site} : {nombre} reservations")
    print(f"Total : {sum(reservations_par_site.values())} reservations")

    afficher_titre("4. Quantite totale reservee par pole (du plus grand au plus petit)")
    quantites_par_site = total_par(reservations, "code_site", "quantite")
    for code_site, quantite in trier_decroissant(quantites_par_site):
        print(f"{code_site} : {quantite} unites")
    print(f"Total : {sum(quantites_par_site.values())} unites")

    afficher_titre("5. Nombre de materiels par etat")
    for etat, nombre in trier_decroissant(compter_par(materiel, "etat")):
        print(f"{etat} : {nombre} materiels")

    afficher_titre("6. Categories de materiel")
    categories = compter_par(materiel, "categorie")
    print(f"Nombre de valeurs distinctes de categorie : {len(categories)}")

    afficher_titre("7. Prets en cours")
    en_cours = reservations_en_cours(reservations)
    print(f"Nombre de reservations en cours (materiel non encore rendu) : {len(en_cours)}")

if __name__ == "__main__":
    main()
