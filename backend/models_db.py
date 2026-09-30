import os
import json
import uuid
from datetime import datetime
from sqlalchemy import (
    Column, Integer, String, Float, Boolean, Text, DateTime, ForeignKey, Index
)
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()

class Complaint(Base):
    """
    Primary Complaint Entity representing an incoming or historical cybercrime complaint.
    Stores complete operational metadata, victim info, classification, risk, and status.
    """
    __tablename__ = 'complaints'

    id = Column(Integer, primary_key=True, autoincrement=True)
    uuid = Column(String(36), unique=True, default=lambda: str(uuid.uuid4()), nullable=False, index=True)
    complaint_id = Column(String(32), unique=True, nullable=False, index=True)  # e.g. CC-2026-IN-000142
    title = Column(String(255), nullable=True)
    description = Column(Text, nullable=False)
    
    # Dates
    incident_date = Column(String(32), nullable=True)
    complaint_date = Column(String(32), nullable=True)
    
    # Geography & Station
    state = Column(String(64), nullable=True, index=True)
    district = Column(String(64), nullable=True)
    city = Column(String(64), nullable=True, index=True)
    cyber_cell_station = Column(String(255), nullable=True)
    location = Column(String(128), nullable=True)  # Legacy compatibility
    
    # Channel & Category
    complaint_channel = Column(String(64), default='National Cyber Crime Portal')
    crime_type = Column(String(64), nullable=True, index=True)
    category = Column(String(64), nullable=True)  # Legacy compatibility
    subcategory = Column(String(128), nullable=True)
    
    # Financial & Impact
    reported_amount = Column(Float, default=0.0)
    financial_loss = Column(Float, default=0.0)
    victim_age_group = Column(String(32), default='26-40')
    victim_gender = Column(String(32), default='Male')
    victim_type = Column(String(32), default='Individual')  # Individual, Enterprise, Senior Citizen
    
    # Technical Vectors
    platform = Column(String(64), default='Online Banking / UPI')
    payment_method = Column(String(64), default='UPI')
    attack_vector = Column(String(128), nullable=True)
    suspected_modus_operandi = Column(Text, nullable=True)
    digital_evidence_available = Column(Text, default='Bank Statement, SMS Headers')
    
    # Flags
    account_compromised = Column(Boolean, default=False)
    personal_info_exposed = Column(Boolean, default=False)
    prior_complaint_indicator = Column(Boolean, default=False)
    
    # ML & Risk Engine Outputs
    predicted_category = Column(String(64), nullable=True, index=True)
    confidence = Column(Float, default=0.0)
    prediction_confidence = Column(Float, default=0.0)
    risk_score = Column(Integer, default=0, index=True)
    risk_level = Column(String(16), default='LOW', index=True)  # LOW, MEDIUM, HIGH, CRITICAL
    priority = Column(String(16), default='Medium', index=True)  # Low, Medium, High, Critical
    severity = Column(String(16), default='Medium')
    
    # Workflow Status
    current_status = Column(String(32), default='New', index=True)  # New, Under Review, Investigating, Resolved, Closed
    status = Column(String(32), default='New')  # Legacy compatibility
    investigation_status = Column(String(128), default='Initial Triage')
    assigned_officer = Column(String(128), default='Unassigned')
    assigned_officer_id = Column(String(32), nullable=True)
    
    # Rich JSON Fields
    threat_indicators = Column(Text, default='[]')
    reasons = Column(Text, default='[]')
    recommended_actions = Column(Text, default='[]')
    
    # Audit & Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    risk_assessment = relationship("RiskAssessment", back_populates="complaint", uselist=False, cascade="all, delete-orphan")
    ml_prediction = relationship("MLPrediction", back_populates="complaint", uselist=False, cascade="all, delete-orphan")
    threat_indicators_rel = relationship("ThreatIndicator", back_populates="complaint", cascade="all, delete-orphan")
    investigation = relationship("Investigation", back_populates="complaint", uselist=False, cascade="all, delete-orphan")
    timeline_events = relationship("TimelineEvent", back_populates="complaint", cascade="all, delete-orphan", order_by="TimelineEvent.created_at")
    alerts = relationship("Alert", back_populates="complaint", cascade="all, delete-orphan")

    def to_dict(self):
        """Serialize complaint entity safely to dictionary."""
        def safe_json(val):
            if not val:
                return []
            if isinstance(val, (list, dict)):
                return val
            try:
                return json.loads(val)
            except Exception:
                return []

        return {
            "id": self.id,
            "uuid": self.uuid,
            "complaint_id": self.complaint_id,
            "title": self.title or f"{self.crime_type or self.category} Incident in {self.city or self.location}",
            "description": self.description,
            "incident_date": self.incident_date or (self.created_at.strftime("%Y-%m-%d") if self.created_at else None),
            "complaint_date": self.complaint_date or (self.created_at.strftime("%Y-%m-%d") if self.created_at else None),
            "state": self.state or "Unknown",
            "district": self.district or self.city or "Unknown",
            "city": self.city or self.location or "Unknown",
            "location": self.location or self.city or "Unknown",
            "cyber_cell_station": self.cyber_cell_station,
            "complaint_channel": self.complaint_channel,
            "crime_type": self.crime_type or self.category,
            "category": self.category or self.crime_type,
            "subcategory": self.subcategory,
            "reported_amount": float(self.reported_amount or self.financial_loss or 0.0),
            "financial_loss": float(self.financial_loss or self.reported_amount or 0.0),
            "victim_age_group": self.victim_age_group,
            "victim_gender": self.victim_gender,
            "victim_type": self.victim_type,
            "platform": self.platform,
            "payment_method": self.payment_method,
            "attack_vector": self.attack_vector,
            "suspected_modus_operandi": self.suspected_modus_operandi,
            "digital_evidence_available": self.digital_evidence_available,
            "account_compromised": bool(self.account_compromised),
            "personal_info_exposed": bool(self.personal_info_exposed),
            "prior_complaint_indicator": bool(self.prior_complaint_indicator),
            "predicted_category": self.predicted_category or self.crime_type,
            "confidence": float(self.confidence or self.prediction_confidence or 0.0),
            "prediction_confidence": float(self.prediction_confidence or self.confidence or 0.0),
            "risk_score": int(self.risk_score or 0),
            "risk_level": self.risk_level or "LOW",
            "priority": self.priority or "Medium",
            "severity": self.severity or "Medium",
            "current_status": self.current_status or self.status or "New",
            "status": self.status or self.current_status or "New",
            "investigation_status": self.investigation_status or "Initial Triage",
            "assigned_officer": self.assigned_officer or "Unassigned",
            "assigned_officer_id": self.assigned_officer_id,
            "threat_indicators": safe_json(self.threat_indicators),
            "reasons": safe_json(self.reasons),
            "recommended_actions": safe_json(self.recommended_actions),
            "created_at": self.created_at.strftime("%Y-%m-%d %H:%M:%S") if self.created_at else None,
            "updated_at": self.updated_at.strftime("%Y-%m-%d %H:%M:%S") if self.updated_at else None,
            "is_synthetic": True
        }


