import os
import re
import json
import uuid
import random
import hashlib
from datetime import datetime, timedelta
from dotenv import load_dotenv
from sqlalchemy import create_engine, text, inspect
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.pool import QueuePool, StaticPool
from contextlib import contextmanager

# Load environment variables from .env if present
load_dotenv()

from models_db import (
    Base, Complaint, CrimeCategory, RiskAssessment, MLPrediction,
    ThreatIndicator, Investigation, InvestigationNote, EvidenceItem,
    TimelineEvent, Alert, AuditLog, User, Location, KnowledgeDocument,
    SimilarCase, ForecastResult
)
from analyzer import analyze_complaint

# Database configuration
DATABASE_URL = os.getenv("DATABASE_URL")
SQLITE_DB_PATH = os.path.join(os.path.dirname(__file__), 'cybercrime.db')

engine = None
SessionLocal = None
CURRENT_DB_TYPE = "sqlite"

def setup_database_engine():
    global engine, SessionLocal, CURRENT_DB_TYPE
    
    raw_url = os.getenv("DATABASE_URL")
    if raw_url and raw_url.strip():
        # Handle heroku/render postgresql schema prefix
        if raw_url.startswith("postgres://"):
            raw_url = raw_url.replace("postgres://", "postgresql://", 1)
        
        try:
            pg_engine = create_engine(
                raw_url,
                poolclass=QueuePool,
                pool_size=10,
                max_overflow=20,
                pool_pre_ping=True,
                pool_recycle=1800,
                connect_args={"connect_timeout": 5}
            )
            # Test connection
            with pg_engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            
            engine = pg_engine
            CURRENT_DB_TYPE = "postgresql"
            print(f"[DATABASE] Connected to PostgreSQL successfully via DATABASE_URL.")
        except Exception as e:
            print(f"[DATABASE WARNING] PostgreSQL connection failed ({e}). Falling back to SQLite for local environment.")
            sqlite_url = f"sqlite:///{SQLITE_DB_PATH}"
            engine = create_engine(sqlite_url, connect_args={"check_same_thread": False})
            CURRENT_DB_TYPE = "sqlite"
    else:
        sqlite_url = f"sqlite:///{SQLITE_DB_PATH}"
        engine = create_engine(sqlite_url, connect_args={"check_same_thread": False})
        CURRENT_DB_TYPE = "sqlite"
        print(f"[DATABASE] Using SQLite local database: {SQLITE_DB_PATH}")

    session_factory = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    SessionLocal = scoped_session(session_factory)
    return engine, SessionLocal

# Initialize engine on import
setup_database_engine()

@contextmanager
def get_session():
    """Provide a transactional scope around a series of operations."""
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()

def get_db_status():
    """Health check diagnostic returning connection status and database engine."""
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        
        with get_session() as session:
            complaint_count = session.query(Complaint).count()
            critical_count = session.query(Complaint).filter(Complaint.risk_score >= 75).count()
            alert_count = session.query(Alert).filter(Alert.status == 'Unread').count()
            evidence_count = session.query(EvidenceItem).count()

        return {
            "status": "connected",
            "type": CURRENT_DB_TYPE,
            "dialect": engine.dialect.name,
            "complaint_count": complaint_count,
            "critical_count": critical_count,
            "unread_alerts": alert_count,
            "evidence_count": evidence_count,
            "pool_size": getattr(engine.pool, "size", lambda: 1)() if hasattr(engine.pool, "size") else 1
        }
    except Exception as e:
        return {
            "status": "error",
            "type": CURRENT_DB_TYPE,
            "error": str(e)
        }

# Predefined realistic stations and officers across 8 Indian States & 12 Cities
INDIAN_JURISDICTIONS = {
    "Karnataka": {
        "code": "KA",
        "cities": [
            ("Bengaluru", "Cyber Crime Police Station, CID Karnataka, Palace Road"),
            ("Mangaluru", "Cyber Economic & Narcotics (CEN) PS, Mangaluru City"),
            ("Mysuru", "City Cyber Crime Police Station, Mysuru Urban Police")
        ]
    },
    "Maharashtra": {
        "code": "MH",
        "cities": [
            ("Mumbai", "South Region Cyber Police Station, BKC Bandra Mumbai"),
            ("Pune", "Cyber Crime Investigation Cell, Shivajinagar Pune")
        ]
    },
    "Telangana": {
        "code": "TS",
        "cities": [
            ("Hyderabad", "Cyber Crimes Police Station, CCS Hyderabad City Police")
        ]
    },
    "Delhi": {
        "code": "DL",
        "cities": [
            ("Delhi", "Special Cell Cyber Prevention (IFSO Unit), Dwarka Delhi"),
            ("New Delhi", "Cyber Police Station, Central District, Daryaganj New Delhi")
        ]
    },
    "Tamil Nadu": {
        "code": "TN",
        "cities": [
            ("Chennai", "Cyber Crime Cell, Central Crime Branch (CCB), Vepery Chennai")
        ]
    },
    "Gujarat": {
        "code": "GJ",
        "cities": [
            ("Ahmedabad", "Cyber Crime Police Station, Crime Branch, Gaekwad Haveli Ahmedabad")
        ]
    },
    "West Bengal": {
        "code": "WB",
        "cities": [
            ("Kolkata", "Cyber Police Station, Lalbazar Kolkata Police HQ")
        ]
    },
    "Uttar Pradesh": {
        "code": "UP",
        "cities": [
            ("Noida", "Cyber Crime Police Station, Sector 36 Gautam Buddha Nagar Noida"),
            ("Lucknow", "Cyber Crime Police Station, Hazratganj Lucknow")
        ]
    }
}

