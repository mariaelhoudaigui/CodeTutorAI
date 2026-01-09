import streamlit as st
import requests
from streamlit_monaco_editor import st_monaco

# -------------------------------------------------------------------
# CONFIG
# -------------------------------------------------------------------
st.set_page_config(page_title="Tuteur IA", page_icon="🐍", layout="wide")

API_CHAT = "http://127.0.0.1:8080/chat"
API_EXEC = "http://127.0.0.1:8080/execute"
API_QUIZ = "http://127.0.0.1:8080/quiz"

st.title("Tuteur IA — Coding")

# -------------------------------------------------------------------
# SESSION
# -------------------------------------------------------------------
if "messages" not in st.session_state:
    st.session_state.messages = []
if "latest_question" not in st.session_state:
    st.session_state.latest_question = ""
if "latest_tutorial" not in st.session_state:
    st.session_state.latest_tutorial = ""
if "quiz" not in st.session_state:
    st.session_state.quiz = []

# -------------------------------------------------------------------
# LAYOUT
# -------------------------------------------------------------------
col_ide, col_chat = st.columns([1, 1.6])

# ===================================================================
# CHATBOT COLONNE
# ===================================================================
with col_chat:
    st.subheader("Chatbot Coding")

    # Historique du chat
    chat_box = st.empty()
    with chat_box.container():
        for msg in st.session_state.messages:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

    # Input utilisateur
    if prompt := st.chat_input("Pose ta question..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        st.session_state.latest_question = prompt  # mémoriser la dernière question

        with st.chat_message("user"):
            st.markdown(prompt)

        # Appel API FastAPI pour générer tutoriel
        with st.chat_message("assistant"):
            with st.spinner("En cours..."):
                try:
                    response = requests.post(API_CHAT, json={"message": prompt})
                    if response.status_code == 200:
                        ai = response.json()["response"]
                        st.session_state.latest_tutorial = ai
                    else:
                        ai = f"Erreur API : {response.text}"
                except Exception:
                    ai = "Impossible de contacter le serveur FastAPI."
                st.markdown(ai)
                st.session_state.messages.append({"role": "assistant", "content": ai})

# ===================================================================
# IDE COLONNE
# ===================================================================
with col_ide:
    st.subheader("IDE Multilangage")

    LANGAGES = {
        "Python": "python",
        "JavaScript": "javascript",
        "C": "c",
        "Java": "java",
        "Go": "go",
        "Ruby": "ruby",
        "PHP": "php",
    }

    langage = st.selectbox("Choisir un langage :", list(LANGAGES.keys()))
    monaco_lang = LANGAGES[langage]

    code_default = {
        "Python": "print('Hello Python!')",
        "JavaScript": "console.log('Hello JS!')",
        "C": "#include <stdio.h>\nint main(){ printf(\"Hello C!\"); return 0; }",
        "Java": "class Main{ public static void main(String[] args){ System.out.println(\"Hello Java!\"); }}",
        "Go": "package main\nimport \"fmt\"\nfunc main(){ fmt.Println(\"Hello Go!\") }",
        "Ruby": "puts 'Hello Ruby!'",
        "PHP": "<?php echo 'Hello PHP!'; ?>"
    }

    code = st_monaco(
        value=code_default[langage],
        language=monaco_lang,
        theme="vs-dark",
        height="350px"
    )

    if st.button("▶️ Run", type="primary"):
        try:
            res = requests.post(API_EXEC, json={
                "language": langage.lower(),
                "code": code
            })
            if res.status_code == 200:
                st.subheader("Résultat :")
                st.code(res.json().get("output", ""))
            else:
                st.error(f"Erreur API : {res.text}")
        except Exception as e:
            st.error(f"Erreur de communication : {e}")

    # ===================================================================
    # QUIZ FIXE SOUS IDE
    # ===================================================================
    st.subheader("Quiz basé sur votre dernière question")

    if st.session_state.latest_question:
        if st.button("Start Quiz"):
            try:
                res = requests.post(API_QUIZ, json={
                    "tutorial_text": st.session_state.latest_question,
                    "num_questions": 5
                })
                if res.status_code == 200:
                    st.session_state.quiz = res.json()["quiz"]
                else:
                    st.error(f"Erreur API : {res.text}")
            except Exception as e:
                st.error(f"Erreur communication : {e}")

    # Affichage du quiz si généré
    if st.session_state.quiz:
        score = 0
        for i, q in enumerate(st.session_state.quiz):
            st.markdown(f"**Q{i+1}: {q['question']}**")
            user_choice = st.radio("", q["options"], key=f"q{i}")
            if user_choice == q["answer"]:
                score += 1

        if st.button("Valider le Quiz"):
            st.success(f"Votre score : {score} / {len(st.session_state.quiz)}")