class CrimeCategory(Base):
    """Reference taxonomy of recognized cybercrime categories."""
    __tablename__ = 'crime_categories'

    id = Column(Integer, primary_key=True, autoincrement=True)
    category_name = Column(String(64), unique=True, nullable=False)
    description = Column(Text, nullable=True)
    base_threat_weight = Column(Integer, default=12)
    statutory_reference = Column(String(128), nullable=True)  # e.g. Section 66D IT Act
    created_at = Column(DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "category_name": self.category_name,
            "description": self.description,
            "base_threat_weight": self.base_threat_weight,
            "statutory_reference": self.statutory_reference
        }


class RiskAssessment(Base):
    """
    Explainable multi-factor risk assessment record linked to a complaint.
    Stores the exact breakdown of score components for full auditable transparency.
    """
    __tablename__ = 'risk_assessments'

    id = Column(Integer, primary_key=True, autoincrement=True)
    complaint_id = Column(String(32), ForeignKey('complaints.complaint_id', ondelete='CASCADE'), nullable=False, index=True)
    base_score = Column(Integer, default=0)
    category_factor = Column(Integer, default=0)
    severity_factor = Column(Integer, default=0)
    financial_factor = Column(Integer, default=0)
    account_compromised_factor = Column(Integer, default=0)
    pii_factor = Column(Integer, default=0)
    threat_indicators_factor = Column(Integer, default=0)
    confidence_factor = Column(Float, default=0.0)
    final_score = Column(Integer, nullable=False)
    risk_level = Column(String(16), nullable=False)
    explainability_json = Column(Text, default='{}')
    created_at = Column(DateTime, default=datetime.utcnow)

    complaint = relationship("Complaint", back_populates="risk_assessment")

    def to_dict(self):
        def parse_json(val):
            try:
                return json.loads(val) if val else {}
            except Exception:
                return {}

        return {
            "id": self.id,
            "complaint_id": self.complaint_id,
            "breakdown": {
                "category_factor": self.category_factor,
                "severity_factor": self.severity_factor,
                "financial_factor": self.financial_factor,
                "account_compromised_factor": self.account_compromised_factor,
                "pii_factor": self.pii_factor,
                "threat_indicators_factor": self.threat_indicators_factor,
                "confidence_factor": round(float(self.confidence_factor or 0), 1)
            },
            "final_score": self.final_score,
            "risk_level": self.risk_level,
            "explainability": parse_json(self.explainability_json),
            "created_at": self.created_at.strftime("%Y-%m-%d %H:%M:%S") if self.created_at else None
        }


