import os
import re
import json
import urllib.request
import urllib.parse
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI(title="SudheerQK Architecture AI")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["POST", "GET", "OPTIONS"],
    allow_headers=["*"],
)

KNOWLEDGE_DOCS = [
    {
        "tags": {"edb", "postgres", "postgresql", "v18", "vector", "pg_vector", "cert", "certification", "credly", "pgbouncer"},
        "text": "<strong>EDB Postgres® AI Database Advanced v18 Certified:</strong> Sudheer Kumar is officially certified by EnterpriseDB (verified via Credly) and designs PostgreSQL 14–18 HA clusters, <code>pg_vector</code> IVFFlat/HNSW similarity search indices, PgBouncer connection pooling, and WAL streaming replication."
    },
    {
        "tags": {"nutanix", "ndb", "era", "prism", "ahv", "time machine", "clone", "dbaas", "dr"},
        "text": "<strong>Nutanix Cloud & NDB DBaaS (v2.10.1 / v2.11.1):</strong> Sudheer leads enterprise Nutanix Database Service upgrades across Production and DR clusters, configuring Time Machine SLA policies, zero-byte database clones, and Prism Central REST API automation."
    },
    {
        "tags": {"sql", "mssql", "alwayson", "always on", "ag", "wsfc", "failover", "cluster", "quorum"},
        "text": "<strong>SQL Server Always On Availability Groups:</strong> Enterprise multi-subnet AG topologies (SQL 2012–2022), WSFC quorum and cloud/file witness architectures, zero-downtime rolling upgrades, and T-SQL query plan tuning."
    },
    {
        "tags": {"caddy", "self-host", "self host", "apple", "mac", "server", "vault", "cloudflare", "fastapi", "architecture", "website"},
        "text": "<strong>Self-Hosted Apple Silicon Infrastructure:</strong> <code>sudheerqk.com</code> and Sudheer's Private Vault run 24/7 on a low-power Apple Silicon M1 server using Caddy reverse proxy, Cloudflare Zero-Trust tunnels, FastAPI microservices, and a PostgreSQL + <code>pg_vector</code> backend."
    },
    {
        "tags": {"sudheer", "kumar", "riyadh", "saudi", "bank", "aljazira", "contact", "email", "hire", "role", "experience"},
        "text": "<strong>About Sudheer Kumar:</strong> Nutanix Database Specialist & Infrastructure Engineer based in Riyadh, Saudi Arabia (deployed at Bank AlJazira via Maalim Al Khobra Company; previously Cognizant & Softenger UAE). Available for global architecture consultation at <strong>contact@sudheerqk.com</strong>."
    }
]

STOP_WORDS = {
    "i", "want", "to", "know", "something", "about", "what", "is", "are", "the",
    "a", "an", "tell", "me", "explain", "can", "you", "please", "how", "does",
    "work", "of", "in", "on", "for", "good", "things", "give", "details"
}

class AskRequest(BaseModel):
    question: str

def get_natural_greeting(q_clean: str) -> str | None:
    greetings_map = [
        ("good morning", "Good morning! How can I help you today?"),
        ("good afternoon", "Good afternoon! How can I help you today?"),
        ("good evening", "Good evening! How can I help you today?"),
        ("namaste", "Namaste! How can I help you today?"),
        ("hola", "Hola! How can I help you today?"),
        ("hello", "Hello! How can I help you today?"),
        ("hey", "Hey there! How can I help you today?"),
        ("hi", "Hi! How can I help you today?"),
    ]
    words = q_clean.split()
    if len(words) <= 4:
        for trigger, reply in greetings_map:
            if q_clean == trigger or trigger in q_clean:
                return f"{reply} Feel free to ask about Sudheer's database architecture, cloud engineering, or any general topic."
    return None

def get_self_awareness_reply(q_clean: str) -> str | None:
    self_triggers = [
        "your name", "who are you", "what are you", "about you",
        "about yourself", "introduce yourself", "what can you do", "how do you work"
    ]
    if any(t in q_clean for t in self_triggers):
        return (
            "I'm <strong>Sudheer's Architecture AI Assistant</strong> — a self-hosted RAG & live-knowledge assistant running on <strong>Sudheer Kumar's Apple Silicon M1 server</strong>.<br><br>"
            "• <strong>Stack:</strong> FastAPI + Caddy reverse proxy + Cloudflare Zero-Trust Tunnel + PostgreSQL.<br>"
            "• <strong>What I can do:</strong> Answer deep technical questions about Sudheer's EDB Postgres® AI v18, Nutanix NDB, and SQL Server AlwaysOn architectures, or look up live world and technology topics on demand."
        )
    return None

def extract_search_topic(query: str) -> str:
    cleaned = re.sub(r"[^\w\s\-\.]", "", query.lower()).strip()
    keywords = [w for w in cleaned.split() if w not in STOP_WORDS]
    return " ".join(keywords) if keywords else cleaned

