"""
Money Trail Flask Blueprint
Endpoints for multi-hop money flow graph, Freeze Priority Scoring, time-dispersion simulation, and statutory freeze notices.
"""

from flask import Blueprint, request, jsonify
from .moneytrail_service import moneytrail_service

moneytrail_bp = Blueprint('moneytrail_bp', __name__)

@moneytrail_bp.route('/trail/<case_id>', methods=['GET'])
@moneytrail_bp.route('/trail', methods=['GET'])
def get_trail(case_id=None):
    if not case_id:
        case_id = request.args.get('case_id', 'CR-2026-98214')
    result = moneytrail_service.get_fund_trail(case_id)
    return jsonify({
        "status": "success",
        "data": result
    })

@moneytrail_bp.route('/simulate', methods=['POST'])
def simulate_dispersion():
    data = request.get_json() or {}
    case_id = data.get('case_id', 'CR-2026-98214')
    minutes = int(data.get('minutes_elapsed', 45))

    result = moneytrail_service.simulate_time_dispersion(case_id, minutes)
    return jsonify({
        "status": "success",
        "data": result
    })

@moneytrail_bp.route('/generate-notice', methods=['POST'])
def generate_notice():
    data = request.get_json() or {}
    case_id = data.get('case_id', 'CR-2026-98214')
    mule_account = data.get('mule_account', '104928172901')
    bank_name = data.get('bank_name', 'Canara Bank')
    officer_name = data.get('officer_name', 'Inspector Rajesh Kumar')
    badge_no = data.get('badge_no', 'KA-CYBER-8841')

    result = moneytrail_service.generate_statutory_notice(
        case_id=case_id,
        mule_account=mule_account,
        bank_name=bank_name,
        officer_name=officer_name,
        badge_no=badge_no
    )
    return jsonify({
        "status": "success",
        "data": result
    })
