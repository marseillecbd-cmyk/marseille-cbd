import os
import requests
from flask import Flask, render_template_string, request
import math
from datetime import datetime
import csv

app = Flask(__name__)

# Ta configuration Telegram officielle
TOKEN = "8929246651:AAFSqQ_k4Wi5GIOl3a773czmfcenO_jWrAc"
CHAT_ID = "6141877001"

# Coordonnées du centre de ta zone (La Plaine / Cours Ju)
CENTRE_LAT = 43.2938
CENTRE_LON = 5.3854
RAYON_MAX_KM = 1.0

# Fichier de comptabilité local
FICHIER_COMPTA = "compta.csv"

# 📦 GESTION DU STOCK (Modifie tes quantités ici)
STOCKS = {
    "Amnesia Haze": {"2g": 10, "5g": 5, "10g": 3},
    "Orange Bud": {"2g": 8, "5g": 4, "10g": 2},
    "Cookie Kush": {"2g": 12, "5g": 6, "10g": 4},
    "Skuff - Polen": {"2g": 15, "5g": 7, "10g": 3},
    "Creamy Piatella": {"2g": 5, "5g": 3, "10g": 1}
}

def calculer_distance(lat1, lon1, lat2, lon2):
    """ Calcule la distance en km entre deux points """
    R = 6371.0
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)
    a = math.sin(delta_phi / 2.0)**2 + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2.0)**2
    c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))
    return R * c