def format_rich_sentences(text: str, max_sentences: int = 4, max_chars: int = 620) -> str:
    sentences = re.split(r'(?<=[.!?])\s+', text.strip())
    selected = " ".join(sentences[:max_sentences])
    if len(selected) > max_chars:
        selected = selected[:max_chars].rsplit(" ", 1)[0] + "..."
    return selected

def search_live_web(query: str) -> tuple[str, str]:
    topic = extract_search_topic(query)
    if not topic or len(topic) < 2:
        return "", ""

    # 1. Wikipedia REST Summary API (clean, factual, comprehensive 3-4 sentence overview)
    try:
        wiki_slug = urllib.parse.quote(topic.title().replace(" ", "_"))
        wiki_url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{wiki_slug}"
        req = urllib.request.Request(wiki_url, headers={"User-Agent": "SudheerQK-AI/3.0"})
        with urllib.request.urlopen(req, timeout=3.5) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            extract = (data.get("extract") or "").strip()
            title = data.get("title") or topic.title()
            if extract and data.get("type") != "disambiguation":
                return title, format_rich_sentences(extract, max_sentences=4, max_chars=620)
    except Exception:
        pass

    # 2. DuckDuckGo Instant Answer API fallback
    try:
        url = f"https://api.duckduckgo.com/?q={urllib.parse.quote(topic)}&format=json&no_html=1&skip_disambig=1"
        req = urllib.request.Request(url, headers={"User-Agent": "SudheerQK-AI/3.0"})
        with urllib.request.urlopen(req, timeout=3.5) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            abstract = (data.get("AbstractText") or "").strip()
            heading = data.get("Heading") or topic.title()
            if abstract:
                return heading, format_rich_sentences(abstract, max_sentences=4, max_chars=620)
    except Exception:
        pass

    return topic.title(), ""

@app.get("/health")
def health():
    return {"status": "online", "service": "SudheerQK Architecture AI v3.0"}

@app.post("/ask")
@app.post("/api/ask")
async def ask_ai(payload: AskRequest):
    q = payload.question.strip()
    q_clean = re.sub(r"[^\w\s]", "", q.lower()).strip()
    words = set(q_clean.split())

    # 1. Natural conversational greeting
    greeting_reply = get_natural_greeting(q_clean)
    if greeting_reply:
        return {"answer": greeting_reply, "source": "assistant"}

    # 2. Assistant self-awareness ("tell me about you", "what is your name", "how do you work")
    self_reply = get_self_awareness_reply(q_clean)
    if self_reply:
        return {"answer": self_reply, "source": "assistant"}

    # 3. Portfolio RAG knowledge base matching
    matched = []
    for item in KNOWLEDGE_DOCS:
        score = sum(1 for tag in item["tags"] if (tag in words if " " not in tag else tag in q_clean))
        if score > 0:
            matched.append((score, item["text"]))
    matched.sort(key=lambda x: x[0], reverse=True)
    rag_hits = [m[1] for m in matched]

    # 4. Live web lookup for general world/technology questions
    topic_title, web_snippet = ("", "") if rag_hits else search_live_web(q)

    # 5. Synthesize via local Ollama LLM if active on port 11434
    try:
        context = "\n".join(rag_hits[:2]) if rag_hits else (web_snippet or "\n".join(d["text"] for d in KNOWLEDGE_DOCS[:2]))
        ollama_payload = json.dumps({
            "model": os.getenv("OLLAMA_MODEL", "llama3.2"),
            "prompt": (
                "You are Sudheer's Architecture AI Assistant — friendly, articulate, and intelligent. "
                "Write a well-structured, engaging answer using HTML <strong> and <br> tags where helpful.\n"
                f"Context:\n{context}\n\nUser Question: {q}\nAnswer:"
            ),
            "stream": False
        }).encode("utf-8")
        req = urllib.request.Request("http://127.0.0.1:11434/api/generate", data=ollama_payload, headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=6) as resp:
            res_json = json.loads(resp.read().decode("utf-8"))
            if res_json.get("response"):
                return {"answer": res_json["response"].strip(), "source": "ollama+rag"}
    except Exception:
        pass

    # 6. Return matched RAG knowledge
    if rag_hits:
        return {"answer": rag_hits[0], "source": "rag"}

    # 7. Return rich structured Live Web Summary
    if web_snippet:
        return {
            "answer": f"<strong>{topic_title}:</strong> {web_snippet}",
            "source": "web"
        }

    return {
        "answer": "I couldn't find an exact summary for that phrasing—try asking with a specific topic (for example, <em>\"Tell me about India\"</em>, <em>\"How does PostgreSQL WAL work?\"</em>, or <em>\"Sudheer's Nutanix NDB setup\"</em>).",
        "source": "assistant"
    }