class MLPrediction(Base):
    """
    Machine Learning inference audit record storing predictions, confidences,
    model metadata, and token attributions.
    """
    __tablename__ = 'ml_predictions'

    id = Column(Integer, primary_key=True, autoincrement=True)
    complaint_id = Column(String(32), ForeignKey('complaints.complaint_id', ondelete='CASCADE'), nullable=False, index=True)
    predicted_category = Column(String(64), nullable=False)
    confidence = Column(Float, nullable=False)
    model_name = Column(String(128), default='Calibrated Linear Classifier')
    model_version = Column(String(32), default='cybercrime-classifier-v2')
    probabilities_json = Column(Text, default='[]')
    top_features_json = Column(Text, default='[]')
    created_at = Column(DateTime, default=datetime.utcnow)

    complaint = relationship("Complaint", back_populates="ml_prediction")

    def to_dict(self):
        def parse_json(val):
            try:
                return json.loads(val) if val else []
            except Exception:
                return []

        return {
            "id": self.id,
            "complaint_id": self.complaint_id,
            "predicted_category": self.predicted_category,
            "confidence": round(float(self.confidence), 1),
            "model_name": self.model_name,
            "model_version": self.model_version,
            "probabilities": parse_json(self.probabilities_json),
            "top_features": parse_json(self.top_features_json),
            "created_at": self.created_at.strftime("%Y-%m-%d %H:%M:%S") if self.created_at else None
        }


class ThreatIndicator(Base):
    """
    Extracted threat indicator (IOC) such as URL, IP, Phone, VPA, Malware, Hash.
    Clearly marked as synthetic demonstration data.
    """
    __tablename__ = 'threat_indicators'

    id = Column(Integer, primary_key=True, autoincrement=True)
    complaint_id = Column(String(32), ForeignKey('complaints.complaint_id', ondelete='CASCADE'), nullable=False, index=True)
    indicator_value = Column(String(255), nullable=False, index=True)
    indicator_type = Column(String(64), nullable=False)  # URL, DOMAIN, PHONE, EMAIL, UPI_VPA, IP_ADDRESS, CRYPTO_WALLET, MALWARE, KEYWORD
    code = Column(String(64), nullable=True)
    label = Column(String(128), nullable=True)
    severity = Column(String(16), default='Medium')
    confidence = Column(Float, default=0.85)
    source = Column(String(64), default='Complaint Narrative NLP Extraction')
    first_seen = Column(DateTime, default=datetime.utcnow)
    is_synthetic = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    complaint = relationship("Complaint", back_populates="threat_indicators_rel")

    def to_dict(self):
        return {
            "id": self.id,
            "complaint_id": self.complaint_id,
            "indicator_value": self.indicator_value,
            "indicator_type": self.indicator_type,
            "code": self.code or self.indicator_type,
            "label": self.label or self.indicator_value,
            "severity": self.severity,
            "confidence": self.confidence,
            "source": self.source,
            "is_synthetic": self.is_synthetic,
            "first_seen": self.first_seen.strftime("%Y-%m-%d %H:%M:%S") if self.first_seen else None
        }


