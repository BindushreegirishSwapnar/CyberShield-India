"""
Scam Dojo Flask Blueprint
Endpoints for interactive gamified AI roleplay, live Red Flag Coach analysis, and certificates.
"""

from flask import Blueprint, request, jsonify
from .dojo_service import dojo_service

dojo_bp = Blueprint('dojo_bp', __name__)

@dojo_bp.route('/scenarios', methods=['GET'])
def get_scenarios():
    scenarios = dojo_service.get_all_scenarios()
    return jsonify({
        "status": "success",
        "count": len(scenarios),
        "data": scenarios,
        "is_synthetic": True
    })

@dojo_bp.route('/chat', methods=['POST'])
def process_turn():
    data = request.get_json() or {}
    scenario_id = data.get('scenario_id', 'digital_arrest')
    conversation_history = data.get('conversation_history', [])
    user_message = data.get('user_message', '')
    elder_mode = bool(data.get('elder_mode', False))

    if not user_message.strip():
        return jsonify({
            "status": "error",
            "message": "Citizen response message is required."
        }), 400

    result = dojo_service.evaluate_turn(
        scenario_id=scenario_id,
        conversation_history=conversation_history,
        user_message=user_message,
        elder_mode=elder_mode
    )

    return jsonify({
        "status": "success",
        "data": result
    })

@dojo_bp.route('/evaluate', methods=['POST'])
def evaluate_session():
    data = request.get_json() or {}
    scenario_id = data.get('scenario_id', 'digital_arrest')
    total_score = int(data.get('total_score', 0))
    turns_played = int(data.get('turns_played', 3))
    elder_mode = bool(data.get('elder_mode', False))

    result = dojo_service.generate_final_evaluation(
        scenario_id=scenario_id,
        total_score=total_score,
        turns_played=turns_played,
        elder_mode=elder_mode
    )

    return jsonify(result)
