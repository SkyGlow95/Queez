import streamlit as st
from firebase_admin import credentials, firestore, initialize_app, get_app, App
import streamlit_authenticator as stauth
import auth

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

db = auth.init_firestore()
# Initialisez l'état d'authentification si nécessaire
if 'authentication_status' not in st.session_state:
    st.session_state['authentication_status'] = None

# Essayez de vous connecter
try:
    auth.name, auth.authentication_status, auth.username = auth.authenticator.login('Login', 'main')
except KeyError as e:
    pass

if auth.authentication_status:
    st.session_state['name'] = auth.name  # Stocker le nom dans l'état de session
    auth.authenticator.logout('Logout', 'main', key='unique_logout_key')
    st.write(f'Bienvenue {auth.name}')
elif auth.authentication_status == False:
    st.error('Nom d’utilisateur/mot de passe incorrect')
    try:
        if auth.authenticator.register_user('Register user', preauthorization=False):
            st.success('User registered successfully')
    except Exception as e:
        st.error(e)
elif auth.authentication_status is None:
    st.warning('Veuillez entrer votre nom d’utilisateur et votre mot de passe')
    try:
        if auth.authenticator.register_user('Register user', preauthorization=False):
            st.success('User registered successfully')
    except Exception as e:
        st.error(e)

def get_rankings():
    try:
        rankings_query = db.collection("rank").order_by("score", direction=firestore.Query.DESCENDING).stream()
        rankings = {}
        for rank in rankings_query:
            rank_data = rank.to_dict()
            mode_de_jeu = rank_data.get("mode_de_jeu", "Inconnu")
            if mode_de_jeu not in rankings:
                rankings[mode_de_jeu] = []
            rankings[mode_de_jeu].append(rank_data)
        return rankings
    except Exception as e:
        print("Erreur lors de la récupération des classements :", e)
        return {}


def display_rankings():
    rankings = get_rankings()
    
    with st.sidebar.expander("Classement"):
        # Créer un tableau de classement pour chaque mode de jeu
        for mode_de_jeu, mode_rankings in rankings.items():
            st.markdown(f"### Classement pour {mode_de_jeu}")
            
            # Limiter l'affichage à 10 entrées par mode de jeu
            top_rankings = mode_rankings[:10]

            # Créer un tableau de classement pour les 10 premiers
            top_ranking_markdown = ""
            for index, rank in enumerate(top_rankings, start=1):
                user_id = rank.get("user_id", "Inconnu")
                score = rank.get("score", 0)
                temps_total = rank.get("temps_total", 0)
                
                # Convertir le temps total en minutes et secondes
                minutes, seconds = divmod(temps_total, 60)
                time_str = f"{int(minutes)}m {seconds:.2f}s"

                top_ranking_markdown += f"{index}. **{user_id}** - {score} points - {time_str}\n"

            # Afficher le classement des 10 premiers
            st.markdown(top_ranking_markdown)

            # Si il y a plus que 10 classements, permettre de défiler pour voir les autres
            if len(mode_rankings) > 10:
                with st.container():
                    st.write("Voir plus de classements...")
                    for index, rank in enumerate(mode_rankings[10:], start=11):
                        user_id = rank.get("user_id", "Inconnu")
                        score = rank.get("score", 0)
                        st.text(f"{index}. {user_id} - {score} points")

get_rankings()
display_rankings()

def send_message(message):
    """Envoie un message au chat."""
    if message:  # On ne fait rien si le message est vide
        # Utiliser le nom d'utilisateur authentifié à partir du module auth
        username = auth.name if auth.authentication_status else "Anonyme"
        db.collection("chats").add({
            "username": username,
            "message": message,
            "timestamp": firestore.SERVER_TIMESTAMP  # Utilise l'horodatage du serveur
        })

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
            message = st.text_input("Message", key='chat_message')
            submit_button = st.form_submit_button("Envoyer")
            if submit_button and message:
                send_message(message)
                st.rerun()  # Rafraîchir après l'envoi du message
        
        # Afficher les messages
        for message in messages_list:
            message_data = message.to_dict()
            st.write(f"**{message_data['username']}**: {message_data['message']}")

display_chat()
