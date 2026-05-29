import os
import requests
from flask import Flask, render_template_string, request

app = Flask(__name__)

# Configuration de ton bot Telegram
TOKEN = "8929246651:AAFSqQ_k4Wi5GI0l3a773czmfcen0_jWrAc"

CHAT_ID = "6141877001"


HTML_FORM = """
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Marseille CBD</title>
    <style>
        body { font-family: Arial, sans-serif; background-color: #121212; color: #ffffff; padding: 20px; display: flex; justify-content: center; }
        .container { background-color: #1e1e1e; padding: 30px; border-radius: 10px; max-width: 400px; width: 100%; box-shadow: 0 4px 10px rgba(0,0,0,0.5); }
        h1 { color: #2ecc71; text-align: center; margin-bottom: 5px; }
        p { text-align: center; color: #aaa; font-size: 14px; margin-top: 0; }
        label { display: block; margin: 15px 0 5px; font-weight: bold; }
        input, select, button { width: 100%; padding: 12px; margin-bottom: 10px; border-radius: 5px; border: none; box-sizing: border-box; }
        input, select { background-color: #2a2a2a; color: white; border: 1px solid #333; }
        button { background-color: #2ecc71; color: white; font-weight: bold; font-size: 16px; cursor: pointer; margin-top: 15px; }
        button:hover { background-color: #27ae60; }
        .success { background-color: #27ae60; color: white; padding: 15px; border-radius: 5px; text-align: center; font-weight: bold; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🌿 Marseille CBD</h1>
        <p>Livraison rapide - La Plaine / Cours Ju</p>
        <hr style="border: 0.5px solid #333;">

        {% if succes %}
            <div class="success">✅ Commande validée ! Un livreur vous contacte par SMS d'ici 5 minutes.</div>
        {% endif %}

        <form method="POST" action="/">
            <label>Votre Prénom :</label>
            <input type="text" name="prenom" placeholder="Ex: Jean" required>

            <label>Numéro de Téléphone (Pour le livreur) :</label>
            <input type="tel" name="telephone" placeholder="Ex: 0612345678" required>

            <label>Adresse de livraison (Marseille) :</label>
            <input type="text" name="adresse" placeholder="Ex: 12 Rue des Trois Rois" required>

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
        
        # Préparation du texte pour Telegram
        texte_telegram = f"🔔 *NOUVELLE COMMANDE REÇUE !*\n\n👤 *Prénom :* {prenom}\n📞 *Tél :* {telephone}\n📍 *Adresse :* {adresse}\n📦 *Produit :* {choix_commande}"
        
        # Envoi au Bot Telegram
        url_telegram = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
        payload = {
            "chat_id": CHAT_ID,
            "text": texte_telegram
        }
        
        try:
            requests.post(url_telegram, json=payload)
            succes = True
        except Exception as e:
            print(f"!!! ERREUR TELEGRAM CRUCIALE !!!: {e}")
            
    return render_template_string(HTML_FORM, succes=succes)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
