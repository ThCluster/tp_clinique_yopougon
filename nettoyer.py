from pathlib import Path
import logging
import re

BASE_DIR = Path(__file__).parent


def logger():
    fichier_log = BASE_DIR / "data" / "logs" / "pipeline.log"
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
        handlers=[
            logging.FileHandler(fichier_log, encoding="utf-8"),
            logging.StreamHandler(),
        ],
    )
    return logging.getLogger("pipeline")


l = logger()

        
def normaliser_fichier(nom):
    chemin = Path(nom)
    extension = chemin.suffix.lower()
    nom_sans_extension = chemin.stem.lower()
    nom_sans_extension = re.sub(r"[\s-]+", "_", nom_sans_extension )
    nom_sans_extension = re.sub(r"[^a-z0-9_]", "", nom_sans_extension )
    nom_sans_extension = re.sub(r"_+", "_", nom_sans_extension )
    nom_sans_extension = nom_sans_extension .strip("_")
 
    return nom_sans_extension + extension    
    
def nettoyer_fichier(d):
    for fichier in d.rglob("*"):
        if not fichier.is_file():
            continue
        f = fichier.name 
        nv = normaliser_fichier(f)
        destination = fichier.parent / nv 
        if destination.exists():
            l.warning(f"Collision détectée : {destination} ")  
            continue
        fichier.rename(destination)
        l.info(f"renommage {f} - {nv}")

vb = BASE_DIR / "data" / "brut" 
if __name__== "__main__":
    nettoyer_fichier(vb)
    
    
