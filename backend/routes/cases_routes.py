import csv
import io
import json
import random
from datetime import datetime
from flask import Blueprint, request, jsonify, Response
from sqlalchemy import or_, and_, desc, asc
from database import get_session, INDIAN_JURISDICTIONS, OFFICERS_POOL
from models_db import (
    Complaint, RiskAssessment, MLPrediction, ThreatIndicator,
    Investigation, InvestigationNote, EvidenceItem, TimelineEvent, Alert, AuditLog
)
from analyzer import analyze_complaint

cases_bp = Blueprint('cases_bp', __name__)

@cases_bp.route('', methods=['GET'])
@cases_bp.route('/', methods=['GET'])
def get_cases():
    """
    Fetch complaints with server-side pagination, full-text search,
    multi-parameter filtering, and deterministic sorting.
    """
    try:
        # Query parameters
        page = max(1, int(request.args.get('page', 1)))
        page_size = min(100, max(1, int(request.args.get('page_size', request.args.get('limit', 20)))))
        
        search = request.args.get('search', '').strip()
        crime_type = request.args.get('crime_type') or request.args.get('category')
        risk_level = request.args.get('risk_level')
        severity = request.args.get('severity')
        current_status = request.args.get('status') or request.args.get('current_status')
        state = request.args.get('state')
        city = request.args.get('city') or request.args.get('location')
        assigned_officer = request.args.get('assigned_officer')
        date_from = request.args.get('date_from')
        date_to = request.args.get('date_to')
        min_loss = request.args.get('min_loss', type=float)
        max_loss = request.args.get('max_loss', type=float)
        
        sort_by = request.args.get('sort_by', 'created_at')
        sort_order = request.args.get('sort_order', 'desc').lower()

        with get_session() as session:
            query = session.query(Complaint)

            # Apply filters
            if crime_type and crime_type != 'All':
                query = query.filter(or_(Complaint.crime_type == crime_type, Complaint.predicted_category == crime_type, Complaint.category == crime_type))

            if risk_level and risk_level != 'All':
                query = query.filter(Complaint.risk_level == risk_level.upper())

            if severity and severity != 'All':
                query = query.filter(Complaint.severity == severity)

            if current_status and current_status != 'All':
                query = query.filter(or_(Complaint.current_status == current_status, Complaint.status == current_status))

            if state and state != 'All':
                query = query.filter(Complaint.state == state)

            if city and city != 'All':
                query = query.filter(or_(Complaint.city.ilike(f"%{city}%"), Complaint.location.ilike(f"%{city}%")))

            if assigned_officer and assigned_officer != 'All':
                query = query.filter(Complaint.assigned_officer.ilike(f"%{assigned_officer}%"))

            if date_from:
                query = query.filter(Complaint.complaint_date >= date_from)

            if date_to:
                query = query.filter(Complaint.complaint_date <= date_to)

            if min_loss is not None:
                query = query.filter(Complaint.financial_loss >= min_loss)

            if max_loss is not None:
                query = query.filter(Complaint.financial_loss <= max_loss)

            if search:
                pattern = f"%{search}%"
                query = query.filter(or_(
                    Complaint.complaint_id.ilike(pattern),
                    Complaint.description.ilike(pattern),
                    Complaint.city.ilike(pattern),
                    Complaint.state.ilike(pattern),
                    Complaint.crime_type.ilike(pattern),
                    Complaint.predicted_category.ilike(pattern),
                    Complaint.platform.ilike(pattern),
                    Complaint.assigned_officer.ilike(pattern)
                ))

            # Total matching count
            total_count = query.count()

            # Sorting
            sort_attr = getattr(Complaint, sort_by, Complaint.created_at)
            order_func = desc if sort_order == 'desc' else asc
            query = query.order_by(order_func(sort_attr), desc(Complaint.id))

            # Pagination
            offset = (page - 1) * page_size
            complaints = query.offset(offset).limit(page_size).all()

            total_pages = (total_count + page_size - 1) // page_size

            return jsonify({
                "status": "success",
                "total": total_count,
                "page": page,
                "page_size": page_size,
                "total_pages": total_pages,
                "count": len(complaints),
                "data": [c.to_dict() for c in complaints]
            }), 200

    except Exception as e:
        return jsonify({"status": "error", "message": f"Unable to fetch cases: {str(e)}"}), 500