OFFICERS_POOL = [
    ("Insp. Anand Patil", "KA-COP-4102", "Karnataka"),
    ("Sub-Insp. Priya Nair", "KA-COP-5209", "Karnataka"),
    ("Insp. Sandeep Deshmukh", "MH-COP-7811", "Maharashtra"),
    ("Sub-Insp. Rohan Sawant", "MH-COP-8321", "Maharashtra"),
    ("Insp. Vikramaditya Reddy", "TS-COP-3184", "Telangana"),
    ("Sub-Insp. Kavitha Rao", "TS-COP-4412", "Telangana"),
    ("Insp. Rajiv Tyagi", "DL-COP-9014", "Delhi"),
    ("Sub-Insp. Neha Sharma", "DL-COP-9523", "Delhi"),
    ("Insp. Meenakshi Sundaram", "TN-COP-6421", "Tamil Nadu"),
    ("Sub-Insp. Hardik Patel", "GJ-COP-2219", "Gujarat"),
    ("Insp. Anirban Mukherjee", "WB-COP-8843", "West Bengal"),
    ("Insp. Amitav Srivastava", "UP-COP-7104", "Uttar Pradesh")
]

# Realistic narrative templates covering all 10 cybercrime categories with coherent technical vectors
NARRATIVE_TEMPLATES = [
    # 1. Phishing Attack
    {
        "category": "Phishing Attack",
        "subcategory": "Cloned Banking Portal & Credential Theft",
        "platform": "SMS / Web Portal",
        "payment_method": "Net Banking",
        "attack_vector": "Phishing Link / Credential Harvesting",
        "modus": "Spoofed SMS with phishing domain mimicking SBI NetBanking requiring immediate PAN update.",
        "victim_type": "Individual",
        "age_groups": ["26-40", "41-60"],
        "loss_range": (15000, 120000),
        "templates": [
            "Received SMS purporting to be from State Bank of India claiming account blocked due to unverified PAN. Followed link to http://sbi-kyc-verify-portal.online and entered username, login password, and OTP. Within minutes, ₹{loss} was debited to beneficiary account {vpa}.",
            "Phishing email claiming an electricity bill surcharge had failed. Clicked on www.billdesk-electricity-update.site and provided debit card number, CVV, and SMS OTP. Unauthorized debit of ₹{loss} was immediately confirmed.",
            "Deceptive WhatsApp message claiming income tax refund of ₹42,500 pending. Directed to enter netbanking credentials on cloned refund portal http://incometax-efiling-refund.site. Total loss of ₹{loss} via multiple IMPS transfers."
        ]
    },
    # 2. Online Financial Fraud
    {
        "category": "Online Financial Fraud",
        "subcategory": "QR Code Scanning Coercion / OLX Advance",
        "platform": "OLX / Google Pay / PhonePe",
        "payment_method": "UPI",
        "attack_vector": "QR Code Reversal Coercion",
        "modus": "Fraudulent buyer sent QR code claiming it would credit money, but debit occurred upon entering UPI PIN.",
        "victim_type": "Individual",
        "age_groups": ["18-25", "26-40"],
        "loss_range": (10000, 85000),
        "templates": [
            "Posted sofa for sale on OLX. Buyer claimed to be army personnel and sent Google Pay QR code stating scan is required to receive ₹{loss}. Entered UPI PIN and amount was instantly debited to {vpa}. Fraudster phone number: +91-{phone}.",
            "Scammer called posing as customer service for courier delivery. Induced me to scan a dynamic QR code on PhonePe for a 5-rupee address correction fee. Account debited by ₹{loss} to unknown merchant.",
            "Fraudulent UPI request received on PayTM labeled 'Cashback Credit'. Upon clicking approve and entering UPI PIN, ₹{loss} was transferred to beneficiary VPA {vpa} with UTR {utr}."
        ]
    },
    # 3. Account Takeover
    {
        "category": "Account Takeover",
        "subcategory": "Telecom SIM Swap & 2FA Bypass",
        "platform": "Telecom Cellular / Net Banking",
        "payment_method": "IMPS / RTGS",
        "attack_vector": "SIM Swap / OTP Interception",
        "modus": "Duplicate SIM card issued via forged Aadhaar, disconnecting victim's mobile and intercepting 2FA OTPs.",
        "victim_type": "Individual",
        "age_groups": ["26-40", "41-60"],
        "loss_range": (50000, 350000),
        "templates": [
            "My mobile network lost signal completely. During the 5-hour outage, perpetrators executed a SIM swap at a local telecom store and siphoned ₹{loss} across 4 IMPS transfers from my HDFC bank account. Suspect phone: +91-{phone}.",
            "Instagram business account with 45,000 followers hijacked after receiving fake copyright infringement notice link. Hacker changed recovery email to hacker99@protonmail.com and demanded ₹{loss} in USDT for restoration.",
            "Corporate email account hijacked via session cookie theft. Unauthorized actor initiated fraudulent wire transfer of ₹{loss} to foreign intermediary account before access was revoked."
        ]
    },
    # 4. Ransomware / Malware
    {
        "category": "Ransomware / Malware",
        "subcategory": "Enterprise Endpoint Encryption & Extortion",
        "platform": "Windows Server / Remote Desktop",
        "payment_method": "Cryptocurrency",
        "attack_vector": "RDP Brute Force / Malicious Payload",
        "modus": "LockBit 3.0 ransomware deployed on core database servers, encrypting customer data with ransom note.",
        "victim_type": "Enterprise",
        "age_groups": ["Enterprise"],
        "loss_range": (300000, 2500000),
        "templates": [
            "Hospital diagnostic laboratory server encrypted overnight by LockBit 3.0 ransomware. All patient radiology reports locked with .lockbit3 extension. Ransom note README_DECRYPT.txt demands 2.5 Bitcoin to wallet {wallet}. Estimated business impact ₹{loss}.",
            "Accounting firm network compromised via AnyDesk remote session payload. SQL database and Tally backup files encrypted with AES-256. Threat actors demanding payment of ₹{loss} in Monero cryptocurrency.",
            "Educational institution student administration system infected with trojan dropper via malicious email invoice attachment. All admission databases inaccessible; recovery cost estimated at ₹{loss}."
        ]
    },
    # 5. Data Breach
    {
        "category": "Data Breach",
        "subcategory": "Cloud Storage Exfiltration & Dark Web Leak",
        "platform": "AWS S3 / Dark Web Forums",
        "payment_method": "Cryptocurrency",
        "attack_vector": "Misconfigured Cloud Bucket / API Leak",
        "modus": "Misconfigured AWS S3 object storage exposed 120,000 customer KYC records subsequently listed on BreachForums.",
        "victim_type": "Enterprise",
        "age_groups": ["Enterprise"],
        "loss_range": (250000, 1800000),
        "templates": [
            "Fintech startup customer KYC database containing 90,000 Aadhaar card copies, phone numbers, and bank details posted on dark web hacker forum. Threat actor demanding ₹{loss} equivalent in Ethereum to remove database.",
            "Healthcare portal API authentication flaw allowed unauthenticated scraping of 45,000 patient electronic prescriptions. Audit logs show exfiltration originating from IP {ip}.",
            "E-commerce database compromised via SQL injection on staging endpoint. 200,000 customer addresses and transaction histories downloaded by unauthorized external entity."
        ]
    },
    # 6. Identity Theft
    {
        "category": "Identity Theft",
        "subcategory": "Matrimonial Profile Impersonation & Loan Fraud",
        "platform": "Instagram / Jeevansathi / Instant Loan Apps",
        "payment_method": "None",
        "attack_vector": "Identity Cloning / Forged Documents",
        "modus": "Stolen identity documents used to secure fraudulent personal loans from unauthorized digital lending apps.",
        "victim_type": "Individual",
        "age_groups": ["26-40", "41-60"],
        "loss_range": (20000, 150000),
        "templates": [
            "Discovered that an unknown person obtained two instant digital personal loans totaling ₹{loss} in my name using a forged copy of my PAN card and morphed electricity bill on a loan app.",
            "Fake social media profile created on Facebook and Instagram using my photographs and personal identity. Imposter contacted my professional contacts and relatives requesting urgent financial help.",
            "Imposter created verified matrimonial profile using my identity and contacted multiple families, collecting ₹{loss} as booking deposits before disappearing."
        ]
    },
    # 7. Investment/Crypto Fraud
    {
        "category": "Investment/Crypto Fraud",
        "subcategory": "Telegram Task Rating & Crypto Ponzi",
        "platform": "Telegram / WhatsApp / Fake Exchange",
        "payment_method": "UPI / IMPS / Crypto",
        "attack_vector": "Social Engineering / Ponzi Scheme",
        "modus": "Part-time YouTube video liking task promised high returns, leading to VIP crypto investment group where withdrawal was frozen.",
        "victim_type": "Individual",
        "age_groups": ["18-25", "26-40"],
        "loss_range": (50000, 800000),
        "templates": [
            "Offered part-time job on WhatsApp to review Google Maps hotels for ₹150 each. Moved to Telegram group where admin promised 30% daily returns on crypto recharge. Transferred ₹{loss} to beneficiary VPAs {vpa} before all withdrawals were frozen.",
            "Lured into fake institutional stock trading app 'Goldman Global VIP' offering pre-IPO share allocations. Invested ₹{loss} via multiple RTGS transfers. App showed ₹18,00,000 balance but customer care demanded 20% tax before withdrawal.",
            "Joined automated forex trading bot promising guaranteed monthly returns. Deposited ₹{loss} into crypto wallet {wallet}. Bot stopped responding and administrator deleted Telegram account."
        ]
    },
    # 8. Online Shopping Fraud
    {
        "category": "Online Shopping Fraud",
        "subcategory": "Counterfeit E-Commerce & Flash Sale Scam",
        "platform": "Fake E-Commerce Portal / Instagram Store",
        "payment_method": "UPI Gateway",
        "attack_vector": "Deceptive Storefront / Payment Gateway Abuse",
        "modus": "Fake festive flash sale offering heavily discounted electronics. Payment collected via UPI but empty parcel or counterfeit items delivered.",
        "victim_type": "Individual",
        "age_groups": ["18-25", "26-40"],
        "loss_range": (5000, 60000),
        "templates": [
            "Purchased Apple iPhone 15 on festive clearance sale portal www.festive-gadgets-clearance.store for ₹{loss}. Paid in advance via UPI. Received courier parcel containing stones and soap cakes. Merchant phone disconnected: +91-{phone}.",
            "Ordered designer clothing through Instagram boutique sponsored advertisement for ₹{loss}. Payment made to {vpa}. No tracking number provided and account blocked immediately after payment confirmation.",
            "Booked luxury hotel resort package in Goa on cloned booking portal www.goa-beach-resort-offers.site for ₹{loss}. Arrived at destination to discover reservation was nonexistent."
        ]
    },
    # 9. Social Engineering
    {
        "category": "Social Engineering",
        "subcategory": "Digital Arrest / Fake Law Enforcement Coercion",
        "platform": "WhatsApp Video / Skype / RTGS",
        "payment_method": "Net Banking RTGS",
        "attack_vector": "Authority Impersonation / Psychological Coercion",
        "modus": "Fraudsters dressed in police uniform contacted victim on Skype, claiming parcel contained MDMA drugs, placing victim under continuous 'digital arrest'.",
        "victim_type": "Senior Citizen",
        "age_groups": ["41-60", "Senior Citizen (60+)"],
        "loss_range": (200000, 1800000),
        "templates": [
            "Received WhatsApp video call from caller in police uniform claiming FedEx parcel sent in my name to Cambodia contained contraband MDMA. Placed under 36-hour Skype 'digital arrest' and coerced into transferring ₹{loss} to RBI verification account {vpa}.",
            "Caller claiming to be customs officer at Mumbai International Airport stated my son was detained in a financial laundering probe. Coerced into immediate transfer of ₹{loss} via RTGS to avoid public arrest.",
            "Received call from fake telecom verification officer threatening immediate mobile disconnection within 2 hours unless I completed biometric verification on remote app AnyDesk. Perpetrator accessed bank app and siphoned ₹{loss}."
        ]
    },
    # 10. Cyber Bullying / Harassment
    {
        "category": "Cyber Bullying / Harassment",
        "subcategory": "Morphed Non-Consensual Imagery & Extortion",
        "platform": "Telegram / Instagram / WhatsApp",
        "payment_method": "UPI",
        "attack_vector": "Doxxing / Deepfake Extortion",
        "modus": "Perpetrator accessed gallery photos, generated morphed explicit photographs, and threatened to circulate to family and employer unless extortion paid.",
        "victim_type": "Individual",
        "age_groups": ["18-25", "26-40"],
        "loss_range": (10000, 80000),
        "templates": [
            "Downloaded instant loan app that scraped phone contacts. Scammers morphed my facial photo into obscene images and created WhatsApp group with my office colleagues, threatening dissemination unless ₹{loss} paid immediately to {vpa}.",
            "Unknown stalker creating anonymous Instagram accounts sending abusive voice messages and defamatory posts regarding my personal life. Threatening physical harm unless personal meetings arranged. Suspect IP: {ip}.",
            "Perpetrator recorded private video during Skype conversation and demanding ₹{loss} via UPI to prevent uploading to public social media platforms."
        ]
    }
]

