"""
CyberNexa Chatbot service.
Provides keyword-matched responses for both Cyber Intelligence and Women Safety queries.
Falls back to RAG retrieval for cyber topics if no direct answer matches.
No external LLM required.
"""

import re

# ── Cyber Intelligence responses ─────────────────────────────────────────────
CYBER_RESPONSES = [
    (r"phish|fake (bank|sms|email|link)|suspicious (link|message|email)",
     "Phishing is a deceptive message designed to steal your credentials or money. "
     "Do NOT click any link in unexpected messages. Verify by calling your bank on the official number printed on your card. "
     "Report the message to your bank's fraud helpline and preserve it as evidence."),

    (r"otp|one.time.password|verification code",
     "Never share an OTP with anyone — not even someone claiming to be from your bank or TRAI. "
     "Legitimate organizations never ask for OTPs over calls or SMS. "
     "If you have shared an OTP, contact your bank immediately to block your account."),

    (r"upi|gpay|paytm|phonepe|payment fraud|money (debit|transfer|sent)",
     "For UPI fraud: immediately call your bank's 24/7 helpline and request a transaction dispute. "
     "File a complaint at cybercrime.gov.in or call the National Cyber Crime Helpline 1930. "
     "Preserve all transaction IDs and screenshots as evidence."),

    (r"ransomware|encrypt|files locked|ransom",
     "Do not pay the ransom. Disconnect the affected device from the network immediately. "
     "Contact your organization's IT security team or a cybersecurity professional. "
     "Report to cert-in.org.in. Restore from clean backups if available."),

    (r"hack(ed)?|account (taken|compromis|stolen)",
     "Immediately change the password from a different device. Enable two-factor authentication. "
     "Revoke all active sessions in account settings. Check for linked apps and remove unknown ones. "
     "Report to the platform and file a complaint at cybercrime.gov.in."),

    (r"identity theft|aadhaar misuse|pan misuse|fake profile",
     "File a complaint with the local cybercrime police station and at cybercrime.gov.in. "
     "For Aadhaar misuse, lock your biometrics at uidai.gov.in. "
     "Contact the platform hosting the fake profile for immediate removal."),

    (r"data breach|my data leaked|personal info (online|exposed)",
     "Change passwords for all affected accounts immediately. Enable 2FA everywhere. "
     "Monitor your bank statements and credit reports for unusual activity. "
     "Report the breach to cert-in.org.in if it involves a company or service provider."),

    (r"social engineering|fake (officer|police|cbi|rbi|trai)|impersonat",
     "Legitimate government agencies never demand money over the phone. "
     "Hang up immediately. Verify by calling the official agency number from their website. "
     "File a complaint at cybercrime.gov.in or call 1930."),

    (r"cyber bully|harass(ment)?|threaten|stalk(ing)?|abuse online",
     "Screenshot and preserve all evidence before blocking. Report to the platform. "
     "File a complaint at cybercrime.gov.in under the harassment/cyberstalking category. "
     "Contact the National Commission for Women helpline: 7827170170."),

    (r"report|complaint|where to report|how to report",
     "You can report cybercrime at:\n"
     "• cybercrime.gov.in — National Cyber Crime Reporting Portal\n"
     "• Call 1930 — National Cyber Crime Helpline\n"
     "• Your nearest cybercrime police station\n"
     "• cert-in.org.in — for technical incidents"),

    (r"predict|what (crime|category)|analyze",
     "Use the Cybercrime Prediction page to submit your complaint. "
     "The AI model will classify it into one of 8 categories: Phishing, Financial Fraud, Ransomware, "
     "Identity Theft, Cyber Bullying, Data Breach, Account Takeover, or Social Engineering."),

    (r"password|secure (my )?account|2fa|two.factor",
     "Use a unique password of 12+ characters for every account. "
     "Enable two-factor authentication (2FA) wherever available. "
     "Use a reputable password manager. Never reuse passwords across sites."),
]