@cases_bp.route('/<identifier>', methods=['GET'])
def get_case_detail(identifier):
    """
    Retrieve comprehensive case record including ML inference audit,
    explainable risk breakdown, extracted IOCs, evidence items, notes, and timeline.
    """
    try:
        with get_session() as session:
            complaint = None
            if identifier.isdigit():
                complaint = session.query(Complaint).filter(Complaint.id == int(identifier)).first()
            
            if not complaint:
                complaint = session.query(Complaint).filter(
                    (Complaint.complaint_id == identifier) | (Complaint.uuid == identifier)
                ).first()

            if not complaint:
                return jsonify({"status": "fail", "message": f"Case '{identifier}' not found."}), 404

            comp_dict = complaint.to_dict()

            # Associated Risk Assessment
            risk_rec = session.query(RiskAssessment).filter(RiskAssessment.complaint_id == complaint.complaint_id).first()
            comp_dict["risk_assessment_detail"] = risk_rec.to_dict() if risk_rec else None

            # Associated ML Prediction
            ml_rec = session.query(MLPrediction).filter(MLPrediction.complaint_id == complaint.complaint_id).first()
            comp_dict["ml_prediction_detail"] = ml_rec.to_dict() if ml_rec else None

            # Extracted Threat Indicators
            threat_recs = session.query(ThreatIndicator).filter(ThreatIndicator.complaint_id == complaint.complaint_id).all()
            comp_dict["threat_indicators_list"] = [t.to_dict() for t in threat_recs]

            # Investigation Record
            inv_rec = session.query(Investigation).filter(Investigation.complaint_id == complaint.complaint_id).first()
            comp_dict["investigation_detail"] = inv_rec.to_dict() if inv_rec else None

            # Notes
            note_recs = session.query(InvestigationNote).filter(
                InvestigationNote.complaint_id == complaint.complaint_id
            ).order_by(desc(InvestigationNote.created_at)).all()
            comp_dict["notes"] = [n.to_dict() for n in note_recs]

            # Evidence Items
            evidence_recs = session.query(EvidenceItem).filter(
                EvidenceItem.complaint_id == complaint.complaint_id
            ).order_by(desc(EvidenceItem.created_at)).all()
            comp_dict["evidence_items"] = [e.to_dict() for e in evidence_recs]

            # Timeline Events
            timeline_recs = session.query(TimelineEvent).filter(
                TimelineEvent.complaint_id == complaint.complaint_id
            ).order_by(asc(TimelineEvent.created_at)).all()
            comp_dict["timeline"] = [t.to_dict() for t in timeline_recs]

            # Alerts
            alert_recs = session.query(Alert).filter(Alert.complaint_id == complaint.complaint_id).all()
            comp_dict["alerts"] = [a.to_dict() for a in alert_recs]

            return jsonify({
                "status": "success",
                "data": comp_dict
            }), 200

    except Exception as e:
        return jsonify({"status": "error", "message": f"Error retrieving case detail: {str(e)}"}), 500

