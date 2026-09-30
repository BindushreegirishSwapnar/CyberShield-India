import os
import json
from collections import defaultdict
from flask import Blueprint, jsonify, request
from sqlalchemy import func, desc, or_
from database import get_session
from models_db import Complaint, ThreatIndicator

graph_bp = Blueprint('graph_bp', __name__)

MULE_RINGS = [
    {
        "cluster_id": 1,
        "cluster_name": "Jamtara Fast-Loan UPI Ring",
        "description": "Multi-account rapid rotation via micro-lending APKs and unverified payment handles.",
        "primary_vector": "UPI / Micro-Loan APK",
        "phones": ["+91 98234 11092", "+91 98234 11093", "+91 98234 11094"],
        "upis": ["quickloan.instant@ybl", "fastcash.verify@icici", "loanhelp.desh@okhdfcbank"],
        "accounts": ["HDFC-00421099234", "ICICI-1102938491"],
        "urls": ["http://fastloan-quick-in.apk/download", "http://urgent-cash-loan.in"]
    },
    {
        "cluster_id": 2,
        "cluster_name": "Mewat Marketplace Impersonation Hub",
        "description": "Defence personnel identity theft on classifieds with fake advance QR payments.",
        "primary_vector": "QR Code / Classifieds",
        "phones": ["+91 97110 55421", "+91 97110 55422"],
        "upis": ["armycanteen.pay@paytm", "subedar.canteen.support@axisbank"],
        "accounts": ["SBI-3094829104", "PNB-09823411234"],
        "urls": ["http://olx-army-clearance.store"]
    },
    {
        "cluster_id": 3,
        "cluster_name": "Southeast Asia Telegram Task Fraud",
        "description": "Part-time YouTube like/hotel review investment trap with synthetic trading balances.",
        "primary_vector": "Telegram / Fake Crypto Exchange",
        "phones": ["+91 88001 22934", "+91 88001 22935"],
        "upis": ["globaltask.payout@okaxis", "cryptoreward.node@sbi"],
        "accounts": ["KOTAK-9921004921", "AXIS-91902004231"],
        "urls": ["http://asia-hotel-task-vip.com", "http://telegram-earn-fast.in"]
    },
    {
        "cluster_id": 4,
        "cluster_name": "Cyberabad Digital Arrest Syndicate",
        "description": "CBI/ED impersonation video calling demanding RBI escrow deposits.",
        "primary_vector": "VoIP Video / Fake Supreme Court Warrant",
        "phones": ["+91 94440 99120", "+91 94440 99121"],
        "upis": ["rbi.investigation.escrow@govtsbi", "customs.clearance.hq@sbi"],
        "accounts": ["SBI-990011223344", "BOI-445566778899"],
        "urls": ["http://cbi-narcotics-inquiry.org", "http://rbi-supervision-escrow.net"]
    },
    {
        "cluster_id": 5,
        "cluster_name": "Bengaluru Corporate Mule Account Ring",
        "description": "Shell private limited current accounts layered across fintech payment gateways.",
        "primary_vector": "Layered Current Accounts",
        "phones": ["+91 99004 88711", "+91 99004 88712"],
        "upis": ["vertextech.solutions@hdfc", "zenithexports.billing@icici"],
        "accounts": ["HDFC-502000492819", "YES-002938472910"],
        "urls": ["http://fintech-gateway-secure.co.in"]
    },
    {
        "cluster_id": 6,
        "cluster_name": "Gurugram Crypto Arbitrage Ponzi",
        "description": "Guaranteed daily USDT returns routed through P2P crypto sellers and frozen wallets.",
        "primary_vector": "P2P Crypto / USDT",
        "phones": ["+91 91223 44556", "+91 91223 44557"],
        "upis": ["crypto.exchange.usdt@pnb", "arbitrage.wealth@okaxis"],
        "accounts": ["ICICI-4029100234", "AXIS-2039481029"],
        "urls": ["http://apex-crypto-yield.io", "http://usdt-p2p-arbitrage.com"]
    }
]

