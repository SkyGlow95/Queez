import streamlit as st
from firebase_admin import credentials, firestore, initialize_app, get_app, App
from main import init_firestore
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

db = init_firestore()

auth.name, auth.authentication_status, auth.username = auth.authenticator.login('Login', 'main')

if auth.authentication_status:
    st.session_state['name'] = auth.name  # Stocker le nom dans l'état de session
    auth.authenticator.logout('Logout', 'main', key='unique_logout_key')
    st.write(f'Bienvenue {auth.name}')
    # Ici, vous pouvez ajouter le contenu de votre application personnelle
elif auth.authentication_status == False:
    st.error('Nom d’utilisateur/mot de passe incorrect')
elif auth.authentication_status is None:
    st.warning('Veuillez entrer votre nom d’utilisateur et votre mot de passe')

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

get_rankings()
display_rankings()
