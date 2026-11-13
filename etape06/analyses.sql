-- Etape 6 - Requetes d'analyse du pret de materiel (CCFL)
-- Lancer depuis la racine du projet : psql -d ccfl -f etape06/analyses.sql


-- Question 1 : par site, nombre de reservations, quantite totale et
-- associations distinctes. LEFT JOIN pour afficher a 0 un pole sans reservation.
SELECT s.code_site,
       s.nom,
       COUNT(r.id_reservation) AS nb_reservations,
       COALESCE(SUM(r.quantite), 0) AS quantite_totale,
       COUNT(DISTINCT r.id_association) AS nb_associations
FROM site s
LEFT JOIN reservation r ON r.code_site = s.code_site
GROUP BY s.code_site, s.nom
ORDER BY nb_reservations DESC;
-- 5 lignes


-- Question 2 : nombre de reservations par mois de date_debut.
SELECT to_char(r.date_debut, 'YYYY-MM') AS mois, COUNT(*) AS nb_reservations
FROM reservation r
GROUP BY to_char(r.date_debut, 'YYYY-MM')
ORDER BY mois;
-- 13 lignes. Octobre 2026 est bas (78 contre 202) car le mois est incomplet.


-- Question 3 : les 10 materiels les plus reserves.
SELECT m.id_materiel,
       m.designation,
       m.categorie,
       COUNT(*) AS nb_reservations
FROM reservation r
JOIN materiel m ON m.id_materiel = r.id_materiel
GROUP BY m.id_materiel, m.designation, m.categorie
ORDER BY nb_reservations DESC, m.id_materiel
LIMIT 10;
-- 10 lignes


-- Question 4 : taux de retard en %, globalement puis par site.
-- Closes uniquement : un pret en cours n'est pas un retard. Le 100.0 force
-- la division decimale.
SELECT 0 AS tri,
       'TOTAL' AS perimetre,
       ROUND(100.0 * COUNT(*) FILTER (WHERE r.date_retour_reelle > r.date_fin_prevue) / COUNT(*), 2) AS taux_retard_pct
FROM reservation r
WHERE r.date_retour_reelle IS NOT NULL
UNION ALL
SELECT 1,
       r.code_site,
       ROUND(100.0 * COUNT(*) FILTER (WHERE r.date_retour_reelle > r.date_fin_prevue) / COUNT(*), 2)
FROM reservation r
WHERE r.date_retour_reelle IS NOT NULL
GROUP BY r.code_site
ORDER BY tri, taux_retard_pct DESC;
-- 6 lignes : 1 globale (32.41 %) puis 5 sites. La colonne tri garde la
-- ligne globale en tete.


-- Question 5 : categories dont le nombre de reservations depasse la moyenne.
WITH reservations_par_categorie AS (
    SELECT m.categorie, COUNT(*) AS nb_reservations
    FROM reservation r
    JOIN materiel m ON m.id_materiel = r.id_materiel
    GROUP BY m.categorie
)

SELECT categorie, nb_reservations
FROM reservations_par_categorie
WHERE nb_reservations > (SELECT AVG(nb_reservations) FROM reservations_par_categorie)
ORDER BY nb_reservations DESC;
-- 2 lignes : Mobilier et Securite, au-dessus d'une moyenne de 760.


-- Question 6 : par site, le materiel le plus reserve. ROW_NUMBER classe
-- dans chaque site, le second critere de tri departage les ex aequo.
WITH comptage_par_site AS (
    SELECT r.code_site,
           m.id_materiel,
           m.designation,
           COUNT(*) AS nb_reservations, ROW_NUMBER() OVER (PARTITION BY r.code_site ORDER BY COUNT(*) DESC, m.id_materiel) AS rang
    FROM reservation r
    JOIN materiel m ON m.id_materiel = r.id_materiel
    GROUP BY r.code_site, m.id_materiel, m.designation
)

SELECT code_site,
       id_materiel,
       designation,
       nb_reservations
FROM comptage_par_site
WHERE rang = 1
ORDER BY nb_reservations DESC;
-- 5 lignes, une par site


-- Question 7 : duree reelle moyenne en jours, globalement puis par
-- categorie, sur les closes.
SELECT 0 AS tri, 'TOTAL' AS categorie, ROUND(AVG(r.date_retour_reelle - r.date_debut), 1) AS duree_moyenne_jours
FROM reservation r
WHERE r.date_retour_reelle IS NOT NULL
UNION ALL
SELECT 1,
       m.categorie, ROUND(AVG(r.date_retour_reelle - r.date_debut), 1)
FROM reservation r
JOIN materiel m ON m.id_materiel = r.id_materiel
WHERE r.date_retour_reelle IS NOT NULL
GROUP BY m.categorie
ORDER BY tri, duree_moyenne_jours DESC;
-- 7 lignes : 1 globale (5.7 jours) puis 6 categories.


-- Cout des requetes
-- Les plus couteuses sont les questions 5, 6 et 7 : elles joignent les 4 560
-- reservations a materiel avant d'agreger. La 5 relit son propre resultat
-- pour la moyenne, la 6 trie dans chaque site par fonction fenetre.
-- Les questions 1 et 2 ne lisent qu'une table et profitent des index poses
-- a l'etape 4 sur code_site et date_debut : ce sont les plus rapides.
