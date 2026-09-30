"""
Agentic Copilot Flask Blueprint
Endpoints for multi-tool agent execution, natural language BI chart generation, and global command palette.
"""

from flask import Blueprint, request, jsonify
from .agent_service import agent_service

agent_bp = Blueprint('agent_bp', __name__)

@agent_bp.route('/chat', methods=['POST'])
def agent_chat():
    data = request.get_json() or {}
    prompt = data.get('prompt', '')
    case_context = data.get('case_context', None)
    history = data.get('conversation_history', [])

    if not prompt.strip():
        return jsonify({"status": "error", "message": "prompt is required"}), 400

    result = agent_service.execute_agent_loop(
        prompt=prompt,
        case_context=case_context,
        conversation_history=history
    )
    return jsonify(result)

@agent_bp.route('/quick-command', methods=['POST'])
def quick_command():
    data = request.get_json() or {}
    query = data.get('query', '').strip()

    # Spotlight search results across cases, actions, and features
    results = [
        {"type": "action", "title": "Freeze Account Under Sec 94 BNSS", "category": "Rapid Interdiction", "action": "open_freeze"},
        {"type": "action", "title": "Check Lookalike Domain Whitelist", "category": "Safe-Scan", "action": "open_scan"},
        {"type": "case", "title": "Case #CR-2026-98214 (Online Financial Fraud - ₹4,50,000)", "category": "Active Investigation", "case_id": "CR-2026-98214"},
        {"type": "case", "title": "Case #CR-2026-10492 (Digital Arrest Extortion - ₹1,80,000)", "category": "Active Investigation", "case_id": "CR-2026-10492"},
        {"type": "nav", "title": "Scam Dojo • AI Roleplay Simulator", "category": "Citizen Training", "tab": "dojo"},
        {"type": "nav", "title": "Emerging Threat Detector (Zero-Day Discovery)", "category": "AI Research", "tab": "threats"},
        {"type": "nav", "title": "Money Trail Multi-Hop Sankey Flow", "category": "Investigator Tools", "tab": "moneytrail"}
    ]

    if query:
        q_lower = query.lower()
        filtered = [r for r in results if q_lower in r['title'].lower() or q_lower in r['category'].lower()]

        # Query database for matching complaints by state, ID, or crime_type
        try:
            from database import get_session
            from models_db import Complaint
            session = get_session()
            db_matches = session.query(Complaint).filter(
                (Complaint.complaint_id.ilike(f"%{query}%")) |
                (Complaint.state.ilike(f"%{query}%")) |
                (Complaint.crime_type.ilike(f"%{query}%"))
            ).limit(5).all()
            for c in db_matches:
                filtered.append({
                    "type": "case",
                    "title": f"Case #{c.complaint_id} ({c.crime_type} - {c.state} - ₹{int(c.financial_loss or 0):,})",
                    "category": f"{c.state} Cyber Cell",
                    "case_id": c.complaint_id
                })
            session.close()
        except Exception:
            pass
        results = filtered

    return jsonify({
        "status": "success",
        "query": query,
        "count": len(results),
        "results": results
    })
