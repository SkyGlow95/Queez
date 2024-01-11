import streamlit as st
from firebase_admin import credentials, firestore, initialize_app, get_app, App
import uuid
import hashlib
import random

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