@cases_bp.route('', methods=['POST'])
@cases_bp.route('/', methods=['POST'])
def create_case():
    """
    Register a new cybercrime complaint. Runs calibrated NLP classification,
    multi-factor risk scoring, IOC extraction, and persists full relational case graph.
    """
    try:
        data = request.get_json() or {}
        description = data.get('description', '').strip()
        location_raw = data.get('location', '').strip() or data.get('city', '').strip() or 'Mumbai'
        state = data.get('state', '').strip()
        category = data.get('category', 'Phishing Attack').strip()
        severity = data.get('severity', 'Medium').strip()
        financial_loss = float(data.get('financial_loss', 0.0) or 0.0)
        incident_date = data.get('incident_date', datetime.now().strftime('%Y-%m-%d')).strip()
        personal_info_exposed = bool(data.get('personal_info_exposed', False))
        account_compromised = bool(data.get('account_compromised', False))
        victim_age_group = data.get('victim_age_group', '26-40')
        platform = data.get('platform', 'Online Banking / UPI')
        payment_method = data.get('payment_method', 'UPI')

        if not description:
            return jsonify({"status": "fail", "message": "Complaint narration is mandatory."}), 400

        # Infer state if missing
        if not state or state not in INDIAN_JURISDICTIONS:
            loc_lower = location_raw.lower()
            if any(c in loc_lower for c in ['bengaluru', 'bangalore', 'mysuru', 'mangaluru']):
                state = 'Karnataka'
            elif any(c in loc_lower for c in ['mumbai', 'pune', 'nagpur']):
                state = 'Maharashtra'
            elif 'hyderabad' in loc_lower:
                state = 'Telangana'
            elif 'delhi' in loc_lower:
                state = 'Delhi'
            elif 'chennai' in loc_lower:
                state = 'Tamil Nadu'
            elif 'ahmedabad' in loc_lower:
                state = 'Gujarat'
            elif 'kolkata' in loc_lower:
                state = 'West Bengal'
            elif any(c in loc_lower for c in ['noida', 'lucknow', 'kanpur']):
                state = 'Uttar Pradesh'
            else:
                state = 'Maharashtra'

        state_meta = INDIAN_JURISDICTIONS.get(state, INDIAN_JURISDICTIONS["Maharashtra"])
        state_code = state_meta["code"]
        city_name = location_raw if location_raw else state_meta["cities"][0][0]
        station_name = state_meta["cities"][0][1]

        # Officer for state
        state_officers = [o for o in OFFICERS_POOL if o[2] == state]
        officer = state_officers[0] if state_officers else OFFICERS_POOL[0]
        officer_name, officer_id = officer[0], officer[1]

        with get_session() as session:
            # Query existing for similarity
            existing_rows = session.query(Complaint).limit(50).all()
            existing_list = [c.to_dict() for c in existing_rows]

            # Run analysis engine
            analysis = analyze_complaint(
                description=description,
                reported_category=category,
                severity=severity,
                financial_loss=financial_loss,
                personal_info_exposed=personal_info_exposed,
                account_compromised=account_compromised,
                existing_complaints=existing_list
            )

            # Generate new complaint serial number
            current_max = session.query(Complaint).count()
            serial = current_max + 101
            complaint_id = f"CC-2026-{state_code}-{serial:06d}"
            now_dt = datetime.now()

            priority = "Critical" if analysis["risk_score"] >= 75 else "High" if analysis["risk_score"] >= 50 else "Medium"

            complaint = Complaint(
                complaint_id=complaint_id,
                title=f"{analysis['predicted_category']} Incident in {city_name}",
                description=description,
                incident_date=incident_date,
                complaint_date=now_dt.strftime("%Y-%m-%d"),
                state=state,
                district=city_name,
                city=city_name,
                location=city_name,
                cyber_cell_station=station_name,
                complaint_channel="National Cyber Crime Portal",
                crime_type=category,
                category=category,
                subcategory="Online Fraudulent Incident",
                reported_amount=financial_loss,
                financial_loss=financial_loss,
                victim_age_group=victim_age_group,
                victim_gender="Individual",
                victim_type="Individual",
                platform=platform,
                payment_method=payment_method,
                attack_vector="Digital Fraud Vector",
                suspected_modus_operandi=f"Reported {category} involving {platform}.",
                account_compromised=account_compromised,
                personal_info_exposed=personal_info_exposed,
                predicted_category=analysis["predicted_category"],
                confidence=analysis["confidence"],
                prediction_confidence=analysis["confidence"],
                risk_score=analysis["risk_score"],
                risk_level=analysis["risk_level"],
                priority=priority,
                severity=severity,
                current_status="New",
                status="New",
                investigation_status="Initial Triage",
                assigned_officer=officer_name,
                assigned_officer_id=officer_id,
                threat_indicators=json.dumps(analysis["threat_indicators"]),
                reasons=json.dumps(analysis["reasons"]),
                recommended_actions=json.dumps(analysis["recommended_actions"]),
                created_at=now_dt,
                updated_at=now_dt
            )
            session.add(complaint)

            # 1. Risk Assessment
            breakdown = analysis.get("risk_breakdown", {})
            risk_rec = RiskAssessment(
                complaint_id=complaint_id,
                base_score=breakdown.get("category_factor", 12),
                category_factor=breakdown.get("category_factor", 12),
                severity_factor=breakdown.get("severity_factor", 12),
                financial_factor=breakdown.get("financial_factor", 0),
                account_compromised_factor=breakdown.get("account_compromised_factor", 0),
                pii_factor=breakdown.get("pii_factor", 0),
                threat_indicators_factor=breakdown.get("threat_indicators_factor", 0),
                confidence_factor=breakdown.get("confidence_factor", 0.0),
                final_score=analysis["risk_score"],
                risk_level=analysis["risk_level"],
                explainability_json=json.dumps(analysis["reasons"]),
                created_at=now_dt
            )
            session.add(risk_rec)

            # 2. ML Prediction
            ml_rec = MLPrediction(
                complaint_id=complaint_id,
                predicted_category=analysis["predicted_category"],
                confidence=analysis["confidence"],
                model_name=analysis["model_name"],
                model_version=analysis["model_version"],
                probabilities_json=json.dumps(analysis["class_probabilities"]),
                top_features_json=json.dumps(analysis.get("top_tokens", [])),
                created_at=now_dt
            )
            session.add(ml_rec)

            # 3. Threat Indicators
            for ind in analysis.get("threat_indicators", []):
                val = ind.get("raw_value") or ind.get("label", "")
                session.add(ThreatIndicator(
                    complaint_id=complaint_id,
                    indicator_value=val,
                    indicator_type=ind.get("indicator_type", ind.get("code", "KEYWORD")),
                    code=ind.get("code"),
                    label=ind.get("label"),
                    severity=ind.get("severity", "Medium"),
                    confidence=0.92,
                    source="Complaint Narrative NLP Extraction",
                    first_seen=now_dt,
                    is_synthetic=True,
                    created_at=now_dt
                ))

            # 4. Investigation Record
            inv_rec = Investigation(
                case_number=f"INV-2026-{state_code}-{serial:06d}",
                complaint_id=complaint_id,
                lead_analyst=officer_name,
                lead_analyst_id=officer_id,
                status="Initial Triage",
                priority=priority,
                escalation_level="Tier-2 Special Cyber Cell" if priority in ["High", "Critical"] else "Standard",
                opened_at=now_dt,
                summary=f"Automated intake of complaint. Predicted {analysis['predicted_category']} with {analysis['risk_level']} risk."
            )
            session.add(inv_rec)

            # 5. Timeline Event
            session.add(TimelineEvent(
                complaint_id=complaint_id,
                event_type="COMPLAINT_RECEIVED",
                title="Complaint Registered",
                description=f"Complaint lodged via National Cyber Crime Portal. Assigned to {station_name}.",
                actor="Complainant / Intake Desk",
                created_at=now_dt
            ))
            session.add(TimelineEvent(
                complaint_id=complaint_id,
                event_type="ML_CLASSIFIED",
                title=f"AI Crime Type Classified: {analysis['predicted_category']}",
                description=f"Model classified complaint narrative with {analysis['confidence']}% confidence.",
                actor="ML Classification Engine",
                created_at=now_dt
            ))
            session.add(TimelineEvent(
                complaint_id=complaint_id,
                event_type="RISK_ASSESSED",
                title=f"Dynamic Risk Level: {analysis['risk_level']} ({analysis['risk_score']}/100)",
                description="Dynamic risk calculation generated with full component breakdown.",
                actor="Dynamic Risk Engine",
                created_at=now_dt
            ))

            # 6. High Risk Alert
            if analysis["risk_score"] >= 75:
                session.add(Alert(
                    alert_code=f"ALT-2026-{serial:06d}",
                    complaint_id=complaint_id,
                    severity="CRITICAL",
                    title=f"CRITICAL CYBER INCIDENT: {analysis['predicted_category'].upper()}",
                    message=f"Case {complaint_id} flagged Critical Risk ({analysis['risk_score']}/100). Immediate triage required.",
                    status="Unread",
                    created_at=now_dt
                ))

            # 7. Audit Log
            session.add(AuditLog(
                timestamp=now_dt.strftime("%d %b %Y, %I:%M %p"),
                user_email="system@cybercrime.gov.in",
                user_role="System",
                action="CREATE_CASE",
                target_entity="Complaint",
                target_id=complaint_id,
                details=f"Complaint {complaint_id} registered and triaged automatically.",
                ip_address=request.remote_addr or "127.0.0.1"
            ))

        return jsonify({
            "status": "success",
            "message": f"Complaint {complaint_id} registered and analyzed successfully.",
            "data": {
                **analysis,
                "complaint_id": complaint_id,
                "state": state,
                "city": city_name,
                "cyber_cell_station": station_name,
                "financial_loss": financial_loss,
                "incident_date": incident_date,
                "current_status": "New",
                "assigned_officer": officer_name
            }
        }), 201

    except Exception as e:
        return jsonify({"status": "error", "message": f"Unable to register complaint: {str(e)}"}), 500

