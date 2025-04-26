import os
import sys
import csv
import dotenv
import requests
from datetime import datetime, timezone
from tqdm import tqdm
dotenv.load_dotenv()
url = "https://bikechallenge.ffvelo.fr"

username = ""
password = ""


class Getter:
    """
        Classe pour faire les requêtes
    """

    def __init__(self, base_url):
        self.base_url = base_url
        self.token = ""

    def do_get(self, route):
        """
            Get
        :param route:
        :return:
        """
        # print("get", route)
        response = requests.get(self.base_url + route,
                                headers={"Content-Type": "application/ld+json",
                                         "accept": "application/ld+json",
                                         'Authorization': f'Bearer {self.token}'})

        json_resp = response.json()
        resp = json_resp["member"]
        if "view" in json_resp:
            if "next" in json_resp["view"]:
                resp += self.do_get(json_resp["view"]["next"])
        return resp

    def do_post(self, route, content):
        """
            Post
        :param route:
        :param content:
        """
        response = requests.post(self.base_url + route, json=content,
                                 headers={"Content-Type": "application/ld+json",
                                          "accept": "application/ld+json",
                                          'Authorization': f'Bearer {self.token}'})

        print(response.json())

    def gettoken(self, uname, pwd, token=''):
        """
            Récupérer le token
        :param token:
        :param uname:
        :param pwd:
        """
        if token == '':
            response = requests.post(self.base_url + "/api/auth", json={"username": uname, "password": pwd},
                                     headers={"Content-Type": "application/ld+json",
                                              "accept": "application/ld+json"})

            self.token = response.json()["token"]
        else:
            self.token = token


class Interface:
    """
        Interface utilisateur
    """

    def __init__(self):
        self.evenements = []
        self.event_choisi = {}
        self.epreuve = {}
        self.dossards = []
        self.result_dict = {}
        self.getter = Getter(url)

    def choix_evenement(self):
        """
            Choix de l'évènement
        """
        print("Choisissez un évènement :")
        for evenement in self.evenements:
            print(f' - {evenement["id"]} ({evenement["name"]})')

        num_event_choisi_str = input("Entrez l'id de l'évènement : ")

        try:
            num_event_choisi = int(num_event_choisi_str)
            for ev in self.evenements:
                if ev["id"] == num_event_choisi:
                    self.event_choisi = ev
                    break
        except ValueError:
            print("La valeur n'est pas valide")
            sys.exit()

    def choix_epreuve(self):
        """
            Choix de l'évènement
        """
        print("\n#########################\n")
        print("Choisissez une épreuve :")
        for idx, epreuve in enumerate(self.event_choisi["dataEpreuvesJson"]):
            print(f' - {idx} ({epreuve["nom"]})')

        num_epr_choisi_str = input("Entrez le numéro de l'épreuve : ")

        try:
            num_epr_choisi = int(num_epr_choisi_str)
            self.epreuve = self.event_choisi["dataEpreuvesJson"][num_epr_choisi]

        except ValueError:
            print("La valeur n'est pas valide")
            sys.exit()

    def dossard_by_plaque(self, plaque):
        """
            Dossard d'après la place
        :param plaque:
        :return:
        """
        out = {}
        for doss in self.dossards:
            if doss["dossardId"].startswith(str(plaque)):
                out = doss
                break
        return out

    def get_datas(self, filename):
        self.result_dict = {}
        with open(filename, 'r', encoding='utf-8', newline='') as csvfile:
            reader = csv.reader(csvfile, delimiter=";")
            next(reader)
            for row in reader:
                key, value = row
                self.result_dict[round(float(key))] = round(float(value))

    def send_pointages(self):
        utc_now = datetime.now(timezone.utc)
        iso8601_string = utc_now.isoformat()
        for plaque, points in tqdm(self.result_dict.items()):
            dossard = self.dossard_by_plaque(plaque)

            content = {
                "uuidEpreuve": self.epreuve["uuid"],
                "balise": "",
                "dossards": dossard["@id"],
                "evenement": self.event_choisi["@id"],
                "heureDePointage": iso8601_string,
                "dataPointageJson": {"points": points}
            }

            self.getter.do_post("/api/pointages", content)
            print("\Terminé !\n")

    def main(self):
        """
            Lancer l'interface utilisateur
        """
        self.getter.gettoken(os.getenv("UNAME"), os.getenv("PASSWORD"))
        # json.dump(evenements, open("evenements.json", "w", encoding="utf-8"))

        self.evenements = self.getter.do_get("/api/evenements")
        self.choix_evenement()
        self.choix_epreuve()
        self.dossards = self.getter.do_get(
            f"/api/dossards?evenementId={self.event_choisi['id']}")
        self.get_datas("user/points.csv")
        self.send_pointages()


interface = Interface()
interface.main()
