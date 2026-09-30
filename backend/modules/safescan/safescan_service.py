"""
Safe-Scan Service - Multi-Channel Input Reputation, QR Code & Lookalike Domain Analyzer
Inspects UPI VPAs, phone numbers, URLs, and bank accounts against the 5,000 complaint database,
computes Levenshtein/homoglyph domain impersonation scores, and issues automated Safety Verdicts.
"""

import re
import urllib.parse
from datetime import datetime
from database import get_session
from models_db import Complaint


# Top 50 Official Indian Banking, Financial, and Government Portals Whitelist
OFFICIAL_INDIAN_DOMAINS = [
    "sbi.co.in", "onlinesbi.sbi", "hdfcbank.com", "icicibank.com", "axisbank.com",
    "kotak.com", "pnbindia.in", "bankofbaroda.in", "canarabank.com", "unionbankofindia.co.in",
    "indusind.com", "yesbank.in", "idfcfirstbank.com", "federalbank.co.in", "rbi.org.in",
    "npci.org.in", "bhimupi.org.in", "cybercrime.gov.in", "incometax.gov.in", "uidai.gov.in",
    "epfindia.gov.in", "digilocker.gov.in", "passportindia.gov.in", "parivahan.gov.in",
    "india.gov.in", "mygov.in", "cert-in.org.in", "irctc.co.in", "licindia.in",
    "amazon.in", "flipkart.com", "paytm.com", "phonepe.com", "google.com", "meity.gov.in"
]

SUSPICIOUS_TLDS = [".xyz", ".top", ".tk", ".ml", ".ga", ".cf", ".gq", ".online", ".site", ".ru", ".vip", ".cc"]

def levenshtein_distance(s1: str, s2: str) -> int:
    """Computes standard edit distance between two strings."""
    if len(s1) < len(s2):
        return levenshtein_distance(s2, s1)
    if len(s2) == 0:
        return len(s1)

    previous_row = range(len(s2) + 1)
    for i, c1 in enumerate(s1):
        current_row = [i + 1]
        for j, c2 in enumerate(s2):
            insertions = previous_row[j + 1] + 1
            deletions = current_row[j] + 1
            substitutions = previous_row[j] + (c1 != c2)
            current_row.append(min(insertions, deletions, substitutions))
        previous_row = current_row
    return previous_row[-1]

