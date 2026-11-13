
DROP TABLE IF EXISTS reservation;
DROP TABLE IF EXISTS association;
DROP TABLE IF EXISTS materiel;
DROP TABLE IF EXISTS site;


-- --------------------------------------------------------------------
-- site : les cinq poles de retrait
-- --------------------------------------------------------------------

CREATE TABLE site (
    code_site CHAR(7) PRIMARY KEY,
    nom TEXT NOT NULL,
    commune TEXT NOT NULL,
    annee_ouverture SMALLINT NOT NULL,
    surface_m2 INTEGER NOT NULL
);


-- --------------------------------------------------------------------
-- materiel : le parc prêtable, stocke dans un pole
-- --------------------------------------------------------------------

CREATE TABLE materiel (
    id_materiel INTEGER PRIMARY KEY,
    reference CHAR(8) NOT NULL UNIQUE,
    designation TEXT NOT NULL,
    categorie TEXT NOT NULL,
    etat TEXT NOT NULL,
    annee_achat SMALLINT,
    code_site CHAR(7) NOT NULL REFERENCES site (code_site),
    valeur_achat NUMERIC(8,2)
);


-- --------------------------------------------------------------------
-- association : les associations conventionnees
-- --------------------------------------------------------------------

CREATE TABLE association (
    id_association INTEGER PRIMARY KEY,
    nom TEXT NOT NULL,
    type_association TEXT NOT NULL,
    commune TEXT NOT NULL,
    code_postal CHAR(5),
    date_convention DATE NOT NULL,
    code_site CHAR(7) NOT NULL REFERENCES site (code_site),
    convention_active BOOLEAN NOT NULL
);


-- --------------------------------------------------------------------
-- reservation : les prets
-- --------------------------------------------------------------------

CREATE TABLE reservation (
    id_reservation CHAR(7) PRIMARY KEY,
    id_materiel INTEGER NOT NULL REFERENCES materiel (id_materiel),
    id_association INTEGER NOT NULL REFERENCES association (id_association),
    code_site CHAR(7) NOT NULL REFERENCES site (code_site),
    quantite INTEGER NOT NULL CONSTRAINT quantite_strictement_positive CHECK (quantite > 0),
    date_debut DATE NOT NULL,
    date_fin_prevue DATE NOT NULL,
    date_retour_reelle DATE, 
    
    CONSTRAINT fin_prevue_apres_debut CHECK (date_fin_prevue >= date_debut)
);


-- --------------------------------------------------------------------
-- Index
-- --------------------------------------------------------------------

-- Question 2 : regroupement par mois de date_debut.
CREATE INDEX idx_reservation_date_debut ON reservation (date_debut);

-- Questions 3 et 6, et jointure vers materiel : une cle etrangere
-- n'est pas indexee automatiquement sous PostgreSQL.
CREATE INDEX idx_reservation_id_materiel ON reservation (id_materiel);

-- Questions 1 et 4 : comptages et taux de retard par pole.
CREATE INDEX idx_reservation_code_site ON reservation (code_site);
