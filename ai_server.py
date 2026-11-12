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
        "text": "<strong>EDB Postgres® AI Database Advanced v18 Certified:</strong> Sudheer Kumar is officially certified by EnterpriseDB (verified via Credly) and designs PostgreSQL 14–18 HA clusters, <code>pg_vector</code> IVFFlat/HNSW similarity search indices, PgBouncer pooling, and WAL streaming replication."
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
        "tags": {"sudheer", "kumar", "riyadh", "saudi", "bank", "aljazira", "contact", "email", "hire", "role", "experience", "who"},
        "text": "<strong>About Sudheer Kumar:</strong> Nutanix Database Specialist & Infrastructure Engineer based in Riyadh, Saudi Arabia (deployed at Bank AlJazira via Maalim Al Khobra Company; previously Cognizant & Softenger UAE). Available for global architecture consultation at <strong>contact@sudheerqk.com</strong>."
    }
]

GREETINGS = {"hi", "hello", "hey", "greetings", "good morning", "good afternoon", "good evening", "hola", "namaste"}
STOP_WORDS = {"i", "want", "to", "know", "about", "what", "is", "are", "the", "a", "an", "tell", "me", "explain", "can", "you", "please", "how", "does", "work", "of", "in", "on", "for"}

class AskRequest(BaseModel):
    question: str

def extract_search_topic(query: str) -> str:
    cleaned = re.sub(r"[^\w\s\-\.]", "", query.lower()).strip()
    keywords = [w for w in cleaned.split() if w not in STOP_WORDS]
    return " ".join(keywords) if keywords else cleaned

def search_live_web(query: str) -> str:
    topic = extract_search_topic(query)
    if not topic:
        return ""

    # 1. Try DuckDuckGo Instant Answer API with cleaned topic
    try:
        url = f"https://api.duckduckgo.com/?q={urllib.parse.quote(topic)}&format=json&no_html=1&skip_disambig=1"
        req = urllib.request.Request(url, headers={"User-Agent": "SudheerQK-AI/2.0"})
        with urllib.request.urlopen(req, timeout=3) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            abstract = (data.get("AbstractText") or "").strip()
            if abstract:
                return abstract
    except Exception:
        pass

    # 2. Fallback to Wikipedia REST Summary API (reliable for countries, tech concepts, protocols)
    try:
        wiki_slug = urllib.parse.quote(topic.title().replace(" ", "_"))
        wiki_url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{wiki_slug}"
        req = urllib.request.Request(wiki_url, headers={"User-Agent": "SudheerQK-AI/2.0"})
        with urllib.request.urlopen(req, timeout=3) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            extract = (data.get("extract") or "").strip()
            if extract and data.get("type") != "disambiguation":
                # Keep concise (first 2 sentences)
                sentences = re.split(r'(?<=[.!?])\s+', extract)
                return " ".join(sentences[:2])
    except Exception:
        pass

    return ""

@app.get("/health")
def health():
    return {"status": "online", "service": "SudheerQK Architecture AI v2"}

@app.post("/ask")
@app.post("/api/ask")
async def ask_ai(payload: AskRequest):
    q = payload.question.strip()
    q_clean = re.sub(r"[^\w\s]", "", q.lower()).strip()
    words = set(q_clean.split())

    # 1. Handle pure greetings cleanly without dumping random bio/dictionary text
    if q_clean in GREETINGS or (len(words) <= 2 and words & GREETINGS):
        return {
            "answer": "Hello! I'm Sudheer's Architecture AI Assistant. You can ask me about Sudheer's <strong>EDB Postgres® AI v18</strong> work, <strong>Nutanix NDB</strong> clusters, <strong>SQL Server AlwaysOn AG</strong>, or any general tech and world topic via live web lookup.",
            "source": "assistant"
        }

    # 2. Exact word-token matching against Sudheer's portfolio RAG knowledge base
    matched = []
    for item in KNOWLEDGE_DOCS:
        score = sum(1 for tag in item["tags"] if (tag in words if " " not in tag else tag in q_clean))
        if score > 0:
            matched.append((score, item["text"]))
    matched.sort(key=lambda x: x[0], reverse=True)
    rag_hits = [m[1] for m in matched]

    # 3. Try local Ollama LLM if available on port 11434
    web_snippet = "" if rag_hits else search_live_web(q)
    try:
        context = "\n".join(rag_hits[:2]) if rag_hits else (web_snippet or "\n".join(d["text"] for d in KNOWLEDGE_DOCS[:2]))
        ollama_payload = json.dumps({
            "model": os.getenv("OLLAMA_MODEL", "llama3.2"),
            "prompt": f"You are Sudheer Kumar's helpful AI Assistant. Answer directly and concisely using HTML <strong> tags where appropriate.\nContext:\n{context}\n\nQuestion: {q}\nAnswer:",
            "stream": False
        }).encode("utf-8")
        req = urllib.request.Request("http://127.0.0.1:11434/api/generate", data=ollama_payload, headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=5) as resp:
            res_json = json.loads(resp.read().decode("utf-8"))
            if res_json.get("response"):
                return {"answer": res_json["response"].strip(), "source": "ollama+rag"}
    except Exception:
        pass

    # 4. Return Portfolio RAG hit if question is about Sudheer/databases
    if rag_hits:
        return {"answer": rag_hits[0], "source": "rag"}

    # 5. Otherwise return Live Web Context for general queries (e.g., "I want to know about India")
    if web_snippet:
        return {"answer": f"<strong>Live Web Summary:</strong> {web_snippet}", "source": "web"}

    return {
        "answer": "I didn't find a direct match for that query. Try asking about <strong>EDB Postgres AI v18</strong>, <strong>Nutanix NDB 2.11</strong>, <strong>SQL Server AlwaysOn AG</strong>, or any general topic!",
        "source": "assistant"
    }
