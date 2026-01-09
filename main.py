import io
import uvicorn
import subprocess
import sys
import tempfile
from fastapi import FastAPI
from pydantic import BaseModel
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_core.prompts import PromptTemplate
import google.generativeai as genai
from dotenv import load_dotenv
import os
import json

import requests

load_dotenv()
# --- CONFIGURATION GEMINI ---
# Remplace par ta vraie clé

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

genai.configure(api_key=GOOGLE_API_KEY)
MODEL_NAME = "gemini-flash-latest"
model = genai.GenerativeModel(
    model_name=MODEL_NAME,
    system_instruction=(
        "Tu es un assistant expert en programmation. "
        "Ta mission est de produire des TUTORIELS COMPLETS, STRUCTURÉS et PROGRESSIFS "
        "en 3 niveaux :\n\n"
        "1) Débutant : explication simple, pas à pas, analogies, notions fondamentales, prérequis.\n"
        "2) Intermédiaire : exemples pratiques complets, exercices guidés, erreurs courantes.\n"
        "3) Avancé : architecture pro, bonnes pratiques, optimisation, mini-projet.\n\n"
        "Tu écris dans un style clair, pédagogique, avec des exemples de code commentés." )
)
# --- FASTAPI ---
app = FastAPI(title="Backend Chat IA")

class ChatRequest(BaseModel):
    message: str
class CodeRequest(BaseModel):
    language: str
    code: str


class QuizRequest(BaseModel):
    tutorial_text: str
    num_questions: int = 8  # nombre de questions à générer


# --- Charger les textes depuis le JSON ---
with open("geeks_texts.json", "r", encoding="utf-8") as f:
    all_texts = json.load(f)

# --- RAG (FAISS) ---
embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
vector_store = FAISS.from_texts(all_texts, embeddings)
retriever = vector_store.as_retriever(search_type="similarity", search_kwargs={"k": 4})


prompt_template = PromptTemplate(
    input_variables=["context", "question"],
    template=
        "CONTEXT DOCUMENTAIRE RAG :\n{context}\n\n"
        "QUESTION UTILISATEUR : {question}\n\n"
        "=== CONSIGNES ===\n"
        "Tu dois produire un TUTORIEL COMPLET en respectant la structure suivante :\n"
        "1. Contexte général et but du tutoriel\n"
        "2. Niveau Débutant : bases + exemples simples\n"
        "3. Niveau Intermédiaire : exercices + mini-projet guidé\n"
        "4. Niveau Avancé : concepts experts + optimisation + projet avancé\n"
        "5. Résumé + exercices finaux\n\n"
        "=== RÉPONSE EXPERTE ===\n"
)


def generate_gemini(text):
    try:
        response = model.generate_content(text)
        return response.text
    except Exception as e:
        return f"Erreur API : {str(e)}"

@app.post("/chat")

def chat_endpoint(req: ChatRequest):
    user_msg = req.message
    
    # RAG : On ajoute la question et on cherche le contexte
    docs = retriever.invoke(user_msg)
    context_text = "\n".join([d.page_content for d in docs])
    
    final_prompt = prompt_template.format(context=context_text, question=user_msg)
    
    # Génération
    response_text = generate_gemini(final_prompt)
    
    return {"response": response_text}


# Tu peux garder un mapping, mais avec les noms de langage Piston
LANGUAGE_MAP = {
    "python": "python",
    "javascript": "javascript",
    "c": "c",
    "java": "java",
    "go": "go",
    "ruby": "ruby",
    "php": "php",
}


@app.post("/execute")
def execute_code(req: CodeRequest):

    language = req.language.lower()

    if language not in ["python", "javascript", "java", "c", "go", "rust", "ruby", "php"]:
        return {"output": f"Langage {req.language} non supporté."}

    payload = {
        "language": language,
        "version": "*",  # Piston choisit automatiquement la version la plus récente
        "files": [
            {
                "content": req.code
            }
        ],
        "stdin": ""
    }

    try:
        response = requests.post(
            "https://emkc.org/api/v2/piston/execute",
            json=payload
        )

        if response.status_code != 200:
            return {"output": f"Erreur Piston : {response.status_code} - {response.text}"}

        result = response.json()

        output = result.get("run", {}).get("output", "")

        if not output:
            output = "Aucun résultat."

        return {"output": output.strip()}

    except Exception as e:
        return {"output": f"Erreur API Piston : {e}"}
    
@app.post("/quiz")
def generate_quiz(req: QuizRequest):
    # Prompt simplifié pour Gemini
    prompt_quiz = (
        f"Tu es un expert pédagogique en programmation. "
        f"Génère {req.num_questions} questions de quiz basées uniquement sur ce tutoriel :\n\n"
        f"{req.tutorial_text}\n\n"
        f"Répond **uniquement** avec un JSON strict de la forme :\n"
        f"[{{'question':'Texte de la question','options':['A','B','C','D'],'answer':'A'}}, ...]\n"
        f"Aucune autre explication, aucun texte supplémentaire, seulement le JSON."
    )

    # Appel Gemini
    response_text = generate_gemini(prompt_quiz)

    # Tentative de parsing JSON
    try:
        quiz_json = json.loads(response_text)
        if not isinstance(quiz_json, list):
            raise ValueError("JSON mal formé")
    except Exception as e:
        # Si la génération échoue, renvoyer toujours un JSON vide et le texte brut
        return {
            "quiz": [],
            "error": f"Impossible de générer le quiz correctement: {e}",
            "raw": response_text
        }

    return {"quiz": quiz_json}

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8080)
