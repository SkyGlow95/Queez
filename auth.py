import streamlit as st
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

# Créer un widget de connexion
name, authentication_status, username = authenticator.login('Login', 'main')

try:
    if authenticator.register_user('Register user', preauthorization=False):
        st.success('User registered successfully')
except Exception as e:
    st.error(e)

if st.session_state["authentication_status"]:
    try:
        if authenticator.update_user_details(st.session_state["username"], 'Update user details'):
            st.success('Entries updated successfully')
    except Exception as e:
        st.error(e)

with open('config.yaml', 'w') as file:
    yaml.dump(config, file, default_flow_style=False)

# Gérer le statut d'authentification
if authentication_status:
    st.session_state['name'] = name  # Stocker le nom dans l'état de session
    authenticator.logout('Logout', 'main', key='unique_logout_key')
    st.write(f'Bienvenue {name}')
    # Ici, vous pouvez ajouter le contenu de votre application personnelle
elif authentication_status == False:
    st.error('Nom d’utilisateur/mot de passe incorrect')
elif authentication_status is None:
    st.warning('Veuillez entrer votre nom d’utilisateur et votre mot de passe')

if st.session_state["authentication_status"]:
    try:
        if authenticator.reset_password(st.session_state["username"], 'Reset password'):
            st.success('Password modified successfully')
    except Exception as e:
        st.error(e)
