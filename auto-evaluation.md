# Auto-évaluation — GHARAB Mourad

## Étapes

| Étape | État (terminée / partielle / non abordée) | Points de vérification obtenus | Ce qui a bloqué | Temps réel passé par étape |
|---|---|---|---|---|
| 1 | terminée | 5/5 : 5 sites, 367 matériels, 210 associations, 4618 réservations ; POL-HAZ en tête avec 1869 réservations et somme des 5 pôles = 4618 ; 181 matériels à l'état bon ; 14 valeurs distinctes de categorie au lieu de 6 (relevé, non corrigé, à traiter à l'étape 3) ; 72 réservations en cours. | Rien de bloquant. Point d'attention : date_retour_reelle vide se teste avec .strip() pour attraper aussi les chaînes d'espaces, sinon le compte des prêts en cours est faux. | 1h
| 2 | terminée  | 7/7 : df_reservations.shape = (4618, 8) et df_materiel.shape = (367, 8) ; les 3 colonnes de dates en datetime64 et valeur_achat en float64 après conversion ; 72 manquants sur date_retour_reelle, cohérent avec l'étape 1. Les 3 points restants (21 lignes sans matériel, lignes de df_complet, top 10 à 48 réservations) portent sur les consignes 5 à 8, non traitées. | valeur_achat ressort en texte parce que 5 matériels ont leur valeur saisie avec une virgule décimale ; convertie dans le script avec str.replace puis to_numeric, les 11 cellules vides restant vides. La fusion gonflait df_complet : materiel.csv contient 7 doublons stricts, donc un drop_duplicates() est nécessaire avant le merge, sinon le top 10 est faussé. | 1h |
| 3 | terminée | 6/6 : 14 catégories d'anomalies de a à n ; chaque anomalie de materiel.csv sous 4 % (max 3,0 %) ; 21 réservations à matériel inexistant, identique à l'étape 2 ; materiel_propre.csv = 360 lignes et 6 catégories ; reservations_propre.csv = 4560 lignes ; prêts en cours 72 → 71. | L'écart sur les prêts en cours : la réservation R253433 est un prêt non rendu mais pointe vers le matériel 9999 inexistant, elle est écartée au titre de l'anomalie l. Deux pièges de typage trouvés en vérifiant les fichiers produits : code_postal sortait en 59270.0 et annee_achat en 2021.0, corrigés avec dtype à la lecture et Int64. | 1h30 |
| 4 | terminée |  4/4 : schéma exécuté deux fois sans erreur, \dt retourne 4 tables, 5 clés étrangères, et les insertions avec POL-XXX et quantité 0 sont bien refusées. |  | 45mn |
| 5 | terminée  |  5/5 : 5 sites et 210 associations ; 360 matériels et 4560 réservations, identiques aux fichiers nettoyés de l'étape 3 ; script relancé sans erreur avec des comptages identiques ; 71 réservations sans date de retour, comme le rapport de l'étape 3 ; 0 réservation orpheline en jointure sur materiel. | : un mot de passe contenant un @ cassait l'URL de connexion assemblée à la main — psycopg lisait le mot de passe comme une partie du nom d'hôte. Corrigé avec URL.create(), qui échappe les caractères spéciaux. | 1h |
| 6 | non abordée | | | |
| 7 | non abordée | | | |

## Ce que je sais faire mieux qu'en septembre
J'écris des fonctions qui renvoient une valeur au lieu de tout imprimer dedans, et je déclare mes chemins en constantes relatives en haut du module.
Je retrouve le même résultat par deux chemins : csv.DictReader + Counter en Python pur.
Je travaille avec git sans y réfléchir : dépôt public, un commit par étape, .gitignore propre sans venv ni cache.

## Ce qui me résiste encore
Le typage pandas : je n'anticipe pas qu'une colonne avec des cellules vides sorte en float64, ni qu'une seule virgule décimale fasse basculer toute une colonne en texte.
Je dois encore faire l'effort conscient de vérifier un résultat après coup au lieu de supposer qu'il est bon.