@graph_bp.route('/entities', methods=['GET'])
def get_graph_entities():
    """
    Returns graph nodes and links for Entity Link Analysis.
    Guarantee:
    - Return format: {nodes:[{id,type,label,risk}], links:[{source,target,type}]}
    - Every source and target strictly exists in nodes.
    - Contains at least 6 realistic mule-ring clusters.
    """
    try:
        cluster_filter = request.args.get('cluster_id')
        entity_filter = request.args.get('type')
        search_query = request.args.get('search', '').strip().lower()

        nodes_dict = {}
        links_list = []

        # 1. Fetch complaints from database
        with get_session() as session:
            db_complaints = session.query(Complaint).order_by(desc(Complaint.financial_loss)).limit(90).all()
            complaint_dicts = [c.to_dict() for c in db_complaints]

        cluster_summaries = []

        # 2. Build Seeded Clusters and attach complaints to them
        for ring_idx, ring in enumerate(MULE_RINGS):
            cid = ring["cluster_id"]
            cname = ring["cluster_name"]

            # Select a subset of complaints for this cluster (4 complaints each)
            start_i = ring_idx * 4
            assigned_cases = complaint_dicts[start_i:start_i + 4]
            cluster_loss = sum(float(c.get("financial_loss", 0)) for c in assigned_cases)

            cluster_summaries.append({
                "cluster_id": cid,
                "cluster_name": cname,
                "description": ring["description"],
                "primary_vector": ring["primary_vector"],
                "complaints_count": len(assigned_cases),
                "total_loss_inr": cluster_loss
            })

            # Add shared phone node
            phone_id = f"phone_c{cid}_0"
            phone_val = ring["phones"][0]
            nodes_dict[phone_id] = {
                "id": phone_id,
                "type": "phone",
                "label": phone_val,
                "risk": 85,
                "cluster_id": cid,
                "cluster_name": cname,
                "details": {
                    "entity_type": "Phone Number",
                    "value": phone_val,
                    "service_provider": "Airtel / Jio Pre-activated SIM",
                    "linked_cases": len(assigned_cases),
                    "cluster_name": cname,
                    "status": "Flagged & IMEI Traced"
                }
            }

            # Add shared UPI node
            upi_id = f"upi_c{cid}_0"
            upi_val = ring["upis"][0]
            nodes_dict[upi_id] = {
                "id": upi_id,
                "type": "upi_vpa",
                "label": upi_val,
                "risk": 92,
                "cluster_id": cid,
                "cluster_name": cname,
                "details": {
                    "entity_type": "UPI VPA",
                    "value": upi_val,
                    "beneficiary_name": "Mule Corporate / Dummy Holder",
                    "bank_handle": upi_val.split('@')[-1] if '@' in upi_val else "NPCI",
                    "linked_cases": len(assigned_cases),
                    "cluster_name": cname,
                    "status": "Debit Freeze Requested (1930)"
                }
            }

            # Add shared Bank Account node
            acc_id = f"bank_c{cid}_0"
            acc_val = ring["accounts"][0]
            nodes_dict[acc_id] = {
                "id": acc_id,
                "type": "bank_account",
                "label": acc_val,
                "risk": 90,
                "cluster_id": cid,
                "cluster_name": cname,
                "details": {
                    "entity_type": "Mule Bank Account",
                    "account_number": acc_val,
                    "cluster_name": cname,
                    "freeze_status": "Lien Marked via I4C Portal",
                    "risk_tier": "High Risk Syndicate Mule"
                }
            }

            # Add shared URL node
            url_id = f"url_c{cid}_0"
            url_val = ring["urls"][0]
            nodes_dict[url_id] = {
                "id": url_id,
                "type": "url",
                "label": url_val.replace("http://", "").replace("https://", "")[:20],
                "risk": 80,
                "cluster_id": cid,
                "cluster_name": cname,
                "details": {
                    "entity_type": "Phishing URL / Malicious APK",
                    "full_url": url_val,
                    "cluster_name": cname,
                    "domain_status": "CERT-In Takedown Notice Issued"
                }
            }

            # Connect Shared Entities together in this syndicate
            links_list.append({"source": upi_id, "target": acc_id, "type": "settles_into"})
            links_list.append({"source": phone_id, "target": upi_id, "type": "registered_upi"})
            links_list.append({"source": url_id, "target": upi_id, "type": "hosted_gateway"})

            # Now add and connect each complaint in this cluster
            for c in assigned_cases:
                c_id = f"case_{c['complaint_id']}"
                nodes_dict[c_id] = {
                    "id": c_id,
                    "type": "complaint",
                    "label": c['complaint_id'],
                    "risk": int(c.get('risk_score', 75)),
                    "cluster_id": cid,
                    "cluster_name": cname,
                    "details": {
                        "complaint_id": c['complaint_id'],
                        "state": c.get('state'),
                        "city": c.get('city'),
                        "category": c.get('predicted_category') or c.get('crime_type'),
                        "financial_loss": float(c.get('financial_loss', 0)),
                        "risk_score": int(c.get('risk_score', 75)),
                        "priority": c.get('priority', 'High'),
                        "status": c.get('current_status', 'Investigating'),
                        "date": c.get('complaint_date'),
                        "cluster_name": cname
                    }
                }

                # Link complaint to phone and UPI
                links_list.append({"source": c_id, "target": phone_id, "type": "called_by"})
                links_list.append({"source": c_id, "target": upi_id, "type": "transacted_to"})

        # 3. Add standalone high-value cases and their indicators from remaining complaints
        remaining = complaint_dicts[24:50]
        for c in remaining:
            c_id = f"case_{c['complaint_id']}"
            nodes_dict[c_id] = {
                "id": c_id,
                "type": "complaint",
                "label": c['complaint_id'],
                "risk": int(c.get('risk_score', 70)),
                "cluster_id": 0,
                "cluster_name": "Unclustered Triage",
                "details": {
                    "complaint_id": c['complaint_id'],
                    "state": c.get('state'),
                    "category": c.get('predicted_category'),
                    "financial_loss": float(c.get('financial_loss', 0)),
                    "risk_score": int(c.get('risk_score', 70))
                }
            }

        # 4. Strict Link Validation (Source & Target MUST exist in nodes)
        valid_node_ids = set(nodes_dict.keys())
        sanitized_links = []
        for l in links_list:
            if l["source"] in valid_node_ids and l["target"] in valid_node_ids:
                sanitized_links.append(l)

        # 5. Apply Optional Query Filters
        final_nodes = list(nodes_dict.values())
        if cluster_filter and cluster_filter != 'All':
            cid_int = int(cluster_filter) if cluster_filter.isdigit() else cluster_filter
            final_nodes = [n for n in final_nodes if n.get("cluster_id") == cid_int]
            final_ids = {n["id"] for n in final_nodes}
            sanitized_links = [l for l in sanitized_links if l["source"] in final_ids and l["target"] in final_ids]

        if entity_filter and entity_filter != 'All':
            ef = entity_filter.lower()
            final_nodes = [n for n in final_nodes if n["type"].lower() == ef]
            final_ids = {n["id"] for n in final_nodes}
            sanitized_links = [l for l in sanitized_links if l["source"] in final_ids and l["target"] in final_ids]

        if search_query:
            final_nodes = [n for n in final_nodes if search_query in n["label"].lower() or search_query in str(n.get("details", "")).lower()]
            final_ids = {n["id"] for n in final_nodes}
            sanitized_links = [l for l in sanitized_links if l["source"] in final_ids and l["target"] in final_ids]

        return jsonify({
            "status": "success",
            "nodes_count": len(final_nodes),
            "links_count": len(sanitized_links),
            "nodes": final_nodes,
            "links": sanitized_links,
            "clusters": cluster_summaries
        }), 200

    except Exception as e:
        return jsonify({"status": "error", "message": f"Failed to compute entity graph: {str(e)}"}), 500
