import os
import requests
from flask import Flask, render_template_string, request, send_from_directory
import math
from datetime import datetime
import csv
import json

app = Flask(__name__)

# Configuration Telegram
TOKEN = "8929246651:AAFSqQ_k4Wi5GIOl3a773czmfcenO_jWrAc"
CHAT_ID = "6141877001"

# Coordonnées Cours Ju / La Plaine
CENTRE_LAT = 43.2938
CENTRE_LON = 5.3854
RAYON_MAX_KM = 1.0

FICHIER_COMPTA = "compta.csv"

# 📦 STOCKS, INFOS & TRADUCTIONS DES VARIÉTÉS
STOCKS = {
    "Amnesia Haze": {
        "stocks": {"2g": 10, "5g": 5, "10g": 3},
        "culture": "Hydroponique",
        "image": "https://images.unsplash.com/photo-1603909223429-69bb7101f420?w=500&auto=format&fit=crop&q=60",
        "details": {
            "fr": "💧 Culture : HYDROPONIQUE<br>📊 Taux CBD : ~17%<br>🧠 Effets : Énergisant, clarté mentale, idéal pour la journée.<br>🍋 Arômes : Notes prononcées de citron et de pin sauvage.",
            "en": "💧 Grow: HYDROPONIC<br>📊 CBD Rate: ~17%<br>🧠 Effects: Energizing, mental clarity, ideal for daytime.<br>🍋 Flavors: Sharp notes of lemon and wild pine.",
            "es": "💧 Cultivo: HIDROPÓNICO<br>📊 Tasa CBD: ~17%<br>🧠 Efectos: Energizante, claridad mental, ideal para el día.<br>🍋 Aromas: Notas pronunciadas de limón y pino silvestre.",
            "it": "💧 Coltivazione: IDROPONICA<br>📊 Tasso CBD: ~17%<br>🧠 Effetti: Energizzante, chiarezza mentale, ideale per il giorno.<br>🍋 Aromi: Note pronunciate di limone e pino selvatico.",
            "de": "💧 Anbau: HYDROPONISCH<br>📊 CBD-Anteil: ~17%<br>🧠 Wirkung: Energetisierend, geistige Klarheit, ideal für den Tag.<br>🍋 Aromen: Ausgeprägte Zitronen- und Wildkiefernoten."
        }
    },
    "Orange Bud": {
        "stocks": {"2g": 8, "5g": 4, "10g": 2},
        "culture": "Greenhouse",
        "image": "https://images.unsplash.com/photo-1536625803734-e4304899580b?w=500&auto=format&fit=crop&q=60",
        "details": {
            "fr": "☀️ Culture : GREENHOUSE<br>📊 Taux CBD : ~12%<br>🧘 Effets : Relaxation douce, anti-stress naturel.<br>🍊 Arômes : Parfum d'agrumes sucrés et d'orange mûre.",
            "en": "☀️ Grow: GREENHOUSE<br>📊 CBD Rate: ~12%<br>🧘 Effects: Gentle relaxation, natural stress relief.<br>🍊 Flavors: Sweet citrus and ripe orange scent.",
            "es": "☀️ Cultivo: GREENHOUSE<br>📊 Tasa CBD: ~12%<br>🧘 Efectos: Relajación suave, alivio natural del estrés.<br>🍊 Aromas: Aroma a cítricos dulces y naranja madura.",
            "it": "☀️ Coltivazione: GREENHOUSE<br>📊 Tasso CBD: ~12%<br>🧘 Effetti: Rilassamento delicato, antistress naturale.<br>🍊 Aromi: Profumo di agrumi dolci e arancia matura.",
            "de": "☀️ Anbau: GEWÄCHSHAUS<br>📊 CBD-Anteil: ~12%<br>🧘 Wirkung: Sanfte Entspannung, natürlicher Stressabbau.<br>🍊 Aromen: Süßer Zitrus- und reifer Orangenduft."
        }
    },
    "Cookie Kush": {
        "stocks": {"2g": 12, "5g": 6, "10g": 4},
        "culture": "Indoor",
        "image": "https://images.unsplash.com/photo-1568243161214-9728877bc9d7?w=500&auto=format&fit=crop&q=60",
        "details": {
            "fr": "🌿 Culture : INDOOR (Haut de gamme)<br>📊 Taux CBD : ~15%<br>💤 Effets : Apaisement profond, idéal pour la fin de soirée.<br>🍪 Arômes : Saveur gourmande de biscuit et de terre chocolatée.",
            "en": "🌿 Grow: INDOOR (Premium)<br>📊 CBD Rate: ~15%<br>💤 Effects: Deep soothing, ideal for late evening.<br>🍪 Flavors: Gourmet biscuit and chocolatey earth taste.",
            "es": "🌿 Cultivo: INTERIOR (Premium)<br>📊 Tasa CBD: ~15%<br>💤 Efectos: Calmante profundo, ideal para el final de la noche.<br>🍪 Aromas: Sabor gourmet a galleta y tierra achocolatada.",
            "it": "🌿 Coltivazione: INDOOR (Premium)<br>📊 Tasso CBD: ~15%<br>💤 Effetti: Profondo sollievo, ideale per la tarda serata.<br>🍪 Aromi: Gusto goloso di biscotto e terra cioccolatosa.",
            "de": "🌿 Anbau: INDOOR (Premium)<br>📊 CBD-Anteil: ~15%<br>💤 Wirkung: Tiefe Beruhigung, ideal für den späten Abend.<br>🍪 Aromen: Feiner Keksgeschmack und schokoladige Erde."
        }
    },
    "Skuff - Polen": {
        "stocks": {"2g": 15, "5g": 7, "10g": 3},
        "culture": "Dry Sift",
        "image": "https://images.unsplash.com/photo-1556928045-16f7f2319f3c?w=500&auto=format&fit=crop&q=60",
        "details": {
            "fr": "📍 Type : Dry Sift traditionnel<br>📊 Taux CBD : ~25%<br>🍁 Texture : Sablonneuse et malléable.<br>✨ Effets : Relaxation intense et durable.",
            "en": "📍 Type: Traditional Dry Sift<br>📊 CBD Rate: ~25%<br>🍁 Texture: Sandy and malleable.<br>✨ Effects: Intense and long-lasting relaxation.",
            "es": "📍 Tipo: Dry Sift tradicional<br>📊 Tasa CBD: ~25%<br>🍁 Textura: Arenosa y maleable.<br>✨ Efectos: Relajación intensa y duradera.",
            "it": "📍 Tipo: Dry Sift tradizionale<br>📊 Tasso CBD: ~25%<br>🍁 Texture: Sabbiosa e malleabile.<br>✨ Effetti: Rilassamento intenso e duraturo.",
            "de": "📍 Typ: Traditionelles Dry Sift<br>📊 CBD-Anteil: ~25%<br>🍁 Textur: Sandig und formbar.<br>✨ Wirkung: Intensive und lang anhaltende Entspannung."
        }
    },
    "Creamy Piatella": {
        "stocks": {"2g": 5, "5g": 3, "10g": 1},
        "culture": "Premium Cold Cure",
        "image": "https://images.unsplash.com/photo-1611075883654-e0b04fb85dc4?w=500&auto=format&fit=crop&q=60",
        "details": {
            "fr": "❄️ Bubble Hash Ice-O-Lator<br>📊 Taux CBD : ~70% (Ultra Concentré)<br>🧪 Process : Affinage à froid (Cold Cure).<br>🍯 Texture : Crémeuse comme du beurre, pureté absolue.",
            "en": "❄️ Bubble Hash Ice-O-Lator<br>📊 CBD Rate: ~70% (Ultra Concentrated)<br>🧪 Process: Cold Cure ripening.<br>🍯 Texture: Creamy like butter, absolute purity.",
            "es": "❄️ Bubble Hash Ice-O-Lator<br>📊 Tasa CBD: ~70% (Ultra Concentrado)<br>🧪 Proceso: Maduración en frío (Cold Cure).<br>🍯 Textura: Cremosa como la mantequilla, pureza absoluta.",
            "it": "❄️ Bubble Hash Ice-O-Lator<br>📊 Tasso CBD: ~70% (Ultra Concentrato)<br>🧪 Processo: Maturazione a freddo (Cold Cure).<br>🍯 Texture: Cremosa come il burro, purezza assoluta.",
            "de": "❄️ Bubble Hash Ice-O-Lator<br>📊 CBD-Anteil: ~70% (Ultra-konzentriert)<br>🧪 Prozess: Kalte Reifung (Cold Cure).<br>🍯 Textur: Cremig wie Butter, absolute Reinheit."
        }
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
        <title>NATIVE MJ</title>
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
            
            .lang-selector {
                position: absolute;
                top: 20px;
                right: 20px;
                display: flex;
                gap: 8px;
                background: var(--card-bg);
                padding: 6px 10px;
                border-radius: 20px;
                border: 1px solid #2c2c2e;
                z-index: 100;
            }
            .lang-btn {
                font-size: 1.2rem;
                cursor: pointer;
                transition: transform 0.2s;
                background: none;
                border: none;
                padding: 0;
            }
            .lang-btn:hover { transform: scale(1.2); }
            .lang-btn.active { border-bottom: 2px solid var(--accent-color); }

            .header { text-align: center; margin-bottom: 30px; position: relative; width: 100%; max-width: 800px; display: flex; flex-direction: column; align-items: center; }
            .logo-img { width: 120px; height: auto; margin-top: 20px; margin-bottom: 10px; }
            .header h1 { font-size: 2.2rem; letter-spacing: 2px; margin: 0 0 5px 0; font-weight: bold; }
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

            .size-options { display: flex; flex-direction: column; gap: 8px; margin-top: 10px; }
            .size-row { display: flex; justify-content: space-between; align-items: center; background: #2c2c2e; padding: 6px 10px; border-radius: 8px; }
            .size-label { font-size: 0.85rem; font-weight: bold; }
            
            .qty-controls { display: flex; align-items: center; gap: 8px; }
            .qty-btn { background: #3a3a3c; border: none; color: white; width: 26px; height: 26px; border-radius: 6px; font-weight: bold; cursor: pointer; display: flex; align-items: center; justify-content: center; font-size: 1rem; }
            .qty-btn:hover { background: #48484a; }
            .qty-btn:disabled { background: #1c1c1e; color: #48484a; cursor: not-allowed; }
            .qty-val { font-size: 0.9rem; font-weight: bold; min-width: 14px; text-align: center; }
            .qty-val.active { color: var(--accent-color); }
            
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
            
            .spacer { height: 160px; }
        </style>
    </head>
    <body>

        <div class="modal-overlay" id="ageGateOverlay" style="display: flex; z-index: 9999;">
            <div class="modal" style="text-align: center;">
                <h2 data-trans="age_title">🔞 VÉRIFICATION D'ÂGE</h2>
                <p style="color: var(--text-muted); font-size: 0.95rem; margin-bottom: 25px;" data-trans="age_desc">
                    Ce site propose des produits dérivés du CBD réservés aux personnes majeures. Veuillez confirmer votre majorité pour accéder au menu.
                </p>
                <div style="display: flex; gap: 15px; justify-content: center;">
                    <button class="btn-main" onclick="validerAge()" style="width: 130px;" data-trans="age_yes">J'AI +18 ANS</button>
                    <button class="btn-main" onclick="refuserAge()" style="width: 130px; background-color: var(--error-color); color: white;" data-trans="age_no">-18 ANS</button>
                </div>
            </div>
        </div>

        <div class="header">
            <div class="lang-selector">
                <button class="lang-btn active" onclick="changeLanguage('fr')">🇫🇷</button>
                <button class="lang-btn" onclick="changeLanguage('en')">🇬🇧</button>
                <button class="lang-btn" onclick="changeLanguage('es')">🇪🇸</button>
                <button class="lang-btn" onclick="changeLanguage('it')">🇮🇹</button>
                <button class="lang-btn" onclick="changeLanguage('de')">🇩🇪</button>
            </div>

            <img src="/logo.png" class="logo-img" alt="Native MJ Logo">
            <h1>NATIVE MJ</h1>
            <p data-trans="header_sub">Service de livraison privé & expéditions</p>
            <div class="badge" data-trans="header_badge">📍 Zone : La Plaine / Cours Ju (<1km)</div>
        </div>

        {% if statut == "succes" %}
        <div class="modal-overlay" id="statusOverlay" style="display: flex;" onclick="document.getElementById('statusOverlay').style.display='none'">
            <div class="modal" onclick="event.stopPropagation()">
                <div style="text-align: center;">
                    <div style="font-size: 40px; margin-bottom: 10px;">✅</div>
                    <h2 data-trans="status_success_title">COMMANDE VALIDÉE !</h2>
                    <p style="color: var(--text-muted); font-size: 0.95rem;" data-trans="status_success_desc">Votre commande a bien été transmise.</p>
                    <p style="color: var(--accent-color); font-weight: bold;" data-trans="status_success_time">⏱️ Temps estimé : 20 à 45 min selon le rush.</p>
                    <button class="btn-main" onclick="document.getElementById('statusOverlay').style.display='none'" style="margin-top: 15px;" data-trans="close">Fermer</button>
                </div>
            </div>
        </div>
        {% endif %}

        {% if statut == "hors_zone" %}
        <div class="modal-overlay" id="statusOverlay" style="display: flex;" onclick="document.getElementById('statusOverlay').style.display='none'">
            <div class="modal error-modal" onclick="event.stopPropagation()">
                <div style="text-align: center;">
                    <div style="font-size: 40px; margin-bottom: 10px;">❌</div>
                    <h2 data-trans="status_out_title">HORS ZONE</h2>
                    <p style="color: var(--text-muted); font-size: 0.95rem;" data-trans="status_out_desc">Nous livrons uniquement dans un rayon de 1 km autour de La Plaine / Cours Ju.</p>
                    <button class="btn-main" onclick="document.getElementById('statusOverlay').style.display='none'" style="margin-top: 15px; background-color: var(--error-color); color: white;" data-trans="status_out_btn">Modifier l'adresse</button>
                </div>
            </div>
        </div>
        {% endif %}

        {% if statut == "erreur_stock" %}
        <div class="modal-overlay" id="statusOverlay" style="display: flex;" onclick="document.getElementById('statusOverlay').style.display='none'">
            <div class="modal error-modal" onclick="event.stopPropagation()">
                <div style="text-align: center;">
                    <div style="font-size: 40px; margin-bottom: 10px;">⚠️</div>
                    <h2 data-trans="status_stock_title">RUPTURE DE STOCK</h2>
                    <p style="color: var(--text-muted); font-size: 0.95rem;" data-trans="status_stock_desc">Un autre client a validé ce produit juste avant vous. Modifiez votre panier.</p>
                    <button class="btn-main" onclick="document.getElementById('statusOverlay').style.display='none'" style="margin-top: 15px; background-color: var(--error-color); color: white;" data-trans="status_stock_btn">Retour au menu</button>
                </div>
            </div>
        </div>
        {% endif %}

        <div class="section-title" data-trans="sec_flowers">Fleurs</div>
        <div class="grid">
            {% for name, info in stocks.items() if info.culture in ['Hydroponique', 'Greenhouse', 'Indoor'] %}
            <div class="card" data-name="{{ name }}" data-details='{{ info.details|tojson|safe }}' onclick="preparerModal(this)">
                <img src="{{ info.image }}" class="card-img" alt="{{ name }}">
                <div class="card-content">
                    <div>
                        <h3>{{ name }}</h3>
                        <span class="culture-tag">{{ info.culture }}</span>
                    </div>
                    <div class="size-options">
                        {% for size in ['2g', '5g', '10g'] %}
                        {% set price = 10 if name=='Amnesia Haze' else (12 if name=='Orange Bud' else 15) %}
                        {% if size == '5g' %}{% set price = 20 if name=='Amnesia Haze' else (25 if name=='Orange Bud' else 30) %}{% endif %}
                        {% if size == '10g' %}{% set price = 35 if name=='Amnesia Haze' else (45 if name=='Orange Bud' else 55) %}{% endif %}
                        <div class="size-row" onclick="event.stopPropagation();">
                            <span class="size-label">{{ size }} - {{ price }}€</span>
                            <div class="qty-controls">
                                <button class="qty-btn" onclick="updateQty('{{ name }}', '{{ size }}', {{ price }}, -1)" {% if info.stocks[size] <= 0 %}disabled{% endif %}>-</button>
                                <span class="qty-val" id="qty-{{ name }}-{{ size }}">0</span>
                                <button class="qty-btn" onclick="updateQty('{{ name }}', '{{ size }}', {{ price }}, 1)" {% if info.stocks[size] <= 0 %}disabled{% endif %}>+</button>
                            </div>
                        </div>
                        {% endfor %}
                    </div>
                </div>
            </div>
            {% endfor %}
        </div>

        <div class="section-title" data-trans="sec_resins">Résines</div>
        <div class="grid">
            {% for name, info in stocks.items() if info.culture in ['Dry Sift', 'Premium Cold Cure'] %}
            <div class="card" data-name="{{ name }}" data-details='{{ info.details|tojson|safe }}' onclick="preparerModal(this)">
                <img src="{{ info.image }}" class="card-img" alt="{{ name }}">
                <div class="card-content">
                    <div>
                        <h3>{{ name }}</h3>
                        <span class="culture-tag">{{ info.culture }}</span>
                    </div>
                    <div class="size-options">
                        {% for size in ['2g', '5g', '10g'] %}
                        {% set price = 12 if name=='Skuff - Polen' else 20 %}
                        {% if size == '5g' %}{% set price = 25 if name=='Skuff - Polen' else 45 %}{% endif %}
                        {% if size == '10g' %}{% set price = 45 if name=='Skuff - Polen' else 80 %}{% endif %}
                        <div class="size-row" onclick="event.stopPropagation();">
                            <span class="size-label">{{ size }} - {{ price }}€</span>
                            <div class="qty-controls">
                                <button class="qty-btn" onclick="updateQty('{{ name }}', '{{ size }}', {{ price }}, -1)" {% if info.stocks[size] <= 0 %}disabled{% endif %}>-</button>
                                <span class="qty-val" id="qty-{{ name }}-{{ size }}">0</span>
                                <button class="qty-btn" onclick="updateQty('{{ name }}', '{{ size }}', {{ price }}, 1)" {% if info.stocks[size] <= 0 %}disabled{% endif %}>+</button>
                            </div>
                        </div>
                        {% endfor %}
                    </div>
                </div>
            </div>
            {% endfor %}
        </div>

        <div class="spacer"></div>

        <div class="sticky-footer">
            <div class="summary-layout">
                <div class="summary-text" id="footerSummary" data-trans="basket_empty">Aucun produit sélectionné</div>
                <button class="btn-clear" id="btnClearPanier" onclick="viderPanier()" style="display: none;" data-trans="basket_clear">Vider</button>
            </div>
            <button class="btn-main" id="confirmOrderBtn" onclick="openCheckoutModal()" disabled data-trans="btn_confirm">Confirmer la commande</button>
        </div>

        <div class="modal-overlay" id="productModalOverlay" onclick="closeModals()">
            <div class="modal" onclick="event.stopPropagation()">
                <h2 id="modalProductName">Nom</h2>
                <div class="modal-details" id="modalProductDesc">Détails...</div>
                <button class="btn-main" onclick="closeModals()" data-trans="back">Retour</button>
            </div>
        </div>

        <div class="modal-overlay" id="checkoutModalOverlay" onclick="closeModals()">
            <div class="modal" onclick="event.stopPropagation()">
                <h2 id="checkoutModalTitle">Votre Commande</h2>
                <form method="POST">
                    <input type="hidden" id="formCommandeText" name="commande" value="">
                    <input type="hidden" id="formItemsRaw" name="items_raw" value="">
                    
                    <label for="prenom" data-trans="lbl_name">Prénom</label>
                    <input type="text" id="prenom" name="prenom" placeholder="Lucas" required>

                    <label for="telephone" data-trans="lbl_phone">Téléphone</label>
                    <input type="tel" id="telephone" name="telephone" placeholder="0612345678" required>

                    <label for="adresse" data-trans="lbl_address">Adresse ou Bar à Marseille</label>
                    <input type="text" id="adresse" name="adresse" placeholder="Ex: 10 Rue des trois mages" required>

                    <button type="submit" class="btn-main" style="margin-top: 20px;" data-trans="btn_submit">Vérifier & Commander</button>
                </form>
            </div>
        </div>

        <script>
            let panier = {};
            let currentLang = 'fr';
            let activeProductTranslations = null;

            const translations = {
                fr: {
                    age_title: "🔞 VÉRIFICATION D'ÂGE",
                    age_desc: "Ce site propose des produits dérivés du CBD réservés aux personnes majeures. Veuillez confirmer votre majorité pour accéder au menu.",
                    age_yes: "J'AI +18 ANS", age_no: "-18 ANS",
                    header_sub: "Service de livraison privé & expéditions", header_badge: "📍 Zone : La Plaine / Cours Ju (<1km)",
                    sec_flowers: "Fleurs", sec_resins: "Résines",
                    basket_empty: "Aucun produit sélectionné", basket_clear: "Vider",
                    btn_confirm: "Confirmer la commande", back: "Retour",
                    lbl_name: "Prénom", lbl_phone: "Téléphone", lbl_address: "Adresse ou Bar à Marseille",
                    btn_submit: "Vérifier & Commander", close: "Fermer",
                    status_success_title: "COMMANDE VALIDÉE !", status_success_desc: "Votre commande a bien été transmise.", status_success_time: "⏱️ Temps estimé : 20 à 45 min selon le rush.",
                    status_out_title: "HORS ZONE", status_out_desc: "Nous livrons uniquement dans un rayon de 1 km autour de La Plaine / Cours Ju.", status_out_btn: "Modifier l'adresse",
                    status_stock_title: "RUPTURE DE STOCK", status_stock_desc: "Un autre client a validé ce produit juste avant vous. Modifiez votre panier.", status_stock_btn: "Retour au menu"
                },
                en: {
                    age_title: "🔞 AGE VERIFICATION",
                    age_desc: "This site offers CBD products restricted to adults. Please confirm you are over 18 to access the menu.",
                    age_yes: "I AM 18+", age_no: "-18",
                    header_sub: "Private delivery service & shipping", header_badge: "📍 Area: La Plaine / Cours Ju (<1km)",
                    sec_flowers: "Flowers", sec_resins: "Resins",
                    basket_empty: "No product selected", basket_clear: "Clear",
                    btn_confirm: "Confirm Order", back: "Back",
                    lbl_name: "First Name", lbl_phone: "Phone Number", lbl_address: "Address or Bar in Marseille",
                    btn_submit: "Verify & Order", close: "Close",
                    status_success_title: "ORDER CONFIRMED!", status_success_desc: "Your order has been transmitted successfully.", status_success_time: "⏱️ Estimated time: 20 to 45 min depending on rush.",
                    status_out_title: "OUT OF AREA", status_out_desc: "We only deliver within 1 km around La Plaine / Cours Ju.", status_out_btn: "Change address",
                    status_stock_title: "OUT OF STOCK", status_stock_desc: "Another customer confirmed this item just before you. Please update your cart.", status_stock_btn: "Back to menu"
                },
                es: {
                    age_title: "🔞 VERIFICACIÓN DE EDAD",
                    age_desc: "Este sitio ofrece productos de CBD reservados para mayores de edad. Por favor, confirma tu mayoría de edad para acceder.",
                    age_yes: "SOY MAYOR DE 18", age_no: "-18 AÑOS",
                    header_sub: "Servicio de entrega privado y envíos", header_badge: "📍 Zona: La Plaine / Cours Ju (<1km)",
                    sec_flowers: "Flores", sec_resins: "Resinas",
                    basket_empty: "Ningún producto seleccionado", basket_clear: "Vaciar",
                    btn_confirm: "Confirmar pedido", back: "Volver",
                    lbl_name: "Nombre", lbl_phone: "Teléfono", lbl_address: "Dirección o Bar en Marsella",
                    btn_submit: "Verificar y Pedir", close: "Cerrar",
                    status_success_title: "¡PEDIDO CONFIRMADO!", status_success_desc: "Su pedido ha sido enviado con éxito.", status_success_time: "⏱️ Tiempo estimado: 20 a 45 min selon demanda.",
                    status_out_title: "FUERA DE ZONA", status_out_desc: "Solo realizamos entregas en un radio de 1 km alrededor de La Plaine / Cours Ju.", status_out_btn: "Modificar dirección",
                    status_stock_title: "SIN STOCK", status_stock_desc: "Otro cliente validó este producto justo antes que usted. Modifique su carrito.", status_stock_btn: "Volver al menú"
                },
                it: {
                    age_title: "🔞 VERIFICA DELL'ETÀ",
                    age_desc: "Questo sito offre prodotti a base di CBD riservati ai maggiorenni. Conferma la tua maggiore età per accedere al menu.",
                    age_yes: "HO +18 ANNI", age_no: "-18 ANNI",
                    header_sub: "Servizio di consegna privato e spedizioni", header_badge: "📍 Zona: La Plaine / Cours Ju (<1km)",
                    sec_flowers: "Fiori", sec_resins: "Resine",
                    basket_empty: "Nessun prodotto selezionato", basket_clear: "Svuota",
                    btn_confirm: "Conferma l'ordine", back: "Indietro",
                    lbl_name: "Nome", lbl_phone: "Telefono", lbl_address: "Indirizzo o Bar a Marsiglia",
                    btn_submit: "Verifica & Ordina", close: "Chiudi",
                    status_success_title: "ORDINE CONFERMATO!", status_success_desc: "Il tuo ordine è stato trasmesso con successo.", status_success_time: "⏱️ Tempo stimato: da 20 a 45 minuti a seconda dell'affluenza.",
                    status_out_title: "FUORI ZONA", status_out_desc: "Consegniamo solo entro un raggio di 1 km intorno a La Plaine / Cours Ju.", status_out_btn: "Modifica l'indirizzo",
                    status_stock_title: "PRODOTTO ESAURITO", status_stock_desc: "Un altro cliente ha confermato questo produit appena prima di te. Modifica il carrello.", status_stock_btn: "Torna al menu"
                },
                de: {
                    age_title: "🔞 ALTERSPRÜFUNG",
                    age_desc: "Diese Website bietet CBD-Produkte an, die für Erwachsene reserviert sind. Bitte bestätigen Sie Ihre Volljährigkeit, um das Menü aufzurufen.",
                    age_yes: "ICH BIN 18+", age_no: "-18 JAHRE",
                    header_sub: "Privater Lieferservice & Versand", header_badge: "📍 Zone: La Plaine / Cours Ju Umkreis (<1km)",
                    sec_flowers: "Blüten", sec_resins: "Harze",
                    basket_empty: "Kein Produkt ausgewählt", basket_clear: "Leeren",
                    btn_confirm: "Bestellung bestätigen", back: "Zurück",
                    lbl_name: "Vorname", lbl_phone: "Telefonnummer", lbl_address: "Adresse oder Bar in Marseille",
                    btn_submit: "Prüfen & Bestellen", close: "Schließen",
                    status_success_title: "BESTELLUNG BESTÄTIGT!", status_success_desc: "Ihre Bestellung wurde erfolgreich übermittelt.", status_success_time: "⏱️ Voraussichtliche Zeit: 20 bis 45 Min. je nach Auslastung.",
                    status_out_title: "AUSSERHALB DER ZONE", status_out_desc: "Wir liefern nur im Umkreis von 1 km um La Plaine / Cours Ju.", status_out_btn: "Adresse ändern",
                    status_stock_title: "AUSVERKAUFT", status_stock_desc: "Ein anderer Kunde hat dieses Produkt kurz vor Ihnen bestätigt. Bitte ändern Sie Ihren Warenkorb.", status_stock_btn: "Zurück zum Menü"
                }
            };

            function changeLanguage(lang) {
                currentLang = lang;
                document.querySelectorAll('.lang-selector .lang-btn').forEach(btn => btn.classList.remove('active'));
                if (event && event.target) {
                    event.target.classList.add('active');
                }
                
                document.querySelectorAll('[data-trans]').forEach(el => {
                    const key = el.getAttribute('data-trans');
                    if (translations[lang][key]) {
                        el.innerHTML = translations[lang][key];
                    }
                });

                if (activeProductTranslations && activeProductTranslations[lang]) {
                    document.getElementById('modalProductDesc').innerHTML = activeProductTranslations[lang];
                }

                updateFooter();
            }

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

            function updateQty(name, size, price, change) {
                const key = `${name} (${size})`;
                if (!panier[key]) {
                    panier[key] = { qty: 0, price: price, product: name, size: size };
                }
                
                panier[key].qty += change;
                
                if (panier[key].qty <= 0) {
                    delete panier[key];
                    document.getElementById(`qty-${name}-${size}`).innerText = "0";
                    document.getElementById(`qty-${name}-${size}`).classList.remove('active');
                } else {
                    document.getElementById(`qty-${name}-${size}`).innerText = panier[key].qty;
                    document.getElementById(`qty-${name}-${size}`).classList.add('active');
                }
                updateFooter();
            }

            function viderPanier() {
                panier = {};
                document.querySelectorAll('.qty-val').forEach(el => {
                    el.innerText = "0";
                    el.classList.remove('active');
                });
                updateFooter();
            }

            function updateFooter() {
                const keys = Object.keys(panier);
                const mainBtn = document.getElementById('confirmOrderBtn');
                const clearBtn = document.getElementById('btnClearPanier');
                
                if (keys.length === 0) {
                    document.getElementById('footerSummary').innerHTML = translations[currentLang].basket_empty;
                    mainBtn.setAttribute('disabled', 'true');
                    clearBtn.style.display = 'none';
                    return;
                }
                
                let total = 0, itemsText = [];
                for (let item in panier) { 
                    let itemTotal = panier[item].price * panier[item].qty;
                    total += itemTotal; 
                    itemsText.push(`${panier[item].qty}x ${item} <span>[${itemTotal}€]</span>`); 
                }
                
                const basketWord = currentLang === 'fr' ? 'Panier' : (currentLang === 'en' ? 'Cart' : (currentLang === 'es' ? 'Carrito' : (currentLang === 'it' ? 'Carrello' : 'Warenkorb')));
                document.getElementById('footerSummary').innerHTML = `${basketWord} : ${itemsText.join(' + ')} — Total : <span>${total}€</span>`;
                mainBtn.removeAttribute('disabled');
                clearBtn.style.display = 'inline-block';
            }

            function preparerModal(cardElement) {
                const name = cardElement.getAttribute('data-name');
                const detailsObj = JSON.parse(cardElement.getAttribute('data-details'));
                openProductModal(name, detailsObj);
            }

            function openProductModal(name, detailsObj) {
                activeProductTranslations = detailsObj;
                document.getElementById('modalProductName').innerText = name;
                document.getElementById('modalProductDesc').innerHTML = detailsObj[currentLang] || detailsObj['fr'];
                document.getElementById('productModalOverlay').style.display = 'flex';
            }

            function openCheckoutModal() {
                document.getElementById('productModalOverlay').style.display = 'none';
                let total = 0, itemsText = [], rawItems = [];
                
                for (let item in panier) { 
                    let itemTotal = panier[item].price * panier[item].qty;
                    total += itemTotal; 
                    itemsText.push(`${panier[item].qty}x ${item} [${itemTotal}€]`);
                    for(let i=0; i<panier[item].qty; i++) {
                        rawItems.push(`${panier[item].product}:${panier[item].size}`);
                    }
                }
                document.getElementById('checkoutModalTitle').innerText = `Total : ${total}€`;
                document.getElementById('formCommandeText').value = itemsText.join(' / ') + ` (Total: ${total}€)`;
                document.getElementById('formItemsRaw').value = rawItems.join(',');
                document.getElementById('checkoutModalOverlay').style.display = 'flex';
            }

            function closeModals() {
                document.getElementById('productModalOverlay').style.display = 'none';
                document.getElementById('checkoutModalOverlay').style.display = 'none';
                activeProductTranslations = null;
            }
        </script>
    </body>
    </html>
    """
    return HTML_FORM

@app.route('/logo.png')
def serve_logo():
    return send_from_directory(os.getcwd(), 'logo.png')

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
        
        besoin_stock = {}
        for item in liste_items:
            if ":" in item:
                prod, taille = item.split(":")
                key = f"{prod}:{taille}"
                besoin_stock[key] = besoin_stock.get(key, 0) + 1

        for key, qte in besoin_stock.items():
            prod, taille = key.split(":")
            if STOCKS.get(prod, {}).get("stocks", {}).get(taille, 0) < qte:
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
            except Exception as e: 
                print(e)
                statut = "succes"

    return render_template_string(generer_html(statut), stocks=STOCKS, statut=statut)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
