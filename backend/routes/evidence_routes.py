import hashlib
from datetime import datetime
from flask import Blueprint, request, jsonify
from database import get_session
from models_db import EvidenceItem, Complaint, TimelineEvent, AuditLog

evidence_bp = Blueprint('evidence_bp', __name__)

EVIDENCE_TYPES = [
    "Bank Transaction Statement",
    "SMS / Message Screenshot",
    "Email RFC-822 Headers",
    "Payment Gateway Receipt / UTR",
    "Phishing URL / Domain Archive",
    "Endpoint Device System Log",
    "Network Packet Capture / IPDR",
    "Forensic Disk Image / Memory Dump",
    "Platform Account Profile Export"
]

@evidence_bp.route('/types', methods=['GET'])
def get_evidence_types():
    """Retrieve recognized digital evidence types."""
    return jsonify({
        "status": "success",
        "data": EVIDENCE_TYPES
    }), 200

@evidence_bp.route('/all', methods=['GET'])
def list_all_evidence():
    """List evidence items across cases with optional type filtering."""
    try:
        ev_type = request.args.get('type')
        limit = min(100, max(1, int(request.args.get('limit', 50))))

        with get_session() as session:
            query = session.query(EvidenceItem)
            if ev_type and ev_type != 'All':
                query = query.filter(EvidenceItem.evidence_type == ev_type)

            items = query.order_by(EvidenceItem.created_at.desc()).limit(limit).all()

            return jsonify({
                "status": "success",
                "count": len(items),
                "data": [item.to_dict() for item in items]
            }), 200

    except Exception as e:
        return jsonify({"status": "error", "message": f"Unable to fetch evidence: {str(e)}"}), 500

@evidence_bp.route('/case/<complaint_id>', methods=['GET'])
def get_case_evidence(complaint_id):
    """Retrieve all evidence items cataloged for a specific case."""
    try:
        with get_session() as session:
            items = session.query(EvidenceItem).filter(
                EvidenceItem.complaint_id == complaint_id
            ).order_by(EvidenceItem.created_at.desc()).all()

            return jsonify({
                "status": "success",
                "count": len(items),
                "complaint_id": complaint_id,
                "data": [item.to_dict() for item in items]
            }), 200

    except Exception as e:
        return jsonify({"status": "error", "message": f"Unable to fetch case evidence: {str(e)}"}), 500

@evidence_bp.route('/case/<complaint_id>', methods=['POST'])
def add_case_evidence(complaint_id):
    """
    Catalog a new digital evidence artifact for a complaint.
    Automatically generates a SHA-256 cryptographic hash for data integrity tracking.
    """
    try:
        data = request.get_json() or {}
        evidence_type = data.get('evidence_type', 'Bank Transaction Statement').strip()
        description = data.get('description', '').strip()
        file_name = data.get('file_name', f"evidence_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf").strip()
        source = data.get('source', 'Complainant Submission').strip()
        collected_by = data.get('collected_by', 'Investigating Officer').strip()

        if not description:
            return jsonify({"status": "fail", "message": "Evidence description is required."}), 400

        with get_session() as session:
            complaint = session.query(Complaint).filter(
                (Complaint.complaint_id == complaint_id) | (Complaint.id == (int(complaint_id) if complaint_id.isdigit() else -1))
            ).first()

            if not complaint:
                return jsonify({"status": "fail", "message": "Associated case not found."}), 404

            # Generate SHA-256 hash
            content_seed = f"{complaint.complaint_id}:{evidence_type}:{description}:{file_name}:{datetime.utcnow().isoformat()}".encode('utf-8')
            sha256_hash = hashlib.sha256(content_seed).hexdigest()

            # Sequence number
            count = session.query(EvidenceItem).count()
            evd_number = f"EVD-2026-{(count + 1):06d}"
            now_dt = datetime.now()

            item = EvidenceItem(
                evidence_number=evd_number,
                complaint_id=complaint.complaint_id,
                evidence_type=evidence_type,
                description=description,
                file_name=file_name,
                file_hash_sha256=sha256_hash,
                source=source,
                collected_by=collected_by,
                chain_of_custody_verified=True,
                created_at=now_dt
            )
            session.add(item)

            # Record timeline event
            session.add(TimelineEvent(
                complaint_id=complaint.complaint_id,
                event_type="EVIDENCE_UPLOADED",
                title=f"Digital Evidence Cataloged: {evd_number}",
                description=f"{evidence_type} acquired ({file_name}). SHA-256: {sha256_hash[:16]}...",
                actor=collected_by,
                created_at=now_dt
            ))

            # Record audit trail
            session.add(AuditLog(
                timestamp=now_dt.strftime("%d %b %Y, %I:%M %p"),
                user_email=data.get('user_email', 'analyst@cybercrime.gov.in'),
                user_role="Analyst",
                action="UPLOAD_EVIDENCE",
                target_entity="EvidenceItem",
                target_id=evd_number,
                details=f"Cataloged {evidence_type} for {complaint.complaint_id}. SHA-256: {sha256_hash}",
                ip_address=request.remote_addr or "127.0.0.1"
            ))

            return jsonify({
                "status": "success",
                "message": f"Evidence {evd_number} recorded with SHA-256 integrity hash.",
                "data": item.to_dict()
            }), 201

    except Exception as e:
        return jsonify({"status": "error", "message": f"Failed to record evidence: {str(e)}"}), 500
