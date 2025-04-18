import os
import sys

import dotenv
import requests

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
        print("get", route)
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
        print("get Token")
        if token == '':
            response = requests.post(self.base_url + "/api/auth", json={"username": uname, "password": pwd},
                                     headers={"Content-Type": "application/ld+json",
                                              "accept": "application/ld+json"})

            print(response.json())
            self.token = response.json()["token"]
        else:
            self.token = token
        print("fin token")


class Interface:
    """
        Interface utilisateur
    """

    def __init__(self):
        self.evenements = []
        self.event_choisi = {}
        self.epreuve = {}
        self.dossards = []

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
        print("Choisissez un évènement :")
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


    def main(self):
        """
            Lancer l'interface utilisateur
        """
        print("start")
        getter = Getter(url)
        getter.gettoken(os.getenv("UNAME"), os.getenv("PASSWORD"))
        # json.dump(evenements, open("evenements.json", "w", encoding="utf-8"))

        self.evenements = getter.do_get("/api/evenements")
        # self.evenements = json.load(open("evenements.json", encoding="utf-8"))["member"]
        self.choix_evenement()
        print(self.event_choisi)
        self.choix_epreuve()
        print(self.epreuve)
        self.dossards = getter.do_get(f"/api/dossards?evenementId={self.event_choisi['id']}")
        # print(self.dossards)
        print(self.dossard_by_plaque(34))


interface = Interface()
interface.main()
