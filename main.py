import os
import requests
from flask import Flask, render_template_string, request

app = Flask(__name__)

# Ta configuration Telegram officielle
TOKEN = "8929246651:AAFSqQ_k4Wi5GIOl3a773czmfcenO_jWrAc"
CHAT_ID = "6141877001"

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

        .size-options { display: flex; gap: 8px; justify-content: center; margin-top: 15px; }
        .size-btn { background: #2c2c2e; border: none; color: var(--text-main); padding: 8px 14px; border-radius: 6px; font-size: 0.85rem; font-weight: bold; cursor: pointer; transition: background 0.2s; }
        .size-btn:hover { background: #3a3a3c; }
        .size-btn.active { background: var(--accent-color); color: #000; }
        
        .sticky-footer { position: fixed; bottom: 0; left: 0; width: 100%; background: rgba(18, 18, 18, 0.85); backdrop-filter: blur(10px); border-top: 1px solid #2c2c2e; padding: 15px; box-sizing: border-box; display: flex; flex-direction: column; align-items: center; z-index: 10; }
        .summary-text { font-size: 0.95rem; margin-bottom: 10px; color: var(--text-muted); text-align: center; max-width: 600px; }
        .summary-text span { color: var(--accent-color); font-weight: bold; }
        .btn-main { background: var(--accent-color); color: #000; border: none; padding: 12px 30px; font-size: 1rem; font-weight: bold; border-radius: 8px; cursor: pointer; width: 100%; max-width: 400px; transition: opacity 0.2s; text-transform: uppercase; }
        .btn-main:hover { opacity: 0.9; }
        .btn-main:disabled { background: #2c2c2e; color: var(--text-muted); cursor: not-allowed; }

        /* Styles des Fenêtres Pop-up (Modals) */
        .modal-overlay { position: fixed; top:0; left:0; width:100%; height:100%; background: rgba(0,0,0,0.8); backdrop-filter: blur(4px); display: none; justify-content: center; align-items: center; z-index: 100; }
        .modal { background: var(--card-bg); border: 2px solid var(--accent-color); border-radius: 16px; padding: 25px; max-width: 380px; width: 90%; position: relative; box-shadow: 0 10px 30px rgba(0,0,0,0.5); }
        .modal h2 { margin-top: 0; color: var(--accent-color); font-size: 1.4rem; text-align: center; }
        .modal img { width: 100%; border-radius: 8px; margin: 12px 0; object-fit: cover; height: 180px; background: #2c2c2e; }
        .modal-details { font-size: 0.95rem; color: var(--text-main); line-height: 1.5; margin-bottom: 20px; background: rgba(255,255,255,0.03); padding: 12px; border-radius: 8px; border: 1px solid #2c2c2e; }
        
        /* Formulaire */
        label { display: block; margin: 12px 0 4px; font-size: 0.85rem; color: var(--text-muted); text-transform: uppercase; font-weight: bold; }
        input { width: 100%; padding: 12px; background: #2c2c2e; border: 1px solid #3a3a3c; border-radius: 8px; color: white; box-sizing: border-box; font-size: 1rem; }
        input:focus { border-color: var(--accent-color); outline: none; }
        
        .success-screen { text-align: center; padding: 20px; }
        .success-icon { font-size: 40px; color: var(--accent-color); margin-bottom: 10px; }
        
        .spacer { height: 140px; }
    </style>
</head>
<body>

    <div class="header">
        <h1>MARSEILLE CBD</h1>
        <p>Service de livraison privé & expéditions</p>
        <div class="badge">● Ouvert 7j/7 de 18h à 01h</div>
    </div>

    {% if succes %}
    <div class="modal-overlay" id="successOverlay" style="display: flex;" onclick="document.getElementById('successOverlay').style.display='none'">
        <div class="modal" onclick="event.stopPropagation()">
            <div class="success-screen">
                <div class="success-icon">✅</div>
                <h2>COMMANDE VALIDÉE !</h2>
                <p style="color: var(--text-muted); font-size: 0.95rem;">Votre livreur vous contacte sur votre mobile très rapidement pour le créneau.</p>
                <button class="btn-main" onclick="document.getElementById('successOverlay').style.display='none'" style="margin-top: 15px;">Fermer</button>
            </div>
        </div>
    </div>
    {% endif %}

    <div class="section-title">Fleurs</div>
    <div class="grid">
        <div class="card" onclick="openProductModal('Amnesia Haze', '📍 Type : Dominance Sativa<br>💧 Culture : HIDROPÓNICO (Petites têtes d\\'entrée de gamme)<br>📊 Taux CBD : ~17%<br><br>✨ Effets : Énergisant, focus et clarté d\\'esprit. Idéal pour un usage en journée sans effet cassant.<br>🍋 Arômes : Très marqué agrumes, citron authentique et fond boisé.', 'https://images.unsplash.com/photo-1536657464919-892541299952?w=400')">
            <h3>Amnesia Haze</h3>
            <span class="culture-tag">Hidropónico</span>
            <div class="size-options">
                <button class="size-btn" data-product="Amnesia Haze" data-size="2g" onclick="toggleProduct(event, 'Amnesia Haze', '2g', 10)">2g - 10€</button>
                <button class="size-btn" data-product="Amnesia Haze" data-size="5g" onclick="toggleProduct(event, 'Amnesia Haze', '5g', 20)">5g - 20€</button>
                <button class="size-btn" data-product="Amnesia Haze" data-size="10g" onclick="toggleProduct(event, 'Amnesia Haze', '10g', 35)">10g - 35€</button>
            </div>
        </div>

        <div class="card" onclick="openProductModal('Orange Bud', '📍 Type : Dominance Sativa<br>☀️ Culture : GREENHOUSE (Sous serre optimisée)<br>📊 Taux CBD : ~12%<br><br>✨ Effets : Boost d\\'humeur, relaxant léger idéal pour être de bonne humeur en journée ou en soirée tranquille.<br>🍊 Arômes : Parfum d\\'orange douce et de nectarine mûre fruitée.', 'https://images.unsplash.com/photo-1599488615731-7e5c2823ff28?w=400')">
            <h3>Orange Bud</h3>
            <span class="culture-tag">Greenhouse</span>
            <div class="size-options">
                <button class="size-btn" data-product="Orange Bud" data-size="2g" onclick="toggleProduct(event, 'Orange Bud', '2g', 12)">2g - 12€</button>
                <button class="size-btn" data-product="Orange Bud" data-size="5g" onclick="toggleProduct(event, 'Orange Bud', '5g', 25)">5g - 25€</button>
                <button class="size-btn" data-product="Orange Bud" data-size="10g" onclick="toggleProduct(event, 'Orange Bud', '10g', 45)">10g - 45€</button>
            </div>
        </div>

        <div class="card" onclick="openProductModal('Cookie Kush', '📍 Type : Dominance Indica<br>🌿 Culture : INDOOR (Grosses têtes bien denses)<br>📊 Taux CBD : ~15%<br><br>✨ Effets : Relaxation corporelle profonde, idéal anti-stress pour totalement décompresser en fin de soirée.<br>🍏 Arômes : Notes très sucrées, saveur biscuitée gourmande et nuances terreuses.', 'https://images.unsplash.com/photo-1603909223429-69bb7101f420?w=400')">
            <h3>Cookie Kush</h3>
            <span class="culture-tag">Indoor</span>
            <div class="size-options">
                <button class="size-btn" data-product="Cookie Kush" data-size="2g" onclick="toggleProduct(event, 'Cookie Kush', '2g', 15)">2g - 15€</button>
                <button class="size-btn" data-product="Cookie Kush" data-size="5g" onclick="toggleProduct(event, 'Cookie Kush', '5g', 30)">5g - 30€</button>
                <button class="size-btn" data-product="Cookie Kush" data-size="10g" onclick="toggleProduct(event, 'Cookie Kush', '10g', 55)">10g - 55€</button>
            </div>
        </div>
    </div>

    <div class="section-title">Résines</div>
    <div class="grid">
        <div class="card" onclick="openProductModal('Skuff - Polen', '📍 Type : Pollen tamisé à sec (Dry Sift)<br>📊 Taux CBD : ~25%<br>🧈 Texture : Poudreuse et sablonneuse, s\\'effrite très facilement sans chauffer.<br><br>✨ Effets : Apaisement musculaire global, calme mental parfait au quotidien.<br>🌿 Arômes : Très végétal, notes terreuses classiques et parfum de chanvre pur.', 'https://images.unsplash.com/photo-1556928967-df529c9918bc?w=400')">
            <h3>Skuff - Polen</h3>
            <span class="culture-tag">Dry Sift</span>
            <div class="size-options">
                <button class="size-btn" data-product="Skuff - Polen" data-size="2g" onclick="toggleProduct(event, 'Skuff - Polen', '2g', 12)">2g - 12€</button>
                <button class="size-btn" data-product="Skuff - Polen" data-size="5g" onclick="toggleProduct(event, 'Skuff - Polen', '5g', 25)">5g - 25€</button>
                <button class="size-btn" data-product="Skuff - Polen" data-size="10g" onclick="toggleProduct(event, 'Skuff - Polen', '10g', 45)">10g - 45€</button>
            </div>
        </div>
        
        <div class="card" onclick="openProductModal('Creamy Piatella', '📍 Type : Concentré d\\'Exception (Bubble Hash Ice-O-Lator)<br>❄️ Affinage : Cold Cure sous vide (Affinage à froid)<br>📊 Taux CBD : 70% (Ultra puissant et recherché)<br>🧈 Texture : Beurrée, fondante comme du caramel mou, malléabilité parfaite.<br><br>✨ Effets : Relaxation extrême, sédation profonde, idéal contre les grosses insomnies ou fins de journées chargées.<br>🍰 Arômes : Profil terpénique ultra riche, notes crémeuses, sucrées et presque pâtissières.', 'https://images.unsplash.com/photo-1556928967-df529c9918bc?w=400')">
            <h3>Creamy Piatella</h3>
            <span class="culture-tag">Premium Cold Cure</span>
            <div class="size-options">
                <button class="size-btn" data-product="Creamy Piatella" data-size="2g" onclick="toggleProduct(event, 'Creamy Piatella', '2g', 20)">2g - 20€</button>
                <button class="size-btn" data-product="Creamy Piatella" data-size="5g" onclick="toggleProduct(event, 'Creamy Piatella', '5g', 45)">5g - 45€</button>
                <button class="size-btn" data-product="Creamy Piatella" data-size="10g" onclick="toggleProduct(event, 'Creamy Piatella', '10g', 80)">10g - 80€</button>
            </div>
        </div>
    </div>

    <div class="spacer"></div>

    <div class="sticky-footer">
        <div class="summary-text" id="footerSummary">Aucun produit sélectionné</div>
        <button class="btn-main" id="confirmOrderBtn" onclick="openCheckoutModal()" disabled>Confirmer la commande</button>
    </div>

    <div class="modal-overlay" id="productModalOverlay" onclick="closeModals()">
        <div class="modal" onclick="event.stopPropagation()">
            <h2 id="modalProductName">Nom du Produit</h2>
            <img id="modalProductImg" src="" alt="Aperçu produit" style="display: none;">
            <div class="modal-details" id="modalProductDesc">Description...</div>
            <button class="btn-main" onclick="hideProductModal()">Retour aux produits</button>
        </div>
    </div>

    <div class="modal-overlay" id="checkoutModalOverlay" onclick="closeModals()">
        <div class="modal" onclick="event.stopPropagation()">
            <h2 id="checkoutModalTitle">Votre Commande</h2>
            <form method="POST">
                <input type="hidden" id="formCommandeText" name="commande" value="">
                
                <label for="prenom">Prénom</label>
                <input type="text" id="prenom" name="prenom" placeholder="Ex: Lucas" required>

                <label for="telephone">Numéro de téléphone</label>
                <input type="tel" id="telephone" name="telephone" placeholder="Ex: 0612345678" required>

                <label for="adresse">Adresse de livraison à Marseille</label>
                <input type="text" id="adresse" name="adresse" placeholder="Ex: 12 Rue de la République, 13001" required>

                <button type="submit" class="btn-main" style="margin-top: 20px;">Passer la commande</button>
            </form>
        </div>
    </div>

    <script>
        // Le dictionnaire global qui contient le panier
        let panier = {};

        function toggleProduct(event, name, size, price) {
            event.stopPropagation(); // Évite d'ouvrir les détails en cliquant sur le bouton
            
            const key = `${name} (${size})`;
            
            if (panier[key]) {
                // Si le format précis est déjà cliqué, on le retire du panier
                delete panier[key];
                event.target.classList.remove('active');
            } else {
                // Sinon, on décoche d'abord les autres tailles du MÊME produit (pour éviter les doublons étranges sur une même ligne)
                document.querySelectorAll(`.size-btn[data-product="${name}"]`).forEach(btn => {
                    btn.classList.remove('active');
                    const otherSize = btn.getAttribute('data-size');
                    delete panier[`${name} (${otherSize})`];
                });
                
                // On ajoute la nouvelle sélection
                panier[key] = price;
                event.target.classList.add('active');
            }
            
            updateFooter();
        }

        function updateFooter() {
            const keys = Object.keys(panier);
            const mainBtn = document.getElementById('confirmOrderBtn');
            
            if (keys.length === 0) {
                document.getElementById('footerSummary').innerHTML = "Aucun produit sélectionné";
                mainBtn.setAttribute('disabled', 'true');
                return;
            }
            
            let total = 0;
            let itemsText = [];
            
            for (let item in panier) {
                total += panier[item];
                itemsText.push(item);
            }
            
            document.getElementById('footerSummary').innerHTML = `Panier : <span>${itemsText.join(' + ')}</span> — Total : <span>${total}€</span>`;
            mainBtn.removeAttribute('disabled');
        }

        function openProductModal(name, desc, imgSrc) {
            document.getElementById('modalProductName').innerText = name;
            document.getElementById('modalProductDesc').innerHTML = desc;
            
            const imgEl = document.getElementById('modalProductImg');
            if(imgSrc) {
                imgEl.src = imgSrc;
                imgEl.style.display = 'block';
            } else {
                imgEl.style.display = 'none';
            }
            
            document.getElementById('productModalOverlay').style.display = 'flex';
        }

        function hideProductModal() {
            document.getElementById('productModalOverlay').style.display = 'none';
        }

        function openCheckoutModal() {
            hideProductModal();
            
            let total = 0;
            let itemsText = [];
            for (let item in panier) {
                total += panier[item];
                itemsText.push(`${item} [${panier[item]}€]`);
            }
            
            document.getElementById('checkoutModalTitle').innerText = `Total à payer : ${total}€`;
            document.getElementById('formCommandeText').value = itemsText.join(' / ') + ` (Total: ${total}€)`;
            
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

@app.route("/", methods=["GET", "POST"])
def home():
    succes = False
    if request.method == "POST":
        prenom = request.form.get("prenom")
        telephone = request.form.get("telephone")
        adresse = request.form.get("adresse")
        choix_commande = request.form.get("commande")

        texte_telegram = (
            f"🔔 NOUVELLE COMMANDE MULTIPLE REÇUE !\n\n"
            f"👤 Prénom : {prenom}\n"
            f"📞 Tél : {telephone}\n"
            f"📍 Adresse : {adresse}\n\n"
            f"📦 Liste des produits :\n{choix_commande}"
        )

        url_telegram = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
        payload = {"chat_id": CHAT_ID, "text": texte_telegram}

        try:
            reponse = requests.post(url_telegram, json=payload)
            print(f"!!! STATUS TELEGRAM !!! Code: {reponse.status_code}")
            succes = True
        except Exception as e:
            print(f"!!! ERREUR REQUETE TELEGRAM !!!: {e}")
            succes = True

    return render_template_string(HTML_FORM, succes=succes)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
