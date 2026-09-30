import os
import re
import json
import joblib
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

MODELS_DIR = os.path.join(os.path.dirname(__file__), 'models')
VECTORIZER_PATH = os.path.join(MODELS_DIR, 'tfidf_vectorizer_v2.joblib')
MODEL_PATH = os.path.join(MODELS_DIR, 'cybercrime_classifier_v2.joblib')
METRICS_PATH = os.path.join(MODELS_DIR, 'model_metrics.json')

# Cache model and vectorizer in memory
_vectorizer = None
_classifier = None

def get_model_and_vectorizer():
    global _vectorizer, _classifier
    if _vectorizer is None or _classifier is None:
        if os.path.exists(VECTORIZER_PATH) and os.path.exists(MODEL_PATH):
            _vectorizer = joblib.load(VECTORIZER_PATH)
            _classifier = joblib.load(MODEL_PATH)
        else:
            # Fallback to v1 if v2 not present
            fallback_vec = os.path.join(MODELS_DIR, 'tfidf_vectorizer.joblib')
            fallback_clf = os.path.join(MODELS_DIR, 'cybercrime_classifier.joblib')
            if os.path.exists(fallback_vec) and os.path.exists(fallback_clf):
                _vectorizer = joblib.load(fallback_vec)
                _classifier = joblib.load(fallback_clf)
            else:
                raise FileNotFoundError("Trained model artifacts not found in models directory.")
    return _vectorizer, _classifier


def extract_technical_indicators(text):
    """
    Extract technical Indicators of Compromise (IOCs) from complaint text:
    URLs, domains, emails, phone numbers, IP addresses, UPI handles, crypto addresses, and malware names.
    Clearly marks all extracted indicators as synthetic demonstration data.
    """
    if not text:
        return []

    iocs = []
    seen_values = set()

    def add_ioc(val, itype, sev, conf, label):
        val = val.strip().strip('.,;:()[]{}')
        if not val or val in seen_values:
            return
        seen_values.add(val)
        iocs.append({
            "indicator_value": val,
            "indicator_type": itype,
            "code": itype,
            "label": label,
            "severity": sev,
            "confidence": conf,
            "source": "Complaint Narrative Extraction",
            "is_synthetic": True,
            "detail": f"Synthesized {label.lower()} observed in complaint narration."
        })

    # 1. URLs
    urls = re.findall(r'https?://[^\s<>"]+|www\.[^\s<>"]+', text)
    for u in urls:
        add_ioc(u, "URL", "High", 0.95, "Suspicious URL")

    # 2. Domains
    domains = re.findall(r'\b(?:[a-zA-Z0-9-]+\.)+(?:com|org|in|net|xyz|top|cc|online|site|biz|apk|store|vip|tech)\b', text, re.IGNORECASE)
    for d in domains:
        if not any(d in u for u in urls):
            add_ioc(d, "DOMAIN", "Medium", 0.90, "Suspicious Domain")

    # 3. Email Addresses
    emails = re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', text)
    for em in emails:
        add_ioc(em, "EMAIL", "Medium", 0.92, "Suspect Email")

    # 4. Indian Phone Numbers (+91 or 10-digit mobile)
    phones = re.findall(r'(?:\+91[-\s]?)?[6-9]\d{9}\b', text)
    for ph in phones:
        add_ioc(ph, "PHONE", "High", 0.94, "Suspect Phone Number")

    # 5. IP Addresses
    ips = re.findall(r'\b(?:\d{1,3}\.){3}\d{1,3}\b', text)
    for ip in ips:
        if not ip.startswith("0.") and not ip.startswith("255."):
            add_ioc(ip, "IP_ADDRESS", "High", 0.90, "Host / Source IP")

    # 6. UPI Virtual Payment Addresses (VPAs)
    upis = re.findall(r'\b[a-zA-Z0-9.\-_]{2,40}@(okhdfcbank|okaxis|oksbi|okicici|paytm|ybl|apl|upi|ibl|icici|axl)\b', text, re.IGNORECASE)
    # The findall returns groups if capturing group is used, so let's match full pattern
    upi_matches = re.finditer(r'\b[a-zA-Z0-9.\-_]{2,40}@(okhdfcbank|okaxis|oksbi|okicici|paytm|ybl|apl|upi|ibl|icici|axl)\b', text, re.IGNORECASE)
    for m in upi_matches:
        add_ioc(m.group(0), "UPI_VPA", "High", 0.96, "Beneficiary UPI VPA")

    # 7. Cryptocurrency Wallet Addresses
    wallets = re.findall(r'\b(?:0x[a-fA-F0-9]{40}|[13][a-km-zA-HJ-NP-Z1-9]{25,34}|bc1[a-z0-9]{39,59})\b', text)
    for w in wallets:
        add_ioc(w, "CRYPTO_WALLET", "Critical", 0.98, "Cryptocurrency Wallet")

    # 8. Known Malware Families
    malware_matches = re.findall(r'\b(LockBit(?:\s*3\.0)?|WannaCry|Conti|Phobos|BlackCat|AgentTesla|RedLine|DarkComet|AnyDesk|TeamViewer|QuickSupport|RustDesk)\b', text, re.IGNORECASE)
    for mw in malware_matches:
        sev = "Critical" if "lock" in mw.lower() or "cry" in mw.lower() or "conti" in mw.lower() else "High"
        add_ioc(mw, "MALWARE", sev, 0.95, f"Malware / Remote Tool ({mw})")

    # 9. Transaction / UTR References
    utr_matches = re.findall(r'\b(?:UTR|UPI\s*Ref|Txn\s*ID|RRN)[\s:#]+([A-Za-z0-9]{10,22})\b', text, re.IGNORECASE)
    for utr in utr_matches:
        add_ioc(utr, "TRANSACTION_REF", "Medium", 0.90, "Banking Transaction Ref / UTR")

    return iocs


