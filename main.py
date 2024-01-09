import streamlit as st
from firebase_admin import credentials, firestore, initialize_app, get_app, App
import uuid
import hashlib
import random
import streamlit_authenticator as stauth
import yaml
from yaml.loader import SafeLoader
with open('config.yaml') as file:
    config = yaml.load(file, Loader=SafeLoader)

authenticator = stauth.Authenticate(
    config['credentials'],
    config['cookie']['name'],
    config['cookie']['key'],
    config['cookie']['expiry_days'],
    config['preauthorized']
)

name, authentication_status, username = authenticator.login('Login', 'main')

hashed_passwords = stauth.Hasher(['abc', 'def']).generate()

if authentication_status:
    authenticator.logout('Logout', 'main')
    st.write(f'Welcome *{name}*')
    st.title('Some content')
elif authentication_status == False:
    st.error('Username/password is incorrect')
elif authentication_status == None:
    st.warning('Please enter your username and password')

# Initialisation de Firestore
def init_firestore():
    try:
        # Essaye de récupérer l'application Firebase existante
        app = get_app()
    except ValueError:
        # Si elle n'existe pas, initialise une nouvelle application
        cred = credentials.Certificate("path/to/queez-95147-54dbe09946ae.json")
        app = initialize_app(cred)
    return firestore.client(app)

# Initialise Firestore
db = init_firestore()

st.set_page_config(
    page_title="Queez",
    page_icon="🧊",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://www.extremelycoolapp.com/help',
        'Report a bug': "https://www.extremelycoolapp.com/bug",
        'About': "# This is a header. This is an *extremely* cool app!"
    }
)

def register_user(pseudo):
    user_id = str(uuid.uuid4())
    user_data = {"pseudo": pseudo, "user_id": user_id}
    db.collection("users").document(user_id).set(user_data)
    return user_id

def create_or_verify_user(username, password):
    users_ref = db.collection("users")
    user_doc = users_ref.document(username).get()
    hashed_password = hashlib.sha256(password.encode()).hexdigest()

    if user_doc.exists:
        user_data = user_doc.to_dict()
        if user_data['password'] == hashed_password:
            return True, "Connexion réussie"
        else:
            return False, "Mot de passe incorrect"
    else:
        users_ref.document(username).set({"password": hashed_password})
        return True, "Compte créé"
    
def login_interface():
    st.sidebar.title("Connexion")
    username = st.sidebar.text_input("Nom d'utilisateur")
    password = st.sidebar.text_input("Mot de passe", type='password')
    login_button = st.sidebar.button("Connexion / Inscription")

    if login_button:
        success, message = create_or_verify_user(username, password)
        if success:
            st.session_state['user_pseudo'] = username
            st.rerun()  # Rafraîchit la page après la mise à jour de session_state
        else:
            st.sidebar.error(message)

# Fonction pour afficher les sessions actives
def display_active_sessions():
    sessions = db.collection("sessions").where("state", "==", "waiting").stream()
    for session in sessions:
        session_info = session.to_dict()
        session_name = session_info.get("name", "Session Inconnue")
        st.write(f"Session : {session_name}")
        if st.button(f"Rejoindre la session {session_name}"):
            join_session(session.id)

# Fonction pour rejoindre une session
def join_session(session_id):
    # Ajouter la logique pour rejoindre une session
    pass

def get_rankings():
    try:
        rankings = db.collection("rank").order_by("score", direction=firestore.Query.DESCENDING).stream()
        return [(rank.to_dict().get("pseudo", "Inconnu"), rank.to_dict().get("score", 0)) for rank in rankings]
    except Exception as e:
        print("Erreur lors de la récupération des classements :", e)
        return []

def display_rankings():
    rankings = get_rankings()
    
    # Définir un expander dans la barre latérale pour le classement
    with st.sidebar.expander("Classement"):
        # Limiter l'affichage à 10 entrées
        top_rankings = rankings[:10]
        
        # Créer un tableau de classement pour les 10 premiers
        top_ranking_markdown = ""
        for index, (pseudo, score) in enumerate(top_rankings, start=1):
            top_ranking_markdown += f"{index}. **{pseudo}** - {score} points\n"
        
        # Afficher le classement des 10 premiers
        st.markdown(top_ranking_markdown)

        # Si il y a plus que 10 classements, permettre de défiler pour voir les autres
        if len(rankings) > 10:
            with st.container():
                st.write("Voir plus de classements...")
                for index, (pseudo, score) in enumerate(rankings[10:], start=11):
                    st.text(f"{index}. {pseudo} - {score} points")

