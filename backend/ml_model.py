"""
CyberNexa ML Model — TF-IDF + Logistic Regression cybercrime classifier.

Trained on a curated synthetic dataset of cybercrime complaint descriptions.
Model is saved/loaded from model.pkl alongside metrics.json.

Usage:
    from ml_model import load_or_train, predict_complaint
    load_or_train()   # call once at startup
    result = predict_complaint("I received a fake bank message...")
"""

import json
import os
import warnings

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score, classification_report, confusion_matrix, f1_score,
    precision_score, recall_score,
)
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline

warnings.filterwarnings("ignore")

MODEL_DIR = os.path.dirname(__file__)
MODEL_PATH = os.path.join(MODEL_DIR, "model.pkl")
METRICS_PATH = os.path.join(MODEL_DIR, "model_metrics.json")

# ──────────────────────────────────────────────
# Training dataset — synthetic cybercrime complaint descriptions
# ──────────────────────────────────────────────
TRAINING_DATA = [
    # ── Phishing Attack ──────────────────────────────────────────────────
    ("I received an email claiming to be from my bank asking me to verify my account by clicking a link.", "Phishing Attack"),
    ("A suspicious SMS arrived saying my account will be suspended unless I verify my details immediately.", "Phishing Attack"),
    ("Someone sent me a message pretending to be from HDFC Bank asking for my OTP.", "Phishing Attack"),
    ("I got a fake email from what appeared to be Amazon asking me to confirm my payment details.", "Phishing Attack"),
    ("A message told me to click a link to update my KYC details or my account would be blocked.", "Phishing Attack"),
    ("I received a phishing email disguised as an official income tax refund notice.", "Phishing Attack"),
    ("Fake ICICI bank SMS asked me to click a link to reactivate my account.", "Phishing Attack"),
    ("I was sent an email with a link to a fake SBI login page.", "Phishing Attack"),
    ("A fraudulent WhatsApp message claimed to be from PayPal asking for my login credentials.", "Phishing Attack"),
    ("Someone sent me a link claiming my Google account was hacked and I needed to reset my password immediately.", "Phishing Attack"),
    ("I clicked on a fake bank website link and entered my debit card details.", "Phishing Attack"),
    ("A fake IRCTC email asked me to click a link to claim a refund on my cancelled ticket.", "Phishing Attack"),
    ("I received a phishing message pretending to be from SBI alerting me of suspicious login activity.", "Phishing Attack"),
    ("Fake email from Income Tax Department asked me to click a link for a refund of Rs 9500.", "Phishing Attack"),
    ("Someone sent me a fake Axis Bank SMS with a link to verify my net banking credentials.", "Phishing Attack"),
    ("I received a spoofed email from my company's HR asking me to urgently click a link and update personal info.", "Phishing Attack"),
    ("A message arrived claiming I had won a lottery and should click a link to collect the prize.", "Phishing Attack"),
    ("I received a fake customs clearance notice asking me to pay a fee via a link.", "Phishing Attack"),
    ("An email pretending to be from Microsoft asked me to verify my Office 365 credentials via a link.", "Phishing Attack"),
    ("A fake EPFO message asked me to visit a link and enter my PF account details.", "Phishing Attack"),

    # ── Online Financial Fraud ────────────────────────────────────────────
    ("An unauthorized debit of Rs 15,000 appeared on my credit card statement for a transaction I never made.", "Online Financial Fraud"),
    ("Someone transferred money from my bank account without my knowledge using internet banking.", "Online Financial Fraud"),
    ("I received a call from a person claiming to be a bank employee asking for my CVV and card expiry.", "Online Financial Fraud"),
    ("A person asked me to download an app to receive a refund and my account was debited instead.", "Online Financial Fraud"),
    ("I sent money via UPI to a seller who turned out to be a scammer and never delivered the product.", "Online Financial Fraud"),
    ("I was promised a high return on investment and transferred money but never got it back.", "Online Financial Fraud"),
    ("Fake cashback offer on a payment app tricked me into entering my PIN and money was debited.", "Online Financial Fraud"),
    ("I received an SMS saying I won Rs 50,000 and paid a processing fee but received nothing.", "Online Financial Fraud"),
    ("Someone used my credit card number for an international online transaction worth Rs 35,000.", "Online Financial Fraud"),
    ("A fraudulent refund caller said they would return money to my account and instead debited Rs 20,000.", "Online Financial Fraud"),
    ("I was tricked into scanning a QR code to receive a payment but money was debited from my account.", "Online Financial Fraud"),
    ("A stranger on OLX asked me to pay an advance for a product and then disappeared.", "Online Financial Fraud"),
    ("My Paytm wallet was debited Rs 8,000 after I shared a payment link with a stranger.", "Online Financial Fraud"),
    ("I made an online payment on a fake e-commerce site for electronics that was never delivered.", "Online Financial Fraud"),
    ("A job offer required a registration fee payment and the recruiter disappeared after receiving money.", "Online Financial Fraud"),
    ("Someone posing as a customs officer demanded money to release a parcel that never existed.", "Online Financial Fraud"),
    ("I received a request to pay a small fee to unlock a prize and the fee kept increasing.", "Online Financial Fraud"),
    ("A fraudulent mutual fund scheme asked for investment and I lost Rs 1.5 lakh.", "Online Financial Fraud"),
    ("I paid advance rent via GPay to a landlord who had listed a fake property.", "Online Financial Fraud"),
    ("Fake loan app charged processing fees and then disappeared without disbursing any loan.", "Online Financial Fraud"),

    # ── Identity Theft ────────────────────────────────────────────────────
    ("Someone used my Aadhaar number to open a new SIM card and bank account without my knowledge.", "Identity Theft"),
    ("A fake social media profile was created using my name and photos to scam my friends.", "Identity Theft"),
    ("My PAN card details were misused to apply for a loan I never requested.", "Identity Theft"),
    ("I found my personal details listed on the dark web after a data breach.", "Identity Theft"),
    ("Someone stole my driving licence details to create a fake identity document.", "Identity Theft"),
    ("My voter ID details were used fraudulently by another person to cast a vote.", "Identity Theft"),
    ("My email address and phone number were used to register accounts on multiple platforms without permission.", "Identity Theft"),
    ("A person impersonating me contacted my employer to extract personal information.", "Identity Theft"),
    ("My Aadhaar-linked mobile number was ported to another operator without my consent.", "Identity Theft"),
    ("Someone filed a fake insurance claim using my identity and health documents.", "Identity Theft"),
    ("My personal photographs were used to create a fake matrimonial profile.", "Identity Theft"),
    ("A fraudulent loan was taken in my name using forged documents and my stolen identity.", "Identity Theft"),
    ("My credit score was damaged because loans were opened in my name without my knowledge.", "Identity Theft"),
    ("A stranger used my biometric data to withdraw money from an Aadhaar-enabled payment kiosk.", "Identity Theft"),
    ("My passport details were used to book flight tickets by someone else.", "Identity Theft"),
    ("An impersonator used my name and credentials to apply to multiple universities on my behalf.", "Identity Theft"),
    ("Someone registered a company using my documents without my consent.", "Identity Theft"),
    ("My personal information leaked from a hospital database was used by fraudsters.", "Identity Theft"),
    ("Someone created a WhatsApp account with my photo and is contacting my family asking for money.", "Identity Theft"),
    ("A fake profile using my photos was used on a dating platform to defraud other users.", "Identity Theft"),

    # ── Ransomware / Malware ──────────────────────────────────────────────
    ("All files on my computer were encrypted and a ransom note appeared demanding payment in Bitcoin.", "Ransomware / Malware"),
    ("My laptop was infected with ransomware after I opened an email attachment from an unknown sender.", "Ransomware / Malware"),
    ("A malware program installed itself on my device and started sending spam emails from my account.", "Ransomware / Malware"),
    ("After visiting a suspicious website my computer slowed down and started showing constant popup alerts.", "Ransomware / Malware"),
    ("A keylogger was installed on my office computer that captured all my login credentials.", "Ransomware / Malware"),
    ("My files were locked by ransomware and a message demanded Rs 5,00,000 to unlock them.", "Ransomware / Malware"),
    ("A trojan disguised as a software update was installed and my banking passwords were stolen.", "Ransomware / Malware"),
    ("My computer displays a fake Windows warning saying I have a virus and to call a toll-free number.", "Ransomware / Malware"),
    ("Company servers were hit by ransomware and all critical data was encrypted and held hostage.", "Ransomware / Malware"),
    ("Spyware secretly recorded my screen and webcam footage and sent it to a remote attacker.", "Ransomware / Malware"),
    ("I downloaded a free movie from a torrent and it installed a virus that corrupted my files.", "Ransomware / Malware"),
    ("A fake antivirus software was installed that demanded payment to remove threats it had itself planted.", "Ransomware / Malware"),
    ("My phone was infected with malware that sent bulk SMS messages from my number without my knowledge.", "Ransomware / Malware"),
    ("After clicking a malicious link in an SMS all my photos were encrypted and I cannot access them.", "Ransomware / Malware"),
    ("A worm spread through our office network and deleted important files from all connected computers.", "Ransomware / Malware"),
    ("My Android phone was infected with banking malware that intercepted all OTP messages.", "Ransomware / Malware"),
    ("I received a fake invoice PDF that installed a trojan when I opened it.", "Ransomware / Malware"),
    ("My backup drives were also encrypted when the ransomware spread across my local network.", "Ransomware / Malware"),
    ("A fileless malware attack compromised my system memory and stole credentials without leaving files.", "Ransomware / Malware"),
    ("Remote access trojan was found on my home computer that allowed attackers to control it remotely.", "Ransomware / Malware"),

    # ── Cyber Bullying / Harassment ───────────────────────────────────────
    ("Someone is sending me abusive messages every day threatening to harm me if I do not comply.", "Cyber Bullying / Harassment"),
    ("My classmate created a fake Instagram account and posted humiliating content about me.", "Cyber Bullying / Harassment"),
    ("I am receiving repeated threatening phone calls from an unknown number asking for money.", "Cyber Bullying / Harassment"),
    ("Someone is posting personal information about me online to defame me.", "Cyber Bullying / Harassment"),
    ("A group on WhatsApp is spreading false rumors about me using morphed photos.", "Cyber Bullying / Harassment"),
    ("My ex-partner is threatening to share intimate images of me online unless I pay them money.", "Cyber Bullying / Harassment"),
    ("Someone is trolling me relentlessly on Twitter with offensive comments and fake accusations.", "Cyber Bullying / Harassment"),
    ("A former colleague is cyberstalking me and commenting on every post I make on social media.", "Cyber Bullying / Harassment"),
    ("I received a threatening email saying they know where I live and will harm my family.", "Cyber Bullying / Harassment"),
    ("An anonymous account is sending my phone number to strangers and asking them to harass me.", "Cyber Bullying / Harassment"),
    ("Someone is impersonating me on social media and sending offensive messages to my contacts.", "Cyber Bullying / Harassment"),
    ("Morphed obscene images of me were shared in a group chat without my consent.", "Cyber Bullying / Harassment"),
    ("I have been the victim of coordinated online harassment from multiple fake accounts.", "Cyber Bullying / Harassment"),
    ("Someone is blackmailing me with screenshots of private conversations taken out of context.", "Cyber Bullying / Harassment"),
    ("A student is being bullied in online classes by classmates who mute them and post mean comments.", "Cyber Bullying / Harassment"),
    ("I am being sexually harassed via direct messages on Instagram by an unknown person.", "Cyber Bullying / Harassment"),
    ("My phone number was shared on pornographic websites without my consent and I keep receiving lewd calls.", "Cyber Bullying / Harassment"),
    ("A stalker is tracking my location by monitoring my social media check-ins.", "Cyber Bullying / Harassment"),
    ("Someone created a fake matrimonial profile with my photos to damage my reputation.", "Cyber Bullying / Harassment"),
    ("My child is being bullied in online games with offensive language and threats.", "Cyber Bullying / Harassment"),

    # ── Data Breach ───────────────────────────────────────────────────────
    ("Our company database was hacked and customer personal data including email and phone was stolen.", "Data Breach"),
    ("I received a notification that my email and password were found in a data breach.", "Data Breach"),
    ("Sensitive medical records of patients were exposed due to a hospital server compromise.", "Data Breach"),
    ("My login credentials were found leaked on the dark web after an e-commerce site was hacked.", "Data Breach"),
    ("Our internal employee salary data was accessed by an unauthorized party and leaked online.", "Data Breach"),
    ("A third party vendor leaked our client database containing personal and financial information.", "Data Breach"),
    ("Confidential business contracts and trade secrets were stolen from our cloud storage.", "Data Breach"),
    ("Our mobile app server was compromised exposing the personal data of 50,000 users.", "Data Breach"),
    ("I discovered my credit card information being sold on a dark web marketplace.", "Data Breach"),
    ("An insider threat stole and sold our customer database to a competitor.", "Data Breach"),
    ("Our school management system was breached exposing student and parent contact details.", "Data Breach"),
    ("A government portal was hacked and voter registration data was accessed without authorization.", "Data Breach"),
    ("Proprietary source code was stolen from our software company by a malicious actor.", "Data Breach"),
    ("Our API was misconfigured and exposed private user data publicly for several hours.", "Data Breach"),
    ("An unauthorized person accessed our backup server and copied sensitive customer records.", "Data Breach"),
    ("Login credentials for internal tools were leaked when a developer accidentally pushed them to GitHub.", "Data Breach"),
    ("A SQL injection attack on our website exposed all user accounts and passwords.", "Data Breach"),
    ("Our HR system was breached and employee PAN, Aadhaar, and bank details were accessed.", "Data Breach"),
    ("I found my personal data including address and phone number listed on a fraudster website.", "Data Breach"),
    ("A cloud misconfiguration exposed our private S3 bucket containing sensitive customer documents.", "Data Breach"),

    # ── Account Takeover ──────────────────────────────────────────────────
    ("My Instagram account was hacked and the attacker changed the email and password locking me out.", "Account Takeover"),
    ("Someone accessed my Gmail account and sent fraudulent emails to all my contacts.", "Account Takeover"),
    ("My WhatsApp was hijacked by someone who convinced me to share my OTP over the phone.", "Account Takeover"),
    ("My Facebook account was taken over and is being used to scam my friends.", "Account Takeover"),
    ("Someone reset my bank account password using SIM cloning and withdrew all my money.", "Account Takeover"),
    ("My Netflix account was hacked and changed to a different email address.", "Account Takeover"),
    ("An attacker bypassed my two-factor authentication and accessed my crypto wallet.", "Account Takeover"),
    ("My Amazon account was taken over and used to place fraudulent orders.", "Account Takeover"),
    ("My Twitter account was hijacked and started posting spam cryptocurrency links.", "Account Takeover"),
    ("Someone called me pretending to be from Google support and tricked me into giving access to my account.", "Account Takeover"),
    ("My UPI linked bank account was accessed by someone who changed the PIN.", "Account Takeover"),
    ("My work email account was compromised and used to send phishing emails to colleagues.", "Account Takeover"),
    ("Someone used SIM swap fraud to take over my mobile number and access my banking apps.", "Account Takeover"),
    ("My gaming account was stolen and all virtual currency was transferred out.", "Account Takeover"),
    ("My LinkedIn account was compromised and used to send fake job offers to my connections.", "Account Takeover"),
    ("My cloud storage account was accessed by someone who deleted important files.", "Account Takeover"),
    ("An attacker enrolled a new device in my account after receiving a forwarded OTP.", "Account Takeover"),
    ("Someone added themselves as an authorized user on my credit card account without my consent.", "Account Takeover"),
    ("My government portal account was accessed and my personal details were modified.", "Account Takeover"),
    ("Attacker used credential stuffing to access my email account after a data breach on another site.", "Account Takeover"),

    # ── Social Engineering ────────────────────────────────────────────────
    ("A caller claimed to be from Microsoft technical support and convinced me to give remote access to my PC.", "Social Engineering"),
    ("Someone pretending to be a CBI officer called me and threatened to arrest me for money laundering.", "Social Engineering"),
    ("A person posing as my bank's relationship manager called and asked me to verify my account.", "Social Engineering"),
    ("I was convinced by a fake tech support agent that my computer had a virus and paid Rs 8,000 to fix it.", "Social Engineering"),
    ("A caller claimed to be from TRAI and threatened to disconnect my number unless I paid a fine.", "Social Engineering"),
    ("Someone convinced me they were from Narcotics Control Bureau and demanded money to avoid arrest.", "Social Engineering"),
    ("A person posing as an Aadhaar update official visited my home and took photos of my documents.", "Social Engineering"),
    ("A call center scammer pretended to be from the RBI and asked me to transfer money for KYC update.", "Social Engineering"),
    ("Someone pretending to be my friend in trouble abroad called and asked for emergency funds.", "Social Engineering"),
    ("A fraudster posed as a loan recovery agent and extracted bank account details over a call.", "Social Engineering"),
    ("I was tricked by a fake job recruiter into paying for training materials that were never delivered.", "Social Engineering"),
    ("A scammer impersonated my boss via email and asked me to purchase gift cards urgently.", "Social Engineering"),
    ("Someone called claiming to be from electricity department threatening disconnection unless I paid immediately.", "Social Engineering"),
    ("A scammer posed as an insurance agent and collected premium payment for a fake policy.", "Social Engineering"),
    ("I was deceived into providing my Aadhaar OTP to a caller claiming to be from UIDAI.", "Social Engineering"),
    ("A fraud agent pretended to be from Amazon and said I needed to pay to cancel a suspicious order.", "Social Engineering"),
    ("Someone posed as a senior executive of my company using a similar email domain and asked for fund transfer.", "Social Engineering"),
    ("A fake government contractor asked us to pay GST advance before signing a contract.", "Social Engineering"),
    ("I was convinced by a fake investment advisor to transfer my savings into a fraudulent scheme.", "Social Engineering"),
    ("A caller posing as customs clearance officer demanded duty payment for a package I never ordered.", "Social Engineering"),
]


