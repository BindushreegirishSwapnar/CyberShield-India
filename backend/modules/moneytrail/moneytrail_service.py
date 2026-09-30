"""
Money Trail Service - Multi-Hop Fund Flow, Freeze Priority Scoring & Statutory Notice Generation
Visualizes complex money dispersion through mule networks, ranks accounts by freeze priority,
and produces statutory Section 94 BNSS / Section 79(3)(b) IT Act bank freeze orders.
"""

import time
import hashlib
from datetime import datetime
from database import get_session
from models_db import Complaint

class MoneyTrailService:
    def get_fund_trail(self, case_id: str = None):
        """
        Retrieves or simulates a detailed multi-hop money flow for an active investigation.
        """
        # Fetch case from DB if available
        complaint = None
        if case_id:
            try:
                with get_session() as session:
                    complaint = session.query(Complaint).filter_by(complaint_id=case_id).first()
            except Exception as e:
                print("DB fetch error in money trail:", e)

        base_amount = float(complaint.amount if complaint and complaint.amount else 450000.0)
        victim_name = getattr(complaint, 'victim_name', 'Rahul S. Sharma') or 'Rahul S. Sharma'
        victim_bank = getattr(complaint, 'suspect_bank', 'HDFC Bank') or 'State Bank of India'
        category = getattr(complaint, 'category', 'Online Financial Fraud') or 'Online Financial Fraud'

        # Multi-Hop Structure
        # Victim -> Layer 1 (2 nodes) -> Layer 2 (3 nodes) -> Layer 3 Cash-out (2 nodes)
        nodes = [
            {
                "id": "VICTIM_SRC",
                "label": f"Victim Account ({victim_bank})",
                "holder": victim_name,
                "account_no": "XX9812",
                "ifsc": "HDFC0000123",
                "layer": 0,
                "type": "victim",
                "amount": base_amount,
                "status": "debited"
            },
            # Layer 1
            {
                "id": "MULE_L1_A",
                "label": "Mule L1: Canara Bank (Bengaluru)",
                "holder": "Sunil V. Patil (Suspected Mule)",
                "account_no": "104928172901",
                "ifsc": "CNRB0001049",
                "bank": "Canara Bank",
                "layer": 1,
                "type": "mule",
                "initial_amount": round(base_amount * 0.60, 2),
                "current_balance": round(base_amount * 0.45, 2),
                "status": "draining",
                "est_drain_time_mins": 35,
                "jurisdiction": "Karnataka",
                "freeze_priority_score": 94
            },
            {
                "id": "MULE_L1_B",
                "label": "Mule L1: Paytm Payments Bank (Noida)",
                "holder": "M/s QuickPay Retail Enterprise",
                "account_no": "919876543210",
                "ifsc": "PYTM0123456",
                "bank": "Paytm Payments Bank",
                "layer": 1,
                "type": "wallet",
                "initial_amount": round(base_amount * 0.40, 2),
                "current_balance": round(base_amount * 0.20, 2),
                "status": "draining",
                "est_drain_time_mins": 25,
                "jurisdiction": "Uttar Pradesh",
                "freeze_priority_score": 88
            },
            # Layer 2
            {
                "id": "MULE_L2_A",
                "label": "Mule L2: Federal Bank (Ernakulam)",
                "holder": "Arun Kumar G. (Layer 2 Mule)",
                "account_no": "194820194820",
                "ifsc": "FDRL0001948",
                "bank": "Federal Bank",
                "layer": 2,
                "type": "mule",
                "initial_amount": round(base_amount * 0.30, 2),
                "current_balance": round(base_amount * 0.25, 2),
                "status": "urgent",
                "est_drain_time_mins": 55,
                "jurisdiction": "Kerala",
                "freeze_priority_score": 79
            },
            {
                "id": "MULE_L2_B",
                "label": "Mule L2: AU Small Finance Bank (Jaipur)",
                "holder": "Devendra Singh (Layer 2 Mule)",
                "account_no": "210491829104",
                "ifsc": "AUBL0002104",
                "bank": "AU Small Finance Bank",
                "layer": 2,
                "type": "mule",
                "initial_amount": round(base_amount * 0.20, 2),
                "current_balance": round(base_amount * 0.15, 2),
                "status": "urgent",
                "est_drain_time_mins": 45,
                "jurisdiction": "Rajasthan",
                "freeze_priority_score": 76
            },
            # Layer 3 (Endpoints / Cash-out)
            {
                "id": "ENDPOINT_CRYPTO",
                "label": "Crypto Exchange (WazirX USDT Vault)",
                "holder": "Wallet 0x71A...9F2B",
                "account_no": "0x71A89D2F...",
                "ifsc": "N/A (Virtual Asset Intermediary)",
                "bank": "WazirX / Zanmai Labs",
                "layer": 3,
                "type": "crypto",
                "initial_amount": round(base_amount * 0.25, 2),
                "current_balance": round(base_amount * 0.25, 2),
                "status": "withdrawn",
                "est_drain_time_mins": 10,
                "jurisdiction": "Offshore/VDA",
                "freeze_priority_score": 62
            },
            {
                "id": "ENDPOINT_ATM",
                "label": "ATM Micro-Withdrawals (Jamtara/Nuh Hub)",
                "holder": "Multiple Debit Card Cash Withdrawals",
                "account_no": "ATM Fleet POS",
                "ifsc": "N/A (Cash Dispersal)",
                "bank": "Multiple White-Label ATMs",
                "layer": 3,
                "type": "cash_out",
                "initial_amount": round(base_amount * 0.15, 2),
                "current_balance": 0.0,
                "status": "withdrawn",
                "est_drain_time_mins": 0,
                "jurisdiction": "Jharkhand/Haryana",
                "freeze_priority_score": 10
            }
        ]

        # Flow links for Sankey / Flow diagram
        links = [
            {"source": "VICTIM_SRC", "target": "MULE_L1_A", "value": round(base_amount * 0.60, 2)},
            {"source": "VICTIM_SRC", "target": "MULE_L1_B", "value": round(base_amount * 0.40, 2)},
            {"source": "MULE_L1_A", "target": "MULE_L2_A", "value": round(base_amount * 0.35, 2)},
            {"source": "MULE_L1_A", "target": "ENDPOINT_ATM", "value": round(base_amount * 0.15, 2)},
            {"source": "MULE_L1_B", "target": "MULE_L2_B", "value": round(base_amount * 0.20, 2)},
            {"source": "MULE_L1_B", "target": "ENDPOINT_CRYPTO", "value": round(base_amount * 0.20, 2)},
            {"source": "MULE_L2_A", "target": "ENDPOINT_CRYPTO", "value": round(base_amount * 0.05, 2)}
        ]

        # Freeze priority ranking (Only actionable mule accounts)
        actionable = [n for n in nodes if n["type"] in ("mule", "wallet") and n["current_balance"] > 0]
        actionable.sort(key=lambda x: x["freeze_priority_score"], reverse=True)

        return {
            "case_id": case_id or "CR-2026-98214",
            "total_fraud_amount": base_amount,
            "category": category,
            "victim_name": victim_name,
            "nodes": nodes,
            "links": links,
            "freeze_priority_ranking": actionable,
            "summary": {
                "total_layers": 3,
                "total_mule_nodes": 4,
                "currently_recoverable_inr": sum(n["current_balance"] for n in actionable),
                "percent_recoverable": round((sum(n["current_balance"] for n in actionable) / base_amount) * 100, 1),
                "top_freeze_target": actionable[0]["label"] if actionable else "N/A"
            },
            "is_synthetic": True
        }

    def simulate_time_dispersion(self, case_id: str, minutes_elapsed: int):
        """
        Simulates dynamic fund drainage as minutes tick away in the Golden Hour.
        """
        base = self.get_fund_trail(case_id)
        total = base["total_fraud_amount"]
        mins = max(0, min(180, minutes_elapsed))

        # Dynamic decay factor
        # at 0 min: 100% in Layer 1
        # at 45 min: 40% in L1, 35% in L2, 25% cash-out
        # at 120 min: 0% in L1, 20% in L2, 80% cash-out
        l1_pct = max(0.0, 1.0 - (mins / 50.0))
        l2_pct = max(0.0, min(0.6, (mins / 40.0) * (1.0 - (mins / 130.0))))
        cashout_pct = max(0.0, min(1.0, 1.0 - (l1_pct + l2_pct)))

        recoverable_amount = round(total * (l1_pct + l2_pct), 2)
        recoverable_pct = round((recoverable_amount / total) * 100, 1)

        return {
            "case_id": case_id,
            "minutes_elapsed": mins,
            "total_amount": total,
            "recoverable_amount": recoverable_amount,
            "recoverable_percent": recoverable_pct,
            "drain_status": "GOLDEN_HOUR_ACTIVE" if mins <= 120 else "CRITICAL_DRAIN",
            "layer_distribution": {
                "layer_1_balance": round(total * l1_pct * 0.6, 2),
                "layer_2_balance": round(total * l2_pct, 2),
                "cashed_out": round(total * cashout_pct, 2)
            },
            "recommendation": (
                "IMMEDIATE FREEZE: Call Nodal Officer at Canara Bank directly under Sec 94 BNSS."
                if mins < 45 else
                "EXPEDITE INTERDICTION: Funds migrating to Layer 2 and Crypto VDA gateways."
                if mins < 120 else
                "SECONDARY RECOVERY: Subpoena crypto wallet KYC and White-Label ATM logs."
            ),
            "is_synthetic": True
        }

    def generate_statutory_notice(self, case_id: str, mule_account: str, bank_name: str, officer_name: str, badge_no: str):
        """
        Generates formal Section 94 BNSS (formerly Sec 91 CrPC) bank freeze order text.
        """
        timestamp = datetime.now().strftime("%d-%m-%Y %H:%M:%S")
        order_ref = f"LE-BNSS94-{int(time.time())}"
        hash_input = f"{order_ref}:{case_id}:{mule_account}:{officer_name}:{timestamp}"
        digital_seal = hashlib.sha256(hash_input.encode()).hexdigest()

        notice_text = f"""
GOVERNMENT OF INDIA
NATIONAL CYBER CRIME INVESTIGATION WING (I4C)
OFFICE OF THE SUPERINTENDENT OF POLICE / CYBER CRIME CELL

STATUTORY EMERGENCY REQUISITION NOTICE UNDER SECTION 94 BNSS 2023
(READ WITH SECTION 79(3)(b) OF THE INFORMATION TECHNOLOGY ACT, 2000)

Order Reference: {order_ref}
Date & Time of Issue: {timestamp}
Jurisdictional Police Station: Central Cyber Crime Police Station, Bengaluru
Crime FIR / Complaint ID: {case_id}

TO:
The Principal Nodal Officer / Head of Fraud Risk Management (FRM)
{bank_name}, Operations & Compliance Division

SUBJECT: IMMEDIATE DEBIT-FREEZE MANDATE & REQUISITION OF ACCOUNT STATEMENT

Whereas an investigation into a cognizable cyber financial fraud involving reported loss of funds has been initiated pursuant to Section 66D of the Information Technology Act and relevant provisions of the Bharatiya Nyaya Sanhita (BNS) 2023;

And whereas preliminary electronic transaction flow intelligence reveals that fraudulent proceeds were remitted directly into beneficiary account:

   BENEFICIARY ACCOUNT NUMBER: {mule_account}
   DESTINATION INSTITUTION: {bank_name}
   TRANSACTION TRAIL: Layer 1 / Mule Dispersal Node

NOW THEREFORE, in exercise of powers conferred under Section 94 of the Bharatiya Nagarik Suraksha Sanhita (BNSS), 2023:

1. You are hereby DIRECTED to place an IMMEDIATE DEBIT-FREEZE / RESTRICTION on the aforementioned account and all linked netbanking, UPI, and debit card instruments with immediate effect.
2. Ensure that no funds are permitted to be withdrawn via ATM, POS, IMPS, RTGS, or third-party cryptocurrency virtual asset gateways.
3. Transmit within 24 hours to this investigating authority:
   (a) Complete account statement with IP logs from account inception.
   (b) Certified KYC documents (Aadhaar, PAN, registered mobile number).
   (c) CCTV footage / ATM locator logs for any recent cash withdrawals.

Failure to comply with this statutory directive shall render the non-compliant intermediary liable for proceedings under Section 223 BNSS (Disobedience of public servant's order) and loss of statutory safe-harbour immunity under Section 79(3)(b) of the IT Act.

ISSUED UNDER OFFICIAL SEAL:
Investigating Officer: {officer_name}
Designation / Badge Number: {badge_no}, Cyber Crime Unit
Cryptographic Digital Verification Seal: {digital_seal[:32]}...
""".strip()

        return {
            "status": "success",
            "order_reference": order_ref,
            "case_id": case_id,
            "bank_name": bank_name,
            "mule_account": mule_account,
            "officer_name": officer_name,
            "badge_no": badge_no,
            "issued_at": timestamp,
            "digital_seal_hash": digital_seal,
            "statutory_act": "Section 94 BNSS 2023 & Sec 79(3)(b) IT Act 2000",
            "notice_text": notice_text,
            "is_synthetic": True
        }


moneytrail_service = MoneyTrailService()