def enregistrer_vente_anonyme(liste_items, total_prix):
    """ Enregistre la commande dans un fichier Excel/CSV de manière 100% anonyme (Conforme RGPD) """
    try:
        fichier_existe = os.path.exists(FICHIER_COMPTA)
        with open(FICHIER_COMPTA, mode="a", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            if not fichier_existe:
                writer.writerow(["Date et Heure", "Produits", "Total (€)"])
            
            date_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            writer.writerow([date_str, liste_items, f"{total_prix}€"])
    except Exception as e:
        print(f"Erreur enregistrement compta: {e}")

def generer_html(statut_commande=None):
    HTML_FORM = """
    <!DOCTYPE html>
    <html lang="fr">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Marseille CBD</title>
        <style>
            :root {
                --bg-color: #0b0b0c;
                --card-bg: #161618;
                --accent-color: #00ff66;
                --error-color: #ff3b30;
                --text-main: #ffffff;
                --text-muted: #8e8e93;
            }
            body {
                font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
                background-color: var(--bg-color);
                color: var(--text-main);
                margin: 0;
                padding: 20px;
                display: flex;
                flex-direction: column;
                align-items: center;
            }
            .header { text-align: center; margin-bottom: 30px; }
            .header h1 { font-size: 2.2rem; letter-spacing: 2px; margin-bottom: 5px; }
            .header p { color: var(--text-muted); font-size: 0.95rem; margin: 0; }
            .badge { display: inline-block; background: rgba(0, 255, 102, 0.1); color: var(--accent-color); padding: 5px 12px; border-radius: 20px; font-size: 0.85rem; font-weight: bold; margin-top: 10px; }
            
            .section-title { font-size: 1.5rem; font-weight: bold; letter-spacing: 1px; margin: 40px 0 20px; text-transform: uppercase; width: 100%; max-width: 800px; text-align: center; color: var(--text-main); border-bottom: 1px solid rgba(255,255,255,0.1); padding-bottom: 8px;}
            
            .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(240px, 1fr)); gap: 18px; width: 100%; max-width: 800px; margin-bottom: 20px; }
            .card { background: var(--card-bg); border: 1px solid #2c2c2e; border-radius: 12px; padding: 20px; text-align: center; cursor: pointer; transition: transform 0.2s, border-color 0.2s; position: relative; }
            .card:hover { transform: translateY(-2px); border-color: #48484a; }
            .card h3 { margin: 0 0 5px 0; font-size: 1.2rem; }
            .card .culture-tag { font-size: 0.75rem; color: var(--accent-color); text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 12px; display: block; }

            .size-options { display: flex; gap: 8px; justify-content: center; margin-top: 15px; flex-wrap: wrap; }
            .size-btn { background: #2c2c2e; border: none; color: var(--text-main); padding: 8px 14px; border-radius: 6px; font-size: 0.85rem; font-weight: bold; cursor: pointer; transition: background 0.2s; }
            .size-btn:hover { background: #3a3a3c; }
            .size-btn.active { background: var(--accent-color); color: #000; }
            
            .size-btn:disabled { background: #1c1c1e; color: #48484a; border: 1px dashed #3a3a3c; cursor: not-allowed; text-decoration: line-through; }
            
            .sticky-footer { position: fixed; bottom: 0; left: 0; width: 100%; background: rgba(18, 18, 18, 0.85); backdrop-filter: blur(10px); border-top: 1px solid #2c2c2e; padding: 15px; box-sizing: border-box; display: flex; flex-direction: column; align-items: center; z-index: 10; }
            .summary-layout { display: flex; align-items: center; justify-content: center; gap: 15px; margin-bottom: 10px; flex-wrap: wrap; }
            .summary-text { font-size: 0.95rem; color: var(--text-muted); text-align: center; max-width: 500px; margin: 0; }
            .summary-text span { color: var(--accent-color); font-weight: bold; }
            .btn-clear { background: none; border: 1px solid #3a3a3c; color: var(--text-muted); padding: 4px 10px; border-radius: 6px; font-size: 0.8rem; cursor: pointer; transition: all 0.2s; }
            .btn-clear:hover { background: #ff3b30; color: white; border-color: #ff3b30; }

            .btn-main { background: var(--accent-color); color: #000; border: none; padding: 12px 30px; font-size: 1rem; font-weight: bold; border-radius: 8px; cursor: pointer; width: 100%; max-width: 400px; transition: opacity 0.2s; text-transform: uppercase; }
            .btn-main:hover { opacity: 0.9; }
            .btn-main:disabled { background: #2c2c2e; color: var(--text-muted); cursor: not-allowed; }

            .modal-overlay { position: fixed; top:0; left:0; width:100%; height:100%; background: rgba(0,0,0,0.8); backdrop-filter: blur(4px); display: none; justify-content: center; align-items: center; z-index: 100; }
            .modal { background: var(--card-bg); border: 2px solid var(--accent-color); border-radius: 16px; padding: 25px; max-width: 380px; width: 90%; position: relative; box-shadow: 0 10px 30px rgba(0,0,0,0.5); }
            .modal.error-modal { border-color: var(--error-color); }
            .modal h2 { margin-top: 0; color: var(--accent-color); font-size: 1.4rem; text-align: center; }
            .modal.error-modal h2 { color: var(--error-color); }
            .modal-details { font-size: 0.95rem; color: var(--text-main); line-height: 1.5; margin-bottom: 20px; background: rgba(255,255,255,0.03); padding: 12px; border-radius: 8px; border: 1px solid #2c2c2e; }
            
            label { display: block; margin: 12px 0 4px; font-size: 0.85rem; color: var(--text-muted); text-transform: uppercase; font-weight: bold; }
            input { width: 100%; padding: 12px; background: #2c2c2e; border: 1px solid #3a3a3c; border-radius: 8px; color: white; box-sizing: border-box; font-size: 1rem; }
            input:focus { border-color: var(--accent-color); outline: none; }
            
            .success-screen, .error-screen { text-align: center; padding: 20px; }
            .success-icon { font-size: 40px; color: var(--accent-color); margin-bottom: 10px; }
            .error-icon { font-size: 40px; color: var(--error-color); margin-bottom: 10px; }
            
            .spacer { height: 140px; }
        </style>
    </head>
    <body>

        <div class="header">
            <h1>MARSEILLE CBD</h1>
            <p>Service de livraison privé & expéditions</p>
            <div class="badge">📍 Zone : La Plaine / Cours Ju (<1km)</div>
        </div>

        <!-- POPUP REUSSITE -->
        {% if statut == "succes" %}
        <div class="modal-overlay" id="statusOverlay" style="display: flex;" onclick="document.getElementById('statusOverlay').style.display='none'">
            <div class="modal" onclick="event.stopPropagation()">
                <div class="success-screen">
                    <div class="success-icon">✅</div>
                    <h2>COMMANDE VALIDÉE !</h2>
                    <p style="color: var(--text-muted); font-size: 0.95rem; margin-bottom: 5px;">Votre commande a bien été prise en compte.</p>
                    <p style="color: var(--accent-color); font-weight: bold; font-size: 0.95rem;">⏱️ Temps estimé : 20 à 45 min selon le rush.</p>
                    <button class="btn-main" onclick="document.getElementById('statusOverlay').style.display='none'" style="margin-top: 15px;">Fermer</button>
                </div>
            </div>
        </div>
        {% endif %}

        <!-- POPUP HORS ZONE -->
        {% if statut == "hors_zone" %}
        <div class="modal-overlay" id="statusOverlay" style="display: flex;" onclick="document.getElementById('statusOverlay').style.display='none'">
            <div class="modal error-modal" onclick="event.stopPropagation()">
                <div class="error-screen">
                    <div class="error-icon">❌</div>
                    <h2>HORS ZONE DE LIVRAISON</h2>
                    <p style="color: var(--text-muted); font-size: 0.95rem;">Nous livrons uniquement dans un rayon de 1 km autour de La Plaine / Cours Ju.</p>
                    <button class="btn-main" onclick="document.getElementById('statusOverlay').style.display='none'" style="margin-top: 15px; background-color: var(--error-color); color: white;">Modifier l'adresse</button>
                </div>
            </div>
        </div>
        {% endif %}

        <!-- POPUP ERREUR STOCK -->
        {% if statut == "erreur_stock" %}
        <div class="modal-overlay" id="statusOverlay" style="display: flex;" onclick="document.getElementById('statusOverlay').style.display='none'">
            <div class="modal error-modal" onclick="event.stopPropagation()">
                <div class="error-screen">
                    <div class="error-icon">⚠️</div>
                    <h2>RUPTURE SOUDAINE</h2>
                    <p style="color: var(--text-muted); font-size: 0.95rem;">Quelqu'un a validé le dernier sachet juste avant vous. Modifiez votre panier.</p>
                    <button class="btn-main" onclick="document.getElementById('statusOverlay').style.display='none'" style="margin-top: 15px; background-color: var(--error-color); color: white;">Retour au menu</button>
                </div>
            </div>
        </div>
        {% endif %}

        <!-- SECTION FLEURS -->
        <div class="section-title">Fleurs</div>
        <div class="grid">
            <div class="card" onclick="openProductModal('Amnesia Haze', '💧 Culture : HIDROPÓNICO<br>📊 Taux CBD : ~17%')">
                <h3>Amnesia Haze</h3>
                <span class="culture-tag">Hidropónico</span>
                <div class="size-options">
                    <button class="size-btn" data-product="Amnesia Haze" data-size="2g" {% if stocks['Amnesia Haze']['2g'] <= 0 %}disabled{% endif %} onclick="toggleProduct(event, 'Amnesia Haze', '2g', 10)">{% if stocks['Amnesia Haze']['2g'] <= 0 %}Rupture{% else %}2g - 10€{% endif %}</button>
                    <button class="size-btn" data-product="Amnesia Haze" data-size="5g" {% if stocks['Amnesia Haze']['5g'] <= 0 %}disabled{% endif %} onclick="toggleProduct(event, 'Amnesia Haze', '5g', 20)">{% if stocks['Amnesia Haze']['5g'] <= 0 %}Rupture{% else %}5g - 20€{% endif %}</button>
                    <button class="size-btn" data-product="Amnesia Haze" data-size="10g" {% if stocks['Amnesia Haze']['10g'] <= 0 %}disabled{% endif %} onclick="toggleProduct(event, 'Amnesia Haze', '10g', 35)">{% if stocks['Amnesia Haze']['10g'] <= 0 %}Rupture{% else %}10g - 35€{% endif %}</button>
                </div>
            </div>

            <div class="card" onclick="openProductModal('Orange Bud', '☀️ Culture : GREENHOUSE<br>📊 Taux CBD : ~12%')">
                <h3>Orange Bud</h3>
                <span class="culture-tag">Greenhouse</span>
                <div class="size-options">
                    <button class="size-btn" data-product="Orange Bud" data-size="2g" {% if stocks['Orange Bud']['2g'] <= 0 %}disabled{% endif %} onclick="toggleProduct(event, 'Orange Bud', '2g', 12)">{% if stocks['Orange Bud']['2g'] <= 0 %}Rupture{% else %}2g - 12€{% endif %}</button>
                    <button class="size-btn" data-product="Orange Bud" data-size="5g" {% if stocks['Orange Bud']['5g'] <= 0 %}disabled{% endif %} onclick="toggleProduct(event, 'Orange Bud', '5g', 25)">{% if stocks['Orange Bud']['5g'] <= 0 %}Rupture{% else %}5g - 25€{% endif %}</button>
                    <button class="size-btn" data-product="Orange Bud" data-size="10g" {% if stocks['Orange Bud']['10g'] <= 0 %}disabled{% endif %} onclick="toggleProduct(event, 'Orange Bud', '10g', 45)">{% if stocks['Orange Bud']['10g'] <= 0 %}Rupture{% else %}10g - 45€{% endif %}</button>
                </div>
            </div>

            <div class="card" onclick="openProductModal('Cookie Kush', '🌿 Culture : INDOOR<br>📊 Taux CBD : ~15%')">
                <h3>Cookie Kush</h3>
                <span class="culture-tag">Indoor</span>
                <div class="size-options">
                    <button class="size-btn" data-product="Cookie Kush" data-size="2g" {% if stocks['Cookie Kush']['2g'] <= 0 %}disabled{% endif %} onclick="toggleProduct(event, 'Cookie Kush', '2g', 15)">{% if stocks['Cookie Kush']['2g'] <= 0 %}Rupture{% else %}2g - 15€{% endif %}</button>
                    <button class="size-btn" data-product="Cookie Kush" data-size="5g" {% if stocks['Cookie Kush']['5g'] <= 0 %}disabled{% endif %} onclick="toggleProduct(event, 'Cookie Kush', '5g', 30)">{% if stocks['Cookie Kush']['5g'] <= 0 %}Rupture{% else %}5g - 30€{% endif %}</button>
                    <button class="size-btn" data-product="Cookie Kush" data-size="10g" {% if stocks['Cookie Kush']['10g'] <= 0 %}disabled{% endif %} onclick="toggleProduct(event, 'Cookie Kush', '10g', 55)">{% if stocks['Cookie Kush']['10g'] <= 0 %}Rupture{% else %}10g - 55€{% endif %}</button>
                </div>
            </div>
        </div>

        <!-- SECTION RÉSINES -->
        <div class="section-title">Résines</div>
        <div class="grid">
            <div class="card" onclick="openProductModal('Skuff - Polen', '📍 Type : Dry Sift<br>📊 Taux CBD : ~25%')">
                <h3>Skuff - Polen</h3>
                <span class="culture-tag">Dry Sift</span>
                <div class="size-options">
                    <button class="size-btn" data-product="Skuff - Polen" data-size="2g" {% if stocks['Skuff - Polen']['2g'] <= 0 %}disabled{% endif %} onclick="toggleProduct(event, 'Skuff - Polen', '2g', 12)">{% if stocks['Skuff - Polen']['2g'] <= 0 %}Rupture{% else %}2g - 12€{% endif %}</button>
                    <button class="size-btn" data-product="Skuff - Polen" data-size="5g" {% if stocks['Skuff - Polen']['5g'] <= 0 %}disabled{% endif %} onclick="toggleProduct(event, 'Skuff - Polen', '5g', 25)">{% if stocks['Skuff - Polen']['5g'] <= 0 %}Rupture{% else %}5g - 25€{% endif %}</button>
                    <button class="size-btn" data-product="Skuff - Polen" data-size="10g" {% if stocks['Skuff - Polen']['10g'] <= 0 %}disabled{% endif %} onclick="toggleProduct(event, 'Skuff - Polen', '10g', 45)">{% if stocks['Skuff - Polen']['10g'] <= 0 %}Rupture{% else %}10g - 45€{% endif %}</button>
                </div>
            </div>
            
            <div class="card" onclick="openProductModal('Creamy Piatella', '❄️ Bubble Hash Ice-O-Lator<br>📊 Taux CBD : 70%')">
                <h3>Creamy Piatella</h3>
                <span class="culture-tag">Premium Cold Cure</span>
                <div class="size-options">
                    <button class="size-btn" data-product="Creamy Piatella" data-size="2g" {% if stocks['Creamy Piatella']['2g'] <= 0 %}disabled{% endif %} onclick="toggleProduct(event, 'Creamy Piatella', '2g', 20)">{% if stocks['Creamy Piatella']['2g'] <= 0 %}Rupture{% else %}2g - 20€{% endif %}</button>
                    <button class="size-btn" data-product="Creamy Piatella" data-size="5g" {% if stocks['Creamy Piatella']['5g'] <= 0 %}disabled{% endif %} onclick="toggleProduct(event, 'Creamy Piatella', '5g', 45)">{% if stocks['Creamy Piatella']['5g'] <= 0 %}Rupture{% else %}5g - 45€{% endif %}</button>
                    <button class="size-btn" data-product="Creamy Piatella" data-size="10g" {% if stocks['Creamy Piatella']['10g'] <= 0 %}disabled{% endif %} onclick="toggleProduct(event, 'Creamy Piatella', '10g', 80)">{% if stocks['Creamy Piatella']['10g'] <= 0 %}Rupture{% else %}10g - 80€{% endif %}</button>
                </div>
            </div>
        </div>

        <div class="spacer"></div>

        <div class="sticky-footer">
            <div class="summary-layout">
                <div class="summary-text" id="footerSummary">Aucun produit sélectionné</div>
                <button class="btn-clear" id="btnClearPanier" onclick="viderPanier()" style="display: none;">Vider</button>
            </div>
            <button class="btn-main" id="confirmOrderBtn" onclick="openCheckoutModal()" disabled>Confirmer la commande</button>
        </div>

        <div class="modal-overlay" id="productModalOverlay" onclick="closeModals()">
            <div class="modal" onclick="event.stopPropagation()">
                <h2 id="modalProductName">Nom du Produit</h2>
                <div class="modal-details" id="modalProductDesc">Description...</div>
                <button class="btn-main" onclick="hideProductModal()">Retour</button>
            </div>
        </div>

        <div class="modal-overlay" id="checkoutModalOverlay" onclick="closeModals()">
            <div class="modal" onclick="event.stopPropagation()">
                <h2 id="checkoutModalTitle">Votre Commande</h2>
                <form method="POST">
                    <input type="hidden" id="formCommandeText" name="commande" value="">
                    <input type="hidden" id="formItemsRaw" name="items_raw" value="">
                    
                    <label for="prenom">Prénom</label>
                    <input type="text" id="prenom" name="prenom" placeholder="Lucas" required>

                    <label for="telephone">Téléphone</label>
                    <input type="tel" id="telephone" name="telephone" placeholder="0612345678" required>

                    <label for="adresse">Adresse ou Bar à Marseille</label>
                    <input type="text" id="adresse" name="adresse" placeholder="Ex: 10 Rue des trois mages" required>

                    <button type="submit" class="btn-main" style="margin-top: 20px;">Vérifier & Commander</button>
                </form>
            </div>
        </div>

        <script>
            let panier = {};

            function toggleProduct(event, name, size, price) {
                event.stopPropagation();
                const key = `${name} (${size})`;
                
                if (panier[key]) {
                    delete panier[key];
                    event.target.classList.remove('active');
                } else {
                    document.querySelectorAll(`.size-btn[data-product="${name}"]`).forEach(btn => {
                        btn.classList.remove('active');
                        delete panier[`${name} (${btn.getAttribute('data-size')})`];
                    });
                    panier[key] = { price: price, product: name, size: size };
                    event.target.classList.add('active');
                }
                updateFooter();
            }

            function viderPanier() {
                panier = {};
                document.querySelectorAll('.size-btn').forEach(btn => btn.classList.remove('active'));
                updateFooter();
            }

            function updateFooter() {
                const keys = Object.keys(panier);
                const mainBtn = document.getElementById('confirmOrderBtn');
                const clearBtn = document.getElementById('btnClearPanier');
                
                if (keys.length === 0) {
                    document.getElementById('footerSummary').innerHTML = "Aucun produit sélectionné";
                    mainBtn.setAttribute('disabled', 'true');
                    clearBtn.style.display = 'none';
                    return;
                }
                let total = 0, itemsText = [];
                for (let item in panier) { 
                    total += panier[item].price; 
                    itemsText.push(`${item} <span>[${panier[item].price}€]</span>`); 
                }
                document.getElementById('footerSummary').innerHTML = `Panier : ${itemsText.join(' + ')} — Total : <span>${total}€</span>`;
                mainBtn.removeAttribute('disabled');
                clearBtn.style.display = 'inline-block';
            }

            function openProductModal(name, desc) {
                document.getElementById('modalProductName').innerText = name;
                document.getElementById('modalProductDesc').innerHTML = desc;
                document.getElementById('productModalOverlay').style.display = 'flex';
            }

            function hideProductModal() { document.getElementById('productModalOverlay').style.display = 'none'; }

            function openCheckoutModal() {
                hideProductModal();
                let total = 0, itemsText = [], rawItems = [];
                for (let item in panier) { 
                    total += panier[item].price; 
                    itemsText.push(`${item} [${panier[item].price}€]`);
                    rawItems.push(`${panier[item].product}:${panier[item].size}`);
                }
                document.getElementById('checkoutModalTitle').innerText = `Total : ${total}€`;
                document.getElementById('formCommandeText').value = itemsText.join(' / ') + ` (Total: ${total}€)`;
                document.getElementById('formItemsRaw').value = rawItems.join(',');
                document.getElementById('checkoutModalOverlay').style.display = 'flex';
            }

            function closeModals() {
                document.getElementById('productModalOverlay').style.display = 'none';
                document.getElementById('checkoutModalOverlay').style.display = 'none';
            }
        </script>
    </body>
    </html>
    """
    return HTML_FORM

@app.route("/", methods=["GET", "POST"])
def home():
    statut = None
    if request.method == "POST":
        prenom = request.form.get("prenom")
        telephone = request.form.get("telephone")
        adresse = request.form.get("adresse")
        choix_commande = request.form.get("commande")
        items_raw = request.form.get("items_raw")

        liste_items = items_raw.split(",") if items_raw else []
        erreur_stock_detectee = False
        
        for item in liste_items:
            if ":" in item:
                prod, taille = item.split(":")
                if STOCKS.get(prod, {}).get(taille, 0) <= 0:
                    erreur_stock_detectee = True
                    break

        if erreur_stock_detectee:
            statut = "erreur_stock"
        else:
            adresse_recherche = f"{adresse} Marseille"
            url_api = "https://api-adresse.data.gouv.fr/search/"
            params = {"q": adresse_recherche, "limit": 1}
            
            try:
                r = requests.get(url_api, params=params, timeout=5).json()
                if r.get("features"):
                    best_match = r["features"][0]
                    coords = best_match["geometry"]["coordinates"]
                    client_lon, client_lat = coords[0], coords[1]
                    nom_trouve = best_match["properties"]["label"]
                    
                    distance = calculer_distance(CENTRE_LAT, CENTRE_LON, client_lat, client_lon)

                    if distance <= RAYON_MAX_KM:
                        # 1. Baisse de stock immédiate
                        total_prix = 0
                        items_vendus = []
                        for item in liste_items:
                            if ":" in item:
                                prod, taille = item.split(":")
                                STOCKS[prod][taille] -= 1
                                items_vendus.append(f"{prod} ({taille})")

                        if "Total: " in choix_commande:
                            try:
                                total_prix = int(choix_commande.split("Total: ")[1].replace("€)", ""))
                            except:
                                total_prix = 0

                        # 2. Enregistrement comptable anonyme
                        enregistrer_vente_anonyme(" + ".join(items_vendus), total_prix)

                        # 3. Génération du lien de navigation Google Maps direct depuis le Cours Ju
                        lien_itineraire = f"https://www.google.com/maps/dir/{CENTRE_LAT},{CENTRE_LON}/{client_lat},{client_lon}"

                        # 4. Notification Telegram avec Itinéraire Intégré
                        texte_telegram = (
                            f"🔔 NOUVELLE COMMANDE REÇUE !\n\n"
                            f"👤 Prénom : {prenom}\n"
                            f"📞 Tél : {telephone}\n"
                            f"📍 Saisi par le client : {adresse}\n"
                            f"🗺️ Localisé par GPS : {nom_trouve}\n"
                            f"📏 Distance : {distance:.2f} km du Cours Ju\n"
                            f"🧭 ITINÉRAIRE DIRECT : {lien_itineraire}\n\n"
                            f"📦 Commande :\n{choix_commande}"
                        )
                        url_tele = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
                        requests.post(url_tele, json={"chat_id": CHAT_ID, "text": texte_telegram})
                        statut = "succes"
                    else:
                        statut = "hors_zone"
                else:
                    statut = "hors_zone"
            except Exception as e:
                print(f"Erreur technique: {e}")
                statut = "succes"

    return render_template_string(generer_html(statut), stocks=STOCKS, statut=statut)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
