-- Power BI DirectQuery Star Schema Views
-- Generated for Predictive Cyber Crime Intelligence Platform

CREATE VIEW IF NOT EXISTS v_FactComplaints AS
SELECT 
    id,
    complaint_id,
    strftime('%Y%m%d', complaint_date) AS ComplaintDateKey,
    strftime('%Y%m%d', incident_date) AS IncidentDateKey,
    state,
    city,
    crime_type,
    predicted_category,
    reported_amount AS FinancialLossINR,
    risk_score AS RiskScore,
    risk_level AS RiskLevel,
    priority AS Priority,
    current_status AS Status,
    investigation_status AS InvestigationStatus,
    assigned_officer AS AssignedOfficer,
    confidence AS PredictionConfidence
FROM complaints;

CREATE VIEW IF NOT EXISTS v_ExecutiveKPIs AS
SELECT
    COUNT(*) AS TotalComplaints,
    SUM(CASE WHEN risk_score >= 80 THEN 1 ELSE 0 END) AS CriticalCases,
    SUM(CASE WHEN risk_score >= 60 AND risk_score < 80 THEN 1 ELSE 0 END) AS HighRiskCases,
    ROUND(AVG(risk_score), 1) AS AverageRiskScore,
    ROUND(SUM(reported_amount), 2) AS TotalFinancialLossINR,
    ROUND(100.0 * SUM(CASE WHEN current_status = 'Resolved' THEN 1 ELSE 0 END) / COUNT(*), 1) AS ResolutionRatePct
FROM complaints;
