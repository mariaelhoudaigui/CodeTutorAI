import streamlit as st
import requests

# Titre de la page
st.set_page_config(page_title="Tuteur IA ", page_icon="🐍")
st.title("Tuteur IA - Coding ")

# URL de ton backend FastAPI
API_URL = "http://127.0.0.1:8000/chat"

# Initialisation de l'historique de chat dans la session
if "messages" not in st.session_state:
    st.session_state.messages = []

# Afficher les messages précédents
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Zone de saisie utilisateur
if prompt := st.chat_input("Posez votre question ..."):
    # 1. Afficher le message de l'utilisateur
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Sauvegarder dans l'historique
    st.session_state.messages.append({"role": "user", "content": prompt})

    # 2. Appeler l'API (Backend)
    with st.chat_message("assistant"):
        with st.spinner("En cours..."):
            try:
                response = requests.post(API_URL, json={"message": prompt})
                
                if response.status_code == 200:
                    ai_response = response.json().get("response", "Pas de réponse.")
                else:
                    ai_response = f"Erreur {response.status_code}: {response.text}"
                
                st.markdown(ai_response)
                
                # Sauvegarder la réponse dans l'historique
                st.session_state.messages.append({"role": "assistant", "content": ai_response})
                
            except requests.exceptions.ConnectionError:
                st.error("Impossible de contacter le serveur. Vérifiez que api.py est lancé.")