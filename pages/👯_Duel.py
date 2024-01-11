import streamlit as st
from main import init_firestore

db = init_firestore()

# Fonction pour créer une session de duel
def creer_session_duel(nom_session, mode_de_jeu):
    # Logique pour créer une session dans Firestore
    pass

# Fonction pour rejoindre une session de duel
def rejoindre_session_duel(id_session):
    # Logique pour rejoindre une session dans Firestore
    pass

# Fonction pour afficher les sessions disponibles
def afficher_sessions_duel():
    # Récupérer les sessions de Firestore et les afficher
    pass

# Affichage dans la barre latérale pour créer une session
if 'session_creee' not in st.session_state:
    mode_choisi = st.sidebar.selectbox("Choisir le mode de jeu", ["cyber", "litterature", "geographie", "science", "Extrème"])
    if mode_choisi == "Duel":
        nom_session = st.sidebar.text_input("Nom de la session")
        if st.sidebar.button("Créer une session Duel"):
            creer_session_duel(nom_session, mode_choisi)
            st.session_state['session_creee'] = True

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