def detect_threat_indicators(text, personal_info_exposed=False, account_compromised=False):
    """Analyze complaint text and metadata to detect threat behaviors and technical indicators."""
    text_lower = text.lower()
    indicators = []

    # 1. OTP Request
    if re.search(r'\b(otp|one[-\s]?time password|verification code|security code)\b', text_lower):
        indicators.append({
            "code": "OTP_REQUEST",
            "label": "OTP Coercion / Request",
            "severity": "High",
            "detail": "Complaint mentions explicit solicitation of One-Time Password or verification code."
        })

    # 2. Password / Credentials Request
    if re.search(r'\b(password|pin|cvv|atm pin|login credential|secret question|seed phrase)\b', text_lower):
        indicators.append({
            "code": "CREDENTIAL_THEFT",
            "label": "Credential Harvesting Attempt",
            "severity": "High",
            "detail": "Attempt to harvest confidential authentication credentials, CVV, or PINs."
        })

    # 3. Suspicious Link / URL
    if re.search(r'\b(http[s]?://|www\.|link|url|click here|portal|website|cloned page|apk download)\b', text_lower):
        indicators.append({
            "code": "SUSPICIOUS_LINK",
            "label": "Phishing Link / Malicious Domain",
            "severity": "Medium",
            "detail": "Victim was redirected to an external suspicious link, cloned domain, or untrusted APK."
        })

    # 4. Bank / Authority Impersonation
    if re.search(r'\b(bank|rbi|police|officer|manager|customs|tax|income tax|cbi|ed|narcotics|mdma|courier|support|cfo|director)\b', text_lower):
        indicators.append({
            "code": "IMPERSONATION",
            "label": "Law Enforcement / Bank Impersonation",
            "severity": "High",
            "detail": "Perpetrator impersonated police, CBI, RBI officials, or banking institutions."
        })

    # 5. Unauthorized Transaction
    if re.search(r'\b(transferred money|debited|withdrawn|unauthorized transaction|credit card charged|siphoned|emptied|loss of)\b', text_lower):
        indicators.append({
            "code": "UNAUTHORIZED_TRANSACTION",
            "label": "Unauthorized Financial Debit",
            "severity": "High",
            "detail": "Funds or financial assets were debited without authorized account owner consent."
        })

    # 6. Personal Information Exposure
    if personal_info_exposed or re.search(r'\b(aadhaar|pan card|passport|identity proof|photograph|photos|doxxed|private video|medical record)\b', text_lower):
        indicators.append({
            "code": "PII_EXPOSURE",
            "label": "Personal Identity (PII) Exposure",
            "severity": "Medium",
            "detail": "Sensitive identity documents (Aadhaar, PAN) or intimate media were exposed."
        })

    # 7. Account Takeover
    if account_compromised or re.search(r'\b(lost access|hacked account|locked out|hijacked|changed password|changed recovery|sim swap|2fa bypassed)\b', text_lower):
        indicators.append({
            "code": "ACCOUNT_TAKEOVER",
            "label": "Account / SIM Hijack",
            "severity": "High",
            "detail": "Victim's primary credentials, telecom SIM, or user profile were compromised."
        })

    # 8. Threatening Message / Extortion
    if re.search(r'\b(threatening|harassment|abusive|vulgar|blackmail|extortion|harm|stalking|intimidat|death threat|digital arrest)\b', text_lower):
        indicators.append({
            "code": "EXTORTION_HARASSMENT",
            "label": "Coercive Extortion / Harassment",
            "severity": "High",
            "detail": "Coercive intimidation, digital arrest extortion, or harassment detected."
        })

    # 9. Malware / Suspicious Payload
    if re.search(r'\b(malware|virus|trojan|keylogger|spyware|payload|worm|infected|rat|anydesk|teamviewer|quicksupport)\b', text_lower):
        indicators.append({
            "code": "MALWARE_PAYLOAD",
            "label": "Remote Access Tool / Malware",
            "severity": "High",
            "detail": "Malicious software, trojan payload, or remote desktop tool was utilized."
        })

    # 10. Ransom Demand
    if re.search(r'\b(encrypted|ransom|decrypt|bitcoin|cryptocurrency|countdown|locked files|\.locked|\.lockbit)\b', text_lower):
        indicators.append({
            "code": "RANSOM_DEMAND",
            "label": "Ransomware Encryption & Extortion",
            "severity": "Critical",
            "detail": "Endpoint systems encrypted with cryptocurrency ransom demand for recovery."
        })

    # 11. Data Leak / Exfiltration
    if re.search(r'\b(data breach|database leaked|exfiltrat|dumped|dark web|pastebin|records leaked|bucket)\b', text_lower):
        indicators.append({
            "code": "DATA_BREACH",
            "label": "Mass Data Leak / Dark Web Exposure",
            "severity": "Critical",
            "detail": "Organizational or customer database exfiltrated or posted on cyber forums."
        })

    # Merge with technical concrete IOCs
    technical_iocs = extract_technical_indicators(text)
    for ti in technical_iocs:
        indicators.append({
            "code": ti["code"],
            "label": f"{ti['label']}: {ti['indicator_value']}",
            "severity": ti["severity"],
            "detail": ti["detail"],
            "raw_value": ti["indicator_value"],
            "indicator_type": ti["indicator_type"]
        })

    return indicators


