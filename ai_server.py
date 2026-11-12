import os
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
    "<strong>EDB Postgres® AI Database Advanced v18 Certified:</strong> Sudheer Kumar is officially certified by EnterpriseDB (verified via Credly) and designs PostgreSQL 14–18 HA clusters, <code>pg_vector</code> IVFFlat/HNSW similarity search indices, PgBouncer pooling, and WAL streaming replication.",
    "<strong>Nutanix Cloud & NDB DBaaS (v2.10.1 / v2.11.1):</strong> Sudheer leads enterprise Nutanix Database Service upgrades across Production and DR clusters, configuring Time Machine SLA policies, zero-byte database clones, and Prism Central REST API automation.",
    "<strong>SQL Server Always On Availability Groups:</strong> Enterprise multi-subnet AG topologies (SQL 2012–2022), WSFC quorum and cloud/file witness architectures, zero-downtime rolling upgrades, and T-SQL query plan tuning.",
    "<strong>Self-Hosted Apple Silicon Infrastructure:</strong> <code>sudheerqk.com</code> and Sudheer's Private Vault run 24/7 on a low-power Apple Silicon M1 server using Caddy reverse proxy, Cloudflare Zero-Trust tunnels, FastAPI microservices, and a PostgreSQL + <code>pg_vector</code> backend.",
    "<strong>About Sudheer Kumar:</strong> Nutanix Database Specialist & Infrastructure Engineer based in Riyadh, Saudi Arabia (available for global architecture consultation). Direct contact: <strong>contact@sudheerqk.com</strong>."
]

class AskRequest(BaseModel):
    question: str

def search_live_web(query: str) -> str:
    try:
        q = urllib.parse.quote(query)
        url = f"https://api.duckduckgo.com/?q={q}&format=json&no_html=1&skip_disambig=1"
        req = urllib.request.Request(url, headers={"User-Agent": "SudheerQK-AI/1.0"})
        with urllib.request.urlopen(req, timeout=3) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            return data.get("AbstractText") or ""
    except Exception:
        return ""

@app.get("/health")
def health():
    return {"status": "online", "service": "SudheerQK Architecture AI"}

@app.post("/ask")
async def ask_ai(payload: AskRequest):
    q = payload.question.strip()
    q_low = q.lower()

    matched = [doc for doc in KNOWLEDGE_DOCS if any(w in doc.lower() for w in q_low.split() if len(w) > 3)]
    web_snippet = search_live_web(q)

    # Use local Ollama if running on port 11434
    try:
        context = "\n".join(matched or KNOWLEDGE_DOCS[:3])
        if web_snippet:
            context += f"\nLive Web Context: {web_snippet}"
        ollama_payload = json.dumps({
            "model": os.getenv("OLLAMA_MODEL", "llama3.2"),
            "prompt": f"You are Sudheer Kumar's Architecture AI Assistant. Answer concisely and technically using HTML bold tags where helpful.\nContext:\n{context}\n\nQuestion: {q}\nAnswer:",
            "stream": False
        }).encode("utf-8")
        req = urllib.request.Request("http://127.0.0.1:11434/api/generate", data=ollama_payload, headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=6) as resp:
            res_json = json.loads(resp.read().decode("utf-8"))
            if res_json.get("response"):
                return {"answer": res_json["response"].strip(), "source": "ollama+rag"}
    except Exception:
        pass

    base = matched[0] if matched else KNOWLEDGE_DOCS[0]
    if web_snippet:
        return {"answer": f"{base}<br><br><strong>Live Web Context:</strong> {web_snippet}", "source": "rag+web"}
    return {"answer": base, "source": "rag"}
