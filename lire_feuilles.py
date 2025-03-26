"""Lancer l'extraction des données"""
import json
import os

from tqdm import tqdm

import result_extract
from recal import redresser_image


class Feuille:
    """
        Une feuille réponse dont il faut extraire les résultats
    """
    def __init__(self, image_path):
        self.image_path = image_path
        self.results = []

    def compute(self):
        """
            Traiter l'image et extraire les résultats
        """
        self.results = result_extract.main(redresser_image(self.image_path))


images_paths = os.listdir('input')
feuilles = []
for path in images_paths:
    if not path.startswith('.'):
        feuilles.append(Feuille(path))

for feuille in tqdm(feuilles):
    feuille.compute()

json_out = {}
for feuille in feuilles:
    json_out[feuille.image_path] = feuille.results
json.dump(json_out, open("feuilles.json", "w"))