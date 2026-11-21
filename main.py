"""Orchestration et planification du pipeline.

    python main.py              -> attend 23:30 chaque jour (schedule)
    python main.py --maintenant -> exécute le pipeline une fois, tout de suite
"""
import subprocess
import sys
import time
from datetime import datetime

import schedule

import config
from utils import creer_logger


def executer_pipeline():
    logger = creer_logger("main")
    debut = datetime.now()
    logger.info("=" * 60)
    logger.info("DÉBUT DU PIPELINE")

    for etape in config.ETAPES:
        logger.info(">>> Lancement de %s", etape)
        try:
            subprocess.run([sys.executable, str(config.BASE_DIR / etape)], check=True, cwd=config.BASE_DIR)
        except subprocess.CalledProcessError as e:
            logger.error("Échec de %s (code de sortie %d) : arrêt du pipeline", etape, e.returncode)
            logger.info("=" * 60)
            return False
        except OSError as e:
            logger.error("Impossible de lancer %s : %s : arrêt du pipeline", etape, e)
            return False
        logger.info("<<< %s terminé avec succès", etape)

    duree = (datetime.now() - debut).total_seconds()
    logger.info("FIN DU PIPELINE (succès, %.1f s)", duree)
    logger.info("=" * 60)
    return True


def main():
    if "--maintenant" in sys.argv:
        sys.exit(0 if executer_pipeline() else 1)

    logger = creer_logger("main")
    schedule.every().day.at(config.HEURE_EXECUTION).do(executer_pipeline)
    logger.info("Planificateur démarré : exécution quotidienne à %s (Ctrl+C pour arrêter)", config.HEURE_EXECUTION)
    try:
        while True:
            schedule.run_pending()
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("Planificateur arrêté manuellement")


if __name__ == "__main__":
    main()