@cases_bp.route('/<identifier>/status', methods=['PATCH'])
def update_case_status(identifier):
    """Update operational case status and record chronological timeline event."""
    try:
        data = request.get_json() or {}
        new_status = data.get('status', '').strip()
        allowed = ['New', 'Under Review', 'Investigating', 'Resolved', 'Closed']

        if new_status not in allowed:
            return jsonify({"status": "fail", "message": f"Invalid status. Allowed: {', '.join(allowed)}"}), 400

        user_note = data.get('note', '').strip()

        with get_session() as session:
            complaint = session.query(Complaint).filter(
                (Complaint.complaint_id == identifier) | (Complaint.id == (int(identifier) if identifier.isdigit() else -1))
            ).first()

            if not complaint:
                return jsonify({"status": "fail", "message": "Case not found."}), 404

            old_status = complaint.current_status
            complaint.current_status = new_status
            complaint.status = new_status
            complaint.updated_at = datetime.utcnow()

            # Record timeline event
            session.add(TimelineEvent(
                complaint_id=complaint.complaint_id,
                event_type="STATUS_CHANGED",
                title=f"Status Changed: {old_status} → {new_status}",
                description=user_note or f"Investigation stage updated from {old_status} to {new_status}.",
                actor=data.get('analyst_name', 'Analyst'),
                created_at=datetime.utcnow()
            ))

            # Record investigation note if provided
            if user_note:
                session.add(InvestigationNote(
                    complaint_id=complaint.complaint_id,
                    author_name=data.get('analyst_name', 'Analyst'),
                    author_role="Cyber Crime Analyst",
                    note_type="Status Change Note",
                    content=user_note,
                    status_change=new_status,
                    created_at=datetime.utcnow()
                ))

            # Record audit trail
            session.add(AuditLog(
                timestamp=datetime.now().strftime("%d %b %Y, %I:%M %p"),
                user_email=data.get('analyst_email', 'analyst@cybercrime.gov.in'),
                user_role="Analyst",
                action="CHANGE_STATUS",
                target_entity="Complaint",
                target_id=complaint.complaint_id,
                details=f"Status modified from {old_status} to {new_status}.",
                ip_address=request.remote_addr or "127.0.0.1"
            ))

            return jsonify({
                "status": "success",
                "message": f"Status updated to '{new_status}' successfully.",
                "complaint_id": complaint.complaint_id,
                "current_status": new_status
            }), 200

    except Exception as e:
        return jsonify({"status": "error", "message": f"Failed to update status: {str(e)}"}), 500

