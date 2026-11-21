"""Étape 1 : préparation / récupération des données."""
import config
from simuler_donnees import generer_donnees
from utils import creer_arborescence, executer_etape


def recuperer(logger):
    creer_arborescence()
    logger.info("Arborescence vérifiée sous %s", config.DATA_DIR)

    recus = [f for f in config.BRUT_DIR.iterdir() if f.is_file()]
    if not recus and config.SIMULER_SI_VIDE:
        logger.warning("Aucun fichier reçu dans data/brut/ : génération de données de test")
        generer_donnees(logger=logger)
        recus = [f for f in config.BRUT_DIR.iterdir() if f.is_file()]

    logger.info("%d fichier(s) reçu(s) à traiter", len(recus))


if __name__ == "__main__":
    executer_etape("01_recuperer", recuperer)