def generate_synthetic_data(target_count=350):
    """
    Generate 300+ coherent, highly realistic synthetic cybercrime complaint records
    with full relational integrity across all 10 crime categories and 8 states.
    """
    with get_session() as session:
        existing_count = session.query(Complaint).count()
        if existing_count >= target_count:
            print(f"[SEED] Database already has {existing_count} complaints. Skipping generation.")
            return

        needed = target_count - existing_count
        print(f"[SEED] Generating {needed} realistic synthetic complaints with full relational integrity...")

        # Base mock IOC values for realistic synthesis
        vpabanks = ["okhdfcbank", "okaxis", "oksbi", "okicici", "paytm", "ybl"]
        wallets = [
            "0x71C84931a7fF38B9a1945F348F0a57493297a78F",
            "0x3B88A01A94903333Fe35Fe4F3F7383B38c2B527E",
            "bc1qxy2kgdygjrsqtzq2n0yrf2493p83kkfjhx0wlh",
            "1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa"
        ]
        ips = ["185.220.101.5", "194.26.29.112", "45.154.255.89", "103.251.167.22", "192.168.1.104"]

        # Date range: Jan 1 2026 to Sep 29 2026
        base_start = datetime(2026, 1, 1, 9, 0, 0)
        current_now = datetime(2026, 9, 29, 13, 0, 0)
        total_days = (current_now - base_start).days

        statuses = [
            ("New", "Initial Triage", 0.35),
            ("Under Review", "Evidence Acquisition & Intermediary Notices", 0.25),
            ("Investigating", "Forensic Analysis & Bank Debit Freeze Active", 0.25),
            ("Resolved", "Chargesheet Filed / Funds Recovered", 0.15)
        ]

        complaints_batch = []
        created_complaint_ids = []

        for i in range(needed):
            serial = existing_count + i + 101
            
            # Select State and City
            state_name, state_meta = random.choice(list(INDIAN_JURISDICTIONS.items()))
            state_code = state_meta["code"]
            city_name, station_name = random.choice(state_meta["cities"])
            
            # Select Officer for that state or general
            state_officers = [o for o in OFFICERS_POOL if o[2] == state_name]
            officer = random.choice(state_officers) if state_officers else random.choice(OFFICERS_POOL)
            officer_name, officer_id = officer[0], officer[1]

            # Select Narrative Template
            template_group = random.choice(NARRATIVE_TEMPLATES)
            cat_name = template_group["category"]
            subcat = template_group["subcategory"]
            loss = random.randint(*template_group["loss_range"])
            loss = round(loss / 500) * 500  # round to neat numbers

            # Interpolate template variables
            phone_num = f"{random.choice([7, 8, 9])}{random.randint(100000000, 999999999)}"
            vpa = f"merchant.{random.randint(1000, 9999)}@{random.choice(vpabanks)}"
            wallet = random.choice(wallets)
            ip_val = random.choice(ips)
            utr = f"26{random.randint(1000000000, 9999999999)}"

            raw_text = random.choice(template_group["templates"])
            description = raw_text.format(
                loss=f"{loss:,}",
                vpa=vpa,
                phone=phone_num,
                wallet=wallet,
                ip=ip_val,
                utr=utr
            )

            # Dates
            random_offset = random.randint(0, total_days)
            incident_dt = base_start + timedelta(days=random_offset, hours=random.randint(1, 10))
            reporting_lag = random.choice([0, 1, 1, 2, 3, 5])
            complaint_dt = incident_dt + timedelta(days=reporting_lag)
            if complaint_dt > current_now:
                complaint_dt = current_now

            # Severity and Flags
            if loss >= 300000 or cat_name in ["Ransomware / Malware", "Data Breach"]:
                sev = "Critical"
            elif loss >= 50000 or "arrest" in description.lower():
                sev = "High"
            elif loss >= 15000:
                sev = "Medium"
            else:
                sev = "Low"

            acc_compromised = True if cat_name in ["Account Takeover", "Ransomware / Malware"] or "hacked" in description.lower() else False
            pii_exposed = True if cat_name in ["Identity Theft", "Data Breach"] or "pan" in description.lower() or "aadhaar" in description.lower() else False

            # Run analyzer
            analysis = analyze_complaint(
                description=description,
                reported_category=cat_name,
                severity=sev,
                financial_loss=loss,
                personal_info_exposed=pii_exposed,
                account_compromised=acc_compromised
            )

            # Human-readable complaint ID: CC-2026-IN-XXXXXX
            comp_id = f"CC-2026-{state_code}-{serial:06d}"
            created_complaint_ids.append(comp_id)

            # Pick status
            r_status = random.random()
            if r_status < 0.35:
                curr_status, inv_status = "New", "Initial Triage"
            elif r_status < 0.60:
                curr_status, inv_status = "Under Review", "Evidence Acquisition & Intermediary Notices"
            elif r_status < 0.85:
                curr_status, inv_status = "Investigating", "Forensic Analysis & Bank Freeze Active"
            else:
                curr_status, inv_status = "Resolved", "Chargesheet Filed / Funds Recovered"

            priority = "Critical" if analysis["risk_score"] >= 75 else "High" if analysis["risk_score"] >= 50 else "Medium" if analysis["risk_score"] >= 25 else "Low"

            complaint = Complaint(
                complaint_id=comp_id,
                title=f"{cat_name} reported in {city_name}",
                description=description,
                incident_date=incident_dt.strftime("%Y-%m-%d"),
                complaint_date=complaint_dt.strftime("%Y-%m-%d"),
                state=state_name,
                district=city_name,
                city=city_name,
                location=city_name,
                cyber_cell_station=station_name,
                complaint_channel=random.choice(["National Cyber Crime Portal", "1930 Helpline", "Walk-in Cyber Cell", "State Portal"]),
                crime_type=cat_name,
                category=cat_name,
                subcategory=subcat,
                reported_amount=float(loss),
                financial_loss=float(loss),
                victim_age_group=random.choice(template_group["age_groups"]),
                victim_gender=random.choice(["Male", "Female", "Organization"]),
                victim_type=template_group["victim_type"],
                platform=template_group["platform"],
                payment_method=template_group["payment_method"],
                attack_vector=template_group["attack_vector"],
                suspected_modus_operandi=template_group["modus"],
                digital_evidence_available="Bank Statement, SMS Headers, Network Telemetry",
                account_compromised=acc_compromised,
                personal_info_exposed=pii_exposed,
                prior_complaint_indicator=random.choice([False, False, False, True]),
                predicted_category=analysis["predicted_category"],
                confidence=analysis["confidence"],
                prediction_confidence=analysis["confidence"],
                risk_score=analysis["risk_score"],
                risk_level=analysis["risk_level"],
                priority=priority,
                severity=sev,
                current_status=curr_status,
                status=curr_status,
                investigation_status=inv_status,
                assigned_officer=officer_name,
                assigned_officer_id=officer_id,
                threat_indicators=json.dumps(analysis["threat_indicators"]),
                reasons=json.dumps(analysis["reasons"]),
                recommended_actions=json.dumps(analysis["recommended_actions"]),
                created_at=complaint_dt,
                updated_at=complaint_dt
            )
            session.add(complaint)

            # 1. Risk Assessment Record
            breakdown = analysis.get("risk_breakdown", {})
            risk_rec = RiskAssessment(
                complaint_id=comp_id,
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
                created_at=complaint_dt
            )
            session.add(risk_rec)

            # 2. ML Prediction Record
            ml_rec = MLPrediction(
                complaint_id=comp_id,
                predicted_category=analysis["predicted_category"],
                confidence=analysis["confidence"],
                model_name=analysis["model_name"],
                model_version=analysis["model_version"],
                probabilities_json=json.dumps(analysis["class_probabilities"]),
                top_features_json=json.dumps(analysis.get("top_tokens", [])),
                created_at=complaint_dt
            )
            session.add(ml_rec)

            # 3. Threat Indicators Records
            for ind in analysis.get("threat_indicators", []):
                val = ind.get("raw_value") or ind.get("label", "")
                t_ind = ThreatIndicator(
                    complaint_id=comp_id,
                    indicator_value=val,
                    indicator_type=ind.get("indicator_type", ind.get("code", "KEYWORD")),
                    code=ind.get("code"),
                    label=ind.get("label"),
                    severity=ind.get("severity", "Medium"),
                    confidence=0.92,
                    source="Complaint Narrative NLP Extraction",
                    first_seen=incident_dt,
                    is_synthetic=True,
                    created_at=complaint_dt
                )
                session.add(t_ind)

            # 4. Investigation Case
            inv_rec = Investigation(
                case_number=f"INV-2026-{state_code}-{serial:06d}",
                complaint_id=comp_id,
                lead_analyst=officer_name,
                lead_analyst_id=officer_id,
                status=inv_status,
                priority=priority,
                escalation_level="Tier-2 Special Cyber Cell" if priority in ["High", "Critical"] else "Standard",
                opened_at=complaint_dt,
                closed_at=complaint_dt + timedelta(days=12) if curr_status == "Resolved" else None,
                summary=f"Incident registered at {station_name}. ML classification: {analysis['predicted_category']} with {analysis['risk_level']} risk score ({analysis['risk_score']}/100). {inv_status} initiated."
            )
            session.add(inv_rec)

            # 5. Investigation Notes
            note1 = InvestigationNote(
                complaint_id=comp_id,
                author_name=officer_name,
                author_role="Investigation Officer",
                note_type="Triage Note",
                content=f"Initial complaint verified at {station_name}. Complainant reported financial loss of ₹{loss:,}. Automated threat analysis flagged {len(analysis['threat_indicators'])} threat indicators.",
                status_change=curr_status,
                created_at=complaint_dt + timedelta(minutes=45)
            )
            session.add(note1)

            if curr_status in ["Under Review", "Investigating", "Resolved"]:
                note2 = InvestigationNote(
                    complaint_id=comp_id,
                    author_name=officer_name,
                    author_role="Lead Cyber Analyst",
                    note_type="Intermediary Requisition",
                    content=f"Dispatched Section 91 CrPC / Section 94 BNSS preservation notice to nodal officer of beneficiary bank ({vpa}). IPDR request generated for associated caller.",
                    status_change=curr_status,
                    created_at=complaint_dt + timedelta(hours=6)
                )
                session.add(note2)

            # 6. Evidence Items with SHA-256
            mock_hash_seed = f"{comp_id}_{loss}_{serial}".encode('utf-8')
            sha256_val = hashlib.sha256(mock_hash_seed).hexdigest()
            evd_rec = EvidenceItem(
                evidence_number=f"EVD-2026-{serial:06d}",
                complaint_id=comp_id,
                evidence_type="Bank Transaction Statement" if loss > 0 else "Incident Screenshot",
                description=f"Verified statement showing unauthorized debit of ₹{loss:,} with UTR reference {utr}.",
                file_name=f"statement_{comp_id.lower()}.pdf",
                file_hash_sha256=sha256_val,
                source="Complainant Document Verification",
                collected_by=officer_name,
                chain_of_custody_verified=True,
                created_at=complaint_dt + timedelta(minutes=30)
            )
            session.add(evd_rec)

            # 7. Timeline Events
            session.add(TimelineEvent(
                complaint_id=comp_id,
                event_type="COMPLAINT_RECEIVED",
                title="Complaint Lodged",
                description=f"Complaint registered via {complaint.complaint_channel} at {station_name}.",
                actor="Complainant / Citizen Portal",
                created_at=complaint_dt
            ))
            session.add(TimelineEvent(
                complaint_id=comp_id,
                event_type="ML_CLASSIFIED",
                title=f"AI Crime Type Classified: {analysis['predicted_category']}",
                description=f"Calibrated NLP model predicted '{analysis['predicted_category']}' with {analysis['confidence']}% confidence.",
                actor="Automated Classification Engine",
                created_at=complaint_dt + timedelta(minutes=2)
            ))
            session.add(TimelineEvent(
                complaint_id=comp_id,
                event_type="RISK_ASSESSED",
                title=f"Dynamic Risk Assessment: {analysis['risk_score']}/100 ({analysis['risk_level']})",
                description="Multi-factor risk engine calculated component weights across financial impact, category threat, and indicators.",
                actor="Dynamic Risk Engine",
                created_at=complaint_dt + timedelta(minutes=3)
            ))
            session.add(TimelineEvent(
                complaint_id=comp_id,
                event_type="ASSIGNED",
                title=f"Assigned to {officer_name}",
                description=f"Case assigned to jurisdictional investigator ({officer_id}).",
                actor="Triage Coordinator",
                created_at=complaint_dt + timedelta(minutes=20)
            ))

            # 8. High Risk / Critical Alert
            if analysis["risk_score"] >= 75:
                session.add(Alert(
                    alert_code=f"ALT-2026-{serial:06d}",
                    complaint_id=comp_id,
                    severity="CRITICAL",
                    title=f"CRITICAL CYBER THREAT: {analysis['predicted_category'].upper()}",
                    message=f"Case {comp_id} in {city_name}, {state_name} flagged Critical Risk ({analysis['risk_score']}/100). Impact ₹{loss:,}. Immediate triage mandatory.",
                    status="Unread",
                    created_at=complaint_dt + timedelta(minutes=5)
                ))

        print(f"[SEED] Successfully created {needed} synthetic complaints.")

