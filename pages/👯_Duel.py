import streamlit as st
from main import init_firestore
import auth

db = init_firestore()

def creer_session_duel(nom_session, nom_utilisateur, mode_de_jeu):
    session_data = {
        "nom": nom_session,
        "joueur_1": nom_utilisateur,  # Remplacer par le nom du joueur si disponible
        "joueur_2": "",
        "point_joueur_1": 0,
        "point_joueur_2": 0,
        "question_valide_joueur_1": [],
        "question_valide_joueur_2": [],
        "session_lancer": False,
        "mode_de_jeu": mode_de_jeu  # Ajout du mode de jeu
    }
    # Créer un nouveau document dans Firestore
    db.collection("session").document(nom_session).set(session_data)

# Fonction pour rejoindre une session de duel
def rejoindre_session_duel(id_session):
    # Logique pour rejoindre une session dans Firestore
    pass

# Fonction pour afficher les sessions disponibles
def afficher_sessions_duel():
    sessions = db.collection("session").stream()  # Récupérer les sessions de Firestore
    for session in sessions:
        session_data = session.to_dict()
        if session_data["session_lancer"] == False and session_data["joueur_2"] == "":
            st.write(f"Session: {session_data['nom']}, Mode: {session_data['mode_de_jeu']}")
            if st.button(f"Rejoindre {session_data['nom']}", key=session.id):
                rejoindre_session_duel(session.id)
                st.session_state['session_rejointe'] = True
                st.session_state['current_session'] = session_data
                st.rerun()

# Affichage dans la barre latérale pour créer une session
if 'session_creee' not in st.session_state:
    mode_choisi = st.sidebar.selectbox("Choisir le mode de jeu", ["cyber", "litterature", "geographie", "science", "Extrème"], key="mode_choisi_duel")
    nom_session = st.sidebar.text_input("Nom de la session", key="nom_session_duel")
    if st.sidebar.button("Créer une session Duel", key="creer_session_duel"):
        nom_utilisateur = auth.name  # Assurez-vous que auth.name est correctement défini
        creer_session_duel(nom_session, nom_utilisateur, mode_choisi)
        st.session_state['session_creee'] = True
        st.sidebar.write("Session créée avec succès.")
        st.rerun()

# Affichage des sessions disponibles pour rejoindre
if 'session_rejointe' not in st.session_state:
    afficher_sessions_duel()

# Gestion de la partie en mode Duel
if st.session_state.get('session_creee') or st.session_state.get('session_rejointe'):
    # Logique du jeu pour le mode Duel
    pass

# Réinitialiser l'état de la session
if st.button("Fermer la partie"):
    # Réinitialiser les états session_creee et session_rejointe
    del st.session_state['session_creee']
    del st.session_state['session_rejointe']
