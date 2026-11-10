# Annuaire des établissements scolaires

Application Streamlit indépendante pour consulter et analyser les établissements du fichier `annuaire_complet.csv`.

## Tableau de bord et fonctions

- Indicateurs qui suivent les filtres : nombre d’établissements, établissements ouverts, fiches avec téléphone et établissements géolocalisés.
- Graphiques interactifs de répartition par type et région, statut public/privé, services et dispositifs, et année d’ouverture lorsque cette information est disponible.
- Recherche rapide par nom, identifiant, commune, code postal, adresse ou contact.
- Filtres combinables par région, département, type, statut, état, commune et services.
- Annuaire paginé avec une fiche détaillée qui affiche tous les champs disponibles pour l’établissement.
- Carte des coordonnées présentes dans le fichier, sans emplacement inventé pour les coordonnées manquantes.
- Export CSV des résultats actuellement filtrés.

## Prérequis

Python 3.10 ou plus récent et le fichier fourni à cet emplacement :

```text
C:\Users\SuperElectro\Downloads\annuaire_complet.csv
```

Le fichier CSV original est lu directement et n’est ni copié ni modifié par l’application. Les identifiants sont conservés comme du texte. Le lecteur accepte les séparateurs courants, détecte l’UTF-8 ou le Windows-1252 et traite les octets invalides sans bloquer toute l’importation.

## Installation sous Windows (PowerShell)

Depuis le dossier `annuaire_etablissements_app` :

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

Si l’activation PowerShell est bloquée, utilisez directement l’interpréteur de l’environnement :

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

## Démarrage

```powershell
python -m streamlit run app.py
```

Ouvrez l’adresse locale affichée par Streamlit (habituellement `http://localhost:8501`). Pour utiliser un autre fichier, chargez-le dans la barre latérale. Si le fichier fourni n’est pas à son emplacement par défaut, vous pouvez définir `ANNUAIRE_CSV_PATH` avant le démarrage :

```powershell
$env:ANNUAIRE_CSV_PATH = "C:\chemin\vers\mon_annuaire.csv"
python -m streamlit run app.py
```

## Vérification

```powershell
python -m unittest discover -s tests -v
```
