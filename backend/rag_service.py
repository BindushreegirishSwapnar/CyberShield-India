"""Small local retrieval service for educational cybercrime guidance."""

import hashlib
import json
import re
import uuid
from collections import Counter
from datetime import datetime, timezone
from math import sqrt

from database import get_db_connection

VECTOR_SIZE = 256
CHUNK_WORDS = 120
CHUNK_OVERLAP = 24
MIN_RELEVANCE = 0.08

SEED_DOCUMENTS = [
    {
        "title": "Recognizing phishing and fake websites",
        "category": "Phishing",
        "text": "Phishing is deceptive communication that attempts to persuade a recipient to disclose information, open an attachment, or visit a misleading website. Warning signs can include unexpected urgency, mismatched sender details, unusual links, and requests for passwords or one-time passcodes. Do not follow links in an unexpected message. Verify the request using a known official website or a contact method already trusted. Preserve the message and report it through the relevant organization’s official channel. Never share an OTP or password in response to an unsolicited request.",
    },
    {
        "title": "Responding to suspected ransomware or malware",
        "category": "Malware and ransomware",
        "text": "Malware is software that performs unwanted or harmful actions on a device. Ransomware is malware that can deny access to files or systems. If compromise is suspected, follow your organization’s incident response plan and contact its security team. Isolate an affected device from network connections when safe and authorized. Avoid deleting evidence or communicating with an attacker without guidance. Preserve relevant alerts and timestamps, and restore systems only through an approved recovery process.",
    },
    {
        "title": "Protecting accounts from identity theft and takeover",
        "category": "Identity theft",
        "text": "Account takeover occurs when another person gains unauthorized access to an account. Use a unique password for each account and enable multi-factor authentication where available. Do not share verification codes. If an account may be compromised, use the service’s official recovery process from a trusted device, change reused passwords, review active sessions, and notify the service provider. Keep records of suspicious messages and account notifications for follow-up.",
    },
    {
        "title": "Safer digital payments and OTP awareness",
        "category": "Payment fraud",
        "text": "Payment fraud can involve impersonation, misleading payment requests, or attempts to obtain authentication codes. Confirm recipient details and payment requests using a separate trusted channel. Do not disclose an OTP, PIN, or password to a caller or message sender. If a payment seems unauthorized, contact the bank or payment provider promptly using the number or app published through its official channel. Keep transaction references and message records for the provider’s investigation.",
    },
    {
        "title": "Recognizing social engineering",
        "category": "Social engineering",
        "text": "Social engineering uses deception or pressure to influence a person into taking an unsafe action or revealing information. Common warning signs include unexpected urgency, authority claims, secrecy requests, and unusual requests for credentials or money. Pause and verify the request with the person or organization through a separate, known contact method. Follow workplace verification procedures and report suspicious contact to the appropriate support or security team.",
    },
    {
        "title": "Basic DDoS awareness and response coordination",
        "category": "DDoS",
        "text": "A distributed denial-of-service event attempts to affect service availability by directing excessive traffic at a service. Users who observe an outage should report the time, affected service, and visible error to the service owner. System operators should follow their incident response and provider escalation procedures, preserve relevant logs, and communicate status through established channels. Do not attempt to retaliate or probe unrelated systems.",
    },
    {
        "title": "Data exposure and breach response basics",
        "category": "Data breach",
        "text": "A suspected data exposure should be reported promptly through the organization’s approved security or privacy channel. Record what was observed, when it was noticed, and which systems or records may be involved, without copying or sharing sensitive data unnecessarily. Preserve relevant evidence and follow the organization’s incident response process. Do not make public claims about scope or cause before they have been verified by responsible responders.",
    },
    {
        "title": "Preserving evidence and reporting cybercrime",
        "category": "Incident response",
        "text": "For a suspected cybercrime, preserve relevant messages, URLs, transaction references, timestamps, and screenshots where safe and appropriate. Avoid altering original files or forwarding suspicious links to others. Contact the affected service provider or organization through an official channel. Reporting procedures vary by jurisdiction; consult the relevant official government or law-enforcement reporting service for current instructions. This educational note does not provide legal advice or cite a specific law.",
    },
    {
        "title": "Safer passwords and multi-factor authentication",
        "category": "Account security",
        "text": "Use long, unique passwords and avoid reusing them across services. A reputable password manager can help manage unique credentials. Enable multi-factor authentication where available, keep recovery options current, and review account activity. Treat unexpected login prompts and verification-code requests with caution. If credentials may have been exposed, change them through the official service and update any other account where the same password was reused.",
    },
    {
        "title": "Cyberstalking and online harassment safety",
        "category": "Online safety",
        "text": "For repeated unwanted online contact, preserve relevant messages and account details, review privacy and location-sharing settings, and use platform tools to block or report accounts. Tell a trusted person or appropriate support service if safety is a concern. Avoid engaging with threatening accounts when doing so could increase risk. For immediate danger, contact local emergency services. Available reporting options depend on location; use current official channels.",
    },
]


