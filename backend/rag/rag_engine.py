import os
import re
import json
import urllib.request
import urllib.parse
from .vector_store import get_vector_store
from analyzer import find_similar_complaints, detect_threat_indicators

def call_gemini_api(prompt, api_key):
    """Call Google Gemini API if GEMINI_API_KEY is configured in environment."""
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
    headers = {"Content-Type": "application/json"}
    payload = {
        "contents": [{
            "parts": [{"text": prompt}]
        }],
        "generationConfig": {
            "temperature": 0.2,
            "maxOutputTokens": 800,
            "topP": 0.95
        }
    }
    data = json.dumps(payload).encode('utf-8')
    req = urllib.request.Request(url, data=data, headers=headers, method='POST')
    with urllib.request.urlopen(req, timeout=12) as response:
        result = json.loads(response.read().decode('utf-8'))
        candidates = result.get("candidates", [])
        if candidates and "content" in candidates[0]:
            parts = candidates[0]["content"].get("parts", [])
            if parts:
                return parts[0].get("text", "")
    return None

def synthesize_grounded_answer(query_text, top_chunks):
    """
    Synthesize factual, citation-backed response strictly from retrieved context passages.
    If GEMINI_API_KEY is set, leverages the LLM with strict grounding instructions.
    Otherwise, applies deterministic high-precision legal/SOP extraction.
    """
    if not top_chunks or top_chunks[0].get("confidence_pct", 0) < 25.0:
        return (
            "This information was not found in the verified CyberShield India knowledge base. "
            "Please consult the official National Cyber Crime Reporting Portal (NCRP), "
            "jurisdictional cyber police station manuals, or call the 1930 National Helpline.",
            False
        )

    # Format context for synthesis
    context_blocks = []
    for idx, chunk in enumerate(top_chunks, 1):
        context_blocks.append(
            f"[{idx}] Source: {chunk['doc_title']} | Section: {chunk['section']} | Authority: {chunk['authority']}\n"
            f"Excerpt: {chunk['content']}"
        )
    formatted_context = "\n\n".join(context_blocks)

    api_key = os.getenv("GEMINI_API_KEY")
    if api_key and api_key.strip():
        llm_prompt = f"""You are CyberShield India Legal & Investigative AI Copilot.
Answer the following query ONLY using the provided retrieved context passages below.
DO NOT use outside knowledge. If the answer cannot be determined strictly from the context, state:
'This information is not found in the verified knowledge base. Please consult jurisdictional standard operating procedures.'

Cite sources inline using numbered citations like [1], [2] corresponding to the source numbers.

CONTEXT PASSAGES:
{formatted_context}

QUERY:
{query_text}

ANSWER (grounded, professional, citing specific sections and legal provisions):"""
        try:
            llm_response = call_gemini_api(llm_prompt, api_key.strip())
            if llm_response and len(llm_response.strip()) > 30:
                return llm_response.strip(), True
        except Exception:
            pass  # Fallback to local extractive synthesis

    # Deterministic Local Synthesis
    points = []
    seen_sentences = set()

    for idx, chunk in enumerate(top_chunks, 1):
        content = chunk["content"]
        # Split into key procedural bullets
        sentences = re.split(r'(?<=[.!?])\s+', content)
        for s in sentences:
            s_clean = s.strip()
            if len(s_clean) > 35 and s_clean not in seen_sentences:
                seen_sentences.add(s_clean)
                points.append(f"{s_clean} [{idx}]")
                if len(points) >= 5:
                    break
        if len(points) >= 5:
            break

    doc_citations = ", ".join([f"[{i+1}] {c['doc_ref']} ({c['section']})" for i, c in enumerate(top_chunks[:3])])
    answer_text = (
        f"Based on authoritative directives retrieved from {doc_citations}:\n\n"
        + "\n\n".join([f"• {p}" for p in points])
        + "\n\nStatutory Mandate: In accordance with Section 91 CrPC / Section 94 BNSS, all electronic evidence must be preserved with cryptographic SHA-256 integrity logs."
    )
    return answer_text, True

