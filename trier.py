from pathlib import Path
import shutil
import logging
from venv import logger

BASE_DIR = Path(__file__).parent
brut = BASE_DIR / "data" / "brut"

d = {
    ".pdf": "ordonnances",
    ".csv": "analyses",
    ".jpg": "radios",
    ".xlsx": "factures",
    ".log": "logs",
    ".png": "radios",
}


def trier_fichier():
    
     for fichier in brut.iterdir():
    
            if not fichier.is_file():
                continue
            extension = fichier.suffix.lower()
    
            if extension == ".tmp":
                print(f"fichier temporaire détecté : {fichier.name}")
                continue
            if extension not in d:
                print(f"extension inconnue")
                continue
            destination = brut / d[extension]
            destination.mkdir(parents=True,exist_ok=True)
            
            destination = destination / fichier.name
            shutil.move(fichier, destination)
            logging.info(f"Fichier déplacé : {fichier.name} - > {destination}")
    
        
if __name__ == "__main__":
    logging.info("Trie des Fichiers")
    trier_fichier()    
    logging.info("Trie Terminé")
    