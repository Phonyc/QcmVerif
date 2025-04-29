"""Correction des QCM des épreuves pour les jeunes de la FFVélo"""
import json
import os
import sys

import fitz
from flask import Flask, render_template, send_file, redirect, request, jsonify
from tqdm import tqdm

import result_extract
from recal import Redresseur

IMAGES_EXTS = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff']


class Qcm:
    """
        Correction d'un questionnaire
    """

    def __init__(self, config):
        self.folder = config["folder"]
        self.name = config["name"]
        self.reponses = config["reponses"]
        self.except_lines = config["excl_lines"]
        self.except_cols = config["excl_cols"]
        self.pts_par_question = round(config["points_total"] / len(list(self.reponses.keys())), 2)
        self.images_paths = os.listdir(f'{self.folder}/input')
        self.redresseur = Redresseur(self.folder)
        self.data_extract = {}
        self.replace = False
        self.out_results = {}
        if os.path.isfile(f"{self.folder}/result.json"):
            self.out_results = json.load(open(f"{self.folder}/result.json"))
        self.app = Flask(__name__)
        self.setup_routes()

    def setup_routes(self):
        """
            Mettre les routes du serveur en place
        :return:
        """

        @self.app.route('/')
        def home():
            """
                Page accueil : renvoyer vers la première image.
            :return:
            """
            return redirect(f"/verif/{list(self.data_extract.keys())[0]}")

        @self.app.route('/verif/<image_path>', methods=['GET', 'POST'])
        def verif(image_path):
            """
                Page de vérification des cases cochées
            :param image_path:
            :return:
            """
            if request.method == 'POST':
                numplaque = int(request.json["num"])
                self.out_results[str(numplaque)] = request.json["result"]
                self.save_result()
                return jsonify({"status": "ok"})
            else:
                return render_template('index.html', rectangles=self.data_extract[image_path], f_id=image_path)

        @self.app.route('/next/<image_path>')
        def next_page(image_path):
            """
                Retourner la prochaine image
            :param image_path:
            :return:
            """
            cles = list(self.data_extract.keys())
            try:
                index_cle_actuelle = cles.index(image_path)
                if index_cle_actuelle + 1 < len(cles):
                    return redirect(f"/verif/{cles[index_cle_actuelle + 1]}")
                else:
                    return redirect("/calc")
            except ValueError:
                return redirect("/calc")

        @self.app.route('/image/<image_path>')
        def get_image(image_path):
            """
                Retourner l'image
            :param image_path:
            :return:
            """
            return send_file(f'{self.folder}/droit/{image_path}')

        @self.app.route('/calc')
        def calc():
            """
                Lancer le calcul
            :return:
            """
            # os.kill(os.getpid(), signal.SIGINT)
            print("Calcul des points")
            self.calcul()

            return "OK"

    def pdf_to_images(self, input_pdf_path):
        """
            Extraire les pages d'un pdf vers des images
        :param input_pdf_path:
        """
        pdf_document = fitz.open(input_pdf_path)
        for page_number in tqdm(range(len(pdf_document))):
            page = pdf_document[page_number]
            pix = page.get_pixmap()  # Convertir la page en image
            output_image_path = f'{self.folder}/input/frompdf_{page_number + 1}.png'  # Nom de l'image
            pix.save(output_image_path)  # Enregistrer l'image

        pdf_document.close()  # Fermer le document PDF

    def launch(self):
        """
            Fonction principale
        """
        print(f"*** Correction de : {self.name} ***")
        print("Paramètres :")
        print(" - Points par question :", self.pts_par_question)
        if os.path.exists(f"{self.folder}/data_extract.json"):
            input_ecrase = input(
                "\nDes données ont déjà été lues pour ce QCM, les écraser ? (y/N)")
            if input_ecrase.strip() == "y" or input_ecrase.strip() == "Y":
                self.replace = True

            if not self.replace:
                self.data_extract = json.load(
                    (open(f"{self.folder}/data_extract.json", encoding="utf-8")))
        if self.replace:
            self.out_results = {}
        self.extract()
        self.save_extract()

        self.app.run(host="127.0.0.1", port=3000)

    def extract(self):
        """
            Extraire les cases cochées
        """
        print("Préparation...")
        for path in self.images_paths:
            if not path.startswith('.') and path.endswith("pdf"):
                self.pdf_to_images(f'{self.folder}/input/{path}')

        print("Extraction...")
        for path in tqdm(self.images_paths):
            if not path.startswith('.'):
                _, extension = os.path.splitext(path)
                if extension.lower() in IMAGES_EXTS:
                    if path not in self.data_extract:
                        self.data_extract[path] = result_extract.main(
                            self.redresseur.redresser_image(path),
                            except_lines=self.except_lines, except_cols=self.except_cols)

    def single_calc_point(self, entrees):
        """
            Calculer les points d'une feuille
        :param entrees:
        :return:
        """
        points = 0
        for nk, rep in self.reponses.items():
            n_reps = 0
            add_pt = False
            for entree in entrees:
                if entree.startswith(f"{nk}#"):
                    n_reps += 1
                    if entree == f"{nk}#{rep}":
                        add_pt = True

            if n_reps == 1 and add_pt:
                points += self.pts_par_question

        return points

    def calcul(self):
        """
            Calcul global des points
        """
        out = "num plaque;points\n"
        for np, result in self.out_results.items():
            out += f"{np};{self.single_calc_point(result)}\n"
        with open(f"{self.folder}/points.csv", "w", encoding="utf-8") as f:
            print(out)
            f.write(out)
        print("**Points Calculés ***")

    def save_extract(self):
        """
            Sauvegarder les cases extraites
        """
        json.dump(self.data_extract, open(
            f"{self.folder}/data_extract.json", "w", encoding="utf-8"))

    def save_result(self):
        """
            Sauvegarder les réponses entrées
        """
        json.dump(self.out_results, open(
            f"{self.folder}/result.json", "w", encoding="utf-8"))


questionnaires = json.load(open("config.json"))["questionnaires"]
print("\n#########################\n")
print("Choisissez un questionnaire :")
for idx, quest in enumerate(questionnaires):
    print(f' - {idx} ({quest["name"]})')

num_epr_choisi_str = input("\nEntrez le numéro du questionnaire : ")

try:
    num_epr_choisi = int(num_epr_choisi_str)
    quest_def = questionnaires[num_epr_choisi]
except ValueError:
    print("La valeur n'est pas valide")
    sys.exit()
print("")
qcm = Qcm(quest_def)
qcm.launch()
