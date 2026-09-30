from flask import Blueprint, request, jsonify
from database import get_session
from models_db import Complaint
from analyzer import analyze_complaint

analysis_bp = Blueprint('analysis_bp', __name__)

CATEGORIES_INFO = [
    {
        "category": "Phishing Attack",
        "description": "Deceptive electronic communications mimicking trustworthy entities to harvest credentials or financial data.",
        "statutory": "Section 66D IT Act 2000 (Cheating by Personation using Computer Resource)",
        "base_weight": 15
    },
    {
        "category": "Online Financial Fraud",
        "description": "Unauthorized digital fund debits via fraudulent UPI requests, payment gateways, or ATM skimming.",
        "statutory": "Section 66D IT Act & Section 420 IPC / Section 318(4) BNS",
        "base_weight": 18
    },
    {
        "category": "Identity Theft",
        "description": "Fraudulent appropriation and unauthorized use of another person's identifying data or biometric credentials.",
        "statutory": "Section 66C IT Act 2000 (Identity Theft & Electronic Signature Misuse)",
        "base_weight": 15
    },
    {
        "category": "Cyber Bullying / Harassment",
        "description": "Persistent intimidation, stalking, and dissemination of defamatory or non-consensual media online.",
        "statutory": "Section 67 IT Act & Section 354D IPC / Section 78 BNSS",
        "base_weight": 12
    },
    {
        "category": "Ransomware / Malware",
        "description": "Deployment of malicious payloads that encrypt victim endpoints and coerce cryptocurrency extortion.",
        "statutory": "Section 43 & Section 66 IT Act 2000 (Computer Contaminant & Hacking)",
        "base_weight": 20
    },
    {
        "category": "Data Breach",
        "description": "Unauthorized exfiltration and illicit dissemination of confidential personal or enterprise databases.",
        "statutory": "Section 43A IT Act & Digital Personal Data Protection Act 2023",
        "base_weight": 20
    },
    {
        "category": "Account Takeover",
        "description": "Hijacking of user accounts or cellular SIM cards to bypass multi-factor authentication controls.",
        "statutory": "Section 66 & 66C IT Act 2000",
        "base_weight": 18
    },
    {
        "category": "Social Engineering",
        "description": "Psychological manipulation (such as 'Digital Arrest' scams) coercing victims into voluntary fund transfers.",
        "statutory": "Section 419/420 IPC & Section 66D IT Act",
        "base_weight": 14
    },
    {
        "category": "Online Shopping Fraud",
        "description": "Fraudulent e-commerce portals offering counterfeit clearance sales collecting advance UPI payments.",
        "statutory": "Section 66D IT Act & Consumer Protection E-Commerce Rules",
        "base_weight": 10
    },
    {
        "category": "Investment/Crypto Fraud",
        "description": "High-yield task rating schemes and bogus cryptocurrency platforms freezing victim withdrawals.",
        "statutory": "Section 66D IT Act & Banning of Unregulated Deposit Schemes Act (BUDS)",
        "base_weight": 16
    }
]

@analysis_bp.route('', methods=['POST'])
@analysis_bp.route('/', methods=['POST'])
def run_analysis():
    """Real-time complaint narrative triage and explainable AI inference."""
    try:
        data = request.get_json() or {}
        description = data.get('description', '').strip()
        if not description:
            return jsonify({"status": "fail", "message": "Complaint description is required."}), 400

        reported_category = data.get('category', 'Phishing Attack')
        severity = data.get('severity', 'Medium')
        financial_loss = float(data.get('financial_loss', 0.0) or 0.0)
        personal_info_exposed = bool(data.get('personal_info_exposed', False))
        account_compromised = bool(data.get('account_compromised', False))

        with get_session() as session:
            # Query recent complaints for similarity comparison
            existing = session.query(Complaint).limit(60).all()
            existing_dicts = [c.to_dict() for c in existing]

        analysis = analyze_complaint(
            description=description,
            reported_category=reported_category,
            severity=severity,
            financial_loss=financial_loss,
            personal_info_exposed=personal_info_exposed,
            account_compromised=account_compromised,
            existing_complaints=existing_dicts
        )

        return jsonify({
            "status": "success",
            "data": analysis
        }), 200

    except Exception as e:
        return jsonify({"status": "error", "message": f"Analysis failed: {str(e)}"}), 500

@analysis_bp.route('/categories', methods=['GET'])
def get_categories():
    """Retrieve recognized cybercrime categories, statutory provisions, and baseline weights."""
    return jsonify({
        "status": "success",
        "count": len(CATEGORIES_INFO),
        "data": CATEGORIES_INFO
    }), 200
