"""
PostgreSQL Migration & Synchronization Utility
Moves existing SQLite complaint data, relational assessments, evidence, and audit logs
into PostgreSQL via SQLAlchemy and psycopg2.

Usage:
  python migrate_to_postgres.py [optional_postgres_url]
Or set environment variable:
  export DATABASE_URL="postgresql://user:password@localhost:5432/cybercrimepredict"
  python migrate_to_postgres.py
"""

import os
import sys
from dotenv import load_dotenv
from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import sessionmaker

load_dotenv()

from models_db import (
    Base, Complaint, CrimeCategory, RiskAssessment, MLPrediction,
    ThreatIndicator, Investigation, InvestigationNote, EvidenceItem,
    TimelineEvent, Alert, AuditLog, User, Location, KnowledgeDocument,
    SimilarCase, ForecastResult
)

SQLITE_PATH = os.path.join(os.path.dirname(__file__), 'cybercrime.db')

def migrate(target_url=None):
    postgres_url = target_url or os.getenv("DATABASE_URL")
    if not postgres_url or "sqlite" in postgres_url.lower():
        print("ERROR: A valid PostgreSQL connection string is required.")
        print("Provide as argument or set DATABASE_URL environment variable.")
        print("Example: python migrate_to_postgres.py postgresql://postgres:postgres@localhost:5432/cybercrimepredict")
        sys.exit(1)

    if postgres_url.startswith("postgres://"):
        postgres_url = postgres_url.replace("postgres://", "postgresql://", 1)

    print(f"[*] Starting migration from SQLite ({SQLITE_PATH}) to PostgreSQL...")
    print(f"[*] Target PostgreSQL URL: {postgres_url.split('@')[-1] if '@' in postgres_url else 'configured host'}")

    # SQLite Source
    sqlite_engine = create_engine(f"sqlite:///{SQLITE_PATH}")
    SqliteSession = sessionmaker(bind=sqlite_engine)
    src_session = SqliteSession()

    # PostgreSQL Destination
    try:
        pg_engine = create_engine(postgres_url, pool_pre_ping=True)
        with pg_engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        print("[+] PostgreSQL connection confirmed.")
    except Exception as e:
        print(f"[-] Connection failed to PostgreSQL: {e}")
        sys.exit(1)

    PgSession = sessionmaker(bind=pg_engine)
    dst_session = PgSession()

    print("[*] Creating relational tables in PostgreSQL...")
    Base.metadata.create_all(bind=pg_engine)

    TABLES = [
        ("crime_categories", CrimeCategory),
        ("users", User),
        ("locations", Location),
        ("knowledge_documents", KnowledgeDocument),
        ("complaints", Complaint),
        ("risk_assessments", RiskAssessment),
        ("ml_predictions", MLPrediction),
        ("threat_indicators", ThreatIndicator),
        ("investigations", Investigation),
        ("investigation_notes", InvestigationNote),
        ("evidence_items", EvidenceItem),
        ("timeline_events", TimelineEvent),
        ("alerts", Alert),
        ("audit_logs", AuditLog),
        ("similar_cases", SimilarCase),
        ("forecast_results", ForecastResult)
    ]

    total_migrated = 0
    for tbl_name, model_cls in TABLES:
        try:
            records = src_session.query(model_cls).all()
            if not records:
                continue

            print(f"[*] Migrating {tbl_name} ({len(records)} records)...")
            count = 0
            for r in records:
                # Merge into destination session
                dst_session.merge(r)
                count += 1
                if count % 100 == 0:
                    dst_session.commit()
            dst_session.commit()
            total_migrated += count
            print(f"[+] Migrated {count} records to {tbl_name}.")
        except Exception as err:
            dst_session.rollback()
            print(f"[-] Error migrating {tbl_name}: {err}")

    # Verification
    print("\n--- MIGRATION VERIFICATION ---")
    verified = True
    for tbl_name, model_cls in TABLES:
        src_count = src_session.query(model_cls).count()
        dst_count = dst_session.query(model_cls).count()
        match_str = "[OK]" if src_count == dst_count else "[MISMATCH]"
        if src_count != dst_count:
            verified = False
        print(f"  {match_str} {tbl_name:24}: SQLite={src_count} -> PostgreSQL={dst_count}")

    src_session.close()
    dst_session.close()

    if verified:
        print("\n[SUCCESS] All tables and records successfully migrated to PostgreSQL!")
    else:
        print("\n[WARNING] Migration completed with some record discrepancies.")

if __name__ == '__main__':
    url_arg = sys.argv[1] if len(sys.argv) > 1 else None
    migrate(url_arg)
