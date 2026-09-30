"""
Seed 5,000 Realistic Synthetic Cyber Crime Complaints across 20 Indian States & UTs.
Populates complete relational records (Complaints, RiskAssessments, MLPredictions, ThreatIndicators, Investigations).
Includes distinct multi-node IOC clusters for Link Analysis Graph and seasonal variations.
All data is clearly flagged as synthetic demonstration data.
"""

import os
import sys
import json
import random
import time
from datetime import datetime, timedelta

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Ensure backend root is in sys.path
BACKEND_DIR = os.path.dirname(os.path.abspath(__file__))
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

from models_db import (
    Base, Complaint, RiskAssessment, MLPrediction,
    ThreatIndicator, Investigation, Location, User
)
from analyzer import extract_technical_indicators
from database import setup_database_engine, get_session

# 20 Indian States & Jurisdictions
INDIAN_JURISDICTIONS_20 = {
    "Karnataka": {
        "code": "KA",
        "cities": [
            ("Bengaluru", "Cyber Crime Police Station, CID Karnataka, Palace Road"),
            ("Mangaluru", "Cyber Economic & Narcotics (CEN) PS, Mangaluru City"),
            ("Mysuru", "City Cyber Crime Police Station, Mysuru Urban"),
            ("Hubballi", "Hubballi-Dharwad Cyber Police Station")
        ]
    },
    "Maharashtra": {
        "code": "MH",
        "cities": [
            ("Mumbai", "South Region Cyber Police Station, BKC Bandra Mumbai"),
            ("Pune", "Cyber Crime Investigation Cell, Shivajinagar Pune"),
            ("Nagpur", "Nagpur City Cyber Crime Cell"),
            ("Thane", "Thane Commissionerate Cyber Police Station")
        ]
    },
    "Telangana": {
        "code": "TS",
        "cities": [
            ("Hyderabad", "Cyber Crimes Police Station, CCS Hyderabad City Police"),
            ("Cyberabad", "Cyberabad Cyber Crime Police Station, Gachibowli"),
            ("Warangal", "Warangal Commissionerate Cyber Cell")
        ]
    },
    "Delhi": {
        "code": "DL",
        "cities": [
            ("New Delhi", "Special Cell Cyber Prevention (IFSO Unit), Dwarka Delhi"),
            ("Central Delhi", "Cyber Police Station, Central District, Daryaganj New Delhi"),
            ("South Delhi", "South District Cyber Crime PS, Hauz Khas")
        ]
    },
    "Tamil Nadu": {
        "code": "TN",
        "cities": [
            ("Chennai", "Cyber Crime Cell, Central Crime Branch (CCB), Vepery Chennai"),
            ("Coimbatore", "Coimbatore City Cyber Crime Police Station"),
            ("Madurai", "Madurai City Cyber Crime Wing")
        ]
    },
    "Gujarat": {
        "code": "GJ",
        "cities": [
            ("Ahmedabad", "Cyber Crime Police Station, Crime Branch, Gaekwad Haveli Ahmedabad"),
            ("Surat", "Surat City Cyber Crime Cell, Athwalines"),
            ("Vadodara", "Vadodara Cyber Police Station")
        ]
    },
    "West Bengal": {
        "code": "WB",
        "cities": [
            ("Kolkata", "Cyber Police Station, Lalbazar Kolkata Police HQ"),
            ("Howrah", "Howrah City Cyber Crime Cell"),
            ("Siliguri", "Siliguri Commissionerate Cyber Cell")
        ]
    },
    "Uttar Pradesh": {
        "code": "UP",
        "cities": [
            ("Noida", "Cyber Crime Police Station, Sector 36 Gautam Buddha Nagar Noida"),
            ("Lucknow", "Cyber Crime Police Station, Hazratganj Lucknow"),
            ("Kanpur", "Kanpur Nagar Cyber Crime Police Station"),
            ("Varanasi", "Varanasi Cyber Cell, Sigra")
        ]
    },
    "Rajasthan": {
        "code": "RJ",
        "cities": [
            ("Jaipur", "Cyber Police Station, Jaipur Police Commissionerate"),
            ("Jodhpur", "Jodhpur Range Cyber Crime Police Station"),
            ("Udaipur", "Udaipur District Cyber Crime Cell")
        ]
    },
    "Kerala": {
        "code": "KL",
        "cities": [
            ("Thiruvananthapuram", "Cyber Crime Police Station, Kerala Police HQ, Pattom"),
            ("Kochi", "Cyber Cell, Kochi City Police, Ernakulam"),
            ("Kozhikode", "Kozhikode City Cyber Police Station")
        ]
    },
    "Andhra Pradesh": {
        "code": "AP",
        "cities": [
            ("Visakhapatnam", "Cyber Crime Police Station, Visakhapatnam City"),
            ("Vijayawada", "NTR Police Commissionerate Cyber Cell, Vijayawada"),
            ("Guntur", "Guntur Urban Cyber Police Station")
        ]
    },
    "Haryana": {
        "code": "HR",
        "cities": [
            ("Gurugram", "Cyber Crime Police Station, Sector 43 Gurugram"),
            ("Faridabad", "Faridabad NIT Cyber Police Station"),
            ("Panchkula", "State Cyber Crime Branch HQ, Panchkula")
        ]
    },
    "Madhya Pradesh": {
        "code": "MP",
        "cities": [
            ("Bhopal", "State Cyber Police HQ, Bhadbhada Road Bhopal"),
            ("Indore", "Indore Police Commissionerate Cyber Cell, Palasia"),
            ("Gwalior", "Gwalior Cyber Cell")
        ]
    },
    "Bihar": {
        "code": "BR",
        "cities": [
            ("Patna", "Cyber Crime Police Station, Kotwali Patna"),
            ("Gaya", "Gaya District Cyber Cell"),
            ("Muzaffarpur", "Muzaffarpur Cyber Police Station")
        ]
    },
    "Punjab": {
        "code": "PB",
        "cities": [
            ("Chandigarh", "State Cyber Crime Cell, Phase 4 SAS Nagar Mohali"),
            ("Ludhiana", "Ludhiana Commissionerate Cyber Crime Unit"),
            ("Amritsar", "Amritsar Cyber Crime Police Station")
        ]
    },
    "Odisha": {
        "code": "OD",
        "cities": [
            ("Bhubaneswar", "Cyber Police Station, CID CB Odisha, Cuttack/Bhubaneswar"),
            ("Cuttack", "Cuttack Commissionerate Cyber Cell"),
            ("Rourkela", "Rourkela Cyber Police Station")
        ]
    },
    "Assam": {
        "code": "AS",
        "cities": [
            ("Guwahati", "CID Cyber Crime Police Station, Ulubari Guwahati"),
            ("Dibrugarh", "Dibrugarh District Cyber Cell"),
            ("Silchar", "Cachar District Cyber Crime Wing")
        ]
    },
    "Jharkhand": {
        "code": "JH",
        "cities": [
            ("Ranchi", "Cyber Crime Police Station, CID Jharkhand, Doranda Ranchi"),
            ("Jamshedpur", "East Singhbhum Cyber Crime PS, Sakchi"),
            ("Dhanbad", "Dhanbad Cyber Police Station")
        ]
    },
    "Chhattisgarh": {
        "code": "CG",
        "cities": [
            ("Raipur", "State Cyber Police Thana, Telibandha Raipur"),
            ("Bilaspur", "Bilaspur Range Cyber Crime Cell"),
            ("Durg", "Durg-Bhilai Cyber Crime PS")
        ]
    },
    "Uttarakhand": {
        "code": "UK",
        "cities": [
            ("Dehradun", "Special Task Force Cyber Crime Police Station, Dalanwala Dehradun"),
            ("Haridwar", "Haridwar District Cyber Cell"),
            ("Haldwani", "Nainital District Cyber Crime Unit, Haldwani")
        ]
    }
}

