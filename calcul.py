"""Calcul des points"""
import json

n_questions = 5
points_total = 100
pts_par_question = round(points_total / n_questions, 2)
reponses = {
    1: "A",
    2: "A",
    3: "A",
    4: "A",
    5: "A",
}


def arrondir_inf_5(n):
    """
        Arrondir au 5 inférieur
    :param n:
    :return:
    """
    return n - (n % 5)


def calc_point(entrees):
    """
        Calculer les points
    :param entrees:
    :return:
    """
    points = 0
    for nk, rep in reponses.items():
        n_reps = 0
        add_pt = False
        for entree in entrees:
            if entree.startswith(f"{str(nk)}#"):
                n_reps += 1
                if entree == f"{nk}#{rep}":
                    add_pt = True

        if n_reps == 1 and add_pt:
            points += pts_par_question

    return arrondir_inf_5(points)


def export_pts():
    """
        Exporter les points en Csv
    """
    out = "num plaque;points\n"
    results = json.load(open("results.json"))
    for np, result in results.items():
        out += f"{np};{calc_point(result)}\n"
    with open("points.csv", "w", encoding="utf-8") as f:
        f.write(out)

# export_pts()