def calculate_risk_score(
    predicted_category,
    confidence,
    severity,
    financial_loss=0.0,
    personal_info_exposed=False,
    account_compromised=False,
    threat_indicators=None
):
    """
    Deterministic, explainable multi-factor risk scoring engine.
    Calculates 0-100 risk score, risk level, contributing factor points, and audit reasons.
    """
    factors = {
        "category_factor": 0,
        "severity_factor": 0,
        "financial_factor": 0,
        "account_compromised_factor": 0,
        "pii_factor": 0,
        "threat_indicators_factor": 0,
        "confidence_factor": 0.0
    }
    reasons = []
    threat_indicators = threat_indicators or []

    # 1. Base Threat Weight of Predicted Crime Category (Max 20 pts)
    base_category_weights = {
        "Ransomware / Malware": 20,
        "Data Breach": 20,
        "Online Financial Fraud": 18,
        "Account Takeover": 18,
        "Investment/Crypto Fraud": 16,
        "Identity Theft": 15,
        "Phishing Attack": 15,
        "Social Engineering": 14,
        "Cyber Bullying / Harassment": 12,
        "Online Shopping Fraud": 10
    }
    cat_weight = base_category_weights.get(predicted_category, 12)
    factors["category_factor"] = cat_weight
    reasons.append(f"Predicted crime type '{predicted_category}' baseline threat: +{cat_weight} pts (max 20)")

    # 2. Incident Severity (Max 25 pts)
    severity_map = {
        "Critical": 25,
        "High": 20,
        "Medium": 12,
        "Low": 5
    }
    sev_pts = severity_map.get(severity, 12)
    factors["severity_factor"] = sev_pts
    reasons.append(f"Reported incident severity '{severity}': +{sev_pts} pts (max 25)")

    # 3. Financial Loss (Max 20 pts)
    try:
        loss_val = float(financial_loss)
    except (ValueError, TypeError):
        loss_val = 0.0

    if loss_val >= 500000:
        fin_pts = 20
        reasons.append(f"Severe financial impact (> ₹5,00,000): +20 pts (max 20)")
    elif loss_val >= 100000:
        fin_pts = 18
        reasons.append(f"Substantial financial loss (> ₹1,00,000): +18 pts (max 20)")
    elif loss_val >= 25000:
        fin_pts = 14
        reasons.append(f"Significant financial loss (> ₹25,000): +14 pts (max 20)")
    elif loss_val > 0:
        fin_pts = 8
        reasons.append(f"Financial loss recorded (₹{loss_val:,.0f}): +8 pts (max 20)")
    else:
        fin_pts = 0
    factors["financial_factor"] = fin_pts

    # 4. Account Compromised (Max 15 pts)
    if account_compromised:
        acc_pts = 15
        factors["account_compromised_factor"] = acc_pts
        reasons.append("Account takeover / active credential compromise confirmed: +15 pts (max 15)")
    else:
        factors["account_compromised_factor"] = 0

    # 5. Personal Information Exposed (Max 12 pts)
    if personal_info_exposed:
        pii_pts = 12
        factors["pii_factor"] = pii_pts
        reasons.append("Personal identity / sensitive KYC records exposed: +12 pts (max 12)")
    else:
        factors["pii_factor"] = 0

    # 6. Verified Threat Indicators (Max 15 pts)
    indicator_pts = 0
    for ind in threat_indicators:
        s = ind.get("severity", "Medium")
        if s == "Critical":
            indicator_pts += 6
        elif s == "High":
            indicator_pts += 4
        else:
            indicator_pts += 2
    indicator_pts = min(indicator_pts, 15)
    factors["threat_indicators_factor"] = indicator_pts
    if indicator_pts > 0:
        reasons.append(f"{len(threat_indicators)} threat indicator(s) verified: +{indicator_pts} pts (max 15)")

    # 7. ML Confidence Factor (Max 15 pts)
    conf_pts = round((confidence ** 1.3) * 15, 1)
    factors["confidence_factor"] = conf_pts
    conf_pct = confidence * 100
    if conf_pct >= 85:
        reasons.append(f"High ML prediction confidence ({conf_pct:.1f}%): +{conf_pts} pts (max 15)")
    elif conf_pct >= 60:
        reasons.append(f"Moderate ML prediction confidence ({conf_pct:.1f}%): +{conf_pts} pts (max 15)")

    # Sum total and clamp
    raw_total = (
        factors["category_factor"]
        + factors["severity_factor"]
        + factors["financial_factor"]
        + factors["account_compromised_factor"]
        + factors["pii_factor"]
        + factors["threat_indicators_factor"]
        + factors["confidence_factor"]
    )
    final_score = int(round(max(0, min(100, raw_total))))

    # Risk Level mapping
    if final_score >= 75:
        risk_level = "CRITICAL"
    elif final_score >= 50:
        risk_level = "HIGH"
    elif final_score >= 25:
        risk_level = "MEDIUM"
    else:
        risk_level = "LOW"

    return final_score, risk_level, reasons, factors


