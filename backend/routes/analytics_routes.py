import json
from flask import Blueprint, jsonify
from sqlalchemy import func, desc
from database import get_session
from models_db import Complaint, ThreatIndicator, Alert

analytics_bp = Blueprint('analytics_bp', __name__)

@analytics_bp.route('', methods=['GET'])
@analytics_bp.route('/', methods=['GET'])
def get_analytics():
    """
    Comprehensive dynamic statistics derived strictly from the database
    for the Overview and Intelligence Analytics dashboards.
    """
    try:
        with get_session() as session:
            # 1. Total Complaints & Risk Aggregations
            total = session.query(Complaint).count()
            avg_risk = session.query(func.avg(Complaint.risk_score)).scalar() or 0.0
            total_loss = session.query(func.sum(Complaint.financial_loss)).scalar() or 0.0
            
            critical_count = session.query(Complaint).filter(Complaint.risk_score >= 75).count()
            high_count = session.query(Complaint).filter(Complaint.risk_score >= 50, Complaint.risk_score < 75).count()
            medium_count = session.query(Complaint).filter(Complaint.risk_score >= 25, Complaint.risk_score < 50).count()
            low_count = session.query(Complaint).filter(Complaint.risk_score < 25).count()

            open_investigations = session.query(Complaint).filter(
                Complaint.current_status.in_(['New', 'Under Review', 'Investigating'])
            ).count()
            resolved_count = session.query(Complaint).filter(Complaint.current_status == 'Resolved').count()

            # 2. Category Distribution
            cat_rows = session.query(
                Complaint.predicted_category,
                func.count(Complaint.id).label('count'),
                func.round(func.avg(Complaint.risk_score), 1).label('avg_risk'),
                func.sum(Complaint.financial_loss).label('total_loss')
            ).group_by(Complaint.predicted_category).order_by(desc('count')).all()

            category_dist = [
                {
                    "category_name": r[0] or "Unknown",
                    "count": r[1],
                    "avg_risk": float(r[2] or 0),
                    "total_loss": float(r[3] or 0)
                }
                for r in cat_rows if r[0]
            ]

            most_common_crime = category_dist[0]["category_name"] if category_dist else "N/A"

            # 3. Severity Distribution
            sev_rows = session.query(
                Complaint.severity, func.count(Complaint.id)
            ).group_by(Complaint.severity).all()
            severity_dist = {r[0]: r[1] for r in sev_rows if r[0]}

            # 4. Top Cities / Geographic Distribution
            city_rows = session.query(
                Complaint.city,
                Complaint.state,
                func.count(Complaint.id).label('count'),
                func.round(func.avg(Complaint.risk_score), 1).label('avg_risk'),
                func.sum(Complaint.financial_loss).label('total_loss')
            ).group_by(Complaint.city, Complaint.state).order_by(desc('count')).limit(8).all()

            city_dist = [
                {
                    "city": r[0] or "Unknown",
                    "state": r[1] or "Unknown",
                    "count": r[2],
                    "avg_risk": float(r[3] or 0),
                    "total_loss": float(r[4] or 0)
                }
                for r in city_rows
            ]

            # 5. Monthly Trend
            month_rows = session.query(
                func.substr(func.coalesce(Complaint.complaint_date, Complaint.incident_date), 1, 7).label('month_period'),
                func.count(Complaint.id).label('count'),
                func.round(func.avg(Complaint.risk_score), 1).label('avg_risk'),
                func.sum(Complaint.financial_loss).label('total_loss')
            ).filter(Complaint.complaint_date.isnot(None)).group_by('month_period').order_by('month_period').all()

            monthly_trend = [
                {
                    "month_period": r[0],
                    "count": r[1],
                    "avg_risk": float(r[2] or 0),
                    "total_loss": float(r[3] or 0)
                }
                for r in month_rows if r[0]
            ]

            # 6. Status Breakdown
            status_rows = session.query(
                Complaint.current_status, func.count(Complaint.id)
            ).group_by(Complaint.current_status).all()
            status_dist = {r[0]: r[1] for r in status_rows if r[0]}

            # 7. Recent High-Risk Incidents (Risk Score >= 75)
            high_risk_rows = session.query(Complaint).filter(
                Complaint.risk_score >= 70
            ).order_by(desc(Complaint.risk_score), desc(Complaint.created_at)).limit(6).all()

            high_risk_incidents = [c.to_dict() for c in high_risk_rows]

            # 8. Threat Indicators Breakdown
            threat_rows = session.query(
                ThreatIndicator.label,
                ThreatIndicator.indicator_type,
                func.count(ThreatIndicator.id).label('freq')
            ).group_by(ThreatIndicator.label, ThreatIndicator.indicator_type).order_by(desc('freq')).limit(10).all()

            indicator_breakdown = [
                {
                    "indicator": r[0],
                    "type": r[1],
                    "count": r[2]
                }
                for r in threat_rows if r[0]
            ]

            return jsonify({
                "status": "success",
                "data": {
                    "total_complaints": total,
                    "average_risk_score": round(float(avg_risk), 1),
                    "total_financial_loss": float(total_loss),
                    "critical_complaints": critical_count,
                    "high_risk_complaints": high_count,
                    "medium_risk_complaints": medium_count,
                    "low_risk_complaints": low_count,
                    "open_investigations": open_investigations,
                    "resolved_cases": resolved_count,
                    "most_common_crime": most_common_crime,
                    "category_distribution": category_dist,
                    "severity_distribution": severity_dist,
                    "city_distribution": city_dist,
                    "monthly_trend": monthly_trend,
                    "status_distribution": status_dist,
                    "high_risk_incidents": high_risk_incidents,
                    "threat_indicators_breakdown": indicator_breakdown
                }
            }), 200

    except Exception as e:
        return jsonify({"status": "error", "message": f"Analytics engine failed: {str(e)}"}), 500