def seed_master_data():
    """Seed default crime categories, users, locations, and knowledge docs."""
    from werkzeug.security import generate_password_hash
    with get_session() as session:
        # 1. Users
        if session.query(User).count() == 0:
            print("[SEED] Seeding default analyst and admin accounts...")
            users = [
                User(
                    email="admin@cybercrime.gov.in",
                    username="admin",
                    full_name="Dr. Rajeshwar Rao, IPS",
                    role="Administrator",
                    designation="Director General (Cyber Operations & I4C)",
                    state="National Headquarters (New Delhi)",
                    password_hash=generate_password_hash("Admin@2026"),
                    permissions=json.dumps(["all", "manage_users", "override_status", "view_audit_logs", "retrain_models"])
                ),
                User(
                    email="analyst.sharma@cybercrime.gov.in",
                    username="analyst_sharma",
                    full_name="Pooja Sharma",
                    role="Senior Analyst",
                    designation="Lead Intelligence Analyst",
                    state="Maharashtra (Cyber Cell Mumbai)",
                    password_hash=generate_password_hash("Analyst@2026"),
                    permissions=json.dumps(["analyze_complaints", "view_risk", "query_rag", "view_analytics", "export_reports", "assign_cases", "close_cases"])
                ),
                User(
                    email="io.patil@cybercrime.gov.in",
                    username="io_patil",
                    full_name="Inspector Anand Patil",
                    role="Analyst",
                    designation="Station House Officer (Cyber Crime PS)",
                    state="Karnataka (Bengaluru Cyber PS)",
                    password_hash=generate_password_hash("Officer@2026"),
                    permissions=json.dumps(["analyze_complaints", "view_cases", "add_notes", "upload_evidence"])
                ),
                User(
                    email="auditor.verma@cybercrime.gov.in",
                    username="auditor_verma",
                    full_name="Vikram Verma",
                    role="Viewer",
                    designation="State Compliance & Oversight Auditor",
                    state="Telangana (Hyderabad)",
                    password_hash=generate_password_hash("Viewer@2026"),
                    permissions=json.dumps(["view_dashboard", "view_complaints_readonly", "export_summary"])
                )
            ]
            session.add_all(users)

        # 2. Knowledge Documents metadata
        if session.query(KnowledgeDocument).count() == 0:
            kb_dir = os.path.join(os.path.dirname(__file__), 'knowledge_base')
            if os.path.exists(kb_dir):
                print("[SEED] Indexing knowledge base document metadata...")
                for fname in os.listdir(kb_dir):
                    if fname.endswith('.md'):
                        fpath = os.path.join(kb_dir, fname)
                        with open(fpath, 'r', encoding='utf-8') as f:
                            content = f.read()
                        
                        title_m = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
                        title = title_m.group(1).strip() if title_m else fname
                        
                        ref_m = re.search(r'\*\*Document Reference:\*\*\s*(.+)$', content, re.MULTILINE)
                        doc_ref = ref_m.group(1).strip() if ref_m else fname
                        
                        auth_m = re.search(r'\*\*(?:Issuing Authority|Source Authority|Jurisdiction):\*\*\s*(.+)$', content, re.MULTILINE)
                        auth = auth_m.group(1).strip() if auth_m else "National Cyber Intelligence Agency"

                        chunks = len(re.split(r'\n(?=#{2,3}\s+)', content))

                        doc = KnowledgeDocument(
                            doc_title=title,
                            doc_ref=doc_ref,
                            authority=auth,
                            filename=fname,
                            doc_type="Standard Operating Procedure" if "sop" in fname.lower() else "Advisory" if "cert" in fname.lower() else "Statutory Reference",
                            classification="Reference",
                            chunk_count=chunks
                        )
                        session.add(doc)

        # 3. Initial Audit Logs
        if session.query(AuditLog).count() == 0:
            print("[SEED] Seeding initial audit trail logs...")
            session.add(AuditLog(
                timestamp="29 Sep 2026, 09:30 AM",
                user_email="admin@cybercrime.gov.in",
                user_role="Administrator",
                action="SYSTEM_INIT",
                target_entity="Database",
                target_id="POSTGRESQL-INIT",
                details="Enterprise relational schema initialized and verified.",
                ip_address="127.0.0.1"
            ))
            session.add(AuditLog(
                timestamp="29 Sep 2026, 09:45 AM",
                user_email="analyst.sharma@cybercrime.gov.in",
                user_role="Senior Analyst",
                action="LOGIN",
                target_entity="Session",
                target_id="AUTH-002",
                details="Analyst authenticated via multi-factor authentication.",
                ip_address="192.168.1.42"
            ))