def get_recommended_actions(predicted_category, threat_indicators=None):
    """Contextual operational next-steps based on cybercrime category."""
    threat_indicators = threat_indicators or []
    actions = []

    category_actions = {
        "Phishing Attack": [
            "Do NOT click on any links, open attachments, or input OTPs on the referenced page.",
            "Contact your bank helpline to report potential credential leak and update online banking password.",
            "Submit the deceptive SMS header or phishing domain to the National Anti-Phishing Desk (report.phishing@cert-in.org.in).",
            "Enable app-based Multi-Factor Authentication (MFA) across netbanking and primary email accounts."
        ],
        "Online Financial Fraud": [
            "Dial National Cyber Crime Helpline (1930) immediately to register a transaction freeze within the Golden Hour window.",
            "Contact the issuing bank's fraud desk to block affected debit/credit cards and freeze associated UPI handles.",
            "Preserve bank statements showing the exact UTR/RRN numbers, transaction timestamps, and beneficiary VPA/account.",
            "Lodge formal complaint on cybercrime.gov.in with all transactional evidence."
        ],
        "Identity Theft": [
            "Alert family and contacts regarding fraudulent impersonation accounts.",
            "File an official impersonation takedown report with the platform safety team citing original government ID.",
            "Check credit bureaus (CIBIL/Experian) to verify no unauthorized credit lines or loans were initiated.",
            "Lodge an identity theft FIR at the jurisdictional cyber police station under Section 66C IT Act."
        ],
        "Cyber Bullying / Harassment": [
            "Preserve timestamped screenshots and video recordings of all harassing messages, handles, and URLs.",
            "Do NOT engage with or transfer funds to the perpetrator.",
            "Report offensive handles to the intermediary safety moderation team.",
            "File a formal complaint under Section 67 IT Act and Section 354D IPC / Section 78 BNSS."
        ],
        "Ransomware / Malware": [
            "Immediately isolate the infected device by disconnecting from Wi-Fi, LAN, and all networked shared drives.",
            "Do NOT pay ransom; preserve the ransom note (.txt), encrypted sample files, and system event logs.",
            "Notify CERT-In Incident Response Team (incident@cert-in.org.in) within mandatory reporting timelines.",
            "Rebuild endpoints strictly from verified, offline and immutable backups."
        ],
        "Data Breach": [
            "Revoke all active administrative API tokens, database passwords, and SSH keys.",
            "Examine firewall, web server access, and cloud audit logs (AWS CloudTrail / Azure Monitor) to isolate ingress vector.",
            "Issue formal mandatory notification to CERT-In and data protection authorities.",
            "Commission a forensic audit to verify the extent of compromised customer records."
        ],
        "Account Takeover": [
            "Attempt immediate credential recovery using registered alternate recovery channels.",
            "Terminate all active user sessions and revoke third-party authorized OAuth tokens.",
            "Contact telecom provider if SIM swap is suspected to verify identity and restore cellular access.",
            "Update passwords on all financial and personal accounts using unique passphrases."
        ],
        "Social Engineering": [
            "Immediately sever communication with any caller claiming urgency, police authority, or 'digital arrest'.",
            "Never install remote management software (AnyDesk, TeamViewer) at the request of an unknown caller.",
            "Verify caller credentials independently using published official landline numbers.",
            "Educate family members regarding pretexting tactics and bogus legal threats."
        ],
        "Online Shopping Fraud": [
            "Initiate a chargeback dispute with your credit/debit card issuer or UPI merchant aggregator.",
            "Preserve merchant order confirmation, seller communication, and courier tracking details.",
            "Report the fraudulent storefront to the e-commerce marketplace and consumer grievance portal.",
            "Review transaction history for recurrent unauthorized auto-debits."
        ],
        "Investment/Crypto Fraud": [
            "Halt all further deposits; cease communication with administrators demanding 'release fees'.",
            "Preserve complete chat exports, deposit crypto addresses, and transaction hashes (TXIDs).",
            "Lodge complaint with cyber cell financial investigation unit.",
            "Document beneficiary bank accounts and crypto exchange deposit addresses."
        ]
    }

    actions.extend(category_actions.get(predicted_category, [
        "Preserve all digital evidence including screenshots, headers, and logs.",
        "File an incident complaint with the national cyber crime portal.",
        "Change credentials and review active session authorizations."
    ]))

    # Specific indicator actions
    for ind in threat_indicators:
        code = ind.get("code", "")
        if code == "OTP_REQUEST":
            actions.append("Change your netbanking and UPI PINs immediately.")
            break
        elif code in ["MALWARE_PAYLOAD", "MALWARE"]:
            actions.append("Execute an offline endpoint malware scan and purge unauthorized remote tools.")
            break

    # De-duplicate while preserving order
    seen = set()
    unique_actions = []
    for a in actions:
        if a not in seen:
            seen.add(a)
            unique_actions.append(a)

    return unique_actions


