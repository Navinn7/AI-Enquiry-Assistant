# QuAnHack Educational Enquiry Assistant
### RAG-powered Telegram Bot · Groq LLM · ChromaDB

---

## 🚀 What This Does

A Telegram chatbot for educational institutions that:

- **Answers queries** about courses, fees, schedules, and eligibility using RAG (your own documents)  
- **Captures leads** through a structured multi-step conversation  
- **Sends follow-up messages** automatically after a configurable delay  
- **Stores lead data** in a local database and exports it to Excel  

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


---


### STEP 4 — Configure your .env file

Edit the `.env` file in the project root:

```env
GROQ_API_KEY=your_api_key_here
TELEGRAM_BOT_TOKEN=your_telegram_bot_token
```

---

### STEP 5— Add your documents

Place your institution's documents inside the `docs/` folder:
- Course brochures (PDF)
- Fee structure (PDF or .txt)
- FAQ documents (.txt or .md)
- Schedules, eligibility criteria


---

### STEP 6 — Build the knowledge base

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


### STEP 7 — Start the Telegram bot

```bash
python telegram_bot.py
```


---


### STEP 8 — Chat with the bot


---


## How the RAG Works

```
User message
     ↓
Embed query (all-MiniLM-L6-v2)
     ↓
Search ChromaDB → top 6 relevant chunks from your docs
     ↓
Send [chunks + question] to Groq LLM
     ↓
Groq generates a grounded answer
     ↓
Reply sent via Telegram
```

The LLM only uses your documents to answer — it won't hallucinate fees or dates.

---
