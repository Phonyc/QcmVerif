from recal import Redresseur
import os
from tqdm import tqdm
import webbrowser
import json
import result_extract
import sys
from flask import Flask, render_template, send_file, redirect, request, jsonify
IMAGES_EXTS = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff']

import signal
class Qcm:
    def __init__(self, config):
        self.folder = config["folder"]
        self.name = config["name"]
        self.reponses = config["reponses"]
        self.pts_par_question = round(config["points_total"] / len(list(self.reponses.keys())), 2)
        self.images_paths = os.listdir(f'{self.folder}/input')
        self.redresseur = Redresseur(self.folder)
        self.data_extract = {}
        self.replace = False
        self.out_results = {}
        if (os.path.isfile(f"{self.folder}/result.json")):
            self.out_results = json.load(open(f"{self.folder}/result.json"))

        self.app = Flask(__name__)
        self.setup_routes()

    def setup_routes(self):
        @self.app.route('/')
        def home():
            return redirect(f"/verif/{list(self.data_extract.keys())[0]}")

        @self.app.route('/verif/<image_path>', methods=['GET', 'POST'])
        def verif(image_path):
            if request.method == 'POST':
                numplaque = int(request.json["num"])
                self.out_results[str(numplaque)] = request.json["result"]
                self.save_result()
                return jsonify({"status": "ok"})
            else:
                return render_template('index.html', rectangles=self.data_extract[image_path], f_id=image_path)

        @self.app.route('/next/<image_path>')
        def next_page(image_path):
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
            return send_file(f'{self.folder}/droit/{image_path}')

        @self.app.route('/calc')
        def calc():
            # os.kill(os.getpid(), signal.SIGINT)
            self.continue_to_calc()
            return "OK"

    def launch(self):
        print(f"*** Correction de : {self.name} ***")
        print("Paramètres :")
        print(" - Points par question :", self.pts_par_question)
        if os.path.exists(f"{self.folder}/data_extract.json"):
            input_ecrase = input(
                "Des données ont déjà été lues pour ce QCM, les écraser ? (y/N)")
            if (input_ecrase.strip() in "yY"):
                self.replace = True

            if (not self.replace):
                self.data_extract = json.load(
                    (open(f"{self.folder}/data_extract.json", "r", encoding="utf-8")))
        if self.replace:
            self.out_results = {}
        self.extract()
        self.save_extract()

        self.app.run(host="127.0.0.1", port=3000)
    
    def continue_to_calc(self):
        print("Calcul des points")
        self.calcul()

    def extract(self):
        feuilles = []
        for path in tqdm(self.images_paths):
            if not path.startswith('.'):
                _, extension = os.path.splitext(path)
                if extension.lower() in IMAGES_EXTS:
                    if path not in self.data_extract:
                        self.data_extract[path] = result_extract.main(
                            self.redresseur.redresser_image(path))

    def single_calc_point(self, entrees):
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

        return points - (points % 5)

    def calcul(self):
        out = "num plaque;points\n"
        for np, result in self.out_results.items():
            out += f"{np};{self.single_calc_point(result)}\n"
        with open(f"{self.folder}/points.csv", "w", encoding="utf-8") as f:
            print(out)
            f.write(out)
        print("**Points Calculés ***")        

    def save_extract(self):
        json.dump(self.data_extract, open(
            f"{self.folder}/data_extract.json", "w", encoding="utf-8"))

    def save_result(self):
        json.dump(self.out_results, open(
            f"{self.folder}/result.json", "w", encoding="utf-8"))


print(json.load(open("config.json"))["questionnaires"][0])
qcm = Qcm(json.load(open("config.json"))["questionnaires"][0])
qcm.launch()
