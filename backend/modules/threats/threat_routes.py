"""
Emerging Threats Flask Blueprint
Endpoints for zero-day scam cluster discovery, category promotion, and model retraining.
"""

from flask import Blueprint, request, jsonify
from .threat_cluster_service import threat_service

threat_bp = Blueprint('threat_bp', __name__)

@threat_bp.route('/clusters', methods=['GET'])
def get_clusters():
    result = threat_service.get_clusters_and_drift()
    return jsonify(result)

@threat_bp.route('/approve-category', methods=['POST'])
def approve_category():
    data = request.get_json() or {}
    cluster_id = data.get('cluster_id', '')
    if not cluster_id:
        return jsonify({"status": "error", "message": "cluster_id is required"}), 400

    result = threat_service.approve_category(cluster_id)
    return jsonify(result)

@threat_bp.route('/retrain', methods=['POST'])
def retrain_model():
    result = threat_service.trigger_retraining()
    return jsonify(result)