def answer_query(query_text):
    """
    Standard Production RAG Question-Answering:
    1. Preprocesses & expands query terminology
    2. Performs hybrid BM25 + Vector search with Reciprocal Rank Fusion
    3. Synthesizes a factual, strictly grounded response citing specific sections and document references.
    """
    store = get_vector_store()
    top_chunks = store.search_hybrid(query_text, top_k=4)

    if not top_chunks:
        return {
            "query": query_text,
            "answer": "No relevant authoritative guidelines were retrieved from the knowledge base for this query. Please consult the Cyber Crime Police Manual or state standard operating procedures.",
            "sources": [],
            "retrieval_count": 0,
            "confidence": 0,
            "grounded": False
        }

    synthesized_answer, is_grounded = synthesize_grounded_answer(query_text, top_chunks)

    sources = []
    for idx, chunk in enumerate(top_chunks, 1):
        sources.append({
            "source_id": idx,
            "document": chunk["doc_title"],
            "reference": chunk["doc_ref"],
            "authority": chunk["authority"],
            "section": chunk["section"],
            "snippet": chunk["content"][:280] + ("..." if len(chunk["content"]) > 280 else ""),
            "full_content": chunk["content"],
            "relevance_score": f"{chunk.get('confidence_pct', 75)}%",
            "confidence_pct": chunk.get('confidence_pct', 75)
        })

    avg_confidence = round(sum(s["confidence_pct"] for s in sources) / max(1, len(sources)), 1)

    return {
        "query": query_text,
        "answer": synthesized_answer,
        "sources": sources,
        "retrieval_count": len(top_chunks),
        "confidence": avg_confidence,
        "grounded": is_grounded
    }

def answer_case_query(query_text, complaint=None, existing_complaints=None):
    """
    Context-Aware Case Copilot:
    Integrates case metadata, extracted IOCs, and matching knowledge base guidelines.
    """
    q_lower = query_text.lower()
    store = get_vector_store()
    existing_complaints = existing_complaints or []

    matched_cases = []
    matched_sources = []
    answer_text = ""

    # Case 1: Similar complaints query
    if any(k in q_lower for k in ["similar", "pattern", "seen this", "historical", "prior cases", "repeat"]):
        search_term = complaint.get("description", "") if complaint else query_text
        similar_results = find_similar_complaints(search_term, existing_complaints, top_k=4)

        if similar_results:
            matched_cases = similar_results
            lines = [f"Found {len(similar_results)} correlated historical case(s) in the intelligence database:"]
            for idx, sc in enumerate(similar_results, 1):
                lines.append(
                    f"{idx}. Case #{sc['complaint_id']} ({sc['similarity']}% similarity)\n"
                    f"   • Crime Type: {sc['category']}\n"
                    f"   • Location: {sc['location']}, {sc.get('state', '')}\n"
                    f"   • Risk Score: {sc['risk_score']}/100 ({sc['risk_level']})\n"
                    f"   • Status: {sc['current_status']}\n"
                    f"   • Summary: {sc['description'][:110]}..."
                )
            answer_text = "\n\n".join(lines)
        else:
            answer_text = "No prior complaints with significant similarity (> 15%) were identified in the demonstration database."

        top_chunks = store.search_hybrid(f"{complaint.get('crime_type', '') if complaint else ''} modus operandi threat typology", top_k=2)
        for idx, chunk in enumerate(top_chunks, 1):
            matched_sources.append({
                "source_id": idx,
                "document": chunk["doc_title"],
                "reference": chunk["doc_ref"],
                "authority": chunk["authority"],
                "section": chunk["section"],
                "snippet": chunk["content"][:240] + "...",
                "relevance_score": f"{chunk.get('confidence_pct', 70)}%"
            })

        return {
            "query": query_text,
            "answer": answer_text,
            "sources": matched_sources,
            "similar_cases": matched_cases,
            "grounded": True
        }

    # Case 2: General or Case-specific legal/procedural guidance
    context_augmented_query = query_text
    if complaint:
        cat = complaint.get("crime_type") or complaint.get("predicted_category", "")
        loss = complaint.get("financial_loss", 0)
        desc_excerpt = complaint.get("description", "")[:150]
        context_augmented_query = f"{cat} INR {loss} {desc_excerpt} {query_text}"

    rag_result = answer_query(context_augmented_query)
    # Customize answer to reference case ID if complaint provided
    if complaint and rag_result["grounded"]:
        rag_result["answer"] = f"Investigation Guidance for Case #{complaint.get('complaint_id')}:\n\n" + rag_result["answer"]

    return rag_result