@cases_bp.route('/<identifier>/assign', methods=['PATCH'])
def assign_officer(identifier):
    """Assign or re-assign case to an investigator."""
    try:
        data = request.get_json() or {}
        officer_name = data.get('officer_name', '').strip()
        officer_id = data.get('officer_id', '').strip()

        if not officer_name:
            return jsonify({"status": "fail", "message": "Officer name is required."}), 400

        with get_session() as session:
            complaint = session.query(Complaint).filter(
                (Complaint.complaint_id == identifier) | (Complaint.id == (int(identifier) if identifier.isdigit() else -1))
            ).first()

            if not complaint:
                return jsonify({"status": "fail", "message": "Case not found."}), 404

            prev_officer = complaint.assigned_officer
            complaint.assigned_officer = officer_name
            complaint.assigned_officer_id = officer_id
            complaint.updated_at = datetime.utcnow()

            session.add(TimelineEvent(
                complaint_id=complaint.complaint_id,
                event_type="ASSIGNED",
                title=f"Reassigned to {officer_name}",
                description=f"Case reassigned from {prev_officer} to {officer_name} ({officer_id}).",
                actor=data.get('assigned_by', 'Senior Analyst'),
                created_at=datetime.utcnow()
            ))

            session.add(AuditLog(
                timestamp=datetime.now().strftime("%d %b %Y, %I:%M %p"),
                user_email=data.get('assigned_by_email', 'admin@cybercrime.gov.in'),
                user_role="Senior Analyst",
                action="ASSIGN_CASE",
                target_entity="Complaint",
                target_id=complaint.complaint_id,
                details=f"Case assigned to {officer_name}.",
                ip_address=request.remote_addr or "127.0.0.1"
            ))

            return jsonify({
                "status": "success",
                "message": f"Assigned to {officer_name}.",
                "complaint_id": complaint.complaint_id,
                "assigned_officer": officer_name
            }), 200

    except Exception as e:
        return jsonify({"status": "error", "message": f"Failed to assign case: {str(e)}"}), 500