# ──────────────────────────────────────────────
# Augmentation: add slight variations for robustness
# ──────────────────────────────────────────────
AUGMENTED_DATA = []
for text, label in TRAINING_DATA:
    AUGMENTED_DATA.append((text, label))
    # Add a shortened variant
    words = text.split()
    if len(words) > 14:
        AUGMENTED_DATA.append((" ".join(words[:14]), label))

ALL_DATA = AUGMENTED_DATA

CATEGORIES = sorted(set(label for _, label in TRAINING_DATA))


def _build_pipeline():
    return Pipeline([
        ("tfidf", TfidfVectorizer(
            ngram_range=(1, 2),
            max_features=8000,
            sublinear_tf=True,
            min_df=1,
            strip_accents="unicode",
            analyzer="word",
            token_pattern=r"\b[a-zA-Z][a-zA-Z0-9]*\b",
        )),
        ("clf", LogisticRegression(
            max_iter=2000,
            C=5.0,
            class_weight="balanced",
            solver="lbfgs",
            random_state=42,
        )),
    ])


def train_and_save():
    """Train the model and persist it along with metrics."""
    import joblib

    texts = [t for t, _ in ALL_DATA]
    labels = [l for _, l in ALL_DATA]

    X_train, X_test, y_train, y_test = train_test_split(
        texts, labels, test_size=0.20, random_state=42, stratify=labels
    )

    pipeline = _build_pipeline()
    pipeline.fit(X_train, y_train)

    y_pred = pipeline.predict(X_test)
    y_proba = pipeline.predict_proba(X_test)

    accuracy = float(accuracy_score(y_test, y_pred))
    precision = float(precision_score(y_test, y_pred, average="weighted", zero_division=0))
    recall = float(recall_score(y_test, y_pred, average="weighted", zero_division=0))
    f1 = float(f1_score(y_test, y_pred, average="weighted", zero_division=0))

    report = classification_report(y_test, y_pred, output_dict=True, zero_division=0)
    cm = confusion_matrix(y_test, y_pred, labels=CATEGORIES).tolist()

    metrics = {
        "accuracy": round(accuracy, 4),
        "precision": round(precision, 4),
        "recall": round(recall, 4),
        "f1_score": round(f1, 4),
        "train_samples": len(X_train),
        "test_samples": len(X_test),
        "categories": CATEGORIES,
        "classification_report": report,
        "confusion_matrix": cm,
        "confusion_matrix_labels": CATEGORIES,
        "model_type": "TF-IDF (1-2 gram) + Logistic Regression (multinomial)",
        "vectorizer_features": 8000,
        "algorithm": "LogisticRegression(C=5.0, class_weight=balanced, solver=lbfgs)",
    }

    joblib.dump(pipeline, MODEL_PATH)
    with open(METRICS_PATH, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)

    print(f"[CyberNexa ML] Model trained — accuracy: {accuracy:.1%} | F1: {f1:.1%} | "
          f"train: {len(X_train)} | test: {len(X_test)}")
    return pipeline, metrics