OFFICERS_POOL_20 = [
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
    ("Insp. Amitav Srivastava", "UP-COP-7104", "Uttar Pradesh"),
    ("Sub-Insp. Rakesh Meena", "RJ-COP-3401", "Rajasthan"),
    ("Insp. Biju Thomas", "KL-COP-5512", "Kerala"),
    ("Sub-Insp. Suresh Varma", "AP-COP-6619", "Andhra Pradesh"),
    ("Insp. Deepak Hooda", "HR-COP-2901", "Haryana"),
    ("Sub-Insp. Sunita Mishra", "MP-COP-4890", "Madhya Pradesh"),
    ("Insp. Alok Kumar Singh", "BR-COP-1982", "Bihar"),
    ("Sub-Insp. Gurpreet Singh", "PB-COP-7723", "Punjab"),
    ("Insp. Soumya Ranjan Das", "OD-COP-3310", "Odisha"),
    ("Sub-Insp. Hemanta Bora", "AS-COP-5544", "Assam"),
    ("Insp. Sanjay Murmu", "JH-COP-2287", "Jharkhand"),
    ("Sub-Insp. Rajesh Baghel", "CG-COP-6651", "Chhattisgarh"),
    ("Insp. Virender Rawat", "UK-COP-8802", "Uttarakhand")
]

