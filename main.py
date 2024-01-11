import streamlit as st
from firebase_admin import credentials, firestore, initialize_app, get_app, App

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
