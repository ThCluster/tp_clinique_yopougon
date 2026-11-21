"""Étape 7 : archivage ZIP de data/propre/, suppression des .tmp,
rotation des archives (conservation de DUREE_ARCHIVAGE jours)."""
import re
import zipfile
from datetime import date, timedelta

import config
from utils import executer_etape


def creer_archive(logger):
    config.ARCHIVES_DIR.mkdir(parents=True, exist_ok=True)
    archive = config.ARCHIVES_DIR / f"archive_{date.today():%Y-%m-%d}.zip"
    fichiers = [f for f in config.PROPRE_DIR.rglob("*") if f.is_file()]
    with zipfile.ZipFile(archive, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for f in fichiers:
            zf.write(f, f.relative_to(config.PROPRE_DIR))
    logger.info("Archive créée : %s (%d fichier(s))", archive.relative_to(config.BASE_DIR), len(fichiers))


def supprimer_temporaires(logger):
    supprimes = 0
    for f in config.DATA_DIR.rglob(f"*{config.EXTENSION_TEMPORAIRE}"):
        if f.is_file():
            f.unlink()
            supprimes += 1
            logger.info("Fichier temporaire supprimé : %s", f.name)
    logger.info("%d fichier(s) temporaire(s) supprimé(s)", supprimes)


def purger_archives(logger):
    limite = date.today() - timedelta(days=config.DUREE_ARCHIVAGE)
    supprimees = 0
    for archive in config.ARCHIVES_DIR.glob("archive_*.zip"):
        m = re.fullmatch(r"archive_(\d{4}-\d{2}-\d{2})\.zip", archive.name)
        if not m:
            logger.warning("Nom d'archive inattendu, ignorée : %s", archive.name)
            continue
        if date.fromisoformat(m.group(1)) <= limite:
            archive.unlink()
            supprimees += 1
            logger.info("Archive de plus de %d jours supprimée : %s", config.DUREE_ARCHIVAGE, archive.name)
    logger.info("%d ancienne(s) archive(s) supprimée(s)", supprimees)


def sauvegarder(logger):
    creer_archive(logger)
    supprimer_temporaires(logger)
    purger_archives(logger)


if __name__ == "__main__":
    executer_etape("07_sauvegarder", sauvegarder)
