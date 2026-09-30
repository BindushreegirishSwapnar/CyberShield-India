"""
Safe-Scan Flask Blueprint
Exposes multi-channel threat lookup, lookalike domain detection, UPI QR inspection, and OCR parsing.
"""

from flask import Blueprint, request, jsonify
from .safescan_service import safescan_service

safescan_bp = Blueprint('safescan_bp', __name__)

@safescan_bp.route('/lookup', methods=['POST'])
def lookup_entity():
    data = request.get_json() or {}
    entity_type = data.get('entity_type', 'phone').lower()
    entity_value = data.get('entity_value', '')

    if not entity_value.strip():
        return jsonify({"status": "error", "message": "entity_value is required"}), 400

    result = safescan_service.query_reputation_database(entity_type, entity_value)
    
    # If URL, also include lookalike domain check
    if entity_type == 'url':
        result["lookalike_analysis"] = safescan_service.check_lookalike_domain(entity_value)

    return jsonify({
        "status": "success",
        "data": result
    })

@safescan_bp.route('/domain-check', methods=['POST'])
def check_domain():
    data = request.get_json() or {}
    domain = data.get('domain', '')
    if not domain.strip():
        return jsonify({"status": "error", "message": "domain is required"}), 400

    result = safescan_service.check_lookalike_domain(domain)
    return jsonify({
        "status": "success",
        "data": result
    })

@safescan_bp.route('/qr-check', methods=['POST'])
def check_qr():
    data = request.get_json() or {}
    qr_text = data.get('qr_text', '')
    if not qr_text.strip():
        return jsonify({"status": "error", "message": "qr_text is required"}), 400

    result = safescan_service.parse_upi_qr(qr_text)
    return jsonify({
        "status": "success",
        "data": result
    })

@safescan_bp.route('/ocr-analyze', methods=['POST'])
def analyze_ocr():
    data = request.get_json() or {}
    text = data.get('text', '')
    if not text.strip():
        return jsonify({"status": "error", "message": "text is required"}), 400

    result = safescan_service.analyze_extracted_ocr(text)
    return jsonify({
        "status": "success",
        "data": result
    })
