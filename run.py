from flask import Flask, render_template, request, jsonify
import random
import string

# --- INITIALISATION ET ÉTAT GLOBAL ---
app = Flask(__name__)
generated_count = 0
history_list = []
MAX_HISTORY = 5 

# --- LOGIQUE DE L'OUTIL DE SÉCURITÉ ---

def generer_mot_de_passe(longueur=16):
    """Génère un mot de passe fort avec une diversité assurée."""
    minuscules = string.ascii_lowercase
    majuscules = string.ascii_uppercase
    chiffres = string.digits
    symboles = string.punctuation
    
    tous_les_caracteres = minuscules + majuscules + chiffres + symboles
    
    if longueur < 4:
        longueur = 4

    # Assure la présence d'au moins un de chaque type
    mot_de_passe = [
        random.choice(minuscules),
        random.choice(majuscules),
        random.choice(chiffres),
        random.choice(symboles)
    ]
    
    # Complète la longueur restante
    mot_de_passe += random.choices(tous_les_caracteres, k=longueur - 4)
    random.shuffle(mot_de_passe)
    
    return "".join(mot_de_passe[:longueur])

def evaluer_force(mdp):
    """Évalue la force d'un mot de passe sur 7 points."""
    longueur = len(mdp)
    score = 0
    feedback = []
    
    # Critère 1: Longueur (jusqu'à 3 points)
    if longueur >= 16:
        score += 3
        feedback.append("✔️ Longueur excellente (>= 16 caractères).")
    elif longueur >= 12:
        score += 2
        feedback.append("⚠️ Longueur bonne (>= 12 caractères), visez plus long.")
    else:
        score += 1
        feedback.append("❌ Longueur trop courte. Visez au moins 16 caractères.")
        
    # Critère 2: Diversité (jusqu'à 4 points)
    a_minuscule = any(c.islower() for c in mdp)
    a_majuscule = any(c.isupper() for c in mdp)
    a_chiffre = any(c.isdigit() for c in mdp)
    a_symbole = any(c in string.punctuation for c in mdp)
    
    types_present = sum([a_minuscule, a_majuscule, a_chiffre, a_symbole])
    score += types_present
    
    if types_present == 4:
        feedback.append("✔️ Diversité maximale (Min, Maj, Chiffre, Symbole).")
    else:
        feedback.append(f"⚠️ Manque de diversité. Types de caractères présents : {types_present}/4.")

    # Déterminer la force finale
    if score >= 7:
        force = "Très Fort 💪"
    elif score >= 5:
        force = "Fort 👍"
    elif score >= 3:
        force = "Moyen 🤏"
    else:
        force = "Faible 😔"
        
    return force, feedback, score

def get_cyber_tip():
    """Fournit un conseil éducatif."""
    return {
        "title": "Le Danger du 'Credential Stuffing'",
        "content": "Utiliser le même mot de passe pour plusieurs sites est la plus grande menace. Si un site est piraté, vos autres comptes le seront aussi. Utilisez un mot de passe unique partout, aidé par un gestionnaire."
    }

# --- ROUTES FLASK ---

@app.route('/')
def home():
    """Route principale, sert la page HTML et transmet les données initiales."""
    tip = get_cyber_tip()
    return render_template('index.html', 
        cyber_tip_title=tip['title'], 
        cyber_tip_content=tip['content'],
        generated_count=generated_count,
        history_list=history_list
    )

@app.route('/generate', methods=['POST'])
def generate_password_api():
    """API pour la génération (appelée par JavaScript)."""
    global generated_count, history_list
    
    data = request.get_json()
    longueur = data.get('length', 16)
    try:
        longueur = int(longueur) if int(longueur) >= 8 else 16
    except ValueError:
        longueur = 16
        
    mdp = generer_mot_de_passe(longueur)
    
    # Mise à jour de l'état global
    generated_count += 1
    history_list.insert(0, mdp)
    if len(history_list) > MAX_HISTORY:
        history_list.pop()
        
    return jsonify({
        'password': mdp,
        'new_count': generated_count,
        'new_history': history_list
    })

@app.route('/evaluate', methods=['POST'])
def evaluate_password_api():
    """API pour l'évaluation (appelée par JavaScript)."""
    data = request.get_json()
    mdp = data.get('password', '')
    
    force, feedback, score = evaluer_force(mdp)
    
    return jsonify({
        'force': force,
        'feedback': feedback,
        'score': score
    })

if __name__ == '__main__':
    app.run(debug=True)