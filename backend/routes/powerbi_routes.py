import os
import io
import csv
import zipfile
from datetime import datetime
from flask import Blueprint, jsonify, Response, send_file
from sqlalchemy import func, desc
from database import get_session
from models_db import Complaint, RiskAssessment

powerbi_bp = Blueprint('powerbi_bp', __name__)

@powerbi_bp.route('/status', methods=['GET'])
def get_powerbi_status():
    """Returns dataset health and Power BI integration configuration status."""
    try:
        with get_session() as session:
            count = session.query(Complaint).count()

        client_id = os.getenv("POWERBI_CLIENT_ID")
        workspace_id = os.getenv("POWERBI_WORKSPACE_ID")
        report_id = os.getenv("POWERBI_REPORT_ID")
        configured = bool(client_id and workspace_id and report_id)

        return jsonify({
            "status": "success",
            "dataset": {
                "record_count": count,
                "schema_type": "Star Schema (FactComplaints + 6 Dimension Tables)",
                "last_refresh": datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC"),
                "export_formats": ["CSV", "REST API", "ZIP Star Schema Package"]
            },
            "embedded_integration": {
                "configured": configured,
                "workspace_id": workspace_id if configured else None,
                "report_id": report_id if configured else None,
                "message": "Power BI Embedded active." if configured else "Power BI workspace not configured. Use direct CSV export or REST Web connector."
            }
        }), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@powerbi_bp.route('/cases', methods=['GET'])