# ──────────────────────────────────────────────
# Runtime state
# ──────────────────────────────────────────────
_pipeline = None
_metrics = None


def load_or_train():
    """Load from disk if available, otherwise train and save."""
    global _pipeline, _metrics
    import joblib

    if os.path.exists(MODEL_PATH) and os.path.exists(METRICS_PATH):
        try:
            _pipeline = joblib.load(MODEL_PATH)
            with open(METRICS_PATH, encoding="utf-8") as f:
                _metrics = json.load(f)
            print(f"[CyberNexa ML] Model loaded — accuracy: {_metrics.get('accuracy', '?'):.1%}")
            return
        except Exception as e:
            print(f"[CyberNexa ML] Load failed ({e}), retraining...")

    _pipeline, _metrics = train_and_save()


def get_metrics():
    """Return stored metrics dict, or None if model not loaded."""
    return _metrics


def predict_complaint(description: str):
    """
    Predict cybercrime category from complaint text.

    Returns:
        dict with predicted_category, confidence (0-1), all_probabilities,
        method, note, and top_features.
    """
    if _pipeline is None:
        # Fallback to keyword matching if model failed to load
        return _keyword_fallback(description)

    text = description.strip()
    if not text:
        return None

    proba = _pipeline.predict_proba([text])[0]
    classes = _pipeline.classes_
    predicted_idx = int(np.argmax(proba))
    predicted_category = classes[predicted_idx]
    confidence = float(proba[predicted_idx])

    all_probabilities = {
        cat: round(float(p), 4)
        for cat, p in sorted(zip(classes, proba), key=lambda x: x[1], reverse=True)
    }

    # Extract top TF-IDF features for the predicted class
    top_features = _get_top_features(text, predicted_category)

    return {
        "predicted_category": predicted_category,
        "confidence": round(confidence, 4),
        "confidence_percent": f"{confidence:.1%}",
        "all_probabilities": all_probabilities,
        "top_features": top_features,
        "method": "TF-IDF + Logistic Regression",
        "note": (
            "Prediction based on a trained TF-IDF Logistic Regression classifier. "
            "Confidence reflects model probability — not a verified legal finding."
        ),
    }


