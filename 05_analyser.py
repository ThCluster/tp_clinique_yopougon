"""Étape 5 : calcul des statistiques (documents + activité)."""
import json
from collections import Counter

import config
from utils import executer_etape, lire_csv


def stats_documents():
    documents = {}
    for categorie, libelle in config.CATEGORIES_DOCUMENTS.items():
        dossier = config.PROPRE_DIR / categorie
        fichiers = [f for f in dossier.iterdir() if f.is_file()] if dossier.exists() else []
        taille = sum(f.stat().st_size for f in fichiers)
        documents[libelle] = {"nombre": len(fichiers), "taille_mo": round(taille / (1024 * 1024), 2)}
    return documents


def stats_evenements(evenements):
    actions = Counter(e["action"] for e in evenements)
    par_jour = Counter(e["date"] for e in evenements)
    patients = Counter(e["patient"] for e in evenements)
    horaires = Counter(f"{e['heure'][:2]}h00" for e in evenements)

    activite = {
        "admissions": actions.get("admission", 0),
        "consultations": actions.get("consultation", 0),
        "sorties": actions.get("sortie", 0),
        "total_evenements": len(evenements),
        "evenements_par_jour": dict(sorted(par_jour.items())),
    }
    top5 = [{"patient": p, "evenements": n} for p, n in patients.most_common(5)]

    repartition = dict(sorted(horaires.items()))
    pic = max(repartition.items(), key=lambda kv: kv[1]) if repartition else None
    horaires_stats = {
        "repartition": repartition,
        "pic": {"heure": pic[0], "evenements": pic[1]} if pic else None,
    }
    return activite, {"top5": top5, "nombre_patients_distincts": len(patients)}, horaires_stats


def analyser(logger):
    evenements = lire_csv(config.LOGS_EXTRAITS_CSV) if config.LOGS_EXTRAITS_CSV.exists() else []
    if not evenements:
        logger.warning("Aucun événement dans %s", config.LOGS_EXTRAITS_CSV.name)

    activite, patients, horaires = stats_evenements(evenements)
    statistiques = {
        "documents": stats_documents(),
        "activite": activite,
        "patients": patients,
        "horaires": horaires,
    }

    config.STATISTIQUES_JSON.write_text(json.dumps(statistiques, ensure_ascii=False, indent=2), encoding="utf-8")

    for libelle, d in statistiques["documents"].items():
        logger.info("%s : %d fichier(s), %.2f Mo", libelle, d["nombre"], d["taille_mo"])
    logger.info("Admissions=%d Consultations=%d Sorties=%d",
                activite["admissions"], activite["consultations"], activite["sorties"])
    if horaires["pic"]:
        logger.info("Pic d'activité : %s (%d événements)", horaires["pic"]["heure"], horaires["pic"]["evenements"])
    logger.info("Statistiques enregistrées dans %s", config.STATISTIQUES_JSON.relative_to(config.BASE_DIR))


if __name__ == "__main__":
    executer_etape("05_analyser", analyser)
