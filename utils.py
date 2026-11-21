"""Fonctions réutilisables du pipeline."""
import csv
import logging
import os
import re
import sys
import unicodedata
from datetime import date
from pathlib import Path

import config


# ---------------------------------------------------------------------------
# Journalisation
# ---------------------------------------------------------------------------
def creer_logger(nom="pipeline"):
    """Logger qui écrit dans logs/pipeline_YYYY-MM-DD.log et dans la console."""
    config.LOGS_DIR.mkdir(parents=True, exist_ok=True)
    fichier_log = config.LOGS_DIR / f"pipeline_{date.today():%Y-%m-%d}.log"

    logger = logging.getLogger(nom)
    if logger.handlers:  # déjà configuré
        return logger

    logger.setLevel(logging.INFO)
    format_ = logging.Formatter(
        "%(asctime)s - %(levelname)-8s - [%(name)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    fh = logging.FileHandler(fichier_log, encoding="utf-8")
    fh.setFormatter(format_)
    ch = logging.StreamHandler(sys.stdout)
    ch.setFormatter(format_)
    logger.addHandler(fh)
    logger.addHandler(ch)
    logger.propagate = False
    return logger


def executer_etape(nom_etape, fonction):
    """Lance la fonction principale d'une étape, journalise début/fin,
    et termine le script avec le code 1 en cas d'erreur (détecté par main.py)."""
    logger = creer_logger(nom_etape)
    logger.info("Début de l'étape")
    try:
        fonction(logger)
    except Exception:
        logger.exception("Échec de l'étape")
        sys.exit(1)
    logger.info("Fin de l'étape")


def creer_arborescence():
    """Crée tous les dossiers du projet."""
    dossiers = [config.LOGS_DIR, config.PROPRE_DIR, config.RAPPORTS_DIR, config.ARCHIVES_DIR]
    dossiers += [config.BRUT_DIR / c for c in config.CATEGORIES]
    for dossier in dossiers:
        dossier.mkdir(parents=True, exist_ok=True)


# ---------------------------------------------------------------------------
# Catégories
# ---------------------------------------------------------------------------
def retirer_accents(texte):
    """'Échographie' -> 'Echographie'."""
    decompose = unicodedata.normalize("NFKD", texte)
    return "".join(c for c in decompose if not unicodedata.combining(c))


def decouper_nom(nom):
    """('ANALYSE SANG 01/09/2026', '.csv') : contrairement à Path,
    un '/' dans le nom n'est pas pris pour un dossier."""
    racine, extension = os.path.splitext(str(nom))
    return racine, extension.lower()


def est_temporaire(fichier):
    return Path(fichier).suffix.lower() == config.EXTENSION_TEMPORAIRE


def determiner_categorie(nom):
    """Catégorie d'un fichier à partir de son préfixe, puis de son extension.
    Retourne None pour un fichier temporaire ou inconnu."""
    racine, extension = decouper_nom(nom)
    if extension == config.EXTENSION_TEMPORAIRE or extension not in config.EXTENSIONS_CATEGORIES:
        return None
    categorie_extension = config.EXTENSIONS_CATEGORIES[extension]
    if categorie_extension == "logs":
        return "logs"

    premier_mot = re.split(r"[^a-z]+", retirer_accents(racine).lower())[0]
    categorie_prefixe = config.MOTS_CLES_CATEGORIES.get(premier_mot)

    # Le préfixe n'est retenu que s'il est compatible avec l'extension
    # (ex. "radio_xxx.pdf" reste une ordonnance si c'est un PDF).
    if categorie_prefixe == categorie_extension:
        return categorie_prefixe
    return categorie_extension


# ---------------------------------------------------------------------------
# Normalisation des noms
# ---------------------------------------------------------------------------
def _date_iso(a, m, j):
    """Retourne 'YYYY-MM-DD' si la date est valide, sinon None."""
    try:
        return date(int(a), int(m), int(j)).isoformat()
    except ValueError:
        return None


def nom_unique(dossier, nom):
    """Ajoute _2, _3... si le nom existe déjà dans le dossier."""
    dossier = Path(dossier)
    candidat = dossier / nom
    if not candidat.exists():
        return nom
    stem, ext = Path(nom).stem, Path(nom).suffix
    i = 2
    while (dossier / f"{stem}_{i}{ext}").exists():
        i += 1
    return f"{stem}_{i}{ext}"


def normaliser_nom(nom, dossier=None):
    """Normalise un nom de fichier.

    'Ordonnance Dr Koffi 01-09-2026.pdf' -> 'ordo_dr_koffi_2026-09-01.pdf'
    'IMG_20260901_123456.jpg'            -> 'radio_img_2026-09-01_123456.jpg'

    Si `dossier` est fourni, un suffixe _2, _3... est ajouté pour éviter
    d'écraser un fichier existant.
    """
    racine, extension = decouper_nom(nom)
    texte = retirer_accents(racine).lower()

    # 1. Détection des dates -> jetons temporaires (protégés du nettoyage)
    dates = []

    def remplacer(match):
        iso = _date_iso(match["a"], match["m"], match["j"])
        if iso is None:
            return match.group(0)
        dates.append(iso)
        return f" zzdate{len(dates) - 1}zz "

    for motif in (config.REGEX_DATE_AAAAMMJJ, config.REGEX_DATE_JJMMAAAA, config.REGEX_DATE_COMPACTE):
        texte = re.sub(motif, remplacer, texte)

    # 2. Espaces, tirets et caractères spéciaux -> _
    texte = re.sub(r"[\s\-./]+", "_", texte)
    texte = re.sub(r"[^a-z0-9_]", "", texte)
    texte = re.sub(r"_+", "_", texte).strip("_")

    # 3. Remise en place des dates au format YYYY-MM-DD
    for i, iso in enumerate(dates):
        texte = texte.replace(f"zzdate{i}zz", iso)

    # 4. Harmonisation du préfixe
    categorie = determiner_categorie(nom)
    if categorie in config.PREFIXES:
        mots = texte.split("_")
        if mots and mots[0] in config.MOTS_CLES_A_REMPLACER:
            mots = mots[1:]
        texte = config.PREFIXES[categorie] + "_".join(m for m in mots if m)
        texte = texte.rstrip("_")

    if not texte:
        texte = "fichier"
    nouveau = texte + extension

    # 5. Pas de doublon
    if dossier is not None:
        nouveau = nom_unique(dossier, nouveau)
    return nouveau


# ---------------------------------------------------------------------------
# Extraction des logs
# ---------------------------------------------------------------------------
REGEX_LOG = re.compile(config.REGEX_LOG)


def extraire_logs(chemin, logger=None):
    """Lit un journal d'admission et retourne une liste de dictionnaires
    {date, heure, patient, ip, action}. Les lignes mal formées sont signalées
    par un avertissement puis ignorées."""
    logger = logger or logging.getLogger("pipeline")
    evenements = []
    chemin = Path(chemin)
    with chemin.open(encoding="utf-8", errors="replace") as f:
        for numero, ligne in enumerate(f, start=1):
            ligne = ligne.strip()
            if not ligne:
                continue
            match = REGEX_LOG.match(ligne)
            if match is None:
                logger.warning("%s ligne %d mal formée ignorée : %r", chemin.name, numero, ligne)
                continue
            evenement = match.groupdict()
            evenement["patient"] = evenement["patient"].strip()
            evenement["action"] = evenement["action"].lower()
            evenements.append(evenement)
    return evenements


# ---------------------------------------------------------------------------
# CSV
# ---------------------------------------------------------------------------
def ecrire_csv(chemin, lignes, colonnes):
    with Path(chemin).open("w", newline="", encoding=config.ENCODAGE_CSV) as f:
        writer = csv.DictWriter(f, fieldnames=colonnes, delimiter=config.SEPARATEUR_CSV)
        writer.writeheader()
        writer.writerows(lignes)


def lire_csv(chemin):
    with Path(chemin).open(newline="", encoding=config.ENCODAGE_CSV) as f:
        return list(csv.DictReader(f, delimiter=config.SEPARATEUR_CSV))
