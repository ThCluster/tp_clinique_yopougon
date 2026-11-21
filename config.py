"""Configuration centralisée du pipeline de la clinique La Paix (Yopougon)."""
from pathlib import Path

# ---------------------------------------------------------------------------
# Chemins
# ---------------------------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent

DATA_DIR = BASE_DIR / "data"
BRUT_DIR = DATA_DIR / "brut"
PROPRE_DIR = DATA_DIR / "propre"
RAPPORTS_DIR = DATA_DIR / "rapports"
ARCHIVES_DIR = DATA_DIR / "archives"
LOGS_DIR = BASE_DIR / "logs"

# Sous-dossiers de data/brut/ (et de data/propre/)
CATEGORIES = ["ordonnances", "analyses", "radios", "factures", "logs"]

# Catégories de documents prises en compte dans les statistiques
CATEGORIES_DOCUMENTS = {
    "ordonnances": "Ordonnances",
    "analyses": "Analyses",
    "radios": "Radiographies",
    "factures": "Factures",
}

# Fichiers produits
LOGS_EXTRAITS_CSV = PROPRE_DIR / "logs_extraits.csv"
STATISTIQUES_JSON = PROPRE_DIR / "statistiques.json"

# ---------------------------------------------------------------------------
# Extensions
# ---------------------------------------------------------------------------
EXTENSIONS_CATEGORIES = {
    ".pdf": "ordonnances",
    ".csv": "analyses",
    ".jpg": "radios",
    ".jpeg": "radios",
    ".png": "radios",
    ".xlsx": "factures",
    ".log": "logs",
}
EXTENSION_TEMPORAIRE = ".tmp"
EXTENSIONS_AUTORISEES = set(EXTENSIONS_CATEGORIES) | {EXTENSION_TEMPORAIRE}

# ---------------------------------------------------------------------------
# Préfixes
# ---------------------------------------------------------------------------
# Préfixe normalisé de chaque catégorie
PREFIXES = {
    "ordonnances": "ordo_",
    "analyses": "analyse_",
    "radios": "radio_",
    "factures": "facture_",
}

# Mots-clés reconnus en début de nom -> catégorie
MOTS_CLES_CATEGORIES = {
    "ordonnance": "ordonnances",
    "ordo": "ordonnances",
    "analyses": "analyses",
    "analyse": "analyses",
    "radiographie": "radios",
    "radio": "radios",
    "img": "radios",
    "factures": "factures",
    "facture": "factures",
}

# Mots-clés à retirer du nom avant d'ajouter le préfixe normalisé
# ("img" est conservé : radio_img_2026-09-01_123456.jpg)
MOTS_CLES_A_REMPLACER = {"ordonnance", "ordo", "analyses", "analyse",
                         "radiographie", "radio", "factures", "facture"}

# ---------------------------------------------------------------------------
# Motifs regex
# ---------------------------------------------------------------------------
# Ligne du journal d'admission :
# 2026-09-01 08:15:22 Patient: KOFFI Aya IP: 192.168.1.10 Action: admission
REGEX_LOG = (
    r"^(?P<date>\d{4}-\d{2}-\d{2})\s+"
    r"(?P<heure>\d{2}:\d{2}:\d{2})\s+"
    r"Patient:\s*(?P<patient>.+?)\s+"
    r"IP:\s*(?P<ip>(?:\d{1,3}\.){3}\d{1,3})\s+"
    r"Action:\s*(?P<action>\w+)\s*$"
)

# Dates dans les noms de fichiers
REGEX_DATE_JJMMAAAA = r"(?<!\d)(?P<j>\d{1,2})[-_./ ](?P<m>\d{1,2})[-_./ ](?P<a>\d{4})(?!\d)"
REGEX_DATE_AAAAMMJJ = r"(?<!\d)(?P<a>\d{4})[-_./ ](?P<m>\d{1,2})[-_./ ](?P<j>\d{1,2})(?!\d)"
REGEX_DATE_COMPACTE = r"(?<!\d)(?P<a>20\d{2})(?P<m>\d{2})(?P<j>\d{2})(?!\d)"

ACTIONS = ["admission", "consultation", "sortie"]

# ---------------------------------------------------------------------------
# Planification et archivage
# ---------------------------------------------------------------------------
HEURE_EXECUTION = "23:30"
DUREE_ARCHIVAGE = 7  # jours

# ---------------------------------------------------------------------------
# Divers
# ---------------------------------------------------------------------------
NOM_CLINIQUE = "CLINIQUE LA PAIX"
NB_FICHIERS_SIMULES = 60
SIMULER_SI_VIDE = True  # 01_recuperer.py génère des données de test si rien n'est reçu
SEPARATEUR_CSV = ";"
ENCODAGE_CSV = "utf-8-sig"  # lisible directement dans Excel

ETAPES = [
    "01_recuperer.py",
    "02_trier.py",
    "03_nettoyer.py",
    "04_extraire.py",
    "05_analyser.py",
    "06_exporter.py",
    "07_sauvegarder.py",
]