class Investigation(Base):
    """
    Formal Investigation Case record linking complaint with lead analyst,
    case status, priority, and timeline.
    """
    __tablename__ = 'investigations'

    id = Column(Integer, primary_key=True, autoincrement=True)
    case_number = Column(String(32), unique=True, nullable=False, index=True)
    complaint_id = Column(String(32), ForeignKey('complaints.complaint_id', ondelete='CASCADE'), nullable=False, index=True)
    lead_analyst = Column(String(128), default='Unassigned')
    lead_analyst_id = Column(String(32), nullable=True)
    status = Column(String(32), default='Initial Triage', index=True)
    priority = Column(String(16), default='Medium')
    escalation_level = Column(String(32), default='Standard')
    opened_at = Column(DateTime, default=datetime.utcnow)
    closed_at = Column(DateTime, nullable=True)
    summary = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    complaint = relationship("Complaint", back_populates="investigation")
    notes = relationship("InvestigationNote", back_populates="investigation", cascade="all, delete-orphan", order_by="InvestigationNote.created_at.desc()")
    evidence_items = relationship("EvidenceItem", back_populates="investigation", cascade="all, delete-orphan", order_by="EvidenceItem.created_at.desc()")

    def to_dict(self):
        return {
            "id": self.id,
            "case_number": self.case_number,
            "complaint_id": self.complaint_id,
            "lead_analyst": self.lead_analyst,
            "lead_analyst_id": self.lead_analyst_id,
            "status": self.status,
            "priority": self.priority,
            "escalation_level": self.escalation_level,
            "opened_at": self.opened_at.strftime("%Y-%m-%d %H:%M:%S") if self.opened_at else None,
            "closed_at": self.closed_at.strftime("%Y-%m-%d %H:%M:%S") if self.closed_at else None,
            "summary": self.summary,
            "notes_count": len(self.notes) if self.notes else 0,
            "evidence_count": len(self.evidence_items) if self.evidence_items else 0
        }


