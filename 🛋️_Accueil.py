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
        'Get Help': 'https://www.queez.com/help',
        'Report a bug': "https://www.queez.com/bug",
        'About': "# Oe c'est Greg. J'ai fait la *meilleur* app!"
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
        rankings = db.collection("rank").order_by("score", direction=firestore.Query.DESCENDING).stream()
        return [(rank.to_dict().get("user_id", "Inconnu"), rank.to_dict().get("score", 0), rank.to_dict().get("mode_de_jeu", "Inconnu"), rank.to_dict().get("temps_total", 0)) for rank in rankings]
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
        for index, (user_id, score, temps_total, mode_de_jeu) in enumerate(top_rankings, start=1):
            top_ranking_markdown += f"{index}. **{user_id}** - {score} points\n"
        
        # Afficher le classement des 10 premiers
        st.markdown(top_ranking_markdown)

        # Si il y a plus que 10 classements, permettre de défiler pour voir les autres
        if len(rankings) > 10:
            with st.container():
                st.write("Voir plus de classements...")
                for index, (user_id, score) in enumerate(rankings[10:], start=11):
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
