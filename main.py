import os
import requests
from flask import Flask, render_template_string, request
import math
from datetime import datetime
import csv

app = Flask(__name__)

# Configuration Telegram
TOKEN = "8929246651:AAFSqQ_k4Wi5GIOl3a773czmfcenO_jWrAc"
CHAT_ID = "6141877001"

# Coordonnées Cours Ju / La Plaine
CENTRE_LAT = 43.2938
CENTRE_LON = 5.3854
RAYON_MAX_KM = 1.0

FICHIER_COMPTA = "compta.csv"

# 📦 STOCKS & INFOS PRODUITS (Avec descriptions complètes, termes corrigés et images)
STOCKS = {
    "Amnesia Haze": {
        "stocks": {"2g": 10, "5g": 5, "10g": 3},
        "culture": "Hydroponique",
        "details": "💧 Culture : HYDROPONIQUE<br>📊 Taux CBD : ~17%<br>🧠 Effets : Énergisant, clarté mentale, idéal pour la journée.<br>🍋 Arômes : Notes prononcées de citron et de pin sauvage.",
        "image": "https://images.unsplash.com/photo-1603909223429-69bb7101f420?w=500&auto=format&fit=crop&q=60"
    },
    "Orange Bud": {
        "stocks": {"2g": 8, "5g": 4, "10g": 2},
        "culture": "Greenhouse",
        "details": "☀️ Culture : GREENHOUSE<br>📊 Taux CBD : ~12%<br>🧘 Effets : Relaxation douce, anti-stress naturel.<br>🍊 Arômes : Parfum d'agrumes sucrés et d'orange mûre.",
        "image": "https://images.unsplash.com/photo-1536625803734-e4304899580b?w=500&auto=format&fit=crop&q=60"
    },
    "Cookie Kush": {
        "stocks": {"2g": 12, "5g": 6, "10g": 4},
        "culture": "Indoor",
        "details": "🌿 Culture : INDOOR (Haut de gamme)<br>📊 Taux CBD : ~15%<br>💤 Effets : Apaisement profond, idéal pour la fin de soirée.<br>🍪 Arômes : Saveur gourmande de biscuit et de terre chocolatée.",
        "image": "https://images.unsplash.com/photo-1568243161214-9728877bc9d7?w=500&auto=format&fit=crop&q=60"
    },
    "Skuff - Polen": {
        "stocks": {"2g": 15, "5g": 7, "10g": 3},
        "culture": "Dry Sift",
        "details": "📍 Type : Dry Sift traditionnel<br>📊 Taux CBD : ~25%<br>🍁 Texture : Sablonneuse et malléable.<br>✨ Effets : Relaxation intense et durable.",
        "image": "https://images.unsplash.com/photo-1556928045-16f7f2319f3c?w=500&auto=format&fit=crop&q=60"
    },
    "Creamy Piatella": {
        "stocks": {"2g": 5, "5g": 3, "10g": 1},
        "culture": "Premium Cold Cure",
        "details": "❄️ Bubble Hash Ice-O-Lator<br>📊 Taux CBD : ~70% (Ultra Concentré)<br>🧪 Process : Affinage à froid (Cold Cure).<br>🍯 Texture : Crémeuse comme du beurre, pureté absolue.",
        "image": "https://images.unsplash.com/photo-1611075883654-e0b04fb85dc4?w=500&auto=format&fit=crop&q=60"
    }
}

def calculer_distance(lat1, lon1, lat2, lon2):
    R = 6371.0
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)
    a = math.sin(delta_phi / 2.0)**2 + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2.0)**2
    return R * (2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a)))