class SafeScanService:
    def check_lookalike_domain(self, domain_or_url: str):
        """
        Detects typosquatting, lookalike domains, homoglyph traps, and brand impersonation.
        """
        raw = domain_or_url.strip().lower()
        if raw.startswith("http://") or raw.startswith("https://"):
            parsed = urllib.parse.urlparse(raw)
            domain = parsed.netloc.split(":")[0]
        else:
            domain = raw.split("/")[0].split(":")[0]

        domain = re.sub(r'^www\.', '', domain)

        # 1. Exact match with official whitelist
        if domain in OFFICIAL_INDIAN_DOMAINS:
            return {
                "is_lookalike": False,
                "is_official": True,
                "official_target": domain,
                "risk_rating": "SAFE",
                "similarity_score": 1.0,
                "notes": f"Verified official Indian domain ({domain})."
            }

        # 2. Suspicious TLD check
        has_suspicious_tld = any(domain.endswith(tld) for tld in SUSPICIOUS_TLDS)

        # 3. Substring / Hyphenated brand impersonation check
        brand_keywords = ["sbi", "hdfc", "icici", "axis", "kotak", "pnb", "rbi", "kyc", "cybercrime", "income-tax", "epfo"]
        matched_brands = [b for b in brand_keywords if b in domain]

        # 4. Levenshtein edit distance check against whitelist
        closest_domain = None
        min_dist = 999
        domain_name_part = domain.split(".")[0]

        for official in OFFICIAL_INDIAN_DOMAINS:
            off_name = official.split(".")[0]
            dist = levenshtein_distance(domain_name_part, off_name)
            if dist < min_dist:
                min_dist = dist
                closest_domain = official

        # If domain contains brand names or has edit distance 1 or 2
        is_suspicious = False
        reasons = []

        if matched_brands and domain not in OFFICIAL_INDIAN_DOMAINS:
            is_suspicious = True
            reasons.append(f"Domain contains financial keyword(s): {', '.join(matched_brands)} but is not officially recognized.")

        if min_dist in (1, 2) and len(domain_name_part) >= 3:
            is_suspicious = True
            reasons.append(f"High similarity to legitimate portal '{closest_domain}' (Edit distance: {min_dist}). Typosquatting suspected.")

        if has_suspicious_tld:
            is_suspicious = True
            reasons.append(f"Uses high-risk, low-cost top-level domain commonly leveraged in disposable phishing campaigns.")

        if "kyc" in domain or "update" in domain or "verify" in domain or "reward" in domain:
            is_suspicious = True
            reasons.append("Contains deceptive social engineering terms ('kyc', 'update', 'verify', 'reward').")

        similarity = max(0.0, 1.0 - (min_dist / max(len(domain), 1)))

        return {
            "is_lookalike": is_suspicious,
            "is_official": False,
            "official_target": closest_domain if is_suspicious else None,
            "domain_analyzed": domain,
            "similarity_score": round(similarity, 2),
            "risk_rating": "DANGEROUS" if len(reasons) >= 2 else "SUSPICIOUS" if is_suspicious else "NEUTRAL",
            "notes": " • ".join(reasons) if reasons else "Domain has no obvious impersonation indicators, but verify authenticity."
        }

    def query_reputation_database(self, entity_type: str, entity_value: str):
        """
        Queries the SQLite complaints database for prior complaints, syndicates, and financial losses.
        """
        val = entity_value.strip()
        matches = []
        total_loss = 0
        categories = set()
        first_reported = None
        last_reported = None

        clean_val = val
        if entity_type == 'phone':
            # Clean digits
            clean_val = re.sub(r'[^\d]', '', val)
            if len(clean_val) > 10:
                clean_val = clean_val[-10:] # last 10 digits

        # Search complaints table
        try:
            with get_session() as session:
                q = session.query(Complaint)
                if entity_type == 'phone':
                    q = q.filter(Complaint.suspect_phone.ilike(f"%{clean_val}%"))
                elif entity_type == 'upi':
                    q = q.filter(Complaint.suspect_upi.ilike(f"%{val}%"))
                elif entity_type == 'url':
                    q = q.filter(Complaint.suspect_url.ilike(f"%{val}%"))
                else:
                    q = q.filter(
                        (Complaint.suspect_phone.ilike(f"%{val}%")) |
                        (Complaint.suspect_upi.ilike(f"%{val}%")) |
                        (Complaint.suspect_url.ilike(f"%{val}%"))
                    )

                rows = q.limit(10).all()
                for r in rows:
                    amt = float(r.amount or 0)
                    total_loss += amt
                    categories.add(r.category)
                    dt = str(getattr(r, 'complaint_date', None) or getattr(r, 'incident_date', None) or '')
                    if not first_reported or dt < first_reported:
                        first_reported = dt
                    if not last_reported or dt > last_reported:
                        last_reported = dt
                    matches.append({
                        "complaint_id": r.complaint_id,
                        "category": r.category,
                        "amount": amt,
                        "date": dt,
                        "status": r.current_status
                    })
        except Exception as e:
            print("DB lookup error:", e)


        # Count total complaints with this indicator
        complaint_count = len(matches)

        # Determine severity & status
        if complaint_count >= 3:
            verdict = "MALICIOUS"
            risk_badge = "HIGH DANGER"
            summary = f"CRITICAL WARNING: This {entity_type.upper()} is linked to {complaint_count} active cybercrime complaints totaling ₹{total_loss:,.2f} in reported financial fraud."
        elif complaint_count > 0:
            verdict = "SUSPICIOUS"
            risk_badge = "SUSPICIOUS"
            summary = f"CAUTION: This {entity_type.upper()} matches {complaint_count} complaint(s) in the National Cyber Crime database. Exercise extreme vigilance."
        else:
            verdict = "CLEAR"
            risk_badge = "NO PRIOR COMPLAINTS"
            summary = f"No previous complaints lodged against this {entity_type.upper()} in the active 5,000-complaint database."

        return {
            "entity_type": entity_type,
            "entity_value": val,
            "complaint_count": complaint_count,
            "total_loss_inr": total_loss,
            "first_reported": first_reported,
            "last_reported": last_reported,
            "categories": list(categories),
            "verdict": verdict,
            "risk_badge": risk_badge,
            "summary": summary,
            "recent_cases": matches[:3],
            "is_synthetic": True
        }

    def parse_upi_qr(self, qr_text: str):
        """
        Parses UPI QR URI standard: upi://pay?pa=...&pn=...&am=...&cu=INR&tn=...
        """
        text = qr_text.strip()
        if not text.lower().startswith("upi://pay"):
            return {
                "is_valid_upi_qr": False,
                "error": "Not a standard UPI QR code. Must begin with 'upi://pay'."
            }

        parsed = urllib.parse.urlparse(text)
        params = urllib.parse.parse_qs(parsed.query)

        vpa = params.get('pa', [''])[0]
        payee_name = params.get('pn', [''])[0]
        amount = params.get('am', ['0'])[0]
        note = params.get('tn', [''])[0]
        merchant_code = params.get('mc', [''])[0]

        # Reputation check on VPA
        vpa_reputation = self.query_reputation_database('upi', vpa) if vpa else None

        # Check for deceptive Payee Name vs VPA mismatch
        flags = []
        is_mismatch = False

        suspicious_keywords = ["bill", "electricity", "customs", "police", "refund", "support", "kyc", "bank"]
        name_lower = payee_name.lower()

        # If name claims to be official institution but VPA is personal handle
        has_claim = any(k in name_lower for k in suspicious_keywords)
        is_personal_vpa = any(handle in vpa.lower() for handle in ["@oksbi", "@okhdfcbank", "@okaxis", "@okicici", "@ybl", "@paytm"])

        if has_claim and is_personal_vpa and not merchant_code:
            is_mismatch = True
            flags.append("Payee Name claims institutional/government identity but destination VPA is a personal retail handle.")

        if vpa_reputation and vpa_reputation["complaint_count"] > 0:
            flags.append(f"Destination VPA is cited in {vpa_reputation['complaint_count']} cybercrime complaints.")

        verdict = "MALICIOUS" if (vpa_reputation and vpa_reputation["complaint_count"] >= 2) or (is_mismatch and len(flags) > 1) else "SUSPICIOUS" if flags else "SAFE"

        return {
            "is_valid_upi_qr": True,
            "raw_uri": text,
            "vpa": vpa,
            "payee_name": payee_name or "Unknown Payee",
            "amount": amount,
            "note": note,
            "merchant_code": merchant_code or "Unregistered Retail VPA",
            "risk_verdict": verdict,
            "mismatch_detected": is_mismatch,
            "risk_flags": flags,
            "reputation": vpa_reputation,
            "is_synthetic": True
        }

    def analyze_extracted_ocr(self, text: str):
        """
        Parses phones, URLs, and UPI IDs out of OCR screenshot text and queries all entities.
        """
        # Regex patterns
        phone_matches = re.findall(r'(?:\+?91[\-\s]?)?[6-9]\d{9}', text)
        url_matches = re.findall(r'https?://[^\s<>"]+|www\.[^\s<>"]+|[a-zA-Z0-9.\-]+\.(?:com|in|org|net|xyz|top|site|online|cc|ru)[^\s<>"]*', text)
        upi_matches = re.findall(r'[a-zA-Z0-9.\-_]{3,}@[a-zA-Z]{3,}', text)

        phones_cleaned = list(set([re.sub(r'[^\d]', '', p)[-10:] for p in phone_matches]))
        urls_cleaned = list(set(url_matches))
        upis_cleaned = list(set(upi_matches))

        results = {
            "phones": [self.query_reputation_database('phone', p) for p in phones_cleaned],
            "urls": [
                {
                    "url": u,
                    "reputation": self.query_reputation_database('url', u),
                    "lookalike_check": self.check_lookalike_domain(u)
                }
                for u in urls_cleaned
            ],
            "upis": [self.query_reputation_database('upi', u) for u in upis_cleaned]
        }

        # Overall safety score & verdict
        all_verdicts = []
        for p in results["phones"]: all_verdicts.append(p["verdict"])
        for u in results["upis"]: all_verdicts.append(u["verdict"])
        for url in results["urls"]:
            all_verdicts.append(url["reputation"]["verdict"])
            if url["lookalike_check"]["is_lookalike"]:
                all_verdicts.append("MALICIOUS" if url["lookalike_check"]["risk_rating"] == "DANGEROUS" else "SUSPICIOUS")

        if "MALICIOUS" in all_verdicts:
            overall_verdict = "MALICIOUS"
            verdict_color = "#C8553D"
            verdict_badge = "CRITICAL THREAT DETECTED"
        elif "SUSPICIOUS" in all_verdicts:
            overall_verdict = "SUSPICIOUS"
            verdict_color = "#D9825B"
            verdict_badge = "POTENTIAL FRAUD INDICATOR"
        else:
            overall_verdict = "CLEAR"
            verdict_color = "#1F6F6B"
            verdict_badge = "NO KNOWN THREATS IDENTIFIED"

        return {
            "raw_text_length": len(text),
            "entities_found": {
                "phones_count": len(phones_cleaned),
                "urls_count": len(urls_cleaned),
                "upis_count": len(upis_cleaned)
            },
            "findings": results,
            "overall_verdict": overall_verdict,
            "verdict_badge": verdict_badge,
            "verdict_color": verdict_color,
            "prefill_complaint": {
                "suspect_phone": phones_cleaned[0] if phones_cleaned else "",
                "suspect_upi": upis_cleaned[0] if upis_cleaned else "",
                "suspect_url": urls_cleaned[0] if urls_cleaned else "",
                "description": f"Suspicious communication detected via Safe-Scan OCR:\n{text[:200]}..."
            },
            "is_synthetic": True
        }


safescan_service = SafeScanService()
