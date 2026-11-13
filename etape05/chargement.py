import logging
import os
import time

import pandas as pd
from sqlalchemy import URL, create_engine, text
from sqlalchemy.exc import SQLAlchemyError


CHEMIN_SITES = "data/sites.csv"
CHEMIN_MATERIEL = "sorties/materiel_propre.csv"
CHEMIN_ASSOCIATIONS = "sorties/associations_propre.csv"
CHEMIN_RESERVATIONS = "sorties/reservations_propre.csv"
CHEMIN_REJETS = "sorties/rejets_chargement.csv"

ENCODAGE = "utf-8"

TAILLE_LOT = 500


logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s", datefmt="%H:%M:%S")
journal = logging.getLogger("chargement")


def creer_engine():
    hote = os.environ.get("PGHOST", "localhost")
    port = os.environ.get("PGPORT", "5432")
    base = os.environ.get("PGDATABASE", "ccfl")
    utilisateur = os.environ.get("PGUSER", "postgres")
    mot_de_passe = os.environ.get("PGPASSWORD")

    if not mot_de_passe:
        raise SystemExit("PGPASSWORD n'est pas definie, voir l'en-tete du fichier.")

    journal.info(f"Connexion a {hote}:{port}/{base} en tant que {utilisateur}")

    # URL.create echappe les caracteres speciaux du mot de passe. Un @ ou un /
    # dans le mot de passe casserait une URL assemblee a la main.
    url = URL.create(
        "postgresql+psycopg",
        username=utilisateur,
        password=mot_de_passe,
        host=hote,
        port=int(port),
        database=base,
    )
    return create_engine(url)


def en_lignes(df: pd.DataFrame) -> list:
    return df.astype(object).where(df.notna(), None).to_dict("records")


def vider_tables(conn) -> None:
    conn.execute(text("DELETE FROM reservation"))
    conn.execute(text("DELETE FROM association"))
    conn.execute(text("DELETE FROM materiel"))
    conn.execute(text("DELETE FROM site"))
    journal.info("Tables videes")


def inserer(conn, table: str, sql: str, cle: str, lignes: list, rejets: list) -> tuple:
    requete = text(sql)
    inserees = 0
    rejetees = 0

    for debut in range(0, len(lignes), TAILLE_LOT):
        lot = lignes[debut:debut + TAILLE_LOT]
        try:
            with conn.begin_nested():
                conn.execute(requete, lot)
            inserees = inserees + len(lot)
        except SQLAlchemyError:
            journal.warning(f"{table} : un lot a echoue, reprise ligne par ligne")
            for ligne in lot:
                try:
                    with conn.begin_nested():
                        conn.execute(requete, ligne)
                    inserees = inserees + 1
                except SQLAlchemyError as erreur:
                    rejetees = rejetees + 1
                    rejets.append({
                        "table": table,
                        "identifiant": ligne[cle],
                        "motif_rejet": str(erreur.orig).split("\n")[0],
                    })

    return inserees, rejetees


def charger_sites(conn, rejets: list) -> tuple:
    depart = time.perf_counter()
    df = pd.read_csv(CHEMIN_SITES, encoding=ENCODAGE)

    sql = """
        INSERT INTO site (code_site, nom, commune, annee_ouverture, surface_m2)
        VALUES (:code_site, :nom, :commune, :annee_ouverture, :surface_m2)
    """
    inserees, rejetees = inserer(conn, "site", sql, "code_site", en_lignes(df), rejets)

    duree = time.perf_counter() - depart
    journal.info(f"site : {len(df)} lues, {inserees} inserees, {rejetees} rejetees, {duree:.2f}s")
    return len(df), inserees, rejetees