def align_existing_columns():
    """Ensure newly defined model columns exist in existing database tables."""
    columns_to_ensure = [
        ("audit_logs", "created_at", "TIMESTAMP"),
        ("complaints", "uuid", "VARCHAR(36)"),
        ("complaints", "title", "VARCHAR(255)"),
        ("complaints", "victim_type", "VARCHAR(32) DEFAULT 'Individual'"),
        ("complaints", "attack_vector", "VARCHAR(128)"),
        ("complaints", "assigned_officer_id", "VARCHAR(32)"),
        ("risk_assessments", "severity_factor", "INTEGER DEFAULT 0"),
        ("risk_assessments", "account_compromised_factor", "INTEGER DEFAULT 0"),
        ("risk_assessments", "pii_factor", "INTEGER DEFAULT 0"),
        ("risk_assessments", "threat_indicators_factor", "INTEGER DEFAULT 0")
    ]
    try:
        insp = inspect(engine)
        for tbl, col, ctype in columns_to_ensure:
            if insp.has_table(tbl):
                existing = [c["name"] for c in insp.get_columns(tbl)]
                if col not in existing:
                    with engine.connect() as conn:
                        conn.execute(text(f"ALTER TABLE {tbl} ADD COLUMN {col} {ctype}"))
                        conn.commit()
                        print(f"[SCHEMA] Added missing column {col} to {tbl}")
    except Exception as e:
        print(f"[SCHEMA ALIGNMENT NOTICE] {e}")

