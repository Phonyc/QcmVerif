"""
    Serveur pour la vérification manuelle
"""
import json

from flask import Flask, render_template, send_file, redirect, request, jsonify

import calcul

results = json.load(open("feuilles.json"))
num_plaques = {}
ids = []
for k in results:
    ids.append(k)
out = {}
app = Flask(__name__)

@app.route("/")
def index():
    """
        Page de redirection
    :return:
    """
    return redirect("/verif/0")

@app.route('/verif/<feuille_id>', methods=['GET', 'POST'])
def verif(feuille_id):
    """
        Page pour la vérification manuelle
    :param feuille_id:
    :return:
    """
    feuille_id = int(feuille_id)
    if request.method == 'POST':
        numplaque = int(request.json["num"])
        out[numplaque] = request.json["result"]
        json.dump(out, open("results.json", "w"))
        return jsonify({"status": "ok"})
    else:
        if feuille_id < len(ids):
            plaque = ""
            try:
                plaque = num_plaques[ids[feuille_id]]
            except KeyError:
                pass
            return render_template('index.html', rectangles=results[ids[feuille_id]], num=plaque, f_id=feuille_id)
        else:
            return redirect("/calc")

@app.route('/next/<feuille_id>')
def next_page(feuille_id):
    """
        Page suivante pour la vérification manuelle
    :param feuille_id:
    :return:
    """
    feuille_id = int(feuille_id)
    return redirect(f"/verif/{feuille_id + 1}")

@app.route('/image/<feuille_id>')
def get_image(feuille_id):
    """
        Obtenir l'image
    :param feuille_id:
    :return:
    """
    feuille_id = int(feuille_id)
    return send_file(f'red/{ids[feuille_id]}')


@app.route('/calc')
def calc():
    """
        Calculer les points
    :return:
    """

    calcul.export_pts()
    return jsonify({"status": "ok"})


app.run(debug=False, host='0.0.0.0', port=3000)