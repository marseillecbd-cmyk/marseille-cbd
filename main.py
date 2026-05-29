import os
import csv
from datetime import datetime
import requests
from flask import Flask, request, render_template_string

app = Flask(__name__)

# Configurations de tes clés Telegram
TELEGRAM_TOKEN = "8929246651:AAFSqQ_k4Wi5GIOl3a773czmfcenO_jWrAc"
CHAT_ID = "6141877001"

# Fichier pour stocker ta comptabilité automatiquement
COMPTA_FILE = "compta_commandes.csv"

# Fonction pour envoyer le message sur ton Telegram
def envoyer_telegram(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": message, "parse_mode": "Markdown"}
    try:
        requests.post(url, json=payload)
    except Exception as e:
        print(f"Erreur envoi Telegram: {e}")

# Fonction pour sauvegarder la commande dans ton fichier compta
def sauvegarder_compta(prenom, telephone, adresse, commande, total):
    file_exists = os.path.isfile(COMPTA_FILE)
    date_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    with open(COMPTA_FILE, mode="a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        if not file_exists:
            # En-tête du fichier si c'est la première commande
            writer.writerow(["Date", "Prénom", "Téléphone", "Adresse", "Commande", "Total TTC (€)"])
        writer.writerow([date_str, prenom, telephone, adresse, commande, total])

# Page d'accueil avec le formulaire de commande (Design simple et propre)
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Marseille CBD - Livraison Éclair</title>
    <style>
        body { font-family: Arial, sans-serif; background-color: #121212; color: white; padding: 20px; text-align: center; }
        .container { max-width: 400px; margin: auto; background: #1e1e1e; padding: 20px; border-radius: 10px; box-shadow: 0px 4px 10px rgba(0,0,0,0.5); }
        h1 { color: #4CAF50; font-size: 24px; }
        label { display: block; margin: 10px 0 5px; text-align: left; font-weight: bold; }
        input, select { width: 100%; padding: 10px; margin-bottom: 15px; border-radius: 5px; border: 1px solid #333; background: #2a2a2a; color: white; box-sizing: border-box; }
        button { width: 100%; padding: 12px; background-color: #4CAF50; border: none; color: white; font-size: 16px; font-weight: bold; border-radius: 5px; cursor: pointer; }
        button:hover { background-color: #45a049; }
        .success { color: #4CAF50; font-weight: bold; margin-top: 15px; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🌿 Marseille CBD</h1>
        <p>Livraison rapide - La Plaine / Cours Ju</p>
        <hr style="border: 0.5px solid #333;">
        
        {% if succes %}
            <p class="success">✅ Commande validée ! Un livreur vous contacte par SMS d'ici 5 minutes.</p>
        {% endif %}

        <form method="POST" action="/">
            <label>Votre Prénom :</label>
            <input type="text" name="prenom" placeholder="Ex: Jean" required>

            <label>Numéro de Téléphone (Pour le livreur) :</label>
            <input type="tel" name="telephone" placeholder="Ex: 0612345678" required>

            <label>Adresse de livraison (Marseille) :</label>
            <input type="text" name="adresse" placeholder="Ex: 12 Rue des Trois Mages" required>

            <label>Choisissez votre produit :</label>
            <select name="commande">
                <option value="Amnesia Haze - 5g (40€)">Amnesia Haze - 5g (40€)</option>
                <option value="Cookie Kush - 5g (40€)">Cookie Kush - 5g (40€)</option>
                <option value="Pack Découverte - 10g (70€)">Pack Découverte - 10g (70€)</option>
            </select>

            <button type="submit">⚡ PASSER LA COMMANDE</button>
        </form>
    </div>
</body>
</html>
"""

@app.route("/", methods=["GET", "POST"])
def home():
    succes = False
    if request.method == "POST":
        prenom = request.form.get("prenom")
        telephone = request.form.get("telephone")
        adresse = request.form.get("adresse")
        choix_commande = request.form.get("commande")
        
        # Extraire le prix de la chaîne de caractères de manière simple
        total = "40" if "5g" in choix_commande else "70"

        # 1. Sauvegarde automatique dans le fichier Excel/CSV pour ta compta
        sauvegarder_compta(prenom, telephone, adresse, choix_commande, total)

        # 2. Construction du message d'alerte pour ton Telegram
        msg_telegram = (
            f"🚨 *NOUVELLE COMMANDE !*\n\n"
            f"👤 *Client :* {prenom}\n"
            f"📞 *Tel :* {telephone}\n"
            f"📍 *Adresse :* {adresse}\n"
            f"📦 *Produit :* {choix_commande}\n"
            f"💰 *À encaisser :* {total} €\n\n"
            f"🚴 _Sors le vélo, faut livrer !_"
        )
        # Envoi de la notification
        envoyer_telegram(msg_telegram)
        succes = True

    return render_template_string(HTML_TEMPLATE, succes=succes)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