def find_similar_complaints(new_description, existing_complaints, top_k=4):
    """
    Compare complaint narrative against existing database records using TF-IDF cosine similarity.
    Returns the top K similar complaints with similarity percentage.
    """
    if not existing_complaints or not new_description.strip():
        return []

    try:
        vectorizer, _ = get_model_and_vectorizer()
        all_descriptions = [c.get('description', '') for c in existing_complaints]

        db_vecs = vectorizer.transform(all_descriptions)
        new_vec = vectorizer.transform([new_description])

        sims = cosine_similarity(new_vec, db_vecs)[0]

        results = []
        for idx, sim in enumerate(sims):
            sim_pct = round(float(sim) * 100, 1)
            if sim_pct >= 15.0:
                item = existing_complaints[idx]
                results.append({
                    "id": item.get("id"),
                    "complaint_id": item.get("complaint_id", f"CC-CASE-{item.get('id')}"),
                    "similarity": sim_pct,
                    "category": item.get("predicted_category") or item.get("crime_type") or item.get("category", "Unknown"),
                    "description": item.get("description", ""),
                    "location": item.get("city") or item.get("location", "Unknown"),
                    "state": item.get("state", "Unknown"),
                    "risk_score": item.get("risk_score", 0),
                    "risk_level": item.get("risk_level", "LOW"),
                    "current_status": item.get("current_status") or item.get("status", "New")
                })

        results.sort(key=lambda x: x["similarity"], reverse=True)
        return results[:top_k]
    except Exception as e:
        print(f"Error finding similar complaints: {e}")
        return []


