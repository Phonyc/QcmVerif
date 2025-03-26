"""Extraction des données depuis les images"""
import cv2
import numpy as np

LETTRES = "ABCDEFGH"


def set_rectangles(imshape):
    """
        Définir les rectangles des cases réponses
    :param imshape:
    :return:
    """
    rects = []
    hrect = imshape[0] / 28.986
    wrect = imshape[1] / 11.9
    decx = round(imshape[1] / 4.41)
    decy = round(imshape[0] / 4.44)
    for nligne in range(0, 22):
        for ncol in range(0, 8):
            case_name = f'{nligne + 1}#{LETTRES[ncol]}'
            rects.append(
                (round(decx + ncol * wrect), round(decy + hrect * nligne), round(wrect), round(hrect), case_name))
    return rects


def threshold_bin(image_tr_gr):
    """
        Calculer le seuil pour binariser l'image
    :param image_tr_gr:
    :return:
    """
    square_size = 10

    # Obtenir les dimensions de l'image
    h, w = image_tr_gr.shape

    # Calculer les coordonnées des coins
    top_left = image_tr_gr[0:square_size, 0:square_size]
    top_right = image_tr_gr[0:square_size, w - square_size:w]
    bottom_left = image_tr_gr[h - square_size:h, 0:square_size]
    bottom_right = image_tr_gr[h - square_size:h, w - square_size:w]

    # Calculer la couleur moyenne des coins
    mean_top_left = np.mean(top_left)
    mean_top_right = np.mean(top_right)
    mean_bottom_left = np.mean(bottom_left)
    mean_bottom_right = np.mean(bottom_right)

    # Calculer le seuil moyen
    return min(mean_top_left, mean_top_right, mean_bottom_left, mean_bottom_right) - 10


def get_binary_image(intial_image):
    """
        Retourne l'image en noir et blanc
    :param intial_image:
    :return:
    """
    gray_image = cv2.cvtColor(intial_image, cv2.COLOR_BGR2GRAY)
    _, temp_bin_img = cv2.threshold(gray_image, threshold_bin(gray_image), 255, cv2.THRESH_BINARY)
    kernel = np.ones((3, 3), np.uint8)
    return cv2.bitwise_not(cv2.erode(temp_bin_img, kernel, iterations=2))


def add_rect(image, x, y, width, height, _, color):
    """
        Ajouter un rectangle reponse sur l'image
    :param image:
    :param x:
    :param y:
    :param width:
    :param height:
    :param _:
    :param color:
    """
    cv2.rectangle(image, (x, y), (x + width, y + height), color, 2)  # Rouge


def draw_results(image, results):
    """
        Dessiner les rectangles de résultats
    :param image:
    :param results:
    """
    for (x, y, width, height, name, checked) in results:
        color = (0, 0, 255) if checked else (0, 255, 0)
        add_rect(image, x, y, width, height, name, color)


# def detect_plaque(image):
#     x=169
#     y=56
#     width=104
#     height=45
#     cv2.rectangle(image, (x, y), (x + width, y + height), (255, 0, 0), 2)
#     cv2.imshow("image", image)
#     cv2.waitKey(0)
#     plaque_content = image[y:y + height, x:x + width]

def main(image):
    """
        Détecter les réponses cochées
    :param image:
    """
    results = []
    threshold_coche = 0.3

    rectangles = set_rectangles(image.shape)
    binary_image = get_binary_image(image)
    # detect_plaque(image)
    for i, (x, y, width, height, name) in enumerate(rectangles):
        rectangle_content = binary_image[y:y + height, x:x + width]

        percentage_filled = cv2.countNonZero(rectangle_content) / (width * height)

        results.append((x, y, width, height, name, percentage_filled > threshold_coche))

    draw_results(image, results)
    # cv2.imshow('Image', image)
    # cv2.waitKey(0)
    return results