def init_db():
    """Initializes the database schema and seeds realistic data."""
    print(f"[DATABASE] Initializing database tables using SQLAlchemy engine ({CURRENT_DB_TYPE})...")
    Base.metadata.create_all(bind=engine)
    align_existing_columns()
    seed_master_data()

    # Automatic Seeding: Ensure at least 5,000 synthetic complaints exist on first startup
    try:
        with get_session() as session:
            count = session.query(Complaint).count()
        if count < 5000:
            print(f"[DATABASE SEED] Found {count} complaints (< 5,000). Triggering automatic 5,000 seed...")
            from seed_5000_complaints import seed_database_5000
            seed_database_5000(target_count=5000)
        else:
            print(f"[DATABASE SEED] Database already has {count} complaints (>= 5,000). Seeding confirmed.")
    except Exception as e:
        print(f"[DATABASE SEED ERROR] Error during auto-seeding: {e}")
        generate_synthetic_data(target_count=350)

    print(f"[DATABASE] Database ready ({CURRENT_DB_TYPE}).")


# Legacy compatibility function for raw sqlite3 connections
def get_db_connection():
    """Legacy helper returning a connection-like object or sqlite connection."""
    import sqlite3
    conn = sqlite3.connect(SQLITE_DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

if __name__ == '__main__':
    init_db()
    status = get_db_status()
    print("Database Status:", json.dumps(status, indent=2))