def explain_prediction_tokens(text, vectorizer, classifier, top_k=6):
    """Extract top contributing n-grams from the narrative for explainable AI."""
    if not text.strip() or vectorizer is None:
        return []

    try:
        vec = vectorizer.transform([text])
        feature_names = np.array(vectorizer.get_feature_names_out())
        indices = vec.nonzero()[1]

        if len(indices) == 0:
            return []

        weights = vec.data
        words = feature_names[indices]

        features_and_weights = list(zip(words, weights))
        features_and_weights.sort(key=lambda x: x[1], reverse=True)

        explained = []
        for word, w in features_and_weights[:top_k]:
            explained.append({
                "term": str(word),
                "weight": round(float(w), 4),
                "influence_pct": round(float(w) * 100, 1),
                "relevance": "High" if w > 0.3 else "Medium"
            })
        return explained
    except Exception:
        return []


def analyze_complaint(
    description,
    reported_category="Phishing Attack",
    severity="Medium",
    financial_loss=0.0,
    personal_info_exposed=False,
    account_compromised=False,
    existing_complaints=None
):
    """Full end-to-end AI analysis of a cyber crime complaint narrative."""
    vectorizer, classifier = get_model_and_vectorizer()

    # 1. ML Prediction
    text_vec = vectorizer.transform([description])
    predicted_category = classifier.predict(text_vec)[0]

    # Prediction confidence
    probs = classifier.predict_proba(text_vec)[0]
    classes = list(classifier.classes_)
    pred_idx = classes.index(predicted_category)
    confidence = float(probs[pred_idx])
    confidence_pct = round(confidence * 100, 1)

    # Probability distribution across all 10 categories
    class_probabilities = [
        {"category": cat, "confidence": round(float(probs[i]) * 100, 1)}
        for i, cat in enumerate(classes)
    ]
    class_probabilities.sort(key=lambda x: x["confidence"], reverse=True)

    # 2. Explainable Token Attribution
    top_tokens = explain_prediction_tokens(description, vectorizer, classifier)

    # 3. Threat Indicators & IOCs
    threat_indicators = detect_threat_indicators(
        description,
        personal_info_exposed=personal_info_exposed,
        account_compromised=account_compromised
    )

    # 4. Dynamic Explainable Risk Score
    risk_score, risk_level, reasons, risk_breakdown = calculate_risk_score(
        predicted_category=predicted_category,
        confidence=confidence,
        severity=severity,
        financial_loss=financial_loss,
        personal_info_exposed=personal_info_exposed,
        account_compromised=account_compromised,
        threat_indicators=threat_indicators
    )

    # 5. Safety Recommendations
    recommended_actions = get_recommended_actions(
        predicted_category=predicted_category,
        threat_indicators=threat_indicators
    )

    # 6. Similar historical complaints
    similar_complaints = find_similar_complaints(
        new_description=description,
        existing_complaints=existing_complaints or [],
        top_k=4
    )

    # 7. Alert details for High/Critical Risk
    is_high_risk_alert = (risk_score >= 75)
    alert_details = None
    if is_high_risk_alert:
        alert_details = {
            "title": f"PRIORITY CYBERCRIME ALERT: {predicted_category.upper()}",
            "risk_score": risk_score,
            "risk_level": risk_level,
            "crime": predicted_category,
            "reasons": " + ".join(reasons[:3]),
            "recommendation": "Priority incident escalation recommended. Potential for substantial financial, identity, or infrastructure harm.",
            "disclaimer": "Automated analytical triage for operational prioritization; not legal adjudication."
        }

    return {
        "predicted_category": predicted_category,
        "confidence": confidence_pct,
        "confidence_raw": confidence,
        "model_name": "Calibrated Linear Classifier (TF-IDF + Linear SVM/NB)",
        "model_version": "cybercrime-classifier-v2",
        "risk_score": risk_score,
        "risk_level": risk_level,
        "risk_breakdown": risk_breakdown,
        "reasons": reasons,
        "threat_indicators": threat_indicators,
        "recommended_actions": recommended_actions,
        "similar_complaints": similar_complaints,
        "class_probabilities": class_probabilities[:6],
        "top_tokens": top_tokens,
        "is_high_risk_alert": is_high_risk_alert,
        "alert_details": alert_details
    }
