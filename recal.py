"""Recaler les images avec les ronds aux 4 coins"""
import cv2
import numpy as np
import os
class Redresseur:
    def __init__(self, folder):
        self.folder = folder

    def resize_image(self, image):
        """
            Redimensionne l'image
        :param image:
        """
        height, width = image.shape[:2]

        scale = 1000 / max(height, width)
        new_width = int(width * scale)
        new_height = int(height * scale)

        return cv2.resize(image, (new_width, new_height))

    def afficher_cercles(self, image, circles):
        """
            Afficher les cercles trouvés
        :param image:
        :param circles:
        """
        for i in circles[0, :]:
            cv2.circle(image, (i[0], i[1]), i[2], (0, 255, 0), 2)  # Dessiner le cercle

        cv2.imshow('Cercles détectés', image)
        cv2.waitKey(0)

    def redresser_image(self, image_path):
        """
            Redresser l'image avec les cercles
        :param image_path:
        """
        image = self.resize_image(cv2.imread(f"{self.folder}/input/{image_path}"))

        image_gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        # Détection des cercles
        circles = cv2.HoughCircles(image_gray, cv2.HOUGH_GRADIENT, dp=1, minDist=50,
                                param1=150, param2=50, minRadius=20, maxRadius=50)

        if circles is not None:
            circles = np.uint16(np.around(circles))
            points = []
            # Centres des cercles
            for i in circles[0, :]:
                points.append((i[0], i[1]))

            # S'assurer qu'il y a au moins 4 cercles pour redresser l'image
            if len(points) >= 4:
                # Trier les points pour obtenir les coins
                points = sorted(points, key=lambda x: (x[1], x[0]))  # Trier par y, puis par x
                top_points = sorted(points[:2], key=lambda x: x[0])  # Deux points du haut
                bottom_points = sorted(points[2:], key=lambda x: x[0])  # Deux points du bas

                # Définir les points de destination pour la transformation
                destination_points = np.array([
                    [0, 0],  # Coin supérieur gauche
                    [image.shape[1] - 1, 0],  # Coin supérieur droit
                    [image.shape[1] - 1, image.shape[0] - 1],  # Coin inférieur droit
                    [0, image.shape[0] - 1]  # Coin inférieur gauche
                ], dtype='float32')

                # Points source
                source_points = np.array([
                    top_points[0],  # Coin supérieur gauche
                    top_points[1],  # Coin supérieur droit
                    bottom_points[1],  # Coin inférieur droit
                    bottom_points[0]  # Coin inférieur gauche
                ], dtype='float32')
                # Calculer la matrice de transformation
                matrix = cv2.getPerspectiveTransform(source_points, destination_points)

                # Appliquer la transformation de perspective
                image_redressee = cv2.warpPerspective(image, matrix, (image.shape[1], image.shape[0]))
                if not os.path.exists(f'{self.folder}/droit'):
                    os.makedirs(f'{self.folder}/droit')
                cv2.imwrite(f'{self.folder}/droit/{image_path}', image_redressee)
                
                return image_redressee
            else:
                afficher_cercles(image, circles)
                print("Pas assez de cercles détectés pour redresser l'image.")
        else:
            print("Aucun cercle détecté.")

