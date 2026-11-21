# TP 3 — Pipeline automatisé de gestion documentaire

**Clinique « La Paix », Yopougon**

Ce projet automatise le traitement quotidien des documents de la clinique (ordonnances, analyses, radiographies, factures, journaux d'admission, fichiers temporaires) :

```
Réception → Tri → Nettoyage → Extraction → Analyse → Rapport → Archivage
```

Le pipeline s'exécute automatiquement chaque jour à **23h30** et journalise toutes ses opérations.

---

## Important : où sont les données ?

Le dossier `data/` (fichiers de la clinique, rapports, archives) et le dossier `logs/` **ne sont pas dans le dépôt** : ce sont des fichiers **générés** par le programme.
Les données de test (60 fichiers fictifs) sont **créées automatiquement** au premier lancement par `simuler_donnees.py`.
Il suffit donc de lancer le projet (voir ci-dessous) pour voir apparaître toutes les données, les rapports et les journaux.

---

## 1. Installation

Prérequis : **Python 3.10 ou plus récent**.

```bash
git clone https://github.com/ThCluster/tp_clinique_yopougon.git
cd tp_clinique_yopougon
pip install -r requirements.txt
```

La seule bibliothèque externe est `schedule` (planification). Tout le reste vient de la bibliothèque standard (`pathlib`, `shutil`, `re`, `csv`, `logging`, `subprocess`, `zipfile`…).

---

## 2. Lancer le projet

### Option A — Avec le notebook Jupyter (recommandé pour la correction)

Le notebook `tp_clinique.ipynb` présente le TP **partie par partie** : explication, code exécuté et résultats affichés (fichiers générés, noms normalisés, statistiques, rapport, archive…).

- **Avec VS Code** : ouvrir `tp_clinique.ipynb`, choisir un noyau Python (*Select Kernel*), puis cliquer sur **Run All**.
- **Avec Jupyter** :
  ```bash
  pip install notebook
  jupyter notebook tp_clinique.ipynb
  ```
  puis menu **Run → Run All Cells**.

> La première cellule (`REPARTIR_DE_ZERO = True`) supprime le dossier `data/` pour rejouer le TP depuis le début.

### Option B — En ligne de commande

```bash
python main.py --maintenant
```

Exécute immédiatement les 7 étapes, une seule fois (environ 5 secondes). Chaque étape s'affiche dans le terminal.

### Option C — Mode planifié (fonctionnement réel)

```bash
python main.py
```

Le programme reste actif et lance le pipeline **chaque jour à 23h30** (`Ctrl+C` pour arrêter).
Pour tester sans attendre, modifier `HEURE_EXECUTION` dans `config.py` (ex. `"14:20"`).

### Lancer une étape seule

```bash
python simuler_donnees.py   # génère 60 fichiers de test dans data/brut/
python 01_recuperer.py
python 02_trier.py
python 03_nettoyer.py
python 04_extraire.py
python 05_analyser.py
python 06_exporter.py
python 07_sauvegarder.py
```

Les étapes doivent être lancées dans cet ordre (chacune utilise le résultat de la précédente).

---

## 3. Où voir les résultats

Après une exécution :

| Résultat | Emplacement |
|---|---|
| **Rapport lisible pour la direction** | `data/rapports/rapport_AAAA-MM-JJ.txt` |
| Rapport CSV (ouvrable dans Excel) | `data/rapports/rapport_AAAA-MM-JJ.csv` |
| Journal complet des opérations | `logs/pipeline_AAAA-MM-JJ.log` |
| Documents triés et renommés | `data/propre/ordonnances/`, `analyses/`, `radios/`, `factures/`, `logs/` |
| Événements extraits des journaux d'admission | `data/propre/logs_extraits.csv` |
| Statistiques calculées (dictionnaire) | `data/propre/statistiques.json` |
| Archive du jour | `data/archives/archive_AAAA-MM-JJ.zip` |

> `data/brut/` est vide après l'exécution : c'est normal, les fichiers ont été déplacés et renommés dans `data/propre/`, et les `.tmp` ont été supprimés.

Extrait du rapport texte :

```
RAPPORT QUOTIDIEN - CLINIQUE LA PAIX
Date : 21/11/2026

DOCUMENTS TRAITÉS
-----------------
Ordonnances   :  12 fichier(s)  (1.67 Mo)
Analyses      :  12 fichier(s)  (0.48 Mo)
Radiographies :  14 fichier(s)  (13.59 Mo)
Factures      :  10 fichier(s)  (0.61 Mo)

ACTIVITÉ
--------
Admissions    : 37
Consultations : 47
Sorties       : 22

TOP 5 PATIENTS
--------------
1. KOFFI Aya (23 passages)
2. TRAORE Moussa (21 passages)
...

PIC D'ACTIVITÉ
--------------
15h00 - 19 événements
```

Les valeurs changent à chaque exécution, car les données de test sont générées aléatoirement.

---

## 4. Organisation du projet

```
tp_clinique_yopougon/
├── main.py               # Orchestration (subprocess) et planification (schedule)
├── simuler_donnees.py    # Génération des 60 fichiers de test
├── 01_recuperer.py       # Préparation / récupération des données
├── 02_trier.py           # Tri des fichiers (shutil.move)
├── 03_nettoyer.py        # Normalisation des noms (Path.rename)
├── 04_extraire.py        # Extraction des logs (regex à groupes nommés)
├── 05_analyser.py        # Calcul des statistiques
├── 06_exporter.py        # Rapports CSV et texte
├── 07_sauvegarder.py     # Archive ZIP, suppression des .tmp, rotation 7 jours
├── config.py             # Configuration centralisée
├── utils.py              # Fonctions réutilisables
├── tp_clinique.ipynb     # Notebook de présentation
├── requirements.txt
│
├── logs/                 # (généré) pipeline_AAAA-MM-JJ.log
└── data/                 # (généré)
    ├── brut/             # ordonnances/ analyses/ radios/ factures/ logs/
    ├── propre/
    ├── rapports/
    └── archives/
```

---

## 5. Détail des étapes

| Étape | Script | Ce qu'elle fait |
|---|---|---|
| 1 | `01_recuperer.py` | Crée l'arborescence ; si aucun fichier n'est reçu, génère les données de test. |
| 2 | `02_trier.py` | Détermine la catégorie de chaque fichier (préfixe + extension) et le déplace dans `data/brut/<catégorie>/`. Les `.tmp` sont identifiés comme temporaires. |
| 3 | `03_nettoyer.py` | `normaliser_nom()` : minuscules, `_` à la place des espaces/tirets, dates au format `AAAA-MM-JJ`, accents et caractères spéciaux retirés, préfixes `ordo_`/`analyse_`/`radio_`/`facture_`, pas de doublons (`_2`, `_3`…). Ex. : `Ordonnance Dr Koffi 01-09-2026.pdf` → `ordo_dr_koffi_2026-09-01.pdf`. |
| 4 | `04_extraire.py` | `extraire_logs()` lit les journaux d'admission avec une regex à groupes nommés (date, heure, patient, IP, action). Une ligne mal formée déclenche un `logging.warning()` et est ignorée. Résultat : `data/propre/logs_extraits.csv`. |
| 5 | `05_analyser.py` | Nombre et taille des documents par catégorie ; admissions, consultations, sorties ; événements par jour ; top 5 patients ; répartition horaire et pic d'activité. |
| 6 | `06_exporter.py` | Rapports `rapport_AAAA-MM-JJ.csv` et `.txt`. |
| 7 | `07_sauvegarder.py` | Archive ZIP de `data/propre/`, suppression des `.tmp`, suppression des archives de plus de 7 jours. |

**Gestion des erreurs** : `main.py` lance chaque script avec `subprocess.run(..., check=True)`. Si une étape échoue (code de sortie ≠ 0), l'erreur est journalisée (`logging.error()`) et le pipeline s'arrête proprement.

**Configuration** : tous les paramètres (chemins, extensions, préfixes, motifs regex, `HEURE_EXECUTION = "23:30"`, `DUREE_ARCHIVAGE = 7`) sont dans `config.py`.