def mettre_a_jour_classement(score, temps_total):
    # Votre logique pour mettre à jour le classement dans Firestore
    # Exemple :
    user_id = "identifiant_utilisateur"  # Identifiant unique de l'utilisateur
    user_doc = db.collection("rank").document(user_id).get()
    if user_doc.exists:
        db.collection("rank").document(user_id).update({"score": firestore.Increment(score)})
    else:
        db.collection("rank").document(user_id).set({"score": score})

def recuperer_questions(type_question):
    questions = []
    for doc in db.collection("questions").where("type", "==", type_question).stream():
        question_data = doc.to_dict()
        bonne_reponse = question_data['reponse'][0]  # Supposer que la première réponse est la bonne
        random.shuffle(question_data['reponse'])  # Mélanger les réponses

        # Identifier l'index de la bonne réponse après mélange
        question_data['bonne_reponse_index'] = question_data['reponse'].index(bonne_reponse)
        questions.append(question_data)
    return questions


MODES_DE_JEU = ["cyber", "Mode 2", "Mode 3", "Mode 4", "Mode 5"]

def mode_solo():
    st.header("Mode Solo")
    display_rankings()
    display_chat()

    if 'en_jeu' not in st.session_state or not st.session_state['en_jeu']:
        mode_choisi = st.selectbox("Choisir un type de quiz", MODES_DE_JEU)
        if st.button("Commencer le quiz"):
            demarrer_quiz(mode_choisi)

    if st.session_state.get('en_jeu', False):
        afficher_question_et_reponse()

def demarrer_quiz(mode_choisi):
    st.session_state['questions'] = recuperer_questions(mode_choisi)
    random.shuffle(st.session_state['questions'])
    st.session_state['current_question_index'] = 0
    st.session_state['score'] = 0
    st.session_state['en_jeu'] = True
    st.session_state['reponse_validee'] = False
    st.session_state['start_time'] = time.time()  # Enregistrer le début du quiz
    st.rerun()

def afficher_question_et_reponse():
    current_index = st.session_state['current_question_index']
    question = st.session_state['questions'][current_index]
    st.subheader(f"Question {current_index + 1}: {question['question']}")

    if 'time_left' not in st.session_state or st.session_state['time_left'] <= 0:
        st.session_state['time_left'] = 30  # Réinitialiser le temps pour la question

    time_container = st.empty()
    time_container.write(f"Temps restant: {st.session_state['time_left']} secondes")
    st.success(f"Score actuel : {st.session_state['score']}")

    if not st.session_state.get('reponse_validee', False):
        if question['point'] == 5:
            choix = st.text_input("Votre réponse :", key=f"reponse_{current_index}")
        else:
            choix = st.radio("Choisissez votre réponse :", question['reponse'], key=f"reponse_{current_index}")

        if st.button("Valider la réponse", key=f"valider_{current_index}"):
            st.session_state['reponse_validee'] = True
            verifier_et_afficher_reponse(question, choix)
    else:
        afficher_bonne_reponse_et_bouton_suivant(question)

    if st.session_state['time_left'] > 1:
        time.sleep(1)
        st.session_state['time_left'] -= 1
        st.rerun()
    if st.session_state['time_left'] == 1:
        st.session_state['reponse_validee'] = True
        passer_a_la_question_suivante()
        st.rerun()
    else:
        st.session_state['reponse_validee'] = True
        passer_a_la_question_suivante()

def verifier_et_afficher_reponse(question, choix):
    bonne_reponse = question['reponse'][question['bonne_reponse_index']]
    if choix.strip().lower() == bonne_reponse.lower():
        st.session_state['score'] += question['point']
        st.success(f"Réponse correcte! {bonne_reponse}")
    else:
        st.error(f"Mauvaise réponse, la bonne réponse était : {bonne_reponse}")

def afficher_bonne_reponse_et_bouton_suivant(question):
    bonne_reponse = question['reponse'][question['bonne_reponse_index']]
    st.write(f"La bonne réponse était : {bonne_reponse}")
    if st.button("Question suivante", key=f"suivante_{st.session_state['current_question_index']}"):
        passer_a_la_question_suivante()

