# TP CCFL - Pilotage du prêt de matériel aux associations

Projet du TP d'évaluation (PRF Concepteur développeur en science de la donnée).
Tous les scripts se lancent **depuis la racine du projet**, les chemins sont relatifs.

## Prérequis

- Python 3.12, pandas 2.x, SQLAlchemy 2 + psycopg, Streamlit (étape 7)
- PostgreSQL 14 ou supérieur

## Variables d'environnement (aucun secret en dur)

```
PGHOST=localhost
PGPORT=5432
PGDATABASE=ccfl
PGUSER=<utilisateur>
PGPASSWORD=<mot de passe>
```

## Création de la base

```
createdb ccfl
psql -d ccfl -f etape04/schema.sql
```

## Ordre de lancement

```
python etape01/exploration.py        # exploration sans pandas
python etape02/analyse_pandas.py     # agrégats + sorties/top10_materiel.csv
python etape03/qualite.py            # fichiers propres + sorties/rapport_qualite.md
python etape05/chargement.py         # chargement PostgreSQL
psql -d ccfl -f etape06/requetes.sql # SQL d'analyse
streamlit run etape07/app.py         # bonus
```

## Arborescence

- `data/` : les 4 CSV fournis, **jamais modifiés**
- `etape01/` ... `etape07/` : le code de chaque étape
- `sorties/` : tous les fichiers produits (CSV, rapports)
- `auto-evaluation.md` : avancement étape par étape
