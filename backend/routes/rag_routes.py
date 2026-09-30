import os
import json
from flask import Blueprint, request, jsonify
from database import get_session
from models_db import KnowledgeDocument, Complaint, AuditLog
from rag.rag_engine import answer_query, answer_case_query
from rag.vector_store import get_vector_store

rag_bp = Blueprint('rag_bp', __name__)

@rag_bp.route('/query', methods=['POST'])
def query_rag():
    """
    Query the internal knowledge base (SOPs, IT Act legal provisions, RBI directions, CERT-In advisories).
    Returns a grounded answer with explicit document, section, and authority citations.
    """
    try:
        data = request.get_json() or {}
        query_text = data.get('query', '').strip()
        if not query_text:
            return jsonify({"status": "fail", "message": "Query parameter cannot be empty."}), 400

        result = answer_query(query_text)

        # Log query in audit log
        try:
            with get_session() as session:
                session.add(AuditLog(
                    timestamp=data.get('timestamp', 'Now'),
                    user_email=data.get('user_email', 'analyst@cybercrime.gov.in'),
                    user_role="Analyst",
                    action="RAG_QUERY",
                    target_entity="KnowledgeBase",
                    target_id="QUERY",
                    details=f"Query: {query_text[:100]} | Grounded: {result['grounded']}",
                    ip_address=request.remote_addr or "127.0.0.1"
                ))
        except Exception:
            pass

        return jsonify({
            "status": "success",
            "data": result
        }), 200

    except Exception as e:
        return jsonify({"status": "error", "message": f"RAG query execution failed: {str(e)}"}), 500

@rag_bp.route('/case-assistant', methods=['POST'])
def case_investigation_assistant():
    """
    Context-aware investigation assistant workspace endpoint.
    Retrieves both relevant standard operating procedures AND historical similar complaints from the database.
    """
    try:
        data = request.get_json() or {}
        query_text = data.get('query', '').strip()
        complaint_id = data.get('complaint_id')

        if not query_text:
            return jsonify({"status": "fail", "message": "Query text is required."}), 400

        complaint_dict = None
        existing_list = []

        with get_session() as session:
            # If complaint_id specified, load current case context
            if complaint_id:
                complaint = session.query(Complaint).filter(
                    (Complaint.complaint_id == complaint_id) | (Complaint.id == (int(complaint_id) if complaint_id.isdigit() else -1))
                ).first()
                if complaint:
                    complaint_dict = complaint.to_dict()

            # Load candidate complaints for similar case retrieval
            candidates = session.query(Complaint).limit(100).all()
            existing_list = [c.to_dict() for c in candidates if not complaint_dict or c.complaint_id != complaint_dict.get('complaint_id')]

        result = answer_case_query(
            query_text=query_text,
            complaint=complaint_dict,
            existing_complaints=existing_list
        )

        return jsonify({
            "status": "success",
            "active_case": complaint_dict.get('complaint_id') if complaint_dict else None,
            "data": result
        }), 200

    except Exception as e:
        return jsonify({"status": "error", "message": f"Investigation assistant failed: {str(e)}"}), 500

@rag_bp.route('/documents', methods=['GET'])
def list_knowledge_documents():
    """Retrieve metadata for indexed RAG knowledge base documents."""
    try:
        with get_session() as session:
            docs = session.query(KnowledgeDocument).all()
            return jsonify({
                "status": "success",
                "count": len(docs),
                "data": [d.to_dict() for d in docs]
            }), 200
    except Exception as e:
        return jsonify({"status": "error", "message": f"Unable to list documents: {str(e)}"}), 500

@rag_bp.route('/reindex', methods=['POST'])
def reindex_knowledge_base():
    """Trigger rebuild of the semantic vector index from knowledge documents."""
    try:
        store = get_vector_store()
        store.build_index()

        return jsonify({
            "status": "success",
            "message": "Knowledge base index re-built successfully.",
            "chunk_count": len(store.chunks)
        }), 200
    except Exception as e:
        return jsonify({"status": "error", "message": f"Reindex failed: {str(e)}"}), 500

@rag_bp.route('/evaluation', methods=['GET'])
def get_rag_evaluation():
    """Retrieve measured RAG evaluation metrics across 20 golden legal/SOP benchmark Q&A pairs."""
    eval_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'models', 'rag_evaluation_metrics.json')
    if os.path.exists(eval_path):
        try:
            with open(eval_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return jsonify({
                "status": "success",
                "data": data
            }), 200
        except Exception as e:
            return jsonify({"status": "error", "message": f"Error reading evaluation file: {e}"}), 500
    return jsonify({
        "status": "unavailable",
        "message": "Evaluation metrics not found. Run backend/rag/evaluate_rag.py first."
    }), 404

