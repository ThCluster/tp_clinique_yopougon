"""Étape 3 : normalisation des noms.

Chaque fichier de data/brut/<categorie>/ est renommé avec Path.rename()
et rangé dans data/propre/<categorie>/.
"""
import config
from utils import executer_etape, normaliser_nom


def nettoyer(logger):
    renommes = 0
    for categorie in config.CATEGORIES:
        source = config.BRUT_DIR / categorie
        cible = config.PROPRE_DIR / categorie
        cible.mkdir(parents=True, exist_ok=True)
        if not source.exists():
            continue

        for fichier in sorted(source.iterdir()):
            if not fichier.is_file():
                continue
            nouveau_nom = normaliser_nom(fichier.name, dossier=cible)
            fichier.rename(cible / nouveau_nom)
            renommes += 1
            logger.info("Renommé : %s -> propre/%s/%s", fichier.name, categorie, nouveau_nom)

    logger.info("Normalisation terminée : %d fichier(s) renommé(s)", renommes)


if __name__ == "__main__":
    executer_etape("03_nettoyer", nettoyer)
