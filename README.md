# AI Tutor – Code Learning and Execution Application

## Project Description

**AI Tutor** is an interactive web application that acts as a **specialized tutor in programming and computer science**. It allows users to:

- Ask questions about programming and receive **detailed and structured tutorials**.
- Execute code in different languages via an integrated API.
- Generate **interactive quizzes** based on tutorials to reinforce learning.
- Navigate through a user-friendly interface with multiple pages: **Home, Chat, Quiz**.

The application combines several technologies:

- **Backend**: FastAPI for chat, code execution, and quiz generation endpoints.
- **Frontend**: Streamlit for the user interface.
- **RAG (Retrieval-Augmented Generation)**: FAISS + HuggingFaceEmbeddings to enrich answers with existing documents.
- **Generative AI**: Google Gemini (Gemini Flash) to generate structured tutorials and quizzes.

---

## Main Features

1. **AI Tutorial Chat**
   - Ask programming-related questions.
   - The AI politely refuses questions outside its domain.
   - Generates structured tutorials in 3 levels: beginner, intermediate, advanced.

2. **Code Execution**
   - Supports multiple languages: Python, JavaScript, C, Java, Go, Ruby, PHP.
   - Uses the Piston API to execute code on the server side.

3. **Automatically Generated Quiz**
   - From the tutorial text, a 10-question multiple-choice quiz is generated.
   - Answers are formatted in JSON for easy integration into the interface.

4. **RAG (Retrieval-Augmented Generation)**
   - Uses a local corpus `geeks_texts.json` to improve responses.
   - Embeddings generated with HuggingFace + FAISS to retrieve relevant documents.

---

## Installation

### 1. Clone the project

```bash
git clone <PROJECT_URL>
````

### 2. Create a virtual environment

```bash
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
.venv\Scripts\activate     # Windows
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

Create a `.env` file at the project root and add:

```env
GOOGLE_API_KEY=YOUR_GEMINI_API_KEY
```

### 5. Generate the JSON corpus

The `scraper.py` file must be run **only once** to generate `geeks_texts.json`, which will be used by the RAG:

```bash
python scraper.py
```

---

## Running the Application

### FastAPI Backend

```bash
uvicorn main:app --reload
```

* The API will be available at: `http://127.0.0.1:8000`
* Available endpoints:

  * `/chat` : ask a question to the AI tutor
  * `/execute` : execute code
  * `/generate_quiz` : generate a quiz from a tutorial

### Streamlit Frontend

```bash
streamlit run home.py
```

* The main interface (Home) allows navigation to:

  * **Chat**
  * **Quiz**
  * **Code Execution**

---

## Usage

1. **Tutorial Chat**

   * Enter a programming question.
   * Receive a structured tutorial in 3 levels.

2. **Code Execution**

   * Select the language and paste the code.
   * Click `Run` to see the result.

3. **Quiz**

   * Generate a 10-question multiple-choice quiz from the last tutorial.

---

## Screenshots

### Home Page

![Home](home.png)

### Chat Page

![Chat](chat.png)

### Quiz Page

![Quiz](quiz.png)

---

## Contributions

Contributions are welcome!
Please respect coding standards and indicate your changes in separate branches.
