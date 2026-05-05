# QuAnHack Educational Enquiry Assistant
### RAG-powered WhatsApp Bot · Groq LLM · ChromaDB · FastAPI

---

## What This Does

A WhatsApp chatbot for educational institutions that:
- **Answers queries** about courses, fees, schedules, eligibility using RAG (your own documents)
- **Captures leads** through a friendly multi-step conversation
- **Sends follow-up messages** automatically 24 hours after lead capture
- **Stores everything** in a local SQLite database you can query

---

## Prerequisites (install these first)

| Tool | Purpose | Install |
|------|---------|---------|
| Python 3.10+ | Runtime | python.org |
| pip | Package manager | comes with Python |
| Redis | Task queue for follow-ups | see Step 4 |
| ngrok | Expose local server to internet | ngrok.com |

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

#### B. Twilio WhatsApp Sandbox (FREE for testing)
1. Go to https://www.twilio.com and sign up
2. In the Console, go to **Messaging → Try it out → Send a WhatsApp message**
3. You'll see a sandbox number (like `+1 415 523 8886`) and a join code
4. Send the join code from your WhatsApp to that number to activate the sandbox
5. From the Console home page, copy:
   - **Account SID** (starts with `AC`)
   - **Auth Token**
6. Your Twilio WhatsApp number is the sandbox number

---

### STEP 5 — Configure your .env file

Edit the `.env` file in the project root:

```env
GROQ_API_KEY=gsk_your_actual_key_here
TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
TWILIO_AUTH_TOKEN=your_auth_token_here
TWILIO_WHATSAPP_NUMBER=+14155238886
INSTITUTION_NAME=QuAnHack Academy
REDIS_URL=redis://localhost:6379/0
BASE_URL=https://abc123.ngrok-free.app   # fill this in after Step 8
```

---

### STEP 6 — Add your documents

Place your institution's documents inside the `docs/` folder:
- Course brochures (PDF)
- Fee structure (PDF or .txt)
- FAQ documents (.txt or .md)
- Schedules, eligibility criteria

A sample file `docs/quanhack_faq.txt` is already included to get you started.

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

### STEP 8 — Test locally (no WhatsApp needed)

Before connecting WhatsApp, test the bot in your terminal:

```bash
python test_local.py
```

Try these messages:
```
You: hi
You: What are the fees for the Data Science course?
You: When does the next Python batch start?
You: I want to enroll
You: John Smith
You: Data Science
You: john@gmail.com
```

---

### STEP 9 — Start the FastAPI server

Open a **new terminal** (keep test_local.py terminal separate):

```bash
# Make sure venv is active
source venv/bin/activate   # Mac/Linux
# or: venv\Scripts\activate  # Windows

uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Visit http://localhost:8000/health — you should see `{"status": "ok"}`.

---

### STEP 10 — Expose your server with ngrok

Open **another new terminal**:

```bash
ngrok http 8000
```

You'll see output like:
```
Forwarding   https://abc123def.ngrok-free.app → http://localhost:8000
```

Copy that `https://...ngrok-free.app` URL. Update your `.env`:
```
BASE_URL=https://abc123def.ngrok-free.app
```

---

### STEP 11 — Connect Twilio to your server

1. Go to Twilio Console → **Messaging → Settings → WhatsApp Sandbox Settings**
2. In **"When a message comes in"** field, paste:
   ```
   https://abc123def.ngrok-free.app/webhook
   ```
3. Set method to **HTTP POST**
4. Click **Save**

---

### STEP 12 — Start Redis (for follow-up scheduling)

#### Mac:
```bash
brew install redis
brew services start redis
```

#### Ubuntu/Linux:
```bash
sudo apt install redis-server
sudo systemctl start redis
```

#### Windows:
Download from https://github.com/microsoftarchive/redis/releases
Or use WSL (recommended).

Test Redis: `redis-cli ping` should return `PONG`.

---

### STEP 13 — Start Celery worker (for follow-up messages)

Open **another terminal**:

```bash
source venv/bin/activate
celery -A app.tasks worker --loglevel=info
```

You should see the worker start and connect to Redis.

---

### STEP 14 — Send a WhatsApp message!

From your phone (the one you connected to the Twilio sandbox):
- Send "hi" to the Twilio sandbox number
- You should get the welcome message back within seconds!

---

## Admin Endpoints

Once the server is running, you can view data in your browser:

| URL | What it shows |
|-----|--------------|
| http://localhost:8000/health | Server health |
| http://localhost:8000/leads | All captured leads (JSON) |
| http://localhost:8000/history/whatsapp%3A%2B919876543210 | Chat history for a number |
| http://localhost:8000/docs | Interactive API docs (Swagger) |

---

## Project Structure

```
enquiry-assistant/
├── app/
│   ├── __init__.py          ← package marker
│   ├── main.py              ← FastAPI app + routes
│   ├── intent_handler.py    ← message routing logic
│   ├── rag_chain.py         ← RAG pipeline (Groq + ChromaDB)
│   ├── lead_flow.py         ← multi-step lead capture
│   ├── tasks.py             ← Celery follow-up tasks
│   └── database.py          ← SQLAlchemy models (SQLite)
├── docs/                    ← put your PDFs & FAQs here
│   └── quanhack_faq.txt     ← sample knowledge base
├── chroma_db/               ← auto-generated vector store (after ingest)
├── ingest.py                ← run once to build vector store
├── test_local.py            ← test without WhatsApp
├── requirements.txt
├── .env                     ← your secrets
├── leads.db                 ← auto-generated SQLite DB
└── README.md
```

---

## How the RAG Works

```
User message
     ↓
Embed query (all-MiniLM-L6-v2)
     ↓
Search ChromaDB → top 4 relevant chunks from your docs
     ↓
Send [chunks + question] to Groq (llama3-8b-8192)
     ↓
Groq generates a grounded answer
     ↓
Reply sent via Twilio WhatsApp
```

The LLM only uses your documents to answer — it won't hallucinate fees or dates.

---

## Troubleshooting

**Q: `ingest.py` gives import errors**
A: Make sure venv is active: `source venv/bin/activate`

**Q: Groq returns an error**
A: Check your `GROQ_API_KEY` in `.env`. Get a free key at console.groq.com.

**Q: WhatsApp messages not arriving**
A: Check ngrok is running and the webhook URL in Twilio is correct and uses HTTPS.

**Q: Redis connection refused**
A: Start Redis: `brew services start redis` (Mac) or `sudo systemctl start redis` (Linux)

**Q: Bot says "Knowledge base not set up"**
A: Run `python ingest.py` first.

---

## Groq Model Options

Change the model in `app/rag_chain.py` → `llm = ChatGroq(model="...")`

| Model | Speed | Quality | Notes |
|-------|-------|---------|-------|
| `llama3-8b-8192` | ⚡ Fastest | Good | Recommended default |
| `llama3-70b-8192` | Medium | Best | Higher quality answers |
| `mixtral-8x7b-32768` | Fast | Very good | Larger context window |
| `gemma-7b-it` | Fast | Good | Google's model |