def charger_materiel(conn, rejets: list) -> tuple:
    depart = time.perf_counter()
    df = pd.read_csv(CHEMIN_MATERIEL, encoding=ENCODAGE)

    df["annee_achat"] = df["annee_achat"].astype("Int64")

    sql = """
        INSERT INTO materiel (id_materiel, reference, designation, categorie,
                              etat, annee_achat, code_site, valeur_achat)
        VALUES (:id_materiel, :reference, :designation, :categorie,
                :etat, :annee_achat, :code_site, :valeur_achat)
    """
    inserees, rejetees = inserer(conn, "materiel", sql, "id_materiel", en_lignes(df), rejets)

    duree = time.perf_counter() - depart
    journal.info(f"materiel : {len(df)} lues, {inserees} inserees, {rejetees} rejetees, {duree:.2f}s")
    return len(df), inserees, rejetees


def charger_associations(conn, rejets: list) -> tuple:
    depart = time.perf_counter()
    df = pd.read_csv(CHEMIN_ASSOCIATIONS, encoding=ENCODAGE, dtype={"code_postal": "string"})

    # oui / non devient un vrai booleen.
    df["convention_active"] = df["convention_active"].map({"oui": True, "non": False})

    sql = """
        INSERT INTO association (id_association, nom, type_association, commune,
                                 code_postal, date_convention, code_site,
                                 convention_active)
        VALUES (:id_association, :nom, :type_association, :commune,
                :code_postal, :date_convention, :code_site, :convention_active)
    """
    inserees, rejetees = inserer(conn, "association", sql, "id_association",
                                 en_lignes(df), rejets)

    duree = time.perf_counter() - depart
    journal.info(f"association : {len(df)} lues, {inserees} inserees, {rejetees} rejetees, {duree:.2f}s")
    return len(df), inserees, rejetees


def charger_reservations(conn, rejets: list) -> tuple:
    depart = time.perf_counter()
    df = pd.read_csv(CHEMIN_RESERVATIONS, encoding=ENCODAGE)

    sql = """
        INSERT INTO reservation (id_reservation, id_materiel, id_association,
                                 code_site, quantite, date_debut,
                                 date_fin_prevue, date_retour_reelle)
        VALUES (:id_reservation, :id_materiel, :id_association,
                :code_site, :quantite, :date_debut,
                :date_fin_prevue, :date_retour_reelle)
    """
    inserees, rejetees = inserer(conn, "reservation", sql, "id_reservation",
                                 en_lignes(df), rejets)

    duree = time.perf_counter() - depart
    journal.info(f"reservation : {len(df)} lues, {inserees} inserees, {rejetees} rejetees, {duree:.2f}s")
    return len(df), inserees, rejetees


def ecrire_rejets(rejets: list) -> None:
    if len(rejets) == 0:
        journal.info("Aucun rejet, pas de fichier de rejets ecrit")
        return
    pd.DataFrame(rejets).to_csv(CHEMIN_REJETS, index=False, encoding=ENCODAGE)
    journal.info(f"{len(rejets)} rejets ecrits dans {CHEMIN_REJETS}")


def main() -> None:
    depart = time.perf_counter()
    engine = creer_engine()
    rejets = []

    with engine.begin() as conn:
        vider_tables(conn)

        # Ordre des dependances : site d'abord, reservation en dernier.
        total_site = charger_sites(conn, rejets)
        total_materiel = charger_materiel(conn, rejets)
        total_association = charger_associations(conn, rejets)
        total_reservation = charger_reservations(conn, rejets)

    ecrire_rejets(rejets)

    journal.info("--- recapitulatif ---")
    journal.info(f"site        : {total_site[0]} lues, {total_site[1]} inserees, {total_site[2]} rejetees")
    journal.info(f"materiel    : {total_materiel[0]} lues, {total_materiel[1]} inserees, {total_materiel[2]} rejetees")
    journal.info(f"association : {total_association[0]} lues, {total_association[1]} inserees, {total_association[2]} rejetees")
    journal.info(f"reservation : {total_reservation[0]} lues, {total_reservation[1]} inserees, {total_reservation[2]} rejetees")
    journal.info(f"Termine en {time.perf_counter() - depart:.2f}s")

if __name__ == "__main__":
    main()
