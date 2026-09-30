import sqlite3
import os
import pandas as pd
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'backend', 'cybercrime.db')
POWERBI_DIR = os.path.dirname(__file__)
DATASETS_DIR = os.path.join(POWERBI_DIR, 'datasets')
VIEWS_DIR = os.path.join(POWERBI_DIR, 'views')
DOCS_DIR = os.path.join(POWERBI_DIR, 'documentation')

os.makedirs(DATASETS_DIR, exist_ok=True)
os.makedirs(VIEWS_DIR, exist_ok=True)
os.makedirs(DOCS_DIR, exist_ok=True)

def generate_star_schema():
    conn = sqlite3.connect(DB_PATH)
    df_raw = pd.read_sql_query('SELECT * FROM complaints', conn)
    conn.close()

    if df_raw.empty:
        print("No complaints found in database.")
        return

    # Clean dates
    df_raw['incident_date'] = pd.to_datetime(df_raw['incident_date'], errors='coerce').dt.strftime('%Y-%m-%d')
    df_raw['complaint_date'] = pd.to_datetime(df_raw['complaint_date'], errors='coerce').dt.strftime('%Y-%m-%d')

    # 1. DimLocation
    locations = df_raw[['state', 'district', 'city', 'cyber_cell_station']].drop_duplicates().reset_index(drop=True)
    locations['LocationKey'] = locations.index + 1
    loc_path = os.path.join(DATASETS_DIR, 'DimLocation.csv')
    locations.to_csv(loc_path, index=False)
    print(f"Exported {loc_path} ({len(locations)} rows)")

    # 2. DimCrimeType
    crimes = df_raw[['crime_type', 'subcategory', 'predicted_category']].drop_duplicates().reset_index(drop=True)
    crimes['CrimeKey'] = crimes.index + 1
    crime_path = os.path.join(DATASETS_DIR, 'DimCrimeType.csv')
    crimes.to_csv(crime_path, index=False)
    print(f"Exported {crime_path} ({len(crimes)} rows)")

    # 3. DimVictim
    victims = df_raw[['victim_age_group', 'victim_gender']].drop_duplicates().reset_index(drop=True)
    victims['VictimKey'] = victims.index + 1
    victim_path = os.path.join(DATASETS_DIR, 'DimVictim.csv')
    victims.to_csv(victim_path, index=False)
    print(f"Exported {victim_path} ({len(victims)} rows)")

    # 4. DimStatus
    statuses = df_raw[['current_status', 'investigation_status', 'priority', 'risk_level']].drop_duplicates().reset_index(drop=True)
    statuses['StatusKey'] = statuses.index + 1
    status_path = os.path.join(DATASETS_DIR, 'DimStatus.csv')
    statuses.to_csv(status_path, index=False)
    print(f"Exported {status_path} ({len(statuses)} rows)")

    # 5. DimOfficer
    officers = df_raw[['assigned_officer']].drop_duplicates().reset_index(drop=True)
    officers['OfficerKey'] = officers.index + 1
    officer_path = os.path.join(DATASETS_DIR, 'DimOfficer.csv')
    officers.to_csv(officer_path, index=False)
    print(f"Exported {officer_path} ({len(officers)} rows)")

    # 6. DimDate
    all_dates = pd.concat([df_raw['incident_date'], df_raw['complaint_date']]).dropna().unique()
    dates_df = pd.DataFrame({'Date': all_dates})
    dates_df['Date'] = pd.to_datetime(dates_df['Date'])
    dates_df = dates_df.sort_values('Date').reset_index(drop=True)
    dates_df['DateKey'] = dates_df['Date'].dt.strftime('%Y%m%d').astype(int)
    dates_df['FullDate'] = dates_df['Date'].dt.strftime('%Y-%m-%d')
    dates_df['Year'] = dates_df['Date'].dt.year
    dates_df['Quarter'] = 'Q' + dates_df['Date'].dt.quarter.astype(str)
    dates_df['Month'] = dates_df['Date'].dt.strftime('%B')
    dates_df['MonthNum'] = dates_df['Date'].dt.month
    dates_df['DayOfWeek'] = dates_df['Date'].dt.strftime('%A')
    date_path = os.path.join(DATASETS_DIR, 'DimDate.csv')
    dates_df.to_csv(date_path, index=False)
    print(f"Exported {date_path} ({len(dates_df)} rows)")

    # 7. FactComplaints
    facts = df_raw.merge(locations, on=['state', 'district', 'city', 'cyber_cell_station'], how='left')
    facts = facts.merge(crimes, on=['crime_type', 'subcategory', 'predicted_category'], how='left')
    facts = facts.merge(victims, on=['victim_age_group', 'victim_gender'], how='left')
    facts = facts.merge(statuses, on=['current_status', 'investigation_status', 'priority', 'risk_level'], how='left')
    facts = facts.merge(officers, on=['assigned_officer'], how='left')

    facts['IncidentDateKey'] = pd.to_datetime(facts['incident_date']).dt.strftime('%Y%m%d').fillna('0').astype(int)
    facts['ComplaintDateKey'] = pd.to_datetime(facts['complaint_date']).dt.strftime('%Y%m%d').fillna('0').astype(int)

    fact_cols = [
        'id', 'complaint_id', 'IncidentDateKey', 'ComplaintDateKey',
        'LocationKey', 'CrimeKey', 'VictimKey', 'StatusKey', 'OfficerKey',
        'reported_amount', 'financial_loss', 'risk_score', 'confidence',
        'prior_complaint_indicator', 'personal_info_exposed', 'account_compromised'
    ]
    fact_table = facts[[c for c in fact_cols if c in facts.columns]]
    fact_path = os.path.join(DATASETS_DIR, 'FactComplaints.csv')
    fact_table.to_csv(fact_path, index=False)
    print(f"Exported {fact_path} ({len(fact_table)} rows)")

    # 8. Generate SQL Views Script for DirectQuery
    sql_script = '''-- Power BI DirectQuery Star Schema Views
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
'''
    view_path = os.path.join(VIEWS_DIR, 'powerbi_star_schema_views.sql')
    with open(view_path, 'w', encoding='utf-8') as f:
        f.write(sql_script)
    print(f"Exported SQL Views: {view_path}")

if __name__ == '__main__':
    generate_star_schema()
