import os
import re
import json
import urllib.request
import urllib.parse
from typing import List
import psycopg2
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI(title="SudheerQK pg_vector + Ollama AI")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["POST", "GET", "OPTIONS"],
    allow_headers=["*"],
)

SYSTEM_PERSONA = """You are Sudheer's Architecture AI Assistant, an intelligent, warm, and natural conversational AI built by Sudheer Kumar on his self-hosted Apple Silicon M1 server (FastAPI + Caddy + Cloudflare Tunnel + PostgreSQL pg_vector + Ollama).

Behavior rules:
1. Respond naturally like a real conversational AI assistant. If the user greets you ("hi", "helllo", "good morning", "whatsup"), reply warmly and ask how you can help — do NOT dump Sudheer's bio unless asked.
2. When [Retrieved pg_vector Knowledge] is provided and relevant to the user's question, weave those exact technical facts seamlessly into your answer.
3. When [Live Web Context] is provided for general world, science, or tech questions, answer accurately and engagingly using that context and your own knowledge.
4. Keep answers clean, well-structured, and concise (2-5 sentences or neat bullet points). You may use simple HTML tags like <strong> and <br> for readability."""

class ChatTurn(BaseModel):
    role: str
    content: str

class AskRequest(BaseModel):
    question: str
    history: List[ChatTurn] = []

def get_embedding(text: str):
    payload = json.dumps({"model": "nomic-embed-text", "prompt": text}).encode("utf-8")
    req = urllib.request.Request("http://127.0.0.1:11434/api/embeddings", data=payload, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=8) as resp:
        return json.loads(resp.read().decode("utf-8"))["embedding"]

def query_pgvector(question: str, top_k: int = 3) -> list[str]:
    try:
        vec = get_embedding(question)
        vec_str = "[" + ",".join(f"{x:.6f}" for x in vec) + "]"
        conn = psycopg2.connect(dbname="postgres", user="sudheerkumar", host="127.0.0.1", connect_timeout=2)
        cur = conn.cursor()
        cur.execute(
            "SELECT topic, content, (embedding <=> %s::vector) AS dist FROM portfolio_knowledge ORDER BY dist ASC LIMIT %s",
            (vec_str, top_k)
        )
        rows = cur.fetchall()
        cur.close()
        conn.close()
        return [f"{r[0]}: {r[1]}" for r in rows if r[2] < 0.74]
    except Exception:
        return []

def search_live_web(query: str) -> str:
    cleaned = re.sub(r"[^\w\s\-\.]", "", query.lower()).strip()
    stop = {"i", "want", "to", "know", "something", "about", "what", "is", "are", "the", "a", "an", "tell", "me", "explain", "can", "you", "please"}
    topic = " ".join([w for w in cleaned.split() if w not in stop]) or cleaned
    if len(topic) < 3 or any(p in cleaned for p in ["your name", "who are you", "about you", "hi", "hello", "helllo", "whatsup", "morning", "evening"]):
        return ""
    try:
        wiki_slug = urllib.parse.quote(topic.title().replace(" ", "_"))
        wiki_url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{wiki_slug}"
        req = urllib.request.Request(wiki_url, headers={"User-Agent": "SudheerQK-AI/5.0"})
        with urllib.request.urlopen(req, timeout=2.5) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            if data.get("extract") and data.get("type") != "disambiguation":
                return data["extract"][:700]
    except Exception:
        pass
    return ""

@app.get("/health")
def health():
    return {"status": "online", "engine": "pgvector+ollama-chat"}

@app.post("/ask")
@app.post("/api/ask")
async def ask_ai(payload: AskRequest):
    q = payload.question.strip()
    rag_chunks = query_pgvector(q, top_k=2)
    web_ctx = "" if rag_chunks else search_live_web(q)

    messages = [{"role": "system", "content": SYSTEM_PERSONA}]
    for turn in payload.history[-6:]:
        messages.append({"role": turn.role, "content": turn.content})

    context_blocks = []
    if rag_chunks:
        context_blocks.append("[Retrieved pg_vector Knowledge:\n" + "\n".join(rag_chunks) + "]")
    if web_ctx:
        context_blocks.append(f"[Live Web Context: {web_ctx}]")

    user_content = f"{q}\n\n" + "\n".join(context_blocks) if context_blocks else q
    messages.append({"role": "user", "content": user_content})

    try:
        req_body = json.dumps({
            "model": os.getenv("OLLAMA_MODEL", "llama3.2:3b"),
            "messages": messages,
            "stream": False,
            "options": {"temperature": 0.65, "num_predict": 320}
        }).encode("utf-8")
        req = urllib.request.Request("http://127.0.0.1:11434/api/chat", data=req_body, headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=18) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            reply = (data.get("message", {}).get("content") or "").strip()
            if reply:
                reply = re.sub(r"\*\*(.*?)\*\*", r"<strong>\1</strong>", reply).replace("\n", "<br>")
                return {"answer": reply, "source": "pgvector+llm" if rag_chunks else "llm+web"}
    except Exception:
        pass

    if rag_chunks:
        return {"answer": rag_chunks[0], "source": "pgvector"}
    if web_ctx:
        return {"answer": web_ctx, "source": "web"}
    return {"answer": "Hey! How can I help you today? Ask me anything about Sudheer's architecture or any general topic.", "source": "fallback"}