def passer_a_la_question_suivante():
    if st.session_state['current_question_index'] < len(st.session_state['questions']) - 1:
        st.session_state['current_question_index'] += 1
        st.session_state['reponse_validee'] = False
        st.session_state['time_left'] = 30
    else:
        terminer_quiz()

def terminer_quiz():
    temps_total = time.time() - st.session_state['start_time']
    mettre_a_jour_classement(st.session_state['score'], temps_total)
    st.success(f"Quiz terminé. Merci d'avoir participé ! Vous avez pris {temps_total:.2f} secondes.")
    st.button("Retour au choix du mode de jeu", on_click=reset_quiz_state)
    time.sleep(10)
    st.session_state['en_jeu'] = False

def reset_quiz_state():
    for key in ['questions', 'current_question_index', 'score', 'en_jeu', 'reponse_validee', 'start_time', 'time_left']:
        if key in st.session_state:
            del st.session_state[key]

def mode_duel():
    st.header("Mode Duel")
    display_rankings()
    display_chat()
    if st.button("Créer une nouvelle session"):
        create_duel_session()
    display_active_sessions()


# Fonction pour créer une nouvelle session avec des paramètres supplémentaires
def create_new_session(session_name, quiz_choice):
    session_id = str(uuid.uuid4())
    session_data = {
        "players": [], 
        "state": "waiting", 
        "name": session_name, 
        "quiz": quiz_choice
    }
    db.collection("sessions").document(session_id).set(session_data)
    return session_id

def create_duel_session():
    # Définition initiale des valeurs de session_state
    if 'session_name' not in st.session_state:
        st.session_state['session_name'] = ''
    if 'quiz_choice' not in st.session_state:
        st.session_state['quiz_choice'] = 0

    # Création des widgets avec un verrouillage d'état
    session_name = st.text_input("Nom de la session", value=st.session_state['session_name'], key="session_name_input")
    quiz_choice = st.selectbox("Choisir un quiz", ["Sciences", "Art et Littérature", "Géographie", "Aléatoire"], index=st.session_state['quiz_choice'], key="quiz_choice_select")

    # Bouton de création de session avec callback
    create_session_button = st.button("Créer Session")

    if create_session_button:
        # Mise à jour de l'état et création de la session
        st.session_state['session_name'] = session_name
        st.session_state['quiz_choice'] = quiz_choice
        session_id = create_new_session(session_name, quiz_choice)
        st.write(f"Session '{session_name}' créée! ID: {session_id}")

# Fonction pour récupérer les questions
def get_questions(category):
    # Remplacer cette fonction par la logique Firestore pour récupérer les questions
    return ["Question 1", "Question 2", "Question 3"]

# Fonction pour exécuter le quiz
def run_quiz(questions):
    for question in questions:
        st.write(question)
        # Ajouter ici la logique pour afficher les questions et enregistrer les réponses

def send_message(username, message):
    """Envoie un message au chat."""
    if message:  # On ne fait rien si le message est vide
        db.collection("chats").add({
            "username": st.session_state['user_pseudo'],
            "message": message,
            "timestamp": firestore.SERVER_TIMESTAMP  # Utilise l'horodatage du serveur
        })

import time

def display_chat():
    # Afficher le chat dans un expander
    chat_expanded = st.sidebar.expander("Chat")
    with chat_expanded:
        # Récupérer et afficher les messages
        messages_query = db.collection("chats").order_by("timestamp", direction=firestore.Query.DESCENDING).limit(10)
        messages = messages_query.stream()
        messages_list = list(messages)
        
        # Formulaire d'envoi de message
        with st.form(key='chat_form'):
            username = st.session_state.get('user_pseudo', '')
            message = st.text_input("Message", key='chat_message')
            submit_button = st.form_submit_button("Envoyer")
            if submit_button and message:
                send_message(username, message)
                st.rerun()  # Rafraîchir après l'envoi du message
        
        # Afficher les messages
        for message in messages_list:
            message_data = message.to_dict()
            st.write(f"**{message_data['username']}**: {message_data['message']}")

def main():
    st.title("Queez")

    if 'user_pseudo' not in st.session_state:
        login_interface()
    else:
        st.write(f"Bienvenue, {st.session_state['user_pseudo']}")
        mode = st.sidebar.selectbox("Choisir le mode de jeu", ["Solo", "Duel"])
        if mode == "Solo":
            mode_solo()
        elif mode == "Duel":
            mode_duel()


if __name__ == "__main__":
    main()