# ── Women Safety responses ────────────────────────────────────────────────────
SAFETY_RESPONSES = [
    (r"follow(ed|ing)?|someone following|being followed",
     "Stay calm and move to a crowded, well-lit area. "
     "Enter a shop, restaurant, or any public building. "
     "Call someone you trust and stay on the line. "
     "If the threat is immediate, call 112 (emergency) or 1091 (Women Helpline). "
     "Use the Emergency Alert button in this app to notify your trusted contacts."),

    (r"harass(ment)?|misbehav|abuse|someone (touch|grab|assault)",
     "You are not alone. Your safety comes first.\n"
     "1. Move to a safe, public location immediately.\n"
     "2. Call 112 for police or 1091 for Women Helpline.\n"
     "3. Use this app's Emergency Alert to notify trusted contacts.\n"
     "4. Start the Voice Recorder to capture evidence.\n"
     "5. If safe to do so, note the perpetrator's description and location."),

    (r"emergency|danger|help|unsafe|attack",
     "TAP THE RED EMERGENCY BUTTON NOW.\n"
     "It will notify your trusted contacts with your location.\n\n"
     "Emergency numbers:\n"
     "• 112 — Police (all emergencies)\n"
     "• 1091 — Women Helpline\n"
     "• 100 — Police\n"
     "• 181 — Mahila Helpline"),

    (r"record|evidence|proof|voice record",
     "Use the Evidence Recorder on the Women Safety page to capture audio evidence discreetly. "
     "Recordings are stored locally on your device and timestamped. "
     "They can be used as evidence in a police complaint. "
     "Start recording before the situation escalates if safe to do so."),

    (r"location|share (my )?location|where am i|gps",
     "Use the Location Sharing feature on the Women Safety page. "
     "It requests your GPS coordinates (requires your permission) and shares them with selected trusted contacts. "
     "Coordinates are NOT stored on any server without your explicit action."),

    (r"trip|alone|travelling|travel alone|going out",
     "Before you leave:\n"
     "1. Tap 'Start Trip' to begin monitoring.\n"
     "2. Share your live location with trusted contacts.\n"
     "3. Set a check-in reminder.\n"
     "When you arrive safely, tap 'I'm Safe' to notify your contacts automatically."),

    (r"contact|trusted|add contact|emergency contact",
     "Add trusted contacts on the Women Safety page under Emergency Contacts. "
     "You can add family members, friends, or colleagues. "
     "They will be notified when you send an emergency alert. "
     "Keep at least 2 active contacts configured."),

    (r"alarm|loud|noise|scare",
     "Tap 'Activate Loud Alarm' on the Women Safety page. "
     "This plays a loud 880Hz alarm through your device speaker to attract attention. "
     "Note: device volume must be up. This is a deterrent — call 112 as well."),

    (r"report|police|file (a )?complaint|fir",
     "To file a complaint for harassment or assault:\n"
     "• Go to your nearest police station\n"
     "• Call 112 immediately for emergencies\n"
     "• Women Helpline: 1091\n"
     "• NCW Helpline: 7827170170\n"
     "• Online: cybercrime.gov.in for online harassment\n"
     "Preserve all evidence (messages, recordings, photos) before filing."),

    (r"safe|i.m safe|reached|arrived",
     "Tap the 'I'm Safe' button to notify your trusted contacts that you have arrived safely. "
     "This will end any active trip and send a safe confirmation (in simulation mode — no real message is sent in this demo)."),

    (r"four.tap|tap (4|four)|trigger",
     "The four-tap trigger is a discreet emergency feature. "
     "Tap the Emergency Alert button 4 times quickly (within your configured time window). "
     "A countdown will appear — confirm to send an alert to your trusted contacts. "
     "You can configure the tap window and countdown in Safety Settings."),

    (r"what (can|should) (i|you)|how (to|do i)|help me",
     "I can help you with:\n"
     "• Emergency steps if you feel unsafe\n"
     "• How to use the Emergency Alert\n"
     "• Recording voice evidence\n"
     "• Sharing your location\n"
     "• Starting a trip\n"
     "• Adding trusted contacts\n"
     "• Filing a police complaint\n\n"
     "Just describe your situation and I'll guide you."),
]

FALLBACK_CYBER = (
    "I can help with cybercrime questions. Try asking about: phishing, OTP fraud, UPI fraud, "
    "ransomware, account hacking, identity theft, data breaches, or how to report a cybercrime."
)

FALLBACK_SAFETY = (
    "I'm here to help with your safety. You can ask me about: emergency steps, how to record evidence, "
    "sharing your location, adding trusted contacts, starting a trip, or what to do if you feel unsafe."
)


def _match(patterns, text):
    t = text.lower().strip()
    for pattern, response in patterns:
        if re.search(pattern, t):
            return response
    return None


def get_cyber_response(message: str, rag_fallback=None) -> dict:
    """Get a cyber intelligence chatbot response."""
    direct = _match(CYBER_RESPONSES, message)
    if direct:
        return {"answer": direct, "source": "CyberNexa Cyber Assistant", "mode": "direct-match"}
    if rag_fallback:
        try:
            result = rag_fallback(message, limit=2)
            if result.get("retrieved_chunks"):
                chunk = result["retrieved_chunks"][0]
                return {
                    "answer": chunk["content"],
                    "source": f"Knowledge base: {chunk['title']} ({chunk['category']})",
                    "mode": "rag-retrieval",
                    "relevance": chunk.get("relevance"),
                }
        except Exception:
            pass
    return {"answer": FALLBACK_CYBER, "source": "CyberNexa Cyber Assistant", "mode": "fallback"}


def get_safety_response(message: str) -> dict:
    """Get a Women Safety chatbot response."""
    direct = _match(SAFETY_RESPONSES, message)
    if direct:
        return {"answer": direct, "source": "CyberNexa Safety Assistant", "mode": "direct-match"}
    return {"answer": FALLBACK_SAFETY, "source": "CyberNexa Safety Assistant", "mode": "fallback"}
