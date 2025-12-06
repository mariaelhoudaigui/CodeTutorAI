from fastapi import FastAPI
from pydantic import BaseModel
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_core.prompts import PromptTemplate
import google.generativeai as genai
from dotenv import load_dotenv
import os
load_dotenv()
# --- CONFIGURATION GEMINI ---
# Remplace par ta vraie clé
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

genai.configure(api_key=GOOGLE_API_KEY)
MODEL_NAME = "gemini-flash-latest"
model = genai.GenerativeModel(
    model_name=MODEL_NAME,
    system_instruction="Tu es un assistant expert en programmation. Tu crées des tutoriels clairs, structurés et pédagogiques avec des exemples de code concrets et bien commentés."
)

# --- FASTAPI ---
app = FastAPI(title="Backend Chat IA")

class ChatRequest(BaseModel):
    message: str

# --- RAG (FAISS) ---
embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
vector_store = FAISS.from_texts(["Bienvenue dans le tutoriel."], embeddings)
retriever = vector_store.as_retriever(search_type="similarity", search_kwargs={"k": 4})

prompt_template = PromptTemplate(
    input_variables=["context", "question"],
    template="Contexte: {context}\nQuestion: {question}\nRéponse experte:"
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
    vector_store.add_texts([user_msg]) 
    docs = retriever.invoke(user_msg)
    context_text = "\n".join([d.page_content for d in docs])
    
    final_prompt = prompt_template.format(context=context_text, question=user_msg)
    
    # Génération
    response_text = generate_gemini(final_prompt)
    
    return {"response": response_text}

# Pour lancer : uvicorn back:app --reload