class InvestigationNote(Base):
    """Chronological analyst and investigation notes."""
    __tablename__ = 'investigation_notes'

    id = Column(Integer, primary_key=True, autoincrement=True)
    investigation_id = Column(Integer, ForeignKey('investigations.id', ondelete='CASCADE'), nullable=True, index=True)
    complaint_id = Column(String(32), nullable=False, index=True)
    author_name = Column(String(128), nullable=False)
    author_role = Column(String(64), default='Cyber Crime Analyst')
    note_type = Column(String(64), default='Analyst Note')  # Analyst Note, Triage Note, Forensic Finding, Intermediary Requisition
    content = Column(Text, nullable=False)
    status_change = Column(String(32), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    investigation = relationship("Investigation", back_populates="notes")

    def to_dict(self):
        return {
            "id": self.id,
            "complaint_id": self.complaint_id,
            "author_name": self.author_name,
            "author_role": self.author_role,
            "note_type": self.note_type,
            "content": self.content,
            "status_change": self.status_change,
            "created_at": self.created_at.strftime("%Y-%m-%d %H:%M:%S") if self.created_at else None
        }


class EvidenceItem(Base):
    """
    Evidence item with cryptographic SHA-256 hash for integrity verification.
    """
    __tablename__ = 'evidence_items'

    id = Column(Integer, primary_key=True, autoincrement=True)
    investigation_id = Column(Integer, ForeignKey('investigations.id', ondelete='CASCADE'), nullable=True, index=True)
    complaint_id = Column(String(32), nullable=False, index=True)
    evidence_number = Column(String(32), unique=True, nullable=False)  # EVD-2026-0001
    evidence_type = Column(String(64), nullable=False)  # Bank Statement, SMS Screenshot, Transaction Receipt, URL, Device Log
    description = Column(Text, nullable=False)
    file_name = Column(String(255), nullable=True)
    file_hash_sha256 = Column(String(64), nullable=False)
    source = Column(String(128), default='Complainant Upload')
    collected_by = Column(String(128), default='Cyber Crime Desk')
    chain_of_custody_verified = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    investigation = relationship("Investigation", back_populates="evidence_items")

    def to_dict(self):
        return {
            "id": self.id,
            "evidence_number": self.evidence_number,
            "complaint_id": self.complaint_id,
            "evidence_type": self.evidence_type,
            "description": self.description,
            "file_name": self.file_name,
            "file_hash_sha256": self.file_hash_sha256,
            "source": self.source,
            "collected_by": self.collected_by,
            "chain_of_custody_verified": self.chain_of_custody_verified,
            "created_at": self.created_at.strftime("%Y-%m-%d %H:%M:%S") if self.created_at else None
        }


class TimelineEvent(Base):
    """Audit-backed event in a case's chronological investigation history."""
    __tablename__ = 'timeline_events'

    id = Column(Integer, primary_key=True, autoincrement=True)
    complaint_id = Column(String(32), ForeignKey('complaints.complaint_id', ondelete='CASCADE'), nullable=False, index=True)
    event_type = Column(String(64), nullable=False)  # COMPLAINT_RECEIVED, ML_CLASSIFIED, RISK_ASSESSED, ASSIGNED, NOTE_ADDED, EVIDENCE_UPLOADED, STATUS_CHANGED
    title = Column(String(128), nullable=False)
    description = Column(Text, nullable=True)
    actor = Column(String(128), default='System')
    created_at = Column(DateTime, default=datetime.utcnow)

    complaint = relationship("Complaint", back_populates="timeline_events")

    def to_dict(self):
        return {
            "id": self.id,
            "complaint_id": self.complaint_id,
            "event_type": self.event_type,
            "title": self.title,
            "description": self.description,
            "actor": self.actor,
            "created_at": self.created_at.strftime("%d %b %Y, %H:%M") if self.created_at else None
        }


class Alert(Base):
    """Urgent system alert for high-risk or critical cybercrime complaints."""
    __tablename__ = 'alerts'

    id = Column(Integer, primary_key=True, autoincrement=True)
    alert_code = Column(String(32), unique=True, nullable=False)
    complaint_id = Column(String(32), ForeignKey('complaints.complaint_id', ondelete='CASCADE'), nullable=False, index=True)
    severity = Column(String(16), nullable=False)  # HIGH, CRITICAL
    title = Column(String(255), nullable=False)
    message = Column(Text, nullable=False)
    status = Column(String(16), default='Unread')  # Unread, Acknowledged, Resolved
    created_at = Column(DateTime, default=datetime.utcnow)

    complaint = relationship("Complaint", back_populates="alerts")

    def to_dict(self):
        return {
            "id": self.id,
            "alert_code": self.alert_code,
            "complaint_id": self.complaint_id,
            "severity": self.severity,
            "title": self.title,
            "message": self.message,
            "status": self.status,
            "created_at": self.created_at.strftime("%Y-%m-%d %H:%M:%S") if self.created_at else None
        }


class AuditLog(Base):
    """Immutable audit trail of all operational events, logins, and modifications."""
    __tablename__ = 'audit_logs'

    id = Column(Integer, primary_key=True, autoincrement=True)
    timestamp = Column(String(64), nullable=False)
    user_email = Column(String(128), nullable=False)
    user_role = Column(String(64), nullable=False)
    action = Column(String(64), nullable=False)  # LOGIN, CREATE_CASE, ANALYZE_CASE, ASSIGN_CASE, ADD_NOTE, UPLOAD_EVIDENCE, CHANGE_STATUS, GENERATE_REPORT, EXPORT_DATA
    target_entity = Column(String(64), nullable=True)
    target_id = Column(String(64), nullable=True)
    details = Column(Text, nullable=True)
    ip_address = Column(String(64), default='127.0.0.1')
    created_at = Column(DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "timestamp": self.timestamp,
            "user_email": self.user_email,
            "user_role": self.user_role,
            "action": self.action,
            "target_entity": self.target_entity,
            "target_id": self.target_id,
            "details": self.details,
            "ip_address": self.ip_address
        }


class User(Base):
    """Analyst / Investigator user accounts with Role-Based Access Control."""
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, autoincrement=True)
    email = Column(String(128), unique=True, nullable=False, index=True)
    username = Column(String(64), unique=True, nullable=False, index=True)
    full_name = Column(String(128), nullable=False)
    role = Column(String(32), nullable=False)  # Analyst, Senior Analyst, Administrator
    designation = Column(String(128), nullable=True)
    state = Column(String(64), nullable=True)
    password_hash = Column(String(255), nullable=False)
    permissions = Column(Text, default='[]')
    created_at = Column(DateTime, default=datetime.utcnow)

    def to_dict(self):
        try:
            perms = json.loads(self.permissions) if self.permissions else []
        except Exception:
            perms = []
        return {
            "id": self.id,
            "email": self.email,
            "username": self.username,
            "full_name": self.full_name,
            "role": self.role,
            "designation": self.designation,
            "state": self.state,
            "permissions": perms
        }