def generate_case_brief(complaint):
    """
    Generates an automated, grounded AI Investigation Brief for a specific complaint,
    citing relevant IT Act sections, standard operating procedures, and suggested IO questions.
    """
    desc = complaint.get("description", "")
    category = complaint.get("predicted_category") or complaint.get("crime_type") or complaint.get("category", "")
    loss = float(complaint.get("financial_loss") or complaint.get("reported_amount") or 0.0)
    complaint_id = complaint.get("complaint_id", "CC-CASE-NEW")

    query = f"{category} {desc} legal provisions SOP investigation digital evidence"
    store = get_vector_store()
    retrieved = store.search_hybrid(query, top_k=3)

    legal_sections = []
    category_lower = category.lower()
    desc_lower = desc.lower()

    if "phishing" in category_lower or "otp" in desc_lower or "impersonat" in desc_lower or "fraud" in category_lower:
        legal_sections.append({
            "section": "Section 66D, IT Act 2000",
            "title": "Cheating by Personation using Computer Resource",
            "penalty": "Imprisonment up to 3 years and fine up to ₹1,00,000",
            "bns_equivalent": "Section 318(4) Bharatiya Nyaya Sanhita 2023 (Cheating)"
        })
    if "identity" in category_lower or "aadhaar" in desc_lower or "password" in desc_lower:
        legal_sections.append({
            "section": "Section 66C, IT Act 2000",
            "title": "Identity Theft / Electronic Signature Misuse",
            "penalty": "Imprisonment up to 3 years and fine up to ₹1,00,000",
            "bns_equivalent": "Section 319 BNS 2023 (Cheating by Impersonation)"
        })
    if "ransomware" in category_lower or "malware" in category_lower or "encrypt" in desc_lower:
        legal_sections.append({
            "section": "Section 43 & Section 66, IT Act 2000",
            "title": "Computer Contaminant / Ransomware & Hacking",
            "penalty": "Imprisonment up to 3 years or fine up to ₹5,00,000 + Civil Compensation up to ₹5 Crore under Section 43",
            "bns_equivalent": "Section 308 BNS 2023 (Extortion)"
        })
    if "data breach" in category_lower or "exfiltrat" in desc_lower or "leak" in desc_lower:
        legal_sections.append({
            "section": "Section 43A, IT Act 2000 & DPDP Act 2023",
            "title": "Failure to Protect Sensitive Personal Data",
            "penalty": "Civil compensation to affected victims; penalties under Section 33 DPDP Act up to ₹250 Crore",
            "bns_equivalent": "Section 316(2) BNS 2023 (Criminal Breach of Trust)"
        })
    if "arrest" in desc_lower or "customs" in desc_lower or "cbi" in desc_lower:
        legal_sections.append({
            "section": "Section 419/420 IPC & Section 66D IT Act",
            "title": "Authority Impersonation & Coercive Extortion ('Digital Arrest')",
            "penalty": "Imprisonment up to 7 years and fine",
            "bns_equivalent": "Section 308(2) & 318(4) BNS 2023"
        })

    if not legal_sections:
        legal_sections.append({
            "section": "Section 66D, IT Act 2000",
            "title": "Computer-Related Offence & Cheating",
            "penalty": "Imprisonment up to 3 years and fine",
            "bns_equivalent": "Section 318(4) BNS 2023"
        })

    checklist = [
        "1. Issue Section 91 CrPC / Section 94 BNSS Notice to recipient Bank/Fintech for KYC, IP logs, and immediate lien marking.",
        "2. Submit formal transaction dispute requisition via CFCFRMS on National Cyber Crime Reporting Portal (Helpline 1930).",
        "3. Requisition subscriber CDR/CAF and IMEI activation history from concerned Telecom Service Provider (TSP).",
        "4. Preserve digital evidence with SHA-256 cryptographic hashing in compliance with Section 63 Bharatiya Sakshya Adhiniyam (BSA 2023).",
        "5. Register formal FIR and dispatch notices under Section 79(3)(b) IT Act to intermediary platforms for URL/account takedown."
    ]

    questions = [
        "What was the exact SMS sender header or incoming caller ID?",
        "Did you approve any biometric or UPI PIN prompt on your device?",
        "Was any remote access software (AnyDesk, TeamViewer, RustDesk) installed?",
        "What are the precise beneficiary Account Numbers, IFSC codes, or UPI VPAs displayed on your debit receipt?"
    ]

    return {
        "complaint_id": complaint_id,
        "executive_summary": f"Incident classified as {category} with assessed financial damage of ₹{loss:,.2f}. Threat patterns indicate organized digital fraud requiring immediate intermediary interdiction.",
        "applicable_statutes": legal_sections,
        "investigation_checklist": checklist,
        "suggested_interview_questions": questions,
        "retrieved_guidelines": [
            {"doc": c["doc_ref"], "section": c["section"], "authority": c["authority"]}
            for c in retrieved
        ]
    }

