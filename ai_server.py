import os
import re
import json
import urllib.request
import urllib.parse
from typing import List, Dict
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI(title="SudheerQK Real Conversational AI")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["POST", "GET", "OPTIONS"],
    allow_headers=["*"],
)

SYSTEM_PERSONA = """You are Sudheer's Architecture AI Assistant, an intelligent, warm, and natural conversational AI built by Sudheer Kumar on his self-hosted Apple Silicon M1 server (FastAPI + Caddy + Cloudflare Tunnel + PostgreSQL).

Facts about Sudheer Kumar (use ONLY when relevant to the user's question):
- Name: Sudheer Kumar (Nutanix Database Specialist & Infrastructure Engineer based in Riyadh, Saudi Arabia; deployed at Bank AlJazira via Maalim Al Khobra Company; previously Cognizant & Softenger UAE).
- Certifications: EnterpriseDB (EDB) Postgres AI Database Advanced v18 Certified (Credly verified).
- Core Expertise: SQL Server Always On Availability Groups (multi-subnet, WSFC quorum, zero-downtime patching), Nutanix Cloud & NDB DBaaS (v2.10.1 / v2.11.1 Production/DR upgrades, Time Machine SLA, zero-byte clones), PostgreSQL 14-18 with pg_vector (IVFFlat/HNSW), PgBouncer, WAL streaming, and PowerShell/Python automation.
- Self-Hosted Stack: sudheerqk.com and his Private File Vault run on an Apple Silicon M1 server using Caddy, Cloudflare Zero-Trust Tunnel, FastAPI, and PostgreSQL.
- Contact: contact@sudheerqk.com

Behavior rules:
1. Respond naturally like a real human-like AI assistant. If the user says "hi", "helllo", or "good morning", greet them warmly and ask how you can help — do NOT dump Sudheer's resume unless asked.
2. If the user asks about any general topic (countries, science, coding, career advice, etc.), answer helpfully, accurately, and engagingly using your own knowledge and any Live Web Context provided.
3. Keep answers clean, well-structured, and concise (2-5 sentences or neat bullet points). You may use simple HTML tags like <strong> and <br> for readability."""

class ChatTurn(BaseModel):
    role: str
    content: str

class AskRequest(BaseModel):
    question: str
    history: List[ChatTurn] = []

def search_live_web(query: str) -> str:
    cleaned = re.sub(r"[^\w\s\-\.]", "", query.lower()).strip()
    stop = {"i", "want", "to", "know", "something", "about", "what", "is", "are", "the", "a", "an", "tell", "me", "explain", "can", "you", "please"}
    topic = " ".join([w for w in cleaned.split() if w not in stop]) or cleaned
    if len(topic) < 3 or any(p in cleaned for p in ["your name", "who are you", "about you", "hi", "hello", "helllo", "morning", "evening"]):
        return ""
    try:
        wiki_slug = urllib.parse.quote(topic.title().replace(" ", "_"))
        wiki_url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{wiki_slug}"
        req = urllib.request.Request(wiki_url, headers={"User-Agent": "SudheerQK-AI/4.0"})
        with urllib.request.urlopen(req, timeout=2.5) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            if data.get("extract") and data.get("type") != "disambiguation":
                return data["extract"][:700]
    except Exception:
        pass
    return ""

@app.get("/health")
def health():
    return {"status": "online", "engine": "ollama-chat-rag"}

@app.post("/ask")
@app.post("/api/ask")
async def ask_ai(payload: AskRequest):
    q = payload.question.strip()
    web_ctx = search_live_web(q)

    messages = [{"role": "system", "content": SYSTEM_PERSONA}]
    for turn in payload.history[-6:]:
        messages.append({"role": turn.role, "content": turn.content})

    user_content = f"{q}\n\n[Live Web Context: {web_ctx}]" if web_ctx else q
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
                return {"answer": reply, "source": "llm+rag"}
    except Exception as e:
        pass

    if web_ctx:
        return {"answer": web_ctx, "source": "web"}

    return {
        "answer": "Hey! How can I help you today? Ask me anything — from Sudheer's database architecture to general tech or world topics.",
        "source": "fallback"
    }
