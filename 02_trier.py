"""Étape 2 : tri des fichiers de data/brut/ dans leurs sous-dossiers."""
import shutil

import config
from utils import determiner_categorie, est_temporaire, executer_etape, nom_unique


def trier(logger):
    deplaces, temporaires, inconnus = 0, 0, 0

    for fichier in sorted(config.BRUT_DIR.iterdir()):
        if not fichier.is_file():
            continue

        if est_temporaire(fichier):
            temporaires += 1
            logger.info("Fichier temporaire identifié (supprimé à l'archivage) : %s", fichier.name)
            continue

        categorie = determiner_categorie(fichier.name)
        if categorie is None:
            inconnus += 1
            logger.warning("Extension non reconnue, fichier laissé en place : %s", fichier.name)
            continue

        dossier = config.BRUT_DIR / categorie
        dossier.mkdir(parents=True, exist_ok=True)
        destination = dossier / nom_unique(dossier, fichier.name)
        shutil.move(fichier, destination)
        deplaces += 1
        logger.info("Déplacé : %s -> %s/", fichier.name, destination.relative_to(config.DATA_DIR).parent.as_posix())

    logger.info("Tri terminé : %d déplacé(s), %d temporaire(s), %d inconnu(s)", deplaces, temporaires, inconnus)


if __name__ == "__main__":
    executer_etape("02_trier", trier)