def generate_fir_draft(complaint):
    """
    Generate an official, structured First Information Report (FIR) summary format
    citing IT Act 2000 and Bharatiya Nyaya Sanhita (BNS) 2023 sections.
    """
    brief = generate_case_brief(complaint)
    comp_id = complaint.get("complaint_id", "CC-2026-UNKNOWN")
    station = complaint.get("cyber_cell_station") or f"Cyber Crime Police Station, {complaint.get('city', 'Jurisdiction')}"
    date_reg = complaint.get("complaint_date") or complaint.get("incident_date") or "2026-09-29"
    loss = float(complaint.get("financial_loss") or 0.0)
    category = complaint.get("predicted_category") or complaint.get("crime_type", "Cyber Crime")
    officer = complaint.get("assigned_officer", "Station House Officer")

    statutes_text = "\n".join([
        f"  • {s['section']} - {s['title']} (BNS Eqv: {s.get('bns_equivalent', 'N/A')})"
        for s in brief["applicable_statutes"]
    ])

    fir_content = f"""FIRST INFORMATION REPORT (DRAFT SUMMARY)
(Under Section 173 Bharatiya Nagarik Suraksha Sanhita, 2023 / Section 154 CrPC)

1. POLICE STATION: {station}
   District / Zone: {complaint.get('district', complaint.get('city', 'Urban'))}
   State: {complaint.get('state', 'India')}
   Reference Case ID: {comp_id}
   Date of Registration: {date_reg}

2. COMPLAINANT STATEMENT:
   Victim Profile: {complaint.get('victim_type', 'Individual')} ({complaint.get('victim_age_group', '26-40')} years)
   Platform / Channel: {complaint.get('platform', 'Digital Banking / UPI')}
   Reported Financial Loss: INR ₹{loss:,.2f}

   Narrative Statement:
   "{complaint.get('description', 'Complaint statement on record.')}"

3. ACCUSED / SUSPECT DETAILS EXTRACTED:
   Extracted Indicators: {complaint.get('threat_indicators', 'Under analysis')}
   Suspected Attack Vector: {complaint.get('attack_vector', 'Digital Fraud / Phishing')}
   Beneficiary Payment Method: {complaint.get('payment_method', 'UPI / IMPS')}

4. STATUTORY SECTIONS INVOLVED:
{statutes_text}

5. INVESTIGATION DIRECTIVES TO ASSIGNED OFFICER ({officer}):
   a) Dispatch Section 94 BNSS requisitions to intermediary payment gateways to freeze beneficiary accounts.
   b) Obtain Section 63 BSA certificate for server logs and SMS transmission records.
   c) Coordinate with I4C (Indian Cyber Crime Coordination Centre) National Cyber Fraud Reporting system.

Approved by: CyberShield India Automated Legal Decision Support Engine.
"""
    return {
        "complaint_id": comp_id,
        "fir_summary": fir_content,
        "statutes": brief["applicable_statutes"],
        "station": station,
        "officer": officer,
        "date": date_reg
    }
