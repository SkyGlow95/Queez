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
# Affichage des sessions disponibles pour rejoindre
if 'session_rejointe' not in st.session_state:
    afficher_sessions_duel()

if st.session_state.get('session_creee') or st.session_state.get('session_rejointe'):
    # Assurez-vous que session_data est bien défini dans st.session_state
    if 'current_session' in st.session_state:
        session_data = st.session_state['current_session']
        st.sidebar.write(f"Session: {session_data['nom']}")
        st.sidebar.write(f"Joueur 1: {session_data['joueur_1']}")
        st.sidebar.write(f"Joueur 2: {session_data.get('joueur_2', 'En attente...')}")
        st.sidebar.write(f"Mode: {session_data['mode_de_jeu']}")

        if session_data.get('joueur_2') and st.sidebar.button("Lancer la partie"):
            # Logique pour démarrer la partie
            pass
    else:
        st.sidebar.write("Aucune session sélectionnée ou créée.")

# Affichage des sessions disponibles pour rejoindre
def rejoindre_session_duel(id_session):
    # Mise à jour de la session dans Firestore pour ajouter le joueur
    db.collection("session").document(id_session).update({"joueur_2": auth.name})
    # Autres mises à jour si nécessaire

if st.session_state.get('session_creee') or st.session_state.get('session_rejointe'):
    session_data = st.session_state.get('current_session', {})
    st.sidebar.write(f"Session: {session_data['nom']}")
    st.sidebar.write(f"Joueur 1: {session_data['joueur_1']}")
    st.sidebar.write(f"Joueur 2: {session_data.get('joueur_2', 'En attente...')}")
    st.sidebar.write(f"Mode: {session_data['mode_de_jeu']}")

    if session_data.get('joueur_2') and st.sidebar.button("Lancer la partie"):
        # Logique pour démarrer la partie
        pass

# Gestion de la partie en mode Duel
if st.session_state.get('session_creee') or st.session_state.get('session_rejointe'):
    # Logique du jeu pour le mode Duel
    pass

# Réinitialiser l'état de la session
if st.button("Fermer la partie"):
    # Réinitialiser les états session_creee et session_rejointe
    del st.session_state['session_creee']
    del st.session_state['session_rejointe']