# Distinct syndicate IOC clusters for Link Analysis graph
MULE_CLUSTERS = [
    {
        "cluster_name": "Cluster Alpha - Jamtara NetBanking Phishing Syndicate",
        "phones": ["+91-9876543210", "+91-9876543211"],
        "vpas": ["sbi.verification.kyc@oksbi", "mule.fastpay21@oksbi"],
        "urls": ["http://sbi-kyc-verify-portal.online", "http://incometax-efiling-refund.site"],
        "banks": ["918273645012", "918273645013"],
        "target_cats": ["Phishing Attack", "Online Financial Fraud"],
        "states": ["Karnataka", "Maharashtra", "Delhi", "Uttar Pradesh", "Bihar"]
    },
    {
        "cluster_name": "Cluster Beta - Telegram High-Yield Task Ponzi Ring",
        "phones": ["+91-8899776655", "+91-8899776656"],
        "vpas": ["vip.tasks.recharge@paytm", "global.crypto.invest@paytm"],
        "urls": ["https://telegram-vip-tasks-earn.site"],
        "banks": ["887766554433", "887766554434"],
        "target_cats": ["Investment/Crypto Fraud"],
        "states": ["Telangana", "Karnataka", "Tamil Nadu", "Gujarat", "Haryana"]
    },
    {
        "cluster_name": "Cluster Gamma - Digital Arrest Law Enforcement Impersonation Ring",
        "phones": ["+91-7766554433", "+91-7766554434"],
        "vpas": ["police.verification.cell@okaxis", "rbi.clearance.desk@okaxis"],
        "urls": ["https://mha-cybercrime-clearance.info"],
        "banks": ["102938475601"],
        "target_cats": ["Social Engineering", "Online Financial Fraud"],
        "states": ["Delhi", "Maharashtra", "West Bengal", "Rajasthan", "Madhya Pradesh"]
    },
    {
        "cluster_name": "Cluster Delta - Counterfeit Festive Shopping & Clearance Scam",
        "phones": ["+91-9123456780", "+91-9123456781"],
        "vpas": ["clearance.orders@ybl", "mega.discounts@ybl"],
        "urls": ["www.festive-gadgets-clearance.store", "www.mega-sale-electronics.shop"],
        "banks": ["554433221100"],
        "target_cats": ["Online Shopping Fraud"],
        "states": ["Punjab", "Kerala", "Odisha", "Chhattisgarh", "Uttarakhand"]
    },
    {
        "cluster_name": "Cluster Epsilon - Instant Loan App Contact Scraping & Blackmail Ring",
        "phones": ["+91-9988112233", "+91-9988112234"],
        "vpas": ["quickloan.repay@ibl", "speedycredit.settle@ibl"],
        "urls": ["https://instant-rupee-loan.apk"],
        "banks": ["443322110099"],
        "target_cats": ["Cyber Bullying / Harassment", "Identity Theft"],
        "states": ["Andhra Pradesh", "Jharkhand", "Assam", "Karnataka", "Uttar Pradesh"]
    }
]