class Location(Base):
    """Geographic master data: States, Districts, Cities, and Cyber Cells."""
    __tablename__ = 'locations'

    id = Column(Integer, primary_key=True, autoincrement=True)
    state = Column(String(64), nullable=False)
    state_code = Column(String(8), nullable=False)
    district = Column(String(64), nullable=False)
    city = Column(String(64), nullable=False)
    cyber_cell_station = Column(String(255), nullable=False)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)

    def to_dict(self):
        return {
            "id": self.id,
            "state": self.state,
            "state_code": self.state_code,
            "district": self.district,
            "city": self.city,
            "cyber_cell_station": self.cyber_cell_station,
            "latitude": self.latitude,
            "longitude": self.longitude
        }


class KnowledgeDocument(Base):
    """Metadata for indexed RAG knowledge base documents."""
    __tablename__ = 'knowledge_documents'

    id = Column(Integer, primary_key=True, autoincrement=True)
    doc_title = Column(String(255), nullable=False)
    doc_ref = Column(String(128), nullable=False)
    authority = Column(String(128), nullable=False)
    filename = Column(String(128), unique=True, nullable=False)
    doc_type = Column(String(32), default='Standard Operating Procedure')  # SOP, Advisory, Legal Provision, Architecture
    classification = Column(String(32), default='Reference')  # Internal, Reference, Demonstration
    chunk_count = Column(Integer, default=0)
    indexed_at = Column(DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "doc_title": self.doc_title,
            "doc_ref": self.doc_ref,
            "authority": self.authority,
            "filename": self.filename,
            "doc_type": self.doc_type,
            "classification": self.classification,
            "chunk_count": self.chunk_count,
            "indexed_at": self.indexed_at.strftime("%Y-%m-%d %H:%M:%S") if self.indexed_at else None
        }


class SimilarCase(Base):
    """Precomputed or historical similar case linkages between complaints."""
    __tablename__ = 'similar_cases'

    id = Column(Integer, primary_key=True, autoincrement=True)
    complaint_id = Column(String(32), nullable=False, index=True)
    similar_complaint_id = Column(String(32), nullable=False, index=True)
    similarity_score = Column(Float, nullable=False)
    common_vector = Column(String(128), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "complaint_id": self.complaint_id,
            "similar_complaint_id": self.similar_complaint_id,
            "similarity_score": round(float(self.similarity_score), 1),
            "common_vector": self.common_vector
        }


class ForecastResult(Base):
    """Persisted forecast projections for operational planning."""
    __tablename__ = 'forecast_results'

    id = Column(Integer, primary_key=True, autoincrement=True)
    state = Column(String(64), nullable=False)
    crime_category = Column(String(64), nullable=False)
    horizon = Column(String(32), nullable=False)
    period = Column(String(64), nullable=False)
    predicted_cases = Column(Integer, nullable=False)
    lower_ci = Column(Integer, nullable=False)
    upper_ci = Column(Integer, nullable=False)
    growth_rate = Column(Float, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "state": self.state,
            "crime_category": self.crime_category,
            "horizon": self.horizon,
            "period": self.period,
            "predicted_cases": self.predicted_cases,
            "lower_ci": self.lower_ci,
            "upper_ci": self.upper_ci,
            "growth_rate": self.growth_rate,
            "created_at": self.created_at.strftime("%Y-%m-%d %H:%M:%S") if self.created_at else None
        }