def get_fact_cases():
    """Normalized Fact Table endpoint for Power BI Web REST Connector."""
    try:
        with get_session() as session:
            complaints = session.query(Complaint).all()
            data = []
            for c in complaints:
                data.append({
                    "ComplaintKey": c.id,
                    "ComplaintID": c.complaint_id,
                    "ComplaintDate": c.complaint_date,
                    "IncidentDate": c.incident_date,
                    "State": c.state,
                    "City": c.city,
                    "CrimeCategory": c.crime_type,
                    "PredictedCategory": c.predicted_category,
                    "FinancialLoss": float(c.financial_loss or 0.0),
                    "RiskScore": c.risk_score,
                    "RiskLevel": c.risk_level,
                    "Priority": c.priority,
                    "Status": c.current_status,
                    "Platform": c.platform,
                    "PaymentMethod": c.payment_method,
                    "AssignedOfficer": c.assigned_officer
                })

            format_type = request.args.get('format', 'json').lower()
            if format_type == 'csv':
                output = io.StringIO()
                writer = csv.DictWriter(output, fieldnames=list(data[0].keys()) if data else [])
                writer.writeheader()
                writer.writerows(data)
                output.seek(0)
                return Response(
                    output.getvalue(),
                    mimetype="text/csv",
                    headers={"Content-Disposition": "attachment;filename=fact_cases.csv"}
                )

            return jsonify({"status": "success", "count": len(data), "data": data}), 200

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@powerbi_bp.route('/categories', methods=['GET'])
def get_dim_categories():
    """Dimension table DimCrimeType for Power BI."""
    try:
        with get_session() as session:
            rows = session.query(
                Complaint.predicted_category,
                func.count(Complaint.id).label('total_cases'),
                func.sum(Complaint.financial_loss).label('total_loss'),
                func.avg(Complaint.risk_score).label('avg_risk')
            ).group_by(Complaint.predicted_category).all()

            data = [
                {
                    "CrimeKey": idx + 1,
                    "CrimeCategory": r[0] or "Unknown",
                    "TotalCases": r[1],
                    "TotalFinancialLoss": float(r[2] or 0),
                    "AverageRiskScore": round(float(r[3] or 0), 1)
                }
                for idx, r in enumerate(rows) if r[0]
            ]

            format_type = request.args.get('format', 'json').lower()
            if format_type == 'csv':
                output = io.StringIO()
                writer = csv.DictWriter(output, fieldnames=list(data[0].keys()) if data else [])
                writer.writeheader()
                writer.writerows(data)
                output.seek(0)
                return Response(
                    output.getvalue(),
                    mimetype="text/csv",
                    headers={"Content-Disposition": "attachment;filename=dim_crime_categories.csv"}
                )

            return jsonify({"status": "success", "count": len(data), "data": data}), 200

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@powerbi_bp.route('/locations', methods=['GET'])
def get_dim_locations():
    """Dimension table DimLocation for Power BI."""
    try:
        with get_session() as session:
            rows = session.query(
                Complaint.state,
                Complaint.city,
                Complaint.cyber_cell_station,
                func.count(Complaint.id).label('total_cases'),
                func.sum(Complaint.financial_loss).label('total_loss'),
                func.avg(Complaint.risk_score).label('avg_risk')
            ).group_by(Complaint.state, Complaint.city, Complaint.cyber_cell_station).all()

            data = [
                {
                    "LocationKey": idx + 1,
                    "State": r[0] or "Unknown",
                    "City": r[1] or "Unknown",
                    "CyberCellStation": r[2] or "District Cyber Cell",
                    "TotalCases": r[3],
                    "TotalFinancialLoss": float(r[4] or 0),
                    "AverageRiskScore": round(float(r[5] or 0), 1)
                }
                for idx, r in enumerate(rows)
            ]

            format_type = request.args.get('format', 'json').lower()
            if format_type == 'csv':
                output = io.StringIO()
                writer = csv.DictWriter(output, fieldnames=list(data[0].keys()) if data else [])
                writer.writeheader()
                writer.writerows(data)
                output.seek(0)
                return Response(
                    output.getvalue(),
                    mimetype="text/csv",
                    headers={"Content-Disposition": "attachment;filename=dim_locations.csv"}
                )

            return jsonify({"status": "success", "count": len(data), "data": data}), 200

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@powerbi_bp.route('/risk', methods=['GET'])
def get_fact_risk():
    """Fact table FactRisk for Power BI."""
    try:
        with get_session() as session:
            rows = session.query(RiskAssessment).all()
            data = [r.to_dict() for r in rows]

            format_type = request.args.get('format', 'json').lower()
            if format_type == 'csv':
                output = io.StringIO()
                writer = csv.writer(output)
                writer.writerow(['ID', 'ComplaintID', 'FinalScore', 'RiskLevel', 'CategoryFactor', 'SeverityFactor', 'FinancialFactor', 'ConfidenceFactor'])
                for d in data:
                    bd = d.get('breakdown', {})
                    writer.writerow([
                        d.get('id'), d.get('complaint_id'), d.get('final_score'), d.get('risk_level'),
                        bd.get('category_factor'), bd.get('severity_factor'), bd.get('financial_factor'), bd.get('confidence_factor')
                    ])
                output.seek(0)
                return Response(
                    output.getvalue(),
                    mimetype="text/csv",
                    headers={"Content-Disposition": "attachment;filename=fact_risk.csv"}
                )

            return jsonify({"status": "success", "count": len(data), "data": data}), 200

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@powerbi_bp.route('/trends', methods=['GET'])
def get_fact_trends():
    """Fact table FactTrends for Power BI time-series visualization."""
    try:
        with get_session() as session:
            monthly = session.query(
                func.substr(func.coalesce(Complaint.complaint_date, Complaint.incident_date), 1, 7).label('month_period'),
                Complaint.predicted_category,
                func.count(Complaint.id).label('cases'),
                func.sum(Complaint.financial_loss).label('loss'),
                func.round(func.avg(Complaint.risk_score), 1).label('avg_risk')
            ).group_by('month_period', Complaint.predicted_category).order_by('month_period').all()

            data = [
                {
                    "Period": r[0],
                    "CrimeCategory": r[1],
                    "ReportedCases": r[2],
                    "FinancialLoss": float(r[3] or 0),
                    "AverageRiskScore": float(r[4] or 0)
                }
                for r in monthly if r[0] and r[1]
            ]

            format_type = request.args.get('format', 'json').lower()
            if format_type == 'csv':
                output = io.StringIO()
                writer = csv.DictWriter(output, fieldnames=list(data[0].keys()) if data else [])
                writer.writeheader()
                writer.writerows(data)
                output.seek(0)
                return Response(
                    output.getvalue(),
                    mimetype="text/csv",
                    headers={"Content-Disposition": "attachment;filename=fact_trends.csv"}
                )

            return jsonify({"status": "success", "count": len(data), "data": data}), 200

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@powerbi_bp.route('/financial-impact', methods=['GET'])
def get_financial_impact():
    """Financial impact fact breakdown by category, payment method, and state."""
    try:
        with get_session() as session:
            by_pm = session.query(
                Complaint.payment_method,
                func.count(Complaint.id).label('cases'),
                func.sum(Complaint.financial_loss).label('loss')
            ).group_by(Complaint.payment_method).order_by(desc('loss')).all()

            by_state = session.query(
                Complaint.state,
                func.count(Complaint.id).label('cases'),
                func.sum(Complaint.financial_loss).label('loss')
            ).group_by(Complaint.state).order_by(desc('loss')).all()

            return jsonify({
                "status": "success",
                "by_payment_method": [
                    {"method": r[0] or "Unknown", "cases": r[1], "total_loss": float(r[2] or 0)}
                    for r in by_pm
                ],
                "by_state": [
                    {"state": r[0] or "Unknown", "cases": r[1], "total_loss": float(r[2] or 0)}
                    for r in by_state
                ]
            }), 200

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@powerbi_bp.route('/download-package', methods=['GET'])
def download_powerbi_data_package():
    """
    Generate and stream an in-memory ZIP archive containing the complete
    Star Schema CSV dataset, SQL Views, and connection guide for Power BI Desktop.
    """
    try:
        with get_session() as session:
            complaints = session.query(Complaint).all()

        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zf:
            # 1. FactComplaints.csv
            fact_buf = io.StringIO()
            fact_writer = csv.writer(fact_buf)
            fact_writer.writerow([
                'ComplaintKey', 'ComplaintID', 'ComplaintDate', 'IncidentDate',
                'State', 'City', 'CyberCellStation', 'CrimeCategory', 'PredictedCategory',
                'FinancialLossINR', 'RiskScore', 'RiskLevel', 'Priority', 'Status',
                'Platform', 'PaymentMethod', 'AssignedOfficer'
            ])
            for c in complaints:
                fact_writer.writerow([
                    c.id, c.complaint_id, c.complaint_date, c.incident_date,
                    c.state, c.city, c.cyber_cell_station, c.crime_type, c.predicted_category,
                    c.financial_loss, c.risk_score, c.risk_level, c.priority, c.current_status,
                    c.platform, c.payment_method, c.assigned_officer
                ])
            zf.writestr("FactComplaints.csv", fact_buf.getvalue())

            # 2. DimCrimeType.csv
            crime_cats = sorted(list({c.predicted_category for c in complaints if c.predicted_category}))
            dim_crime_buf = io.StringIO()
            c_writer = csv.writer(dim_crime_buf)
            c_writer.writerow(['CrimeKey', 'CrimeCategory'])
            for idx, cc in enumerate(crime_cats, 1):
                c_writer.writerow([idx, cc])
            zf.writestr("DimCrimeType.csv", dim_crime_buf.getvalue())

            # 3. DimLocation.csv
            locations = sorted(list({(c.state, c.city, c.cyber_cell_station) for c in complaints}))
            dim_loc_buf = io.StringIO()
            l_writer = csv.writer(dim_loc_buf)
            l_writer.writerow(['LocationKey', 'State', 'City', 'CyberCellStation'])
            for idx, loc in enumerate(locations, 1):
                l_writer.writerow([idx, loc[0], loc[1], loc[2]])
            zf.writestr("DimLocation.csv", dim_loc_buf.getvalue())

            # 4. DimStatus.csv
            statuses = ['New', 'Under Review', 'Investigating', 'Resolved', 'Closed']
            dim_status_buf = io.StringIO()
            s_writer = csv.writer(dim_status_buf)
            s_writer.writerow(['StatusKey', 'Status'])
            for idx, st in enumerate(statuses, 1):
                s_writer.writerow([idx, st])
            zf.writestr("DimStatus.csv", dim_status_buf.getvalue())

            # 5. powerbi_star_schema_views.sql
            sql_content = """-- Star Schema SQL Views for DirectQuery
CREATE VIEW v_FactComplaints AS
SELECT id AS ComplaintKey, complaint_id AS ComplaintID, complaint_date AS ComplaintDate,
       incident_date AS IncidentDate, state AS State, city AS City,
       crime_type AS CrimeCategory, predicted_category AS PredictedCategory,
       financial_loss AS FinancialLossINR, risk_score AS RiskScore,
       risk_level AS RiskLevel, priority AS Priority, current_status AS Status,
       platform AS Platform, payment_method AS PaymentMethod, assigned_officer AS AssignedOfficer
FROM complaints;
"""
            zf.writestr("powerbi_star_schema_views.sql", sql_content)

            # 6. Readme
            readme = """Power BI Desktop Connection Instructions:
1. Open Power BI Desktop.
2. Select 'Get Data' -> 'Text/CSV' (or 'Folder').
3. Load 'FactComplaints.csv', 'DimLocation.csv', 'DimCrimeType.csv', and 'DimStatus.csv'.
4. In Model view, link FactComplaints[City] -> DimLocation[City] and FactComplaints[PredictedCategory] -> DimCrimeType[CrimeCategory].
"""
            zf.writestr("POWERBI_INSTRUCTIONS.txt", readme)

        zip_buffer.seek(0)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        return send_file(
            zip_buffer,
            mimetype="application/zip",
            as_attachment=True,
            download_name=f"powerbi_dataset_package_{timestamp}.zip"
        )

    except Exception as e:
        return jsonify({"status": "error", "message": f"Package generation failed: {str(e)}"}), 500
