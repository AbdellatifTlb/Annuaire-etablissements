---
title: "Application Streamlit de consultation de l’annuaire des établissements"
type: feature
created: "2026-11-10"
status: done
baseline_commit: NO_VCS
context: []
---

<frozen-after-approval reason="human-owned intent — do not modify unless human renegotiates">

## Intent

**Problem:** Le fichier annuaire_complet.csv contient un grand nombre d’établissements et de champs difficiles à parcourir efficacement dans un tableur. L’utilisateur veut une application indépendante, soignée et pratique pour retrouver un établissement, comparer les résultats et consulter l’ensemble de ses informations.

**Approach:** Créer une application Streamlit autonome dans `C:\Users\SuperElectro\Downloads\annuaire_etablissements_app`, en utilisant le CSV existant sans modifier ni déplacer le fichier source et sans changer aucun fichier du dépôt `projet_immo`. Fournir un tableau de bord interactif présentant les principaux indicateurs et graphiques, une recherche, des filtres pertinents, la consultation de toutes les colonnes d’un établissement, des fonctions d’exploration visuelle et l’export des résultats.

## Boundaries & Constraints

**Always:** Garder l’application et ses instructions d’exécution dans le nouveau dossier hors du dépôt. Charger par défaut `C:\Users\SuperElectro\Downloads\annuaire_complet.csv`, sans en faire une copie imposée; permettre le téléversement d’un autre CSV si la source manque. Préserver les identifiants comme du texte, gérer l’encodage Windows du fichier (notamment CP1252), les valeurs manquantes, les valeurs incohérentes et les colonnes facultatives, et afficher des messages d’erreur utiles. L’interface et la documentation destinées à l’utilisateur sont en français.

**Ask First:** Ne modifier ni déplacer le CSV original, le dépôt immobilier, ni les paramètres de l’environnement global. Ne dépendre d’aucun service payant ou de secrets.

**Never:** Ne réutiliser ni adapter le site Flask immobilier comme application cible. Ne supprimer ou masquer des champs de l’annuaire dans la fiche complète. Ne présenter les coordonnées ou données manquantes comme certaines.

## I/O & Edge-Case Matrix

| Scenario | Input / State | Expected Output / Behavior | Error Handling |
|----------|---------------|----------------------------|----------------|
| HAPPY_PATH | CSV source présente, avec séparateur point-virgule et texte CP1252 | Charger les lignes, proposer les filtres et afficher la fiche complète des résultats retenus | Signaler les colonnes vides ou facultatives sans échec général |
| NO_SOURCE | Fichier par défaut absent | Proposer le téléversement d’un fichier CSV compatible | Message explicite et instructions de correction |
| INVALID_SOURCE | Fichier vide, illisible ou sans colonnes nécessaires | Ne pas afficher de résultats trompeurs | Expliquer les colonnes ou le format attendu |
| NO_MATCHES | Recherche ou filtres sans correspondance | Afficher zéro résultat et conserver les critères choisis | Aucun échec silencieux |

</frozen-after-approval>

## Code Map

- `C:\Users\SuperElectro\Downloads\annuaire_etablissements_app\app.py` — application Streamlit, tableau de bord analytique, chargement, filtres, analyses et fiches.
- `C:\Users\SuperElectro\Downloads\annuaire_etablissements_app\requirements.txt` — dépendances nécessaires pour créer un environnement Python local.
- `C:\Users\SuperElectro\Downloads\annuaire_etablissements_app\README.md` — installation, lancement et explication des fonctionnalités.
- `C:\Users\SuperElectro\Downloads\annuaire_etablissements_app\.streamlit\config.toml` — thème Streamlit de présentation.
- `C:\Users\SuperElectro\Downloads\annuaire_etablissements_app\tests\test_data.py` — vérification ciblée de la lecture et des cas de données.

## Tasks & Acceptance

**Execution:**
- [x] `app.py` — charger et normaliser le CSV avec détection contrôlée de l’encodage et validation, puis offrir un tableau de bord filtrable avec métriques clés et graphiques de répartition par type, statut, région/département, services et année d’ouverture lorsque disponible; recherche textuelle, filtres combinables, carte des établissements géolocalisés, liste paginée, fiche établissement complète et export des résultats — rendre le grand annuaire consultable et analysable sans perte des champs.
- [x] `requirements.txt`, `.streamlit/config.toml` — déclarer uniquement les dépendances nécessaires et appliquer une identité visuelle Streamlit cohérente — assurer une installation locale reproductible et une interface professionnelle.
- [x] `README.md` — documenter création d’environnement, installation, commande de démarrage, source CSV par défaut et téléversement alternatif — permettre à l’utilisateur de lancer seul l’application.
- [x] `tests/test_data.py` — tester la lecture de l’encodage observé, les champs d’identification et les erreurs de source invalide — éviter les régressions sur le traitement des données.

**Acceptance Criteria:**
- Given le CSV fourni, when l’application démarre, then ses caractères accentués, identifiants, colonnes et établissements sont chargés sans modifier le fichier source.
- Given des critères de recherche et plusieurs filtres, when l’utilisateur les combine, then le tableau, les indicateurs, l’analyse et l’export reflètent exactement les mêmes établissements.
- Given des données chargées, when l’utilisateur ouvre le tableau de bord et ajuste un filtre, then les indicateurs et graphiques se recalculent sur les établissements correspondants, sans inventer des valeurs pour les champs absents.
- Given un établissement sélectionné, when l’utilisateur ouvre sa fiche, then toutes les colonnes disponibles sont consultables, y compris les informations de contact, d’adresse, de tutelle, d’enseignement et de localisation lorsqu’elles existent.
- Given des coordonnées valides, when les résultats filtrés en contiennent, then l’application propose une exploration géographique et ne crée pas de coordonnées pour les valeurs manquantes.
- Given un CSV absent, vide, illisible ou incompatible, when le chargement est demandé, then l’utilisateur obtient une marche à suivre explicite plutôt qu’un tableau fallacieux.
- Given un lancement depuis le nouveau dossier, when l’utilisateur suit le README, then Streamlit démarre sans installation dans le dépôt immobilier ni changement de ses fichiers.

## Verification

**Commands:**
- `python -m unittest discover -s tests -v` depuis le nouveau dossier — attendu : tests de lecture, filtres et validation réussis.
- `python -m py_compile app.py data_utils.py` — attendu : compilation réussie.
- `python -m streamlit run app.py` — attendu : démarrage local de l’application avec l’annuaire fourni.

## Suggested Review Order

**Application et données**

- Le tableau de bord, les vues et la connexion des filtres partent de ce point d’entrée.
  [`app.py:471`](./app.py#L471)

- La lecture du CSV protège les accents, les identifiants et les erreurs de fichier.
  [`data_utils.py:49`](./data_utils.py#L49)

- Les filtres combinés sont appliqués de façon identique à tous les résultats.
  [`data_utils.py:120`](./data_utils.py#L120)

- Les indicateurs et graphiques se recalculent sur les établissements filtrés.
  [`app.py:101`](./app.py#L101)

- La fiche affiche les champs d’origine et la liste reste paginée.
  [`app.py:262`](./app.py#L262)

**Vérification et lancement**

- Les tests couvrent les identifiants, encodages, filtres et erreurs de source.
  [`tests/test_data.py:8`](./tests/test_data.py#L8)

- Les instructions décrivent l’installation isolée et le démarrage Windows.
  [`README.md:1`](./README.md#L1)