@cases_bp.route('/export', methods=['GET'])
def export_cases_csv():
    """Stream CSV export of cybercrime complaints."""
    try:
        with get_session() as session:
            complaints = session.query(Complaint).order_by(desc(Complaint.created_at)).all()

            output = io.StringIO()
            writer = csv.writer(output)

            writer.writerow([
                'Complaint ID', 'Title', 'Crime Type', 'Predicted Category', 'Confidence (%)',
                'Risk Score', 'Risk Level', 'Severity', 'Financial Loss (INR)', 'Status',
                'State', 'City', 'Police Station', 'Reported Date', 'Incident Date',
                'Platform', 'Payment Method', 'Assigned Officer', 'Threat Indicators', 'Description'
            ])

            for c in complaints:
                d = c.to_dict()
                threats_str = "; ".join([t.get('label', '') for t in d.get('threat_indicators', [])])
                writer.writerow([
                    d['complaint_id'],
                    d['title'],
                    d['crime_type'],
                    d['predicted_category'],
                    d['confidence'],
                    d['risk_score'],
                    d['risk_level'],
                    d['severity'],
                    d['financial_loss'],
                    d['current_status'],
                    d['state'],
                    d['city'],
                    d['cyber_cell_station'],
                    d['complaint_date'],
                    d['incident_date'],
                    d['platform'],
                    d['payment_method'],
                    d['assigned_officer'],
                    threats_str,
                    d['description'].replace('\n', ' ')
                ])

            output.seek(0)
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"cybercrime_cases_export_{timestamp}.csv"

            return Response(
                output.getvalue(),
                mimetype="text/csv",
                headers={"Content-Disposition": f"attachment;filename={filename}"}
            )

    except Exception as e:
        return jsonify({"status": "error", "message": f"CSV export failed: {str(e)}"}), 500
