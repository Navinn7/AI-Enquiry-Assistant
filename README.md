# QuAnHack Educational Enquiry Assistant
### RAG-powered WhatsApp Bot · Groq LLM · ChromaDB 

---

## What This Does

A WhatsApp chatbot for educational institutions that:
- **Answers queries** about courses, fees, schedules, eligibility using RAG (your own documents)
- **Captures leads** through a friendly multi-step conversation
- **Sends follow-up messages** automatically 24 hours after lead capture
- **Stores everything** in a local SQLite database you can query

---

## Step-by-Step Setup

### STEP 1 — Clone / download the project

```bash
# If you have git:
git clone https://github.com/yourname/enquiry-assistant.git
cd enquiry-assistant

# Or just put all the files into a folder called enquiry-assistant and cd into it
```

---

### STEP 2 — Create a Python virtual environment

```bash
# Create venv
python -m venv venv

# Activate it
# On Windows:
venv\Scripts\activate

# On Mac/Linux:
source venv/bin/activate
```

You should see `(venv)` at the start of your terminal prompt.

---

### STEP 3 — Install dependencies

```bash
pip install -r requirements.txt
```

This installs FastAPI, LangChain, ChromaDB, sentence-transformers, Groq SDK, Twilio, Celery, etc.
It may take 3–5 minutes the first time.

---

### STEP 4 — Get your API keys

#### A. Groq API Key (FREE)
1. Go to https://console.groq.com
2. Sign up / log in
3. Click **API Keys** → **Create API Key**
4. Copy the key (starts with `gsk_`)


### STEP 5 — Configure your .env file

Edit the `.env` file in the project root:

```env
GROQ_API_KEY=gsk_your_actual_key_here

INSTITUTION_NAME=QuAnHack Academy

```

---

### STEP 6 — Add your documents

Place your institution's documents inside the `docs/` folder:
- Course brochures (PDF)
- Fee structure (PDF or .txt)
- FAQ documents (.txt or .md)
- Schedules, eligibility criteria


---

### STEP 7 — Build the knowledge base

```bash
python ingest.py
```

Expected output:
```
📂  Loading documents from  /path/to/docs …
✅  Loaded 45 document page(s)
✂️   Split into 120 chunks
🔢  Embedding with sentence-transformers/all-MiniLM-L6-v2 …
💾  Saving vector store to  /path/to/chroma_db …
🎉  Done! 120 chunks indexed into ChromaDB.
```

> Re-run this whenever you update your documents.

---




