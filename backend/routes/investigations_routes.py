from datetime import datetime
from flask import Blueprint, request, jsonify
from sqlalchemy import desc, asc
from database import get_session
from models_db import Investigation, InvestigationNote, Complaint, TimelineEvent, AuditLog

investigations_bp = Blueprint('investigations_bp', __name__)

@investigations_bp.route('/queue', methods=['GET'])
def get_investigation_queue():
    """
    Retrieve operational investigation queue prioritized by risk score and SLA urgency.
    """
    try:
        status_filter = request.args.get('status')
        priority_filter = request.args.get('priority')
        analyst_filter = request.args.get('analyst')

        with get_session() as session:
            query = session.query(Complaint).filter(Complaint.current_status != 'Closed')

            if status_filter and status_filter != 'All':
                query = query.filter(Complaint.current_status == status_filter)

            if priority_filter and priority_filter != 'All':
                query = query.filter(Complaint.priority == priority_filter)

            if analyst_filter and analyst_filter != 'All':
                query = query.filter(Complaint.assigned_officer.ilike(f"%{analyst_filter}%"))

            # Order by risk score descending
            cases = query.order_by(desc(Complaint.risk_score), desc(Complaint.created_at)).limit(100).all()

            # Queue statistics
            total_active = session.query(Complaint).filter(Complaint.current_status.in_(['New', 'Under Review', 'Investigating'])).count()
            critical_active = session.query(Complaint).filter(Complaint.current_status.in_(['New', 'Under Review', 'Investigating']), Complaint.risk_score >= 75).count()
            under_review = session.query(Complaint).filter(Complaint.current_status == 'Under Review').count()
            investigating = session.query(Complaint).filter(Complaint.current_status == 'Investigating').count()

            queue_items = []
            for c in cases:
                inv = c.investigation
                queue_items.append({
                    "complaint_id": c.complaint_id,
                    "case_number": inv.case_number if inv else f"INV-{c.complaint_id}",
                    "title": c.title,
                    "crime_type": c.crime_type,
                    "predicted_category": c.predicted_category,
                    "risk_score": c.risk_score,
                    "risk_level": c.risk_level,
                    "priority": c.priority,
                    "current_status": c.current_status,
                    "investigation_status": c.investigation_status,
                    "assigned_officer": c.assigned_officer,
                    "financial_loss": c.financial_loss,
                    "city": c.city,
                    "state": c.state,
                    "complaint_date": c.complaint_date,
                    "created_at": c.created_at.strftime("%Y-%m-%d %H:%M") if c.created_at else None,
                    "notes_count": len(inv.notes) if inv and inv.notes else 0,
                    "evidence_count": len(inv.evidence_items) if inv and inv.evidence_items else 0
                })

            return jsonify({
                "status": "success",
                "stats": {
                    "total_active": total_active,
                    "critical_active": critical_active,
                    "under_review": under_review,
                    "investigating": investigating
                },
                "count": len(queue_items),
                "data": queue_items
            }), 200

    except Exception as e:
        return jsonify({"status": "error", "message": f"Unable to fetch queue: {str(e)}"}), 500

@investigations_bp.route('/<complaint_id>', methods=['GET'])
def get_case_investigation(complaint_id):
    """Retrieve full investigation workspace records for a complaint."""
    try:
        with get_session() as session:
            complaint = session.query(Complaint).filter(
                (Complaint.complaint_id == complaint_id) | (Complaint.id == (int(complaint_id) if complaint_id.isdigit() else -1))
            ).first()

            if not complaint:
                return jsonify({"status": "fail", "message": "Case not found."}), 404

            inv = complaint.investigation
            notes = session.query(InvestigationNote).filter(
                InvestigationNote.complaint_id == complaint.complaint_id
            ).order_by(desc(InvestigationNote.created_at)).all()

            timeline = session.query(TimelineEvent).filter(
                TimelineEvent.complaint_id == complaint.complaint_id
            ).order_by(asc(TimelineEvent.created_at)).all()

            return jsonify({
                "status": "success",
                "data": {
                    "complaint": complaint.to_dict(),
                    "investigation": inv.to_dict() if inv else None,
                    "notes": [n.to_dict() for n in notes],
                    "timeline": [t.to_dict() for t in timeline]
                }
            }), 200

    except Exception as e:
        return jsonify({"status": "error", "message": f"Unable to fetch investigation: {str(e)}"}), 500

@investigations_bp.route('/<complaint_id>/notes', methods=['POST'])
def add_investigation_note(complaint_id):
    """Add a timestamped analyst note or findings entry to an active case."""
    try:
        data = request.get_json() or {}
        content = data.get('content', '').strip()
        author_name = data.get('author_name', 'Analyst Pooja Sharma').strip()
        author_role = data.get('author_role', 'Cyber Crime Analyst').strip()
        note_type = data.get('note_type', 'Analyst Note').strip()
        status_change = data.get('status_change')

        if not content:
            return jsonify({"status": "fail", "message": "Note content cannot be empty."}), 400

        with get_session() as session:
            complaint = session.query(Complaint).filter(
                (Complaint.complaint_id == complaint_id) | (Complaint.id == (int(complaint_id) if complaint_id.isdigit() else -1))
            ).first()

            if not complaint:
                return jsonify({"status": "fail", "message": "Case not found."}), 404

            now_dt = datetime.now()

            note = InvestigationNote(
                complaint_id=complaint.complaint_id,
                author_name=author_name,
                author_role=author_role,
                note_type=note_type,
                content=content,
                status_change=status_change,
                created_at=now_dt
            )
            session.add(note)

            # If status change is requested
            if status_change and status_change in ['New', 'Under Review', 'Investigating', 'Resolved', 'Closed']:
                complaint.current_status = status_change
                complaint.status = status_change
                complaint.updated_at = now_dt

                session.add(TimelineEvent(
                    complaint_id=complaint.complaint_id,
                    event_type="STATUS_CHANGED",
                    title=f"Status Changed to {status_change}",
                    description=f"Status updated alongside analyst note: {content[:100]}...",
                    actor=author_name,
                    created_at=now_dt
                ))

            # Record timeline event for note
            session.add(TimelineEvent(
                complaint_id=complaint.complaint_id,
                event_type="NOTE_ADDED",
                title=f"{note_type} Added by {author_name}",
                description=content[:140] + ("..." if len(content) > 140 else ""),
                actor=author_name,
                created_at=now_dt
            ))

            # Audit Log
            session.add(AuditLog(
                timestamp=now_dt.strftime("%d %b %Y, %I:%M %p"),
                user_email=data.get('author_email', 'analyst@cybercrime.gov.in'),
                user_role=author_role,
                action="ADD_NOTE",
                target_entity="Complaint",
                target_id=complaint.complaint_id,
                details=f"Added {note_type}. Length: {len(content)} chars.",
                ip_address=request.remote_addr or "127.0.0.1"
            ))

            return jsonify({
                "status": "success",
                "message": "Note recorded successfully.",
                "data": note.to_dict()
            }), 201

    except Exception as e:
        return jsonify({"status": "error", "message": f"Failed to record note: {str(e)}"}), 500