def _tokens(text):
    ignored = {
        "a", "about", "after", "all", "an", "and", "are", "as", "at", "be", "by", "can",
        "do", "for", "from", "got", "have", "i", "if", "in", "into", "is", "it", "me",
        "my", "of", "on", "or", "someone", "that", "the", "their", "this", "to", "was",
        "what", "when", "with", "you", "your",
    }
    words = re.findall(r"[a-z0-9]+", text.lower())
    return [word[:-1] if word.endswith("s") and len(word) > 4 else word for word in words if word not in ignored]


def _embed(text):
    """Create a deterministic, normalized hashed-term vector without model downloads."""
    counts = Counter(_tokens(text))
    vector = {}
    for token, count in counts.items():
        digest = hashlib.sha256(token.encode("utf-8")).digest()
        index = int.from_bytes(digest[:4], "big") % VECTOR_SIZE
        sign = 1 if digest[4] % 2 else -1
        vector[str(index)] = vector.get(str(index), 0) + sign * (1 + (count - 1) * 0.25)
    magnitude = sqrt(sum(value * value for value in vector.values()))
    return {key: round(value / magnitude, 8) for key, value in vector.items()} if magnitude else {}


def _split(text):
    words = text.split()
    chunks = []
    start = 0
    while start < len(words):
        part = " ".join(words[start:start + CHUNK_WORDS]).strip()
        if part:
            chunks.append(part)
        if start + CHUNK_WORDS >= len(words):
            break
        start += CHUNK_WORDS - CHUNK_OVERLAP
    return chunks


def ingest_document(title, category, source, text, source_type="Curated guidance"):
    title = str(title or "").strip()
    category = str(category or "General").strip()
    source = str(source or "Local knowledge base").strip()
    text = str(text or "").strip()
    if not title or not text:
        raise ValueError("Document title and text are required.")
    if len(text) > 200000:
        raise ValueError("Document text must be 200,000 characters or fewer.")
    document_id = str(uuid.uuid4())
    chunks = _split(text)
    conn = get_db_connection()
    try:
        conn.execute(
            "INSERT INTO rag_documents (document_id, title, category, source, source_type) VALUES (?, ?, ?, ?, ?)",
            (document_id, title, category, source, source_type),
        )
        conn.executemany(
            "INSERT INTO rag_chunks (chunk_id, document_id, section, content, vector) VALUES (?, ?, ?, ?, ?)",
            [
                (str(uuid.uuid4()), document_id, f"Section {index + 1}", chunk, json.dumps(_embed(chunk)))
                for index, chunk in enumerate(chunks)
            ],
        )
        conn.commit()
    finally:
        conn.close()
    return {"document_id": document_id, "title": title, "chunks": len(chunks)}


def ensure_seed_documents():
    conn = get_db_connection()
    try:
        count = conn.execute("SELECT COUNT(*) FROM rag_documents").fetchone()[0]
    finally:
        conn.close()
    if count:
        return
    for document in SEED_DOCUMENTS:
        ingest_document(
            document["title"], document["category"], "CyberNexa local educational guidance",
            document["text"], "Curated guidance",
        )


def list_documents():
    ensure_seed_documents()
    conn = get_db_connection()
    try:
        rows = conn.execute(
            "SELECT d.document_id, d.title, d.category, d.source, d.source_type, d.created_at, d.enabled, COUNT(c.chunk_id) AS chunks "
            "FROM rag_documents d LEFT JOIN rag_chunks c ON c.document_id = d.document_id "
            "GROUP BY d.document_id ORDER BY d.created_at DESC"
        ).fetchall()
        return [dict(row) for row in rows]
    finally:
        conn.close()


