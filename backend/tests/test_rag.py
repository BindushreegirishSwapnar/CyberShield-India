import pytest
from rag.vector_store import get_vector_store
from rag.rag_engine import answer_query, generate_case_brief, generate_fir_draft

def test_vector_store_indexing():
    store = get_vector_store()
    assert len(store.chunks) > 0
    assert store.vectorizer is not None
    assert store.bm25 is not None

def test_hybrid_search_accuracy():
    store = get_vector_store()
    results = store.search_hybrid("Helpline 1930 golden hour RBI debit freeze", top_k=3)
    assert len(results) > 0
    # Top results should match RBI or SOP
    top_doc = results[0]["doc_ref"]
    assert "rbi" in top_doc.lower() or "sop" in top_doc.lower()

def test_rag_answer_grounding():
    result = answer_query("What section of IT Act deals with identity theft and impersonation?")
    assert result["grounded"] is True
    assert len(result["sources"]) > 0
    assert "66" in result["answer"] or "IT Act" in result["answer"]

def test_fir_draft_generation():
    complaint = {
        "complaint_id": "CC-2026-KA-000101",
        "category": "Online Financial Fraud",
        "predicted_category": "Online Financial Fraud",
        "financial_loss": 50000,
        "description": "Victim scanned fraudulent QR code sent on OLX.",
        "state": "Karnataka",
        "city": "Bengaluru",
        "cyber_cell_station": "Cyber Crime Police Station, CID Karnataka"
    }
    fir = generate_fir_draft(complaint)
    assert "fir_summary" in fir
    assert "Section 66D" in fir["fir_summary"] or "Bharatiya Nyaya Sanhita" in fir["fir_summary"]
    assert fir["complaint_id"] == "CC-2026-KA-000101"