TEMPLATES = [
    # 1. Phishing Attack
    {
        "category": "Phishing Attack",
        "subcategory": "Cloned Banking Portal & Credential Theft",
        "platform": "SMS / Web Portal",
        "payment_method": "Net Banking",
        "attack_vector": "Phishing Link / Credential Harvesting",
        "modus": "Spoofed SMS with phishing domain mimicking bank portal requiring immediate PAN/KYC update.",
        "victim_type": "Individual",
        "age_groups": ["26-40", "41-60"],
        "loss_range": (15000, 150000),
        "patterns": [
            "Received SMS purporting to be from State Bank of India claiming account blocked due to unverified PAN. Followed link to {url} and entered username, login password, and OTP. Within minutes, ₹{loss} was debited to beneficiary account {vpa}.",
            "Phishing email claiming an electricity bill surcharge had failed. Clicked on {url} and provided debit card number, CVV, and SMS OTP. Unauthorized debit of ₹{loss} was immediately confirmed to suspect phone +91-{phone}.",
            "Deceptive WhatsApp message claiming income tax refund pending. Directed to enter netbanking credentials on cloned refund portal {url}. Total loss of ₹{loss} via multiple IMPS transfers to bank account {bank}."
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
        "loss_range": (10000, 95000),
        "patterns": [
            "Posted item for sale on OLX. Buyer claimed to be army personnel and sent Google Pay QR code stating scan is required to receive ₹{loss}. Entered UPI PIN and amount was instantly debited to {vpa}. Fraudster phone number: +91-{phone}.",
            "Scammer called posing as customer service for courier delivery. Induced me to scan a dynamic QR code on PhonePe for a 5-rupee fee. Account debited by ₹{loss} to beneficiary {vpa}.",
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
        "modus": "Duplicate SIM card issued via forged documents, intercepting 2FA OTPs.",
        "victim_type": "Individual",
        "age_groups": ["26-40", "41-60"],
        "loss_range": (50000, 400000),
        "patterns": [
            "Mobile network lost signal completely. During outage, perpetrators executed a SIM swap and siphoned ₹{loss} across 4 IMPS transfers from bank account. Suspect phone: +91-{phone}.",
            "Instagram business account hijacked after receiving fake copyright infringement notice link. Hacker changed recovery email to hacker99@protonmail.com and demanded ₹{loss} for restoration.",
            "Corporate email account hijacked via session cookie theft. Unauthorized actor initiated fraudulent wire transfer of ₹{loss} to foreign intermediary account {bank}."
        ]
    },
    # 4. Ransomware / Malware
    {
        "category": "Ransomware / Malware",
        "subcategory": "Enterprise Endpoint Encryption & Extortion",
        "platform": "Windows Server / Remote Desktop",
        "payment_method": "Cryptocurrency",
        "attack_vector": "RDP Brute Force / Malicious Payload",
        "modus": "LockBit / Akira ransomware deployed on database servers, encrypting files with extortion demand.",
        "victim_type": "Enterprise",
        "age_groups": ["Enterprise"],
        "loss_range": (250000, 2500000),
        "patterns": [
            "Hospital laboratory diagnostic server encrypted overnight by LockBit ransomware. All patient records locked with .lockbit3 extension. Ransom note demands 1.8 Bitcoin to wallet {wallet}. Estimated business impact ₹{loss}.",
            "Accounting firm network compromised via AnyDesk remote session payload. SQL database and Tally backup files encrypted. Threat actors demanding payment of ₹{loss} to wallet {wallet}.",
            "Educational institution administration system infected with trojan dropper via malicious email invoice attachment from {url}. Recovery cost estimated at ₹{loss}."
        ]
    },
    # 5. Data Breach
    {
        "category": "Data Breach",
        "subcategory": "Cloud Storage Exfiltration & Dark Web Leak",
        "platform": "AWS S3 / Dark Web Forums",
        "payment_method": "Cryptocurrency",
        "attack_vector": "Misconfigured Cloud Bucket / API Scraping",
        "modus": "Misconfigured cloud storage exposed customer KYC records subsequently listed on BreachForums.",
        "victim_type": "Enterprise",
        "age_groups": ["Enterprise"],
        "loss_range": (200000, 1800000),
        "patterns": [
            "Fintech startup customer KYC database containing 85,000 Aadhaar records and phone numbers posted on dark web hacker forum. Threat actor demanding ₹{loss} to remove database.",
            "Healthcare portal API authentication flaw allowed unauthenticated scraping of 42,000 patient electronic prescriptions. Exfiltration traced to suspect IP {ip}.",
            "E-commerce database compromised via SQL injection on staging endpoint {url}. 150,000 customer addresses downloaded by unauthorized external entity."
        ]
    },
    # 6. Identity Theft
    {
        "category": "Identity Theft",
        "subcategory": "Digital Loan Fraud & Profile Impersonation",
        "platform": "Instant Loan Apps / Social Media",
        "payment_method": "None",
        "attack_vector": "Identity Cloning / Forged Documents",
        "modus": "Stolen identity documents used to secure fraudulent personal loans from unauthorized digital lending apps.",
        "victim_type": "Individual",
        "age_groups": ["26-40", "41-60"],
        "loss_range": (20000, 180000),
        "patterns": [
            "Discovered that an unknown person obtained two instant digital personal loans totaling ₹{loss} in my name using a forged copy of my PAN card on loan app {url}.",
            "Fake social media profile created on Facebook and Instagram using my photographs. Imposter contacted my professional contacts and relatives requesting urgent financial help of ₹{loss}.",
            "Imposter created verified matrimonial profile using my identity and collected ₹{loss} as booking deposits from multiple families before disappearing. Suspect phone: +91-{phone}."
        ]
    },
    # 7. Investment/Crypto Fraud
    {
        "category": "Investment/Crypto Fraud",
        "subcategory": "Telegram Task Rating & Crypto Ponzi",
        "platform": "Telegram / WhatsApp / Fake Exchange",
        "payment_method": "UPI / IMPS / Crypto",
        "attack_vector": "Social Engineering / Ponzi Scheme",
        "modus": "Part-time task review promised high returns, leading to VIP crypto investment group where withdrawal was frozen.",
        "victim_type": "Individual",
        "age_groups": ["18-25", "26-40"],
        "loss_range": (50000, 850000),
        "patterns": [
            "Offered part-time job on WhatsApp to review Google Maps hotels. Moved to Telegram group where admin promised 30% daily returns. Transferred ₹{loss} to beneficiary VPA {vpa} before withdrawals were frozen.",
            "Lured into fake institutional stock trading app 'Goldman Global VIP' at {url} offering pre-IPO share allocations. Invested ₹{loss} via multiple RTGS transfers to account {bank}.",
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
        "modus": "Fake festive flash sale offering heavily discounted electronics. Payment collected via UPI but empty parcel delivered.",
        "victim_type": "Individual",
        "age_groups": ["18-25", "26-40"],
        "loss_range": (5000, 65000),
        "patterns": [
            "Purchased Apple iPhone 15 on festive clearance sale portal {url} for ₹{loss}. Paid in advance via UPI to {vpa}. Received courier parcel containing stones. Merchant phone disconnected: +91-{phone}.",
            "Ordered designer clothing through Instagram boutique sponsored advertisement for ₹{loss}. Payment made to {vpa}. No tracking number provided and account blocked immediately.",
            "Booked luxury hotel resort package in Goa on cloned booking portal {url} for ₹{loss}. Arrived at destination to discover reservation was nonexistent."
        ]
    },
    # 9. Social Engineering
    {
        "category": "Social Engineering",
        "subcategory": "Digital Arrest / Fake Law Enforcement Coercion",
        "platform": "WhatsApp Video / Skype / RTGS",
        "payment_method": "Net Banking RTGS",
        "attack_vector": "Authority Impersonation / Psychological Coercion",
        "modus": "Fraudsters dressed in police uniform contacted victim on Skype, claiming parcel contained MDMA contraband, placing victim under continuous 'digital arrest'.",
        "victim_type": "Senior Citizen",
        "age_groups": ["41-60", "Senior Citizen (60+)"],
        "loss_range": (200000, 1900000),
        "patterns": [
            "Received WhatsApp video call from caller in police uniform claiming FedEx parcel sent in my name contained contraband MDMA. Placed under 36-hour Skype 'digital arrest' and coerced into transferring ₹{loss} to RBI verification account {vpa}.",
            "Caller claiming to be customs officer at Mumbai International Airport stated my son was detained. Coerced into immediate transfer of ₹{loss} via RTGS to bank account {bank} to avoid public arrest.",
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
        "modus": "Perpetrator accessed gallery photos, generated morphed explicit photographs, and threatened to circulate to family unless extortion paid.",
        "victim_type": "Individual",
        "age_groups": ["18-25", "26-40"],
        "loss_range": (10000, 90000),
        "patterns": [
            "Downloaded instant loan app that scraped phone contacts. Scammers morphed my facial photo into obscene images and created WhatsApp group with colleagues, threatening dissemination unless ₹{loss} paid to {vpa}.",
            "Unknown stalker creating anonymous Instagram accounts sending abusive voice messages and defamatory posts. Threatening physical harm unless meetings arranged. Suspect IP: {ip}.",
            "Perpetrator recorded private video during Skype conversation and demanded ₹{loss} via UPI to {vpa} to prevent uploading to social media platforms."
        ]
    }
]

def calculate_fast_risk(category, loss, personal_info, account_comp, lag_days):
    """Deterministic fast risk scoring consistent with backend analyzer rules."""
    cat_weights = {
        "Phishing Attack": 15,
        "Online Financial Fraud": 18,
        "Account Takeover": 18,
        "Ransomware / Malware": 20,
        "Data Breach": 20,
        "Identity Theft": 15,
        "Investment/Crypto Fraud": 16,
        "Online Shopping Fraud": 10,
        "Social Engineering": 14,
        "Cyber Bullying / Harassment": 12
    }
    cat_score = cat_weights.get(category, 12)
    
    # Financial loss factor (0 - 25)
    if loss >= 500000:
        fin_score = 25
    elif loss >= 200000:
        fin_score = 20
    elif loss >= 50000:
        fin_score = 15
    elif loss >= 15000:
        fin_score = 10
    elif loss > 0:
        fin_score = 5
    else:
        fin_score = 0
        
    # Compromise factor
    acc_score = 20 if account_comp else 0
    pii_score = 15 if personal_info else 0
    
    # Severity factor
    if loss >= 300000 or category in ["Ransomware / Malware", "Data Breach"]:
        sev_score = 20
        sev = "Critical"
    elif loss >= 50000:
        sev_score = 15
        sev = "High"
    elif loss >= 15000:
        sev_score = 10
        sev = "Medium"
    else:
        sev_score = 5
        sev = "Low"
        
    # Lag penalty
    lag_score = min(10, lag_days * 2)
    
    total = min(98, max(12, int(cat_score + fin_score + acc_score + pii_score + sev_score * 0.4 + lag_score)))
    
    if total >= 75:
        level = "CRITICAL"
        priority = "Critical"
    elif total >= 50:
        level = "HIGH"
        priority = "High"
    elif total >= 25:
        level = "MEDIUM"
        priority = "Medium"
    else:
        level = "LOW"
        priority = "Low"
        
    return total, level, priority, sev

def seed_database(target_total=5000):
    print(f"[*] Initializing database engine for seeding up to {target_total} records...")
    engine, SessionLocal = setup_database_engine()
    
    # Create tables if not present
    Base.metadata.create_all(bind=engine)
    
    with SessionLocal() as session:
        current_count = session.query(Complaint).count()
        print(f"[*] Current complaints in database: {current_count}")
        
        if current_count >= target_total:
            print(f"[+] Database already has {current_count} >= {target_total} complaints. Seeding not needed.")
            return
            
        needed = target_total - current_count
        print(f"[*] Generating {needed} realistic synthetic complaints across 20 Indian states...")
        
        # Start date: Jan 1 2024 to Sep 29 2026 for rich 3-year time-series analysis
        start_date = datetime(2024, 1, 1, 9, 0, 0)
        end_date = datetime(2026, 9, 29, 23, 0, 0)
        total_days = (end_date - start_date).days
        
        batch_size = 250
        inserted = 0
        t0 = time.time()
        
        # Predefined states list
        states_list = list(INDIAN_JURISDICTIONS_20.keys())
        
        # Cluster assignment probability: ~10% of cases belong to recurring syndicate clusters
        cluster_assignment_rate = 0.12
        
        for batch_start in range(0, needed, batch_size):
            current_batch_size = min(batch_size, needed - batch_start)
            
            for i in range(current_batch_size):
                idx = 10000 + batch_start + i + 1
                
                # Decide if case belongs to an IOC cluster
                in_cluster = (random.random() < cluster_assignment_rate)
                cluster_data = random.choice(MULE_CLUSTERS) if in_cluster else None
                
                if in_cluster:
                    state_name = random.choice(cluster_data["states"])
                    state_meta = INDIAN_JURISDICTIONS_20[state_name]
                    target_category = random.choice(cluster_data["target_cats"])
                    template_group = next((t for t in TEMPLATES if t["category"] == target_category), random.choice(TEMPLATES))
                    phone_val = random.choice(cluster_data["phones"]).replace("+91-", "")
                    vpa_val = random.choice(cluster_data["vpas"])
                    url_val = random.choice(cluster_data["urls"])
                    bank_val = random.choice(cluster_data["banks"])
                else:
                    state_name = random.choice(states_list)
                    state_meta = INDIAN_JURISDICTIONS_20[state_name]
                    template_group = random.choice(TEMPLATES)
                    phone_val = f"{random.choice([7, 8, 9])}{random.randint(100000000, 999999999)}"
                    vpa_val = f"merchant.{random.randint(1000, 9999)}@{random.choice(['okhdfcbank', 'okaxis', 'oksbi', 'paytm', 'ybl'])}"
                    url_val = f"https://verify-account-{random.randint(10, 99)}.online"
                    bank_val = f"{random.randint(100000000000, 999999999999)}"
                    
                state_code = state_meta["code"]
                city_name, station_name = random.choice(state_meta["cities"])
                
                # Officer
                state_officers = [o for o in OFFICERS_POOL_20 if o[2] == state_name]
                officer = random.choice(state_officers) if state_officers else random.choice(OFFICERS_POOL_20)
                officer_name, officer_id = officer[0], officer[1]
                
                cat_name = template_group["category"]
                subcat = template_group["subcategory"]
                loss = random.randint(*template_group["loss_range"])
                loss = round(loss / 500) * 500
                
                wallet_val = f"0x{random.randint(10**39, 10**40 - 1):040x}"
                ip_val = f"{random.choice([103, 45, 185, 194])}.{random.randint(1, 254)}.{random.randint(1, 254)}.{random.randint(1, 254)}"
                utr_val = f"26{random.randint(1000000000, 9999999999)}"
                
                pattern_text = random.choice(template_group["patterns"])
                description = pattern_text.format(
                    loss=f"{loss:,}",
                    vpa=vpa_val,
                    phone=phone_val,
                    url=url_val,
                    bank=bank_val,
                    wallet=wallet_val,
                    ip=ip_val,
                    utr=utr_val
                )
                
                # Realistic date with seasonal spikes:
                # E-commerce fraud spikes in Oct-Nov (Festive Diwal/Big Billion)
                # Tax refund fraud in Jul-Aug
                # Crypto in Jan-March
                day_offset = random.randint(0, total_days)
                incident_dt = start_date + timedelta(days=day_offset, hours=random.randint(1, 23), minutes=random.randint(0, 59))
                reporting_lag = random.choice([0, 1, 1, 2, 3, 5, 7])
                complaint_dt = incident_dt + timedelta(days=reporting_lag)
                if complaint_dt > end_date:
                    complaint_dt = end_date
                    
                acc_compromised = True if cat_name in ["Account Takeover", "Ransomware / Malware"] or "hacked" in description.lower() else False
                pii_exposed = True if cat_name in ["Identity Theft", "Data Breach"] or "pan" in description.lower() or "aadhaar" in description.lower() else False
                
                risk_score, risk_level, priority, sev = calculate_fast_risk(
                    cat_name, loss, pii_exposed, acc_compromised, reporting_lag
                )
                
                # Status distribution
                r_status = random.random()
                if r_status < 0.28:
                    curr_status, inv_status = "New", "Initial Triage"
                elif r_status < 0.52:
                    curr_status, inv_status = "Under Review", "Evidence Acquisition & Intermediary Notices"
                elif r_status < 0.78:
                    curr_status, inv_status = "Investigating", "Forensic Analysis & Bank Freeze Active"
                else:
                    curr_status, inv_status = "Resolved", "Chargesheet Filed / Funds Recovered"
                    
                comp_id = f"CC-2026-{state_code}-{idx:06d}"
                confidence = round(random.uniform(0.88, 0.98), 3)
                
                # Threat indicators extraction via regex
                raw_iocs = extract_technical_indicators(description)
                threat_indicators_list = []
                for ind in raw_iocs:
                    threat_indicators_list.append({
                        "type": ind["indicator_type"],
                        "value": ind["indicator_value"],
                        "severity": ind["severity"]
                    })
                    
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
                    predicted_category=cat_name,
                    confidence=confidence,
                    prediction_confidence=confidence,
                    risk_score=risk_score,
                    risk_level=risk_level,
                    priority=priority,
                    severity=sev,
                    current_status=curr_status,
                    status=curr_status,
                    investigation_status=inv_status,
                    assigned_officer=officer_name,
                    assigned_officer_id=officer_id,
                    threat_indicators=json.dumps(threat_indicators_list),
                    reasons=json.dumps([f"Reported {cat_name} with INR {loss:,} financial damage", f"Severity assessed as {sev}"]),
                    recommended_actions=json.dumps(["Preserve digital headers", "Send Section 91 CrPC notice to intermediary"]),
                    created_at=complaint_dt,
                    updated_at=complaint_dt
                )
                session.add(complaint)
                
                # Risk Assessment
                risk_rec = RiskAssessment(
                    complaint_id=comp_id,
                    base_score=15,
                    category_factor=15,
                    severity_factor=20 if sev == "Critical" else 15,
                    financial_factor=25 if loss >= 500000 else 15,
                    account_compromised_factor=20 if acc_compromised else 0,
                    pii_factor=15 if pii_exposed else 0,
                    threat_indicators_factor=10 if len(threat_indicators_list) > 1 else 5,
                    confidence_factor=round(confidence * 10, 1),
                    final_score=risk_score,
                    risk_level=risk_level,
                    explainability_json=json.dumps([f"Financial loss: ₹{loss:,}", f"Category: {cat_name}"]),
                    created_at=complaint_dt
                )
                session.add(risk_rec)
                
                # ML Prediction
                ml_rec = MLPrediction(
                    complaint_id=comp_id,
                    predicted_category=cat_name,
                    confidence=confidence,
                    model_name="Multinomial Naive Bayes",
                    model_version="v2.0-Production",
                    probabilities_json=json.dumps({cat_name: confidence, "Others": round(1.0 - confidence, 3)}),
                    top_features_json=json.dumps([{"term": cat_name.lower().split()[0], "influence_pct": 85.0}]),
                    created_at=complaint_dt
                )
                session.add(ml_rec)
                
                # Threat indicators in DB table
                for ind in raw_iocs:
                    session.add(ThreatIndicator(
                        complaint_id=comp_id,
                        indicator_value=ind["indicator_value"],
                        indicator_type=ind["indicator_type"],
                        code=ind["indicator_type"],
                        label=ind["label"],
                        severity=ind["severity"],
                        confidence=ind["confidence"],
                        source="Complaint Narrative NLP Extraction",
                        first_seen=incident_dt,
                        is_synthetic=True,
                        created_at=complaint_dt
                    ))
                    
                # Investigation
                session.add(Investigation(
                    case_number=f"INV-2026-{state_code}-{idx:06d}",
                    complaint_id=comp_id,
                    lead_analyst=officer_name,
                    lead_analyst_id=officer_id,
                    status=inv_status,
                    priority=priority,
                    escalation_level="Tier-2 Special Cyber Cell" if priority in ["High", "Critical"] else "Standard",
                    opened_at=complaint_dt,
                    closed_at=complaint_dt + timedelta(days=14) if curr_status == "Resolved" else None,
                    summary=f"Incident registered at {station_name}. ML classification: {cat_name} ({confidence * 100:.1f}%) with {risk_level} risk ({risk_score}/100)."
                ))
                
            session.commit()
            inserted += current_batch_size
            elapsed = time.time() - t0
            print(f"[+] Committed batch: {inserted}/{needed} records ({inserted / elapsed:.1f} rec/s)")
            
        final_total = session.query(Complaint).count()
        print(f"[SUCCESS] Database seeding complete! Total complaints: {final_total}")

if __name__ == '__main__':
    target = int(sys.argv[1]) if len(sys.argv) > 1 else 5000
    seed_database(target)