def enregistrer_vente_anonyme(liste_items, total_prix):
    try:
        fichier_existe = os.path.exists(FICHIER_COMPTA)
        with open(FICHIER_COMPTA, mode="a", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            if not fichier_existe:
                writer.writerow(["Date et Heure", "Produits", "Total"])
            date_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            writer.writerow([date_str, liste_items, f"{total_prix}€"])
    except Exception as e:
        print(f"Erreur compta: {e}")

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
            
            .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px; width: 100%; max-width: 800px; margin-bottom: 20px; }
            .card { background: var(--card-bg); border: 1px solid #2c2c2e; border-radius: 14px; overflow: hidden; cursor: pointer; transition: transform 0.2s, border-color 0.2s; position: relative; display: flex; flex-direction: column; }
            .card:hover { transform: translateY(-2px); border-color: #48484a; }
            
            .card-img { width: 100%; height: 150px; object-fit: cover; background: #2c2c2e; }
            .card-content { padding: 15px; text-align: center; flex-grow: 1; display: flex; flex-direction: column; justify-content: space-between; }
            
            .card h3 { margin: 0 0 5px 0; font-size: 1.25rem; }
            .card .culture-tag { font-size: 0.75rem; color: var(--accent-color); text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 10px; display: block; }

            .size-options { display: flex; gap: 6px; justify-content: center; margin-top: 10px; flex-wrap: wrap; }
            .size-btn { background: #2c2c2e; border: none; color: var(--text-main); padding: 8px 12px; border-radius: 6px; font-size: 0.8rem; font-weight: bold; cursor: pointer; transition: background 0.2s; }
            .size-btn:hover { background: #3a3a3c; }
            .size-btn.active { background: var(--accent-color); color: #000; }
            .size-btn:disabled { background: #1c1c1e; color: #48484a; border: 1px dashed #3a3a3c; cursor: not-allowed; text-decoration: line-through; }
            
            .sticky-footer { position: fixed; bottom: 0; left: 0; width: 100%; background: rgba(18, 18, 18, 0.9); backdrop-filter: blur(10px); border-top: 1px solid #2c2c2e; padding: 15px; box-sizing: border-box; display: flex; flex-direction: column; align-items: center; z-index: 10; }
            .summary-layout { display: flex; align-items: center; justify-content: center; gap: 15px; margin-bottom: 10px; flex-wrap: wrap; }
            .summary-text { font-size: 0.95rem; color: var(--text-muted); text-align: center; max-width: 500px; margin: 0; }
            .summary-text span { color: var(--accent-color); font-weight: bold; }
            .btn-clear { background: none; border: 1px solid #3a3a3c; color: var(--text-muted); padding: 4px 10px; border-radius: 6px; font-size: 0.8rem; cursor: pointer; }
            .btn-clear:hover { background: #ff3b30; color: white; border-color: #ff3b30; }

            .btn-main { background: var(--accent-color); color: #000; border: none; padding: 12px 30px; font-size: 1rem; font-weight: bold; border-radius: 8px; cursor: pointer; width: 100%; max-width: 400px; text-transform: uppercase; }
            .btn-main:disabled { background: #2c2c2e; color: var(--text-muted); cursor: not-allowed; }

            .modal-overlay { position: fixed; top:0; left:0; width:100%; height:100%; background: rgba(0,0,0,0.85); backdrop-filter: blur(5px); display: none; justify-content: center; align-items: center; z-index: 100; }
            .modal { background: var(--card-bg); border: 2px solid var(--accent-color); border-radius: 16px; padding: 25px; max-width: 380px; width: 90%; position: relative; }
            .modal.error-modal { border-color: var(--error-color); }
            .modal h2 { margin-top: 0; color: var(--accent-color); font-size: 1.4rem; text-align: center; }
            .modal.error-modal h2 { color: var(--error-color); }
            .modal-details { font-size: 0.95rem; color: var(--text-main); line-height: 1.6; margin-bottom: 20px; background: rgba(255,255,255,0.03); padding: 15px; border-radius: 8px; border: 1px solid #2c2c2e; }
            
            label { display: block; margin: 12px 0 4px; font-size: 0.85rem; color: var(--text-muted); text-transform: uppercase; font-weight: bold; }
            input { width: 100%; padding: 12px; background: #2c2c2e; border: 1px solid #3a3a3c; border-radius: 8px; color: white; box-sizing: border-box; }
            input:focus { border-color: var(--accent-color); outline: none; }
            
            .spacer { height: 140px; }
        </style>
    </head>
    <body>

        <!-- 🔞 BARRIÈRE D'ÂGE OBLIGATOIRE -->
        <div class="modal-overlay" id="ageGateOverlay" style="display: flex; z-index: 9999;">
            <div class="modal" style="text-align: center;">
                <h2>🔞 VÉRIFICATION D'ÂGE</h2>
                <p style="color: var(--text-muted); font-size: 0.95rem; margin-bottom: 25px;">
                    Ce site propose des produits dérivés du CBD réservés aux personnes majeures. Veuillez confirmer votre majorité pour accéder au menu.
                </p>
                <div style="display: flex; gap: 15px; justify-content: center;">
                    <button class="btn-main" onclick="validerAge()" style="width: 130px;">J'AI +18 ANS</button>
                    <button class="btn-main" onclick="refuserAge()" style="width: 130px; background-color: var(--error-color); color: white;">-18 ANS</button>
                </div>
            </div>
        </div>

        <div class="header">
            <h1>MARSEILLE CBD</h1>
            <p>Service de livraison privé & expéditions</p>
            <div class="badge">📍 Zone : La Plaine / Cours Ju (<1km)</div>
        </div>

        <!-- POPUPS DE STATUT -->
        {% if statut == "succes" %}
        <div class="modal-overlay" id="statusOverlay" style="display: flex;" onclick="document.getElementById('statusOverlay').style.display='none'">
            <div class="modal" onclick="event.stopPropagation()">
                <div style="text-align: center;">
                    <div style="font-size: 40px; margin-bottom: 10px;">✅</div>
                    <h2>COMMANDE VALIDÉE !</h2>
                    <p style="color: var(--text-muted); font-size: 0.95rem;">Votre commande a bien été transmise.</p>
                    <p style="color: var(--accent-color); font-weight: bold;">⏱️ Temps estimé : 20 à 45 min selon le rush.</p>
                    <button class="btn-main" onclick="document.getElementById('statusOverlay').style.display='none'" style="margin-top: 15px;">Fermer</button>
                </div>
            </div>
        </div>
        {% endif %}

        {% if statut == "hors_zone" %}
        <div class="modal-overlay" id="statusOverlay" style="display: flex;" onclick="document.getElementById('statusOverlay').style.display='none'">
            <div class="modal error-modal" onclick="event.stopPropagation()">
                <div style="text-align: center;">
                    <div style="font-size: 40px; margin-bottom: 10px;">❌</div>
                    <h2>HORS ZONE</h2>
                    <p style="color: var(--text-muted); font-size: 0.95rem;">Nous livrons uniquement dans un rayon de 1 km autour de La Plaine / Cours Ju.</p>
                    <button class="btn-main" onclick="document.getElementById('statusOverlay').style.display='none'" style="margin-top: 15px; background-color: var(--error-color); color: white;">Modifier l'adresse</button>
                </div>
            </div>
        </div>
        {% endif %}

        {% if statut == "erreur_stock" %}
        <div class="modal-overlay" id="statusOverlay" style="display: flex;" onclick="document.getElementById('statusOverlay').style.display='none'">
            <div class="modal error-modal" onclick="event.stopPropagation()">
                <div style="text-align: center;">
                    <div style="font-size: 40px; margin-bottom: 10px;">⚠️</div>
                    <h2>RUPTURE DE STOCK</h2>
                    <p style="color: var(--text-muted); font-size: 0.95rem;">Un autre client a validé ce produit juste avant vous. Modifiez votre panier.</p>
                    <button class="btn-main" onclick="document.getElementById('statusOverlay').style.display='none'" style="margin-top: 15px; background-color: var(--error-color); color: white;">Retour au menu</button>
                </div>
            </div>
        </div>
        {% endif %}

        <!-- SECTION FLEURS -->
        <div class="section-title">Fleurs</div>
        <div class="grid">
            {% for name, info in stocks.items() if info.culture in ['Hydroponique', 'Greenhouse', 'Indoor'] %}
            <div class="card" onclick="openProductModal('{{ name }}', `{{ info.details|safe }}`)">
                <img src="{{ info.image }}" class="card-img" alt="{{ name }}">
                <div class="card-content">
                    <div>
                        <h3>{{ name }}</h3>
                        <span class="culture-tag">{{ info.culture }}</span>
                    </div>
                    <div class="size-options">
                        <button class="size-btn" data-product="{{ name }}" data-size="2g" {% if info.stocks['2g'] <= 0 %}disabled{% endif %} onclick="toggleProduct(event, '{{ name }}', '2g', 10 if name=='Amnesia Haze' else (12 if name=='Orange Bud' else 15))">{% if info.stocks['2g'] <= 0 %}Rupture{% else %}2g - {% if name=='Amnesia Haze' %}10€{% elif name=='Orange Bud' %}12€{% else %}15€{% endif %}{% endif %}</button>
                        <button class="size-btn" data-product="{{ name }}" data-size="5g" {% if info.stocks['5g'] <= 0 %}disabled{% endif %} onclick="toggleProduct(event, '{{ name }}', '5g', 20 if name=='Amnesia Haze' else (25 if name=='Orange Bud' else 30))">{% if info.stocks['5g'] <= 0 %}Rupture{% else %}5g - {% if name=='Amnesia Haze' %}20€{% elif name=='Orange Bud' %}25€{% else %}30€{% endif %}{% endif %}</button>
                        <button class="size-btn" data-product="{{ name }}" data-size="10g" {% if info.stocks['10g'] <= 0 %}disabled{% endif %} onclick="toggleProduct(event, '{{ name }}', '10g', 35 if name=='Amnesia Haze' else (45 if name=='Orange Bud' else 55))">{% if info.stocks['10g'] <= 0 %}Rupture{% else %}10g - {% if name=='Amnesia Haze' %}35€{% elif name=='Orange Bud' %}45€{% else %}55€{% endif %}{% endif %}</button>
                    </div>
                </div>
            </div>
            {% endfor %}
        </div>

        <!-- SECTION RÉSINES -->
        <div class="section-title">Résines</div>
        <div class="grid">
            {% for name, info in stocks.items() if info.culture in ['Dry Sift', 'Premium Cold Cure'] %}
            <div class="card" onclick="openProductModal('{{ name }}', `{{ info.details|safe }}`)">
                <img src="{{ info.image }}" class="card-img" alt="{{ name }}">
                <div class="card-content">
                    <div>
                        <h3>{{ name }}</h3>
                        <span class="culture-tag">{{ info.culture }}</span>
                    </div>
                    <div class="size-options">
                        <button class="size-btn" data-product="{{ name }}" data-size="2g" {% if info.stocks['2g'] <= 0 %}disabled{% endif %} onclick="toggleProduct(event, '{{ name }}', '2g', 12 if name=='Skuff - Polen' else 20)">{% if info.stocks['2g'] <= 0 %}Rupture{% else %}2g - {% if name=='Skuff - Polen' %}12€{% else %}20€{% endif %}{% endif %}</button>
                        <button class="size-btn" data-product="{{ name }}" data-size="5g" {% if info.stocks['5g'] <= 0 %}disabled{% endif %} onclick="toggleProduct(event, '{{ name }}', '5g', 25 if name=='Skuff - Polen' else 45)">{% if info.stocks['5g'] <= 0 %}Rupture{% else %}5g - {% if name=='Skuff - Polen' %}25€{% else %}45€{% endif %}{% endif %}</button>
                        <button class="size-btn" data-product="{{ name }}" data-size="10g" {% if info.stocks['10g'] <= 0 %}disabled{% endif %} onclick="toggleProduct(event, '{{ name }}', '10g', 45 if name=='Skuff - Polen' else 80)">{% if info.stocks['10g'] <= 0 %}Rupture{% else %}10g - {% if name=='Skuff - Polen' %}45€{% else %}80€{% endif %}{% endif %}</button>
                    </div>
                </div>
            </div>
            {% endfor %}
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
                <h2 id="modalProductName">Nom</h2>
                <div class="modal-details" id="modalProductDesc">Détails...</div>
                <button class="btn-main" onclick="closeModals()">Retour</button>
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

            // Contrôle de la barrière d'âge
            window.addEventListener('DOMContentLoaded', () => {
                if (localStorage.getItem('majeur') === 'true') {
                    document.getElementById('ageGateOverlay').style.display = 'none';
                }
            });
            function validerAge() {
                localStorage.setItem('majeur', 'true');
                document.getElementById('ageGateOverlay').style.display = 'none';
            }
            function refuserAge() { window.location.href = "https://www.google.fr"; }

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

            function openCheckoutModal() {
                document.getElementById('productModalOverlay').style.display = 'none';
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
                if STOCKS.get(prod, {}).get("stocks", {}).get(taille, 0) <= 0:
                    erreur_stock_detectee = True
                    break

        if erreur_stock_detectee:
            statut = "erreur_stock"
        else:
            adresse_recherche = f"{adresse} Marseille"
            url_api = "https://api-adresse.data.gouv.fr/search/"
            try:
                r = requests.get(url_api, params={"q": adresse_recherche, "limit": 1}, timeout=5).json()
                if r.get("features"):
                    best_match = r["features"][0]
                    coords = best_match["geometry"]["coordinates"]
                    client_lon, client_lat = coords[0], coords[1]
                    nom_trouve = best_match["properties"]["label"]
                    
                    distance = calculer_distance(CENTRE_LAT, CENTRE_LON, client_lat, client_lon)

                    if distance <= RAYON_MAX_KM:
                        total_prix = 0
                        items_vendus = []
                        for item in liste_items:
                            if ":" in item:
                                prod, taille = item.split(":")
                                STOCKS[prod]["stocks"][taille] -= 1
                                items_vendus.append(f"{prod} ({taille})")

                        if "Total: " in choix_commande:
                            try: total_prix = int(choix_commande.split("Total: ")[1].replace("€)", ""))
                            except: total_prix = 0

                        # Enregistrement compta locale CSV
                        enregistrer_vente_anonyme(" + ".join(items_vendus), total_prix)

                        lien_itineraire = f"https://www.google.com/maps/dir/{CENTRE_LAT},{CENTRE_LON}/{client_lat},{client_lon}"

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
                        requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage", json={"chat_id": CHAT_ID, "text": texte_telegram})
                        statut = "succes"
                    else: statut = "hors_zone"
                else: statut = "hors_zone"
            except: statut = "succes"

    return render_template_string(generer_html(statut), stocks=STOCKS, statut=statut)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
