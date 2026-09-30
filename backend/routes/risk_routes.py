from flask import Blueprint, request, jsonify
from database import get_session
from models_db import RiskAssessment, Complaint
from analyzer import calculate_risk_score, detect_threat_indicators

risk_bp = Blueprint('risk_bp', __name__)

@risk_bp.route('/calculate', methods=['POST'])
def calculate_risk():
    """
    On-demand calculation of deterministic, explainable risk score with full component breakdown.
    Returns:
      - Category Threat (up to 20 pts)
      - Incident Severity (up to 25 pts)
      - Financial Impact (up to 20 pts)
      - Account Compromise (up to 15 pts)
      - Personal Info Exposure (up to 12 pts)
      - Verified Threat Indicators (up to 15 pts)
      - ML Confidence Factor (up to 15 pts)
    """
    try:
        data = request.get_json() or {}
        predicted_category = data.get('category') or data.get('predicted_category', 'Phishing Attack')
        confidence = float(data.get('confidence', 0.85))
        severity = data.get('severity', 'Medium')
        financial_loss = float(data.get('financial_loss', 0.0) or 0.0)
        personal_info_exposed = bool(data.get('personal_info_exposed', False))
        account_compromised = bool(data.get('account_compromised', False))
        
        # Threat indicators can be passed directly or inferred
        threat_indicators = data.get('threat_indicators')
        if threat_indicators is None and data.get('description'):
            threat_indicators = detect_threat_indicators(
                data.get('description', ''),
                personal_info_exposed=personal_info_exposed,
                account_compromised=account_compromised
            )

        final_score, risk_level, reasons, breakdown = calculate_risk_score(
            predicted_category=predicted_category,
            confidence=confidence,
            severity=severity,
            financial_loss=financial_loss,
            personal_info_exposed=personal_info_exposed,
            account_compromised=account_compromised,
            threat_indicators=threat_indicators or []
        )

        # Simulation Lab What-If parameters
        victim_count = int(data.get('victim_count', 1))
        attack_sophistication = str(data.get('attack_sophistication', 'Basic'))
        location_risk = str(data.get('location_risk', 'Moderate'))
        prior_incidents = int(data.get('prior_incidents', 0))

        simulated_additions = 0
        if victim_count > 1:
            pts = min(15, (victim_count - 1) * 3)
            simulated_additions += pts
            reasons.append(f"Multi-victim incident impact ({victim_count} affected parties): +{pts} pts")
            breakdown['multi_victim_factor'] = pts
            
        if attack_sophistication in ['Advanced', 'Ransomware', 'APT / Nation-State']:
            simulated_additions += 12
            reasons.append(f"High attack sophistication ({attack_sophistication}): +12 pts")
            breakdown['sophistication_factor'] = 12
        elif attack_sophistication == 'Intermediate':
            simulated_additions += 6
            reasons.append("Intermediate attack sophistication: +6 pts")
            breakdown['sophistication_factor'] = 6

        if location_risk in ['High Risk Hotspot', 'Critical Multi-Jurisdiction']:
            simulated_additions += 8
            reasons.append("Jurisdictional hot-zone elevation: +8 pts")
            breakdown['location_risk_factor'] = 8

        if prior_incidents > 0:
            pts = min(10, prior_incidents * 2)
            simulated_additions += pts
            reasons.append(f"Prior recurring incident pattern ({prior_incidents} priors): +{pts} pts")
            breakdown['recurrence_factor'] = pts

        final_score = min(100, max(0, final_score + simulated_additions))
        if final_score >= 81:
            risk_level = "CRITICAL"
        elif final_score >= 61:
            risk_level = "HIGH"
        elif final_score >= 31:
            risk_level = "MEDIUM"
        else:
            risk_level = "LOW"

        return jsonify({
            "status": "success",
            "data": {
                "risk_score": final_score,
                "risk_level": risk_level,
                "breakdown": breakdown,
                "reasons": reasons,
                "max_possible_points": {
                    "category_factor": 20,
                    "severity_factor": 25,
                    "financial_factor": 20,
                    "account_compromised_factor": 15,
                    "pii_factor": 12,
                    "threat_indicators_factor": 15,
                    "confidence_factor": 15
                }
            }
        }), 200

    except Exception as e:
        return jsonify({"status": "error", "message": f"Risk calculation failed: {str(e)}"}), 500

@risk_bp.route('/case/<complaint_id>', methods=['GET'])
def get_case_risk(complaint_id):
    """Retrieve the explainable risk breakdown record for a registered complaint."""
    try:
        with get_session() as session:
            risk_rec = session.query(RiskAssessment).filter(RiskAssessment.complaint_id == complaint_id).first()
            if not risk_rec:
                # Try finding complaint first
                complaint = session.query(Complaint).filter(
                    (Complaint.complaint_id == complaint_id) | (Complaint.id == (int(complaint_id) if complaint_id.isdigit() else -1))
                ).first()
                if complaint and complaint.risk_assessment:
                    risk_rec = complaint.risk_assessment
                elif complaint:
                    # Compute on the fly if record was missing
                    final_score, risk_level, reasons, breakdown = calculate_risk_score(
                        predicted_category=complaint.predicted_category or complaint.category,
                        confidence=complaint.confidence or 0.85,
                        severity=complaint.severity,
                        financial_loss=complaint.financial_loss,
                        personal_info_exposed=complaint.personal_info_exposed,
                        account_compromised=complaint.account_compromised
                    )
                    return jsonify({
                        "status": "success",
                        "data": {
                            "complaint_id": complaint.complaint_id,
                            "final_score": final_score,
                            "risk_level": risk_level,
                            "breakdown": breakdown,
                            "reasons": reasons
                        }
                    }), 200

            if not risk_rec:
                return jsonify({"status": "fail", "message": "Risk assessment not found for this case."}), 404

            return jsonify({
                "status": "success",
                "data": risk_rec.to_dict()
            }), 200

    except Exception as e:
        return jsonify({"status": "error", "message": f"Unable to fetch risk assessment: {str(e)}"}), 500
