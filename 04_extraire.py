"""Étape 4 : extraction des événements des journaux d'admission."""
import config
from utils import ecrire_csv, executer_etape, extraire_logs, lire_csv

COLONNES = ["date", "heure", "patient", "ip", "action", "source"]


def extraire(logger):
    dossier_logs = config.PROPRE_DIR / "logs"
    journaux = sorted(dossier_logs.glob("*.log")) if dossier_logs.exists() else []
    if not journaux:
        logger.warning("Aucun journal d'admission trouvé dans %s", dossier_logs)

    # On conserve les événements déjà extraits les jours précédents
    evenements = lire_csv(config.LOGS_EXTRAITS_CSV) if config.LOGS_EXTRAITS_CSV.exists() else []
    deja_lus = {e["source"] for e in evenements}

    nouveaux = 0
    for journal in journaux:
        if journal.name in deja_lus:
            continue
        lignes = extraire_logs(journal, logger)
        for ligne in lignes:
            ligne["source"] = journal.name
        evenements.extend(lignes)
        nouveaux += len(lignes)
        logger.info("%s : %d événement(s) extrait(s)", journal.name, len(lignes))

    evenements.sort(key=lambda e: (e["date"], e["heure"]))
    ecrire_csv(config.LOGS_EXTRAITS_CSV, evenements, COLONNES)
    logger.info("%d nouvel(s) événement(s), %d au total -> %s",
                nouveaux, len(evenements), config.LOGS_EXTRAITS_CSV.relative_to(config.BASE_DIR))


if __name__ == "__main__":
    executer_etape("04_extraire", extraire)
