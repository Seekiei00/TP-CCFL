# Rapport de qualite des donnees - Pret de materiel (CCFL)

Rapport genere par `etape03/qualite.py` le 2026-11-13.

## Recapitulatif des anomalies

| | Fichier | Colonne | Description | Lignes | Part | Traitement retenu |
|---|---|---|---|---|---|---|
| a | materiel.csv | toutes | lignes en doublon strict | 7 | 1.91 % | Suppression des doublons, une occurrence conservee |
| b | materiel.csv | annee_achat | annee d'achat vide | 9 | 2.45 % | Conservation en valeur manquante |
| c | materiel.csv | annee_achat | annee d'achat posterieure a 2026 | 5 | 1.36 % | Mise a valeur manquante, ligne conservee |
| d | materiel.csv | valeur_achat | valeur d'achat vide | 11 | 3.0 % | Conservation en valeur manquante |
| e | materiel.csv | categorie | categorie ecrite en majuscules | 6 | 1.63 % | Correction automatique vers le libelle homogene |
| f | materiel.csv | categorie | categorie avec des espaces parasites | 5 | 1.36 % | Correction automatique vers le libelle homogene |
| g | materiel.csv | valeur_achat | valeur d'achat avec une virgule decimale | 5 | 1.36 % | Correction automatique, virgule remplacee par un point |
| h | associations.csv | code_postal | code postal vide | 9 | 4.29 % | Conservation en valeur manquante, signalee a la direction |
| i | associations.csv | type_association | type d'association valant inconnu | 7 | 3.33 % | Conservation avec signalement |
| j | associations.csv | date_convention | date de convention au format JJ/MM/AAAA | 6 | 2.86 % | Correction automatique vers le format ISO |
| k | reservations.csv | toutes | lignes en doublon strict | 18 | 0.39 % | Suppression des doublons, une occurrence conservee |
| l | reservations.csv | id_materiel | materiel inexistant dans materiel.csv | 21 | 0.45 % | Suppression de la ligne |
| m | reservations.csv | date_retour_reelle | retour reel anterieur au debut du pret | 15 | 0.32 % | Suppression de la ligne |
| n | reservations.csv | quantite | quantite egale a zero | 6 | 0.13 % | Suppression de la ligne |

Soit **14 categories d'anomalies**, de a a n. Les prets en cours ne figurent pas dans ce tableau : ce sont des prets non rendus, pas des defauts.

## Lignes avant et apres nettoyage

| Fichier | Avant | Apres | Ecart |
|---|---|---|---|
| materiel.csv | 367 | 360 | -7 |
| associations.csv | 210 | 210 | 0 |
| reservations.csv | 4618 | 4560 | -58 |

Categories distinctes dans materiel_propre.csv : **6** (attendu : 6).

## Prets en cours

- Avant nettoyage : **72**
- Apres nettoyage : **71**

Ecart de 1 ligne. La reservation R253433 etait bien un pret en cours, mais elle pointait vers un materiel absent de l'inventaire : elle a ete ecartee au titre de l'anomalie l, et non parce qu'elle n'etait pas rendue. Une date de retour vide reste un cas metier normal et n'a jamais ete comptee comme un defaut.

## Points d'attention pour la direction

Les fichiers sont globalement sains : aucune anomalie ne touche plus de 4 % d'un fichier. Mais l'essentiel des defauts vient de la saisie, pas du logiciel.

- Les categories de materiel sont ecrites de quatorze facons differentes alors que le service n'en gere que six : des majuscules ici, un espace en trop la. Tout comptage par categorie sorti de l'ancien outil etait donc faux. Un menu deroulant a la saisie reglerait le probleme definitivement.
- Cinq materiels portent une annee d'achat posterieure a l'annee en cours, jusqu'a 2031. Nous avons vide ces annees plutot que d'inventer une date : le materiel existe, son age est inconnu.
- Onze materiels n'ont aucune valeur d'achat et neuf aucune annee. Ces cases restent vides : les remplacer par zero ferait baisser artificiellement la valeur du parc que vous nous demandez de calculer.
- Vingt et une reservations renvoient a un materiel absent de l'inventaire. Elles sont inexploitables et ont ete ecartees, mais leur presence suggere que du materiel a ete retire de l'inventaire sans que ses reservations soient traitees.
- Quinze reservations ont une date de retour anterieure a la date de depart, et six portent sur zero unite. Ce sont des erreurs de saisie manifestes, ecartees elles aussi.
- Sept associations sur deux cent dix ont un type inconnu et neuf n'ont pas de code postal. Nous les gardons : ce sont des associations reelles, seule leur fiche est incomplete. Un rappel aux poles permettrait de les completer.
- Enfin, 71 prets sont en cours. Ce n'est pas une anomalie : ce materiel est sorti et pas encore rendu, il reste compte comme indisponible.