def _get_top_features(text, predicted_category, top_n=5):
    """Return top contributing TF-IDF tokens for the predicted class."""
    try:
        vectorizer = _pipeline.named_steps["tfidf"]
        clf = _pipeline.named_steps["clf"]
        classes = list(clf.classes_)
        if predicted_category not in classes:
            return []
        class_idx = classes.index(predicted_category)
        tfidf_vector = vectorizer.transform([text])
        feature_names = vectorizer.get_feature_names_out()
        coefs = clf.coef_[class_idx]
        # Multiply TF-IDF weight by class coefficient
        scores = (tfidf_vector.toarray()[0] * coefs)
        top_indices = np.argsort(scores)[-top_n:][::-1]
        return [feature_names[i] for i in top_indices if scores[i] > 0]
    except Exception:
        return []


def _keyword_fallback(description):
    """Simple keyword fallback if sklearn model unavailable."""
    KEYWORDS = {
        "Phishing Attack": ["phishing", "fake", "link", "verify", "otp", "bank", "message", "click"],
        "Online Financial Fraud": ["money", "transfer", "payment", "transaction", "debit", "upi", "fraud"],
        "Ransomware / Malware": ["ransomware", "malware", "encrypt", "virus", "ransom", "file", "locked"],
        "Identity Theft": ["identity", "aadhaar", "pan", "fake profile", "impersonation", "stolen"],
        "Cyber Bullying / Harassment": ["bully", "harassment", "threaten", "abuse", "stalk", "blackmail"],
        "Data Breach": ["breach", "leak", "exposed", "database", "hacked", "stolen data"],
        "Account Takeover": ["account", "hacked", "takeover", "password", "social media"],
        "Social Engineering": ["pretend", "fake call", "impersonate", "trick", "urgent", "authority"],
    }
    text_lower = description.lower()
    scores = {cat: sum(1 for kw in kws if kw in text_lower) for cat, kws in KEYWORDS.items()}
    best = max(scores, key=scores.get)
    return {
        "predicted_category": best if scores[best] > 0 else "Cybercrime Report",
        "confidence": None,
        "confidence_percent": "N/A",
        "all_probabilities": {},
        "top_features": [],
        "method": "keyword-fallback",
        "note": "ML model unavailable. Keyword-based fallback was used.",
    }


if __name__ == "__main__":
    print("Training CyberNexa ML model...")
    pipeline, metrics = train_and_save()
    print(f"Accuracy  : {metrics['accuracy']:.1%}")
    print(f"Precision : {metrics['precision']:.1%}")
    print(f"Recall    : {metrics['recall']:.1%}")
    print(f"F1 Score  : {metrics['f1_score']:.1%}")
    print(f"Categories: {', '.join(metrics['categories'])}")
    print()
    load_or_train()
    tests = [
        "I received a fake bank SMS asking me to click a link to verify my account",
        "Someone transferred money from my UPI without my knowledge",
        "My files were encrypted and a ransom demand appeared on screen",
        "Someone created a fake Instagram profile using my photos",
        "I am receiving abusive threatening messages every day",
        "Our company database was exposed in a hack",
        "My Instagram account was hijacked and password changed",
        "A caller claiming to be from CBI threatened to arrest me unless I paid",
    ]
    for t in tests:
        r = predict_complaint(t)
        print(f"  {t[:60]}")
        print(f"    -> {r['predicted_category']} ({r['confidence_percent']})")
        print()
