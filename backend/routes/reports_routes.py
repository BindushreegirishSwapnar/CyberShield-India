import os
import io
import json
from datetime import datetime
from flask import Blueprint, request, jsonify, Response, render_template_string
from database import get_session
from models_db import Complaint, RiskAssessment, MLPrediction, ThreatIndicator, EvidenceItem, InvestigationNote, TimelineEvent
from rag.rag_engine import generate_case_brief, generate_fir_draft, get_vector_store
from analyzer import find_similar_complaints

reports_bp = Blueprint('reports_bp', __name__)

REPORT_HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>Incident Intelligence Report - {{ complaint.complaint_id }}</title>
  <style>
    body {
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
      margin: 0;
      padding: 30px;
      color: #1e293b;
      background: #ffffff;
      line-height: 1.5;
      font-size: 13px;
    }
    .header {
      border-bottom: 2px solid #0f172a;
      padding-bottom: 15px;
      margin-bottom: 25px;
      display: flex;
      justify-content: space-between;
      align-items: flex-start;
    }
    .title-block h1 {
      margin: 0 0 5px 0;
      font-size: 22px;
      color: #0f172a;
      letter-spacing: -0.5px;
    }
    .badge {
      display: inline-block;
      padding: 4px 10px;
      border-radius: 4px;
      font-weight: 600;
      font-size: 11px;
      text-transform: uppercase;
    }
    .badge-critical { background: #fee2e2; color: #991b1b; border: 1px solid #f87171; }
    .badge-high { background: #ffedd5; color: #9a3412; border: 1px solid #fb923c; }
    .badge-medium { background: #fef3c7; color: #92400e; border: 1px solid #fcd34d; }
    .badge-low { background: #dcfce7; color: #166534; border: 1px solid #86efac; }
    
    .disclaimer-banner {
      background: #f8fafc;
      border: 1px solid #cbd5e1;
      padding: 8px 12px;
      border-radius: 4px;
      font-size: 11px;
      color: #475569;
      margin-bottom: 20px;
    }
    .grid-2 {
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 20px;
      margin-bottom: 20px;
    }
    .panel {
      border: 1px solid #e2e8f0;
      border-radius: 6px;
      padding: 14px;
      background: #ffffff;
    }
    .panel-title {
      font-size: 12px;
      font-weight: 700;
      text-transform: uppercase;
      letter-spacing: 0.5px;
      color: #475569;
      margin-top: 0;
      margin-bottom: 12px;
      border-bottom: 1px solid #f1f5f9;
      padding-bottom: 6px;
    }
    table {
      width: 100%;
      border-collapse: collapse;
      margin-top: 8px;
    }
    th, td {
      text-align: left;
      padding: 6px 8px;
      border-bottom: 1px solid #f1f5f9;
      font-size: 12px;
    }
    th {
      color: #64748b;
      font-weight: 600;
      background: #f8fafc;
    }
    .kv-row {
      display: flex;
      justify-content: space-between;
      padding: 4px 0;
      border-bottom: 1px dashed #f1f5f9;
    }
    .kv-label { color: #64748b; }
    .kv-val { font-weight: 600; color: #0f172a; }
    .timeline-item {
      padding: 8px 0;
      border-left: 2px solid #cbd5e1;
      padding-left: 12px;
      margin-left: 6px;
      position: relative;
    }
    .timeline-item::before {
      content: '';
      position: absolute;
      left: -5px;
      top: 12px;
      width: 8px;
      height: 8px;
      border-radius: 50%;
      background: #3b82f6;
    }
    @media print {
      body { padding: 15px; }
      .no-print { display: none; }
    }
  </style>
</head>
<body>
  <div class="no-print" style="margin-bottom: 20px; text-align: right;">
    <button onclick="window.print()" style="padding: 8px 16px; background: #0f172a; color: #fff; border: none; border-radius: 4px; cursor: pointer; font-weight: 600;">Print / Save as PDF</button>
  </div>

  <div class="header">
    <div class="title-block">
      <h1>CYBER CRIME INCIDENT INTELLIGENCE REPORT</h1>
      <div style="color: #64748b; font-size: 12px;">Case Number: <strong style="color: #0f172a;">{{ complaint.complaint_id }}</strong> | Generated: {{ generated_at }}</div>
    </div>
    <div style="text-align: right;">
      <span class="badge badge-{{ complaint.risk_level.lower() }}">{{ complaint.risk_level }} RISK ({{ complaint.risk_score }}/100)</span>
      <div style="margin-top: 4px; font-size: 11px; color: #64748b;">Status: <strong>{{ complaint.current_status }}</strong></div>
    </div>
  </div>

  <div class="disclaimer-banner">
    <strong>Demonstration Environment — Synthetic Data.</strong> Prepared by CyberCrimePredict Intelligence Framework for triage analysis. Does not constitute official judicial evidentiary submission without physical chain of custody.
  </div>

  <!-- Row 1: Case Summary & Risk Assessment -->
  <div class="grid-2">
    <div class="panel">
      <div class="panel-title">1. Operational Case Overview</div>
      <div class="kv-row"><span class="kv-label">Reported Category</span><span class="kv-val">{{ complaint.crime_type }}</span></div>
      <div class="kv-row"><span class="kv-label">AI Classified Category</span><span class="kv-val">{{ complaint.predicted_category }} ({{ complaint.confidence }}%)</span></div>
      <div class="kv-row"><span class="kv-label">Financial Impact</span><span class="kv-val">₹{{ "{:,.2f}".format(complaint.financial_loss) }}</span></div>
      <div class="kv-row"><span class="kv-label">Incident Date</span><span class="kv-val">{{ complaint.incident_date }}</span></div>
      <div class="kv-row"><span class="kv-label">Reported Date</span><span class="kv-val">{{ complaint.complaint_date }}</span></div>
      <div class="kv-row"><span class="kv-label">Location / City</span><span class="kv-val">{{ complaint.city }}, {{ complaint.state }}</span></div>
      <div class="kv-row"><span class="kv-label">Jurisdictional Unit</span><span class="kv-val">{{ complaint.cyber_cell_station }}</span></div>
      <div class="kv-row"><span class="kv-label">Assigned Officer</span><span class="kv-val">{{ complaint.assigned_officer }}</span></div>
      <div style="margin-top: 12px;">
        <div style="font-weight: 600; color: #475569; font-size: 11px; margin-bottom: 4px;">COMPLAINT NARRATIVE:</div>
        <div style="background: #f8fafc; padding: 10px; border-radius: 4px; font-size: 12px; color: #334155; border: 1px solid #f1f5f9;">
          {{ complaint.description }}
        </div>
      </div>
    </div>

    <div class="panel">
      <div class="panel-title">2. Explainable Risk Score Breakdown</div>
      <div style="text-align: center; margin-bottom: 12px;">
        <span style="font-size: 32px; font-weight: 800; color: #0f172a;">{{ complaint.risk_score }}</span>
        <span style="font-size: 14px; color: #64748b;"> / 100</span>
      </div>
      <table>
        <thead>
          <tr><th>Evaluation Factor</th><th>Points</th><th>Max</th></tr>
        </thead>
        <tbody>
          <tr><td>Crime Category Baseline Threat</td><td>{{ risk_breakdown.get('category_factor', 12) }}</td><td>20</td></tr>
          <tr><td>Incident Severity Level</td><td>{{ risk_breakdown.get('severity_factor', 12) }}</td><td>25</td></tr>
          <tr><td>Financial Loss Impact</td><td>{{ risk_breakdown.get('financial_factor', 0) }}</td><td>20</td></tr>
          <tr><td>Account / Credential Compromise</td><td>{{ risk_breakdown.get('account_compromised_factor', 0) }}</td><td>15</td></tr>
          <tr><td>Personal Information (PII) Exposure</td><td>{{ risk_breakdown.get('pii_factor', 0) }}</td><td>12</td></tr>
          <tr><td>Threat Indicators Verified</td><td>{{ risk_breakdown.get('threat_indicators_factor', 0) }}</td><td>15</td></tr>
          <tr><td>ML Classification Confidence</td><td>{{ risk_breakdown.get('confidence_factor', 0) }}</td><td>15</td></tr>
        </tbody>
      </table>
      <div style="margin-top: 10px;">
        <div style="font-size: 11px; font-weight: 600; color: #64748b;">CONTRIBUTING FACTORS:</div>
        <ul style="margin: 4px 0; padding-left: 18px; font-size: 11px; color: #475569;">
          {% for r in reasons %}
            <li>{{ r }}</li>
          {% endfor %}
        </ul>
      </div>
    </div>
  </div>

  <!-- Row 2: Threat Indicators & Evidence Table -->
  <div class="grid-2">
    <div class="panel">
      <div class="panel-title">3. Verified Threat Indicators (IOCs)</div>
      {% if threat_indicators %}
        <table>
          <thead>
            <tr><th>Indicator / Entity</th><th>Type</th><th>Severity</th></tr>
          </thead>
          <tbody>
            {% for t in threat_indicators %}
              <tr>
                <td><strong>{{ t.get('label') or t.get('indicator_value') }}</strong></td>
                <td>{{ t.get('indicator_type') or t.get('code') }}</td>
                <td>{{ t.get('severity') }}</td>
              </tr>
            {% endfor %}
          </tbody>
        </table>
      {% else %}
        <p style="color: #64748b; font-style: italic;">No automated threat indicators detected in complaint narrative.</p>
      {% endif %}
    </div>

    <div class="panel">
      <div class="panel-title">4. Digital Evidence & Integrity Hashes</div>
      {% if evidence_items %}
        <table>
          <thead>
            <tr><th>Evidence #</th><th>Type</th><th>SHA-256 Hash</th></tr>
          </thead>
          <tbody>
            {% for ev in evidence_items %}
              <tr>
                <td><strong>{{ ev.evidence_number }}</strong></td>
                <td>{{ ev.evidence_type }}</td>
                <td style="font-family: monospace; font-size: 10px;">{{ ev.file_hash_sha256[:20] }}...</td>
              </tr>
            {% endfor %}
          </tbody>
        </table>
      {% else %}
        <p style="color: #64748b; font-style: italic;">No digital evidence artifacts attached yet.</p>
      {% endif %}
    </div>
  </div>

  <!-- Row 3: Statutory Provisions & Standard Operating Procedures -->
  <div class="panel" style="margin-bottom: 20px;">
    <div class="panel-title">5. Grounded Statutory Provisions & SOP Guidance</div>
    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px;">
      <div>
        <div style="font-size: 11px; font-weight: 700; color: #475569; margin-bottom: 6px;">APPLICABLE IT ACT / BNS SECTIONS:</div>
        {% for leg in brief.statutory_provisions %}
          <div style="margin-bottom: 8px; background: #f8fafc; padding: 8px; border-radius: 4px; border: 1px solid #f1f5f9;">
            <div style="font-weight: 700; color: #0f172a;">{{ leg.section }} - {{ leg.title }}</div>
            <div style="font-size: 11px; color: #64748b;">Statutory Penalty: {{ leg.penalty }}</div>
          </div>
        {% endfor %}
      </div>
      <div>
        <div style="font-size: 11px; font-weight: 700; color: #475569; margin-bottom: 6px;">RETRIEVED SOP SOURCES:</div>
        {% for src in brief.grounded_sources %}
          <div style="margin-bottom: 6px; font-size: 11px;">
            • <strong>{{ src.reference }}</strong> ({{ src.document }}) - <em>{{ src.section }}</em> [Relevance: {{ src.relevance }}]
          </div>
        {% endfor %}
      </div>
    </div>
  </div>

  <!-- Row 4: Chronological Timeline -->
  <div class="panel">
    <div class="panel-title">6. Chronological Case Audit Timeline</div>
    <div>
      {% for ev in timeline %}
        <div class="timeline-item">
          <div style="display: flex; justify-content: space-between;">
            <strong style="color: #0f172a;">{{ ev.title }}</strong>
            <span style="font-size: 11px; color: #64748b;">{{ ev.created_at }}</span>
          </div>
          <div style="font-size: 12px; color: #475569;">{{ ev.description }}</div>
          <div style="font-size: 10px; color: #94a3b8;">Actor: {{ ev.actor }}</div>
        </div>
      {% endfor %}
    </div>
  </div>

  <div style="margin-top: 30px; border-top: 1px solid #e2e8f0; padding-top: 12px; display: flex; justify-content: space-between; font-size: 11px; color: #94a3b8;">
    <div>CyberCrimePredict Intelligence Platform — Automated Diagnostic Dossier</div>
    <div>Confidential — For Authorized Cyber Forensic Use Only</div>
  </div>
</body>
</html>
"""

@reports_bp.route('/case/<complaint_id>', methods=['GET'])
def get_case_report_data(complaint_id):
    """Retrieve structured JSON investigation report data for a case."""
    try:
        with get_session() as session:
            complaint = session.query(Complaint).filter(
                (Complaint.complaint_id == complaint_id) | (Complaint.id == (int(complaint_id) if complaint_id.isdigit() else -1))
            ).first()

            if not complaint:
                return jsonify({"status": "fail", "message": "Case not found."}), 404

            comp_dict = complaint.to_dict()
            brief = generate_case_brief(comp_dict)

            # Evidence & Timeline
            evidence = session.query(EvidenceItem).filter(EvidenceItem.complaint_id == complaint.complaint_id).all()
            notes = session.query(InvestigationNote).filter(InvestigationNote.complaint_id == complaint.complaint_id).all()
            timeline = session.query(TimelineEvent).filter(TimelineEvent.complaint_id == complaint.complaint_id).order_by(TimelineEvent.created_at).all()

            # Similar Cases
            candidates = session.query(Complaint).limit(80).all()
            similar = find_similar_complaints(complaint.description, [c.to_dict() for c in candidates if c.complaint_id != complaint.complaint_id], top_k=3)

            return jsonify({
                "status": "success",
                "generated_at": datetime.now().strftime("%d %b %Y, %I:%M %p"),
                "data": {
                    "case": comp_dict,
                    "brief": brief,
                    "evidence": [e.to_dict() for e in evidence],
                    "notes": [n.to_dict() for n in notes],
                    "timeline": [t.to_dict() for t in timeline],
                    "similar_cases": similar
                }
            }), 200

    except Exception as e:
        return jsonify({"status": "error", "message": f"Report compilation failed: {str(e)}"}), 500

@reports_bp.route('/case/<complaint_id>/html', methods=['GET'])
def get_case_report_html(complaint_id):
    """Render a printable, publication-grade HTML investigation dossier."""
    try:
        with get_session() as session:
            complaint = session.query(Complaint).filter(
                (Complaint.complaint_id == complaint_id) | (Complaint.id == (int(complaint_id) if complaint_id.isdigit() else -1))
            ).first()

            if not complaint:
                return "Case not found", 404

            comp_dict = complaint.to_dict()
            brief = generate_case_brief(comp_dict)
            evidence = session.query(EvidenceItem).filter(EvidenceItem.complaint_id == complaint.complaint_id).all()
            timeline = session.query(TimelineEvent).filter(TimelineEvent.complaint_id == complaint.complaint_id).order_by(TimelineEvent.created_at).all()

            risk_rec = complaint.risk_assessment
            risk_breakdown = risk_rec.to_dict().get("breakdown", {}) if risk_rec else {}

            html_output = render_template_string(
                REPORT_HTML_TEMPLATE,
                complaint=comp_dict,
                brief=brief,
                risk_breakdown=risk_breakdown,
                reasons=comp_dict.get('reasons', []),
                threat_indicators=comp_dict.get('threat_indicators', []),
                evidence_items=[e.to_dict() for e in evidence],
                timeline=[t.to_dict() for t in timeline],
                generated_at=datetime.now().strftime("%d %b %Y, %I:%M %p")
            )

            return Response(html_output, mimetype="text/html")

    except Exception as e:
        return f"Error generating report: {str(e)}", 500

@reports_bp.route('/case/<complaint_id>/fir-draft', methods=['GET'])
def get_case_fir_draft(complaint_id):
    """Generate official police First Information Report (FIR) summary for the case."""
    try:
        with get_session() as session:
            complaint = session.query(Complaint).filter(
                (Complaint.complaint_id == complaint_id) | (Complaint.id == (int(complaint_id) if complaint_id.isdigit() else -1))
            ).first()

            if not complaint:
                return jsonify({"status": "fail", "message": "Case not found."}), 404

            comp_dict = complaint.to_dict()
            fir_data = generate_fir_draft(comp_dict)

            return jsonify({
                "status": "success",
                "data": fir_data
            }), 200

    except Exception as e:
        return jsonify({"status": "error", "message": f"FIR generation failed: {str(e)}"}), 500

