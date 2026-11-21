"""Étape 6 : génération des rapports CSV et texte."""
import json
from datetime import date

import config
from utils import ecrire_csv, executer_etape


def rapport_csv(stats, chemin):
    lignes = []

    def ajouter(section, indicateur, valeur, unite=""):
        lignes.append({"section": section, "indicateur": indicateur, "valeur": valeur, "unite": unite})

    for libelle, d in stats["documents"].items():
        ajouter("Documents", f"{libelle} - nombre de fichiers", d["nombre"], "fichiers")
        ajouter("Documents", f"{libelle} - taille totale", d["taille_mo"], "Mo")

    a = stats["activite"]
    ajouter("Activité", "Admissions", a["admissions"])
    ajouter("Activité", "Consultations", a["consultations"])
    ajouter("Activité", "Sorties", a["sorties"])
    for jour, n in a["evenements_par_jour"].items():
        ajouter("Événements par jour", jour, n, "événements")

    for rang, p in enumerate(stats["patients"]["top5"], start=1):
        ajouter("Top 5 patients", f"{rang}. {p['patient']}", p["evenements"], "événements")

    for heure, n in stats["horaires"]["repartition"].items():
        ajouter("Répartition horaire", heure, n, "événements")

    ecrire_csv(chemin, lignes, ["section", "indicateur", "valeur", "unite"])


def rapport_texte(stats, chemin, jour):
    def titre(texte):
        return [texte, "-" * len(texte)]

    docs = stats["documents"]
    largeur = max(len(k) for k in docs)
    l = [f"RAPPORT QUOTIDIEN - {config.NOM_CLINIQUE}", f"Date : {jour:%d/%m/%Y}", ""]

    l += titre("DOCUMENTS TRAITÉS")
    for libelle, d in docs.items():
        l.append(f"{libelle:<{largeur}} : {d['nombre']:>3} fichier(s)  ({d['taille_mo']:.2f} Mo)")
    l.append("")

    a = stats["activite"]
    l += titre("ACTIVITÉ")
    l.append(f"Admissions    : {a['admissions']}")
    l.append(f"Consultations : {a['consultations']}")
    l.append(f"Sorties       : {a['sorties']}")
    l.append("")

    l += titre("ÉVÉNEMENTS PAR JOUR")
    for j, n in a["evenements_par_jour"].items():
        l.append(f"{date.fromisoformat(j):%d/%m/%Y} : {n} événement(s)")
    l.append("")

    l += titre("TOP 5 PATIENTS")
    for rang, p in enumerate(stats["patients"]["top5"], start=1):
        l.append(f"{rang}. {p['patient']} ({p['evenements']} passages)")
    l.append("")

    h = stats["horaires"]
    l += titre("PIC D'ACTIVITÉ")
    if h["pic"]:
        l.append(f"{h['pic']['heure']} - {h['pic']['evenements']} événements")
    else:
        l.append("Aucune activité enregistrée")
    l.append("")

    l += titre("RÉPARTITION PAR HEURE")
    maxi = max(h["repartition"].values(), default=1)
    for heure, n in h["repartition"].items():
        l.append(f"{heure} | {'#' * round(n * 30 / maxi):<30} {n}")
    l.append("")
    l.append("Rapport généré automatiquement par le pipeline documentaire.")

    chemin.write_text("\n".join(l) + "\n", encoding="utf-8")


def exporter(logger):
    if not config.STATISTIQUES_JSON.exists():
        raise FileNotFoundError(f"{config.STATISTIQUES_JSON} introuvable : lancer 05_analyser.py d'abord")
    stats = json.loads(config.STATISTIQUES_JSON.read_text(encoding="utf-8"))

    jour = date.today()
    config.RAPPORTS_DIR.mkdir(parents=True, exist_ok=True)
    csv_path = config.RAPPORTS_DIR / f"rapport_{jour:%Y-%m-%d}.csv"
    txt_path = config.RAPPORTS_DIR / f"rapport_{jour:%Y-%m-%d}.txt"

    rapport_csv(stats, csv_path)
    logger.info("Rapport CSV généré : %s", csv_path.relative_to(config.BASE_DIR))
    rapport_texte(stats, txt_path, jour)
    logger.info("Rapport texte généré : %s", txt_path.relative_to(config.BASE_DIR))


if __name__ == "__main__":
    executer_etape("06_exporter", exporter)