def query_knowledge(query, limit=4, complaint_id=None, user_id=None):
    query = str(query or "").strip()
    if len(query) < 3:
        raise ValueError("Enter a question or incident description with at least 3 characters.")
    if complaint_id is not None:
        try:
            complaint_id = int(complaint_id)
        except (TypeError, ValueError):
            raise ValueError("Complaint ID must be an integer.") from None
        conn = get_db_connection()
        try:
            exists = conn.execute("SELECT 1 FROM complaints WHERE id = ?", (complaint_id,)).fetchone()
        finally:
            conn.close()
        if exists is None:
            raise ValueError("The selected complaint does not exist.")
    ensure_seed_documents()
    query_vector = _embed(query)
    conn = get_db_connection()
    try:
        rows = conn.execute(
            "SELECT c.chunk_id, c.document_id, c.section, c.content, c.vector, d.title, d.category, d.source, d.source_type "
            "FROM rag_chunks c JOIN rag_documents d ON d.document_id = c.document_id WHERE d.enabled = 1"
        ).fetchall()
    finally:
        conn.close()

    query_terms = set(_tokens(query))
    aliases = {
        "otp": {"passcode", "verification", "code", "phishing"},
        "fake": {"phishing", "misleading", "deceptive"},
        "bank": {"payment", "financial"},
        "link": {"website", "url"},
        "password": {"credential", "account"},
        "ransomware": {"malware", "encrypt"},
    }
    expanded_terms = query_terms | {alias for term in query_terms for alias in aliases.get(term, set())}
    matches = []
    for row in rows:
        chunk_vector = json.loads(row["vector"])
        vector_score = sum(value * chunk_vector.get(key, 0) for key, value in query_vector.items())
        searchable = set(_tokens(f"{row['title']} {row['category']} {row['content']}"))
        overlap = len(expanded_terms.intersection(searchable))
        lexical_score = overlap / max(len(expanded_terms), 1)
        score = 0.2 * max(vector_score, 0) + 0.8 * lexical_score
        if score >= MIN_RELEVANCE and overlap:
            matches.append({
                "chunk_id": row["chunk_id"], "document_id": row["document_id"],
                "title": row["title"], "category": row["category"], "source": row["source"],
                "source_type": row["source_type"], "section": row["section"],
                "content": row["content"], "relevance": round(min(score, 1.0), 3),
            })
    matches.sort(key=lambda item: item["relevance"], reverse=True)
    matches = matches[:max(1, min(int(limit), 8))]
    answer = (
        f"RAG Retrieval Mode: Retrieved guidance from '{matches[0]['title']}'. "
        "The explanation below is limited to the displayed knowledge-base excerpt; it is not a verified case finding."
        if matches else "No relevant knowledge-base information was retrieved."
    )
    if matches:
        answer += " Relevant guidance: " + matches[0]["content"]
    conn = get_db_connection()
    try:
        conn.execute(
            "INSERT INTO rag_queries (user_id, complaint_id, query, answer, mode, sources, retrieved_chunks) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (user_id, complaint_id, query, answer, "RAG Retrieval Mode", json.dumps(matches), json.dumps(matches)),
        )
        conn.commit()
    finally:
        conn.close()
    recommendations = []
    if matches:
        for sentence in re.split(r"(?<=[.!?])\s+", matches[0]["content"]):
            if re.search(r"\b(do not|never|verify|preserve|contact|report|follow|use|avoid|enable|change|isolate)\b", sentence, re.I):
                recommendations.append(sentence.strip())
            if len(recommendations) == 3:
                break
    return {
        "mode": "RAG Retrieval Mode",
        "answer": answer,
        "sources": [
            {key: item[key] for key in ("document_id", "title", "category", "source", "source_type", "section", "relevance")}
            for item in matches
        ],
        "retrieved_chunks": matches,
        "recommendations": recommendations,
        "generated_at": datetime.now(timezone.utc).isoformat(),
    }


def query_history(limit=10, user_id=None):
    conn = get_db_connection()
    try:
        if user_id is None:
            rows = conn.execute(
                "SELECT id, user_id, complaint_id, query, answer, mode, sources, retrieved_chunks, created_at FROM rag_queries ORDER BY id DESC LIMIT ?",
                (max(1, min(int(limit), 100)),),
            ).fetchall()
        else:
            rows = conn.execute(
                "SELECT id, user_id, complaint_id, query, answer, mode, sources, retrieved_chunks, created_at FROM rag_queries WHERE user_id = ? ORDER BY id DESC LIMIT ?",
                (user_id, max(1, min(int(limit), 100))),
            ).fetchall()
        result = [dict(row) for row in rows]
        for row in result:
            row["sources"] = json.loads(row["sources"])
            row["retrieved_chunks"] = json.loads(row["retrieved_chunks"])
        return result
    finally:
        conn.close()


def clear_query_history(user_id=None):
    conn = get_db_connection()
    try:
        cursor = conn.execute("DELETE FROM rag_queries WHERE user_id = ?", (user_id,)) if user_id is not None else conn.execute("DELETE FROM rag_queries")
        conn.commit()
        return cursor.rowcount
    finally:
        conn.close()


def reindex_documents():
    conn = get_db_connection()
    try:
        rows = conn.execute("SELECT chunk_id, content FROM rag_chunks").fetchall()
        conn.executemany(
            "UPDATE rag_chunks SET vector = ? WHERE chunk_id = ?",
            [(json.dumps(_embed(row["content"])), row["chunk_id"]) for row in rows],
        )
        conn.commit()
        return len(rows)
    finally:
        conn.close()


def disable_document(document_id):
    conn = get_db_connection()
    try:
        cursor = conn.execute(
            "UPDATE rag_documents SET enabled = 0 WHERE document_id = ? AND enabled = 1",
            (document_id,),
        )
        conn.commit()
        return cursor.rowcount > 0
    finally:
        conn.close()


def document_stats():
    documents = list_documents()
    return {"documents": len(documents), "chunks": sum(item["chunks"] for item in documents), "vector_store": "SQLite hashed-term vectors"}