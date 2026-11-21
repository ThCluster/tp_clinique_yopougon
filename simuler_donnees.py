"""Génère des fichiers fictifs dans data/brut/ pour tester le pipeline."""
import os
import random
from datetime import date, datetime, timedelta

import config
from utils import creer_arborescence, creer_logger

MEDECINS = ["Koffi", "Traoré", "Diallo", "Kouassi", "Bamba", "N'Guessan"]
EXAMENS = ["SANG", "urine", "Biochimie", "glycémie", "NFS", "paludisme"]
ZONES_RADIO = ["thorax", "bras", "genou", "crâne", "bassin", "cheville"]
PATIENTS = [
    "KOFFI Aya", "TRAORE Moussa", "DIALLO Fatou", "KOUASSI Jean", "BAMBA Awa",
    "YAO Serge", "COULIBALY Mariam", "N'GUESSAN Paul", "TOURE Aminata", "KONE Ibrahim",
]
JOURS = [date(2026, 9, 1), date(2026, 9, 2), date(2026, 9, 3)]


def _formats_date(d):
    """Quelques façons irrégulières d'écrire une date dans un nom de fichier."""
    return random.choice([
        f"{d:%d-%m-%Y}", f"{d:%Y-%m-%d}", f"{d:%d.%m.%Y}",
        f"{d:%d_%m_%Y}", f"{d:%Y%m%d}", f"{d:%d %m %Y}",
    ])


def _generateurs():
    """Fabriques de noms par type de fichier."""
    def ordonnance():
        d = _formats_date(random.choice(JOURS))
        return random.choice([
            f"Ordonnance Dr {random.choice(MEDECINS)} {d}.pdf",
            f"ORDONNANCE - dr {random.choice(MEDECINS).upper()} - {d}.pdf",
            f"ordo_{random.choice(MEDECINS).lower()}_{d}.pdf",
            f"Ordonnance n°{random.randint(100, 999)} {d}.PDF",
        ])

    def analyse():
        d = _formats_date(random.choice(JOURS))
        return random.choice([
            f"ANALYSE {random.choice(EXAMENS).upper()} {d}.csv",
            f"Analyse {random.choice(EXAMENS)} {d}.csv",
            f"résultats labo {random.choice(EXAMENS)} {d}.csv",
        ])

    def radio(ext):
        d = random.choice(JOURS)
        return random.choice([
            f"radio {random.choice(ZONES_RADIO)} {_formats_date(d)}.{ext}",
            f"Radiographie {random.choice(ZONES_RADIO).upper()} {_formats_date(d)}.{ext}",
            f"IMG_{d:%Y%m%d}_{random.randint(80000, 175959):06d}.{ext}",
        ])

    def facture():
        d = _formats_date(random.choice(JOURS))
        return random.choice([
            f"Facture PATIENT {d}.xlsx",
            f"FACTURE consultation {d}.xlsx",
            f"facture  N° {random.randint(1000, 9999)} ({d}).xlsx",
        ])

    def temporaire():
        return random.choice([
            f"scanner_temp_{random.randint(1, 99):02d}.tmp",
            f"imprimante_temp_{random.randint(1, 99):02d}.tmp",
            f"~spool{random.randint(100, 999)}.tmp",
        ])

    return [
        (ordonnance, 12, (20, 300)),
        (analyse, 12, (5, 80)),
        (lambda: radio("jpg"), 9, (300, 2000)),
        (lambda: radio("png"), 5, (300, 2000)),
        (facture, 10, (15, 120)),
        (temporaire, 9, (1, 50)),
    ]  # 57 fichiers + 3 journaux = 60


def _ecrire_fichier_fictif(chemin, taille_ko):
    entete = f"Fichier fictif - {chemin.name}\n".encode("utf-8")
    chemin.write_bytes(entete + os.urandom(max(0, taille_ko * 1024 - len(entete))))


def _generer_journal(jour, nb_evenements):
    """Événements d'admission avec un pic d'activité en début d'après-midi."""
    heures = list(range(7, 20))
    poids = [1, 3, 5, 6, 5, 3, 4, 7, 6, 4, 3, 2, 1]
    lignes = []
    for _ in range(nb_evenements):
        h = random.choices(heures, weights=poids)[0]
        moment = datetime(jour.year, jour.month, jour.day, h, random.randint(0, 59), random.randint(0, 59))
        patient = random.choices(PATIENTS, weights=range(len(PATIENTS), 0, -1))[0]
        ip = f"192.168.1.{random.randint(2, 60)}"
        action = random.choices(config.ACTIONS, weights=[3, 5, 3])[0]
        lignes.append((moment, f"{moment:%Y-%m-%d %H:%M:%S} Patient: {patient} IP: {ip} Action: {action}"))
    lignes.sort()
    lignes = [texte for _, texte in lignes]

    # Quelques lignes mal formées pour tester la robustesse
    for erreur in ["LIGNE MAL FORMEE", f"{jour} 25:61:00 Patient: ??? IP: x.x Action:", "### redémarrage du serveur ###"]:
        lignes.insert(random.randint(0, len(lignes)), erreur)
    return "\n".join(lignes) + "\n"


def generer_donnees(nb_fichiers=config.NB_FICHIERS_SIMULES, logger=None):
    logger = logger or creer_logger("simulation")
    creer_arborescence()

    # Journaux d'admission (un par jour)
    noms_journaux = []
    for jour in JOURS:
        nom = random.choice([f"admission_{jour:%Y%m%d}.log", f"Admission {jour:%d-%m-%Y}.log"])
        (config.BRUT_DIR / nom).write_text(_generer_journal(jour, random.randint(30, 45)), encoding="utf-8")
        noms_journaux.append(nom)

    # Documents
    plan = _generateurs()
    total_plan = sum(n for _, n, _ in plan)
    reste = nb_fichiers - len(noms_journaux)
    crees = 0
    for fabrique, nombre, (kmin, kmax) in plan:
        nombre = round(nombre * reste / total_plan)
        for _ in range(nombre):
            for _essai in range(50):  # nom unique dans data/brut/
                chemin = config.BRUT_DIR / fabrique()
                if not chemin.exists():
                    break
            _ecrire_fichier_fictif(chemin, random.randint(kmin, kmax))
            crees += 1

    logger.info("Simulation : %d fichiers générés dans %s (%d journaux + %d documents)",
                crees + len(noms_journaux), config.BRUT_DIR, len(noms_journaux), crees)
    return crees + len(noms_journaux)


if __name__ == "__main__":
    generer_donnees()
