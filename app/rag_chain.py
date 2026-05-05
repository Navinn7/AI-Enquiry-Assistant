"""
rag_chain.py  –  RAG pipeline with conversation memory.
"""

import os
from pathlib import Path
from collections import defaultdict
from dotenv import load_dotenv

load_dotenv()

from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage

CHROMA_DIR       = Path(__file__).parent.parent / "chroma_db"
INSTITUTION_NAME = os.getenv("INSTITUTION_NAME", "Our Academy")

chat_histories: dict[str, list] = defaultdict(list)

RAG_PROMPT_TEMPLATE = """You are a helpful admissions assistant for {institution}.

Answer the student's question using the information provided below.
If the information contains the answer, give a complete and helpful response.
If the answer is not available, say: "I don't have that information right now. Our admissions team can help. Type contact to get connected."

Rules:
- Use ONLY the information below. Do not use outside knowledge.
- NEVER mention the word "context" in your reply. Never say "the provided context" or "based on the context".
- Speak naturally as if you know the answer yourself.
- Do not use markdown symbols like asterisks, hashes, or underscores.
- Use plain text only with line breaks to separate information.
- Keep replies under 200 words.
- Never make up fees, dates, or eligibility criteria.
- If asked to list courses, list ALL courses mentioned in the information below without saying some may be missing.

Information:
{context}"""


def _format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)


class RAGChain:
    def __init__(self):
        self._retriever = None
        self._vectordb  = None
        self._llm       = None
        self._embeddings = None

    def _build(self):
        self._embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

        self._vectordb = Chroma(
            persist_directory=str(CHROMA_DIR),
            embedding_function=self._embeddings,
            collection_name="institution_kb",
        )

        self._retriever = self._vectordb.as_retriever(search_kwargs={"k": 6})

        self._llm = ChatGroq(
            model="llama-3.3-70b-versatile",
            temperature=0.2,
            max_tokens=512,
            api_key=os.getenv("GROQ_API_KEY"),
        )

    def ask(self, question: str, phone: str = "default") -> str:
        phone = str(phone)

        if self._retriever is None:
            if not CHROMA_DIR.exists():
                return (
                    "Knowledge base not set up yet. "
                    "Please run python ingest.py first."
                )
            self._build()

        try:
            # Check relevance using similarity score BEFORE calling LLM
            results = self._vectordb.similarity_search_with_score(question, k=6)
            print(f"[SCORE CHECK] '{question}' → best score: {results[0][1]:.4f}")

            # Chroma L2 distance — lower means more similar
            # Score above 1.5 means the question does not match anything in our docs
            if not results or results[0][1] > 1.4:
                return (
                    "I can only answer questions related to QuAnHack Academy "
                    "courses, fees, schedules, eligibility, and admissions.\n\n"
                    "I don't have information about that topic. "
                    "Type hi to see what I can help you with."
                )

            # Relevant — build context from retrieved docs
            docs = [r[0] for r in results]
            context = _format_docs(docs)

            history = chat_histories[phone][-6:]

            system_content = RAG_PROMPT_TEMPLATE.format(
                institution=INSTITUTION_NAME,
                context=context,
            )

            messages = [SystemMessage(content=system_content)]
            messages.extend(history)
            messages.append(HumanMessage(content=question))

            response = self._llm.invoke(messages)
            result = response.content.strip()

            chat_histories[phone].append(HumanMessage(content=question))
            chat_histories[phone].append(AIMessage(content=result))

            if len(chat_histories[phone]) > 10:
                chat_histories[phone] = chat_histories[phone][-10:]

            return result

        except Exception as e:
            import traceback
            traceback.print_exc()
            print(f"[RAG ERROR] {e}")
            return (
                "Sorry, I ran into a technical issue. "
                "Please try again or type contact to speak with our team."
            )


rag_chain = RAGChain()


def ask_rag(question: str, phone: str = "default") -> str:
    return rag_chain.ask(question, str(phone))