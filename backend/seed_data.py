"""
Seed the CyberNexa database with realistic Indian cybercrime complaint data.
Based on real complaint patterns from NCRB reports, CERT-In advisories, and
cybercrime.gov.in published case summaries (anonymized/synthetic).

Run once: python seed_data.py
"""

from database import init_db, get_db_connection
from auth_service import create_user
from werkzeug.security import generate_password_hash

SAMPLE_COMPLAINTS = [
    # ── Phishing Attack ─────────────────────────────────────────────────
    ("Phishing Attack", "I received an SMS claiming to be from SBI bank stating my account will be blocked. It asked me to click a link and verify my KYC details. I clicked and entered my debit card number and OTP. Later I found Rs 45,000 debited from my account.", "Mumbai", "High", "Under Investigation"),
    ("Phishing Attack", "Got an email from what appeared to be HDFC Bank asking me to update my net banking credentials within 24 hours. The link looked exactly like the real HDFC website. I entered my username and password. My account was accessed by someone else the next day.", "Delhi", "High", "Under Investigation"),
    ("Phishing Attack", "Received a WhatsApp message saying I won Rs 25 lakh in KBC lottery. They asked for my Aadhaar and PAN details to process the prize. I shared the details but never received any prize money.", "Pune", "Medium", "Pending Review"),
    ("Phishing Attack", "Got a fake IRCTC refund email asking me to click a link to get refund of Rs 1,200. After clicking I was taken to a fake page where I entered my card details. Rs 18,500 was deducted from my account.", "Hyderabad", "High", "Resolved"),
    ("Phishing Attack", "Received fake income tax refund SMS with a link. Entered bank details on the fake site. Rs 32,000 debited within minutes.", "Bengaluru", "High", "Under Investigation"),
    ("Phishing Attack", "Someone sent me a link claiming to be Amazon customer care about a refund. I clicked and gave my card OTP. Lost Rs 9,999.", "Chennai", "Medium", "Pending Review"),
    ("Phishing Attack", "Fake Paytm KYC update message asking to call a number. Called and they asked to install an app. After installation my Paytm wallet was emptied of Rs 15,000.", "Kolkata", "High", "Resolved"),
    ("Phishing Attack", "Received phishing email pretending to be from my company HR asking to update bank details for salary. Unknowingly submitted my salary account details.", "Gurugram", "High", "Under Investigation"),

    # ── Online Financial Fraud ──────────────────────────────────────────
    ("Online Financial Fraud", "I was selling an old phone on OLX. The buyer sent Rs 1 payment as advance using a QR code and then asked me to scan another QR to verify. I scanned and Rs 28,000 was debited from my account.", "Jaipur", "High", "Under Investigation"),
    ("Online Financial Fraud", "Got a call from someone claiming to be from Amazon saying my order was cancelled and I need to confirm my bank account to get a refund. I shared my account details and OTP. Rs 57,000 was transferred from my account.", "Mumbai", "Critical", "Under Investigation"),
    ("Online Financial Fraud", "I was looking for work from home jobs. Found a link online that asked for Rs 2,000 registration fee. After paying they asked for Rs 5,000 more for training kit. Total loss Rs 7,000. No work was provided.", "Delhi", "Medium", "Pending Review"),
    ("Online Financial Fraud", "Received a call from a person claiming to be from RBI saying my bank account was suspicious. Asked me to transfer all funds to a safe government account. Lost Rs 2.4 lakh.", "Lucknow", "Critical", "Under Investigation"),
    ("Online Financial Fraud", "Fake loan app deducted Rs 3,000 as processing fee and Rs 2,000 for insurance before disbursing loan. After collecting fees the app stopped working and no loan was given.", "Ahmedabad", "Medium", "Resolved"),
    ("Online Financial Fraud", "A person posing as TRAI officer called and said my mobile number is involved in illegal activities and will be disconnected. Asked me to transfer Rs 10,000 to a safe account. Later realised it was a scam.", "Chandigarh", "High", "Pending Review"),
    ("Online Financial Fraud", "I paid Rs 45,000 advance rent via GPay to a landlord who showed me flat photos online. After payment the landlord became unreachable and the flat did not exist.", "Bengaluru", "High", "Under Investigation"),
    ("Online Financial Fraud", "Received Rs 5,000 in my account by mistake, then a caller asked me to return it. While returning, they tricked me into transferring Rs 50,000 using screen share app.", "Pune", "High", "Under Investigation"),
    ("Online Financial Fraud", "Online investment scheme promised 30% monthly returns. Invested Rs 1.5 lakh. Initially got small returns to build trust. Then they disappeared with entire investment.", "Hyderabad", "Critical", "Under Investigation"),
    ("Online Financial Fraud", "Fake electricity bill payment portal. Paid electricity bill of Rs 2,400 on a fake site. Got an additional debit of Rs 11,500 from saved card details.", "Chennai", "Medium", "Resolved"),

    # ── Ransomware / Malware ────────────────────────────────────────────
    ("Ransomware / Malware", "All files on my office computer were encrypted. A message appeared demanding Rs 5 lakh in Bitcoin to decrypt the files. The attack came through a suspicious email attachment I opened.", "Delhi", "Critical", "Under Investigation"),
    ("Ransomware / Malware", "My laptop was infected after visiting a software download site. A popup appeared claiming to be Windows Security asking me to call a toll free number. Called and gave remote access. Lost Rs 12,000.", "Mumbai", "High", "Resolved"),
    ("Ransomware / Malware", "Company servers were attacked with ransomware. All backup files also got encrypted. Attackers demanded $5,000 in cryptocurrency. Business operations stopped for 3 days.", "Bengaluru", "Critical", "Under Investigation"),
    ("Ransomware / Malware", "Downloaded a free movie from a torrent site. My PC started showing antivirus warnings. All my personal photos were encrypted. Demanded Rs 50,000 to restore them.", "Pune", "High", "Pending Review"),
    ("Ransomware / Malware", "Received an invoice PDF via email. On opening it a macro ran and my PC got infected with malware. Banking credentials were stolen and Rs 78,000 was transferred.", "Hyderabad", "Critical", "Under Investigation"),
    ("Ransomware / Malware", "My Android phone was infected with banking malware. All OTPs sent to my number were being forwarded to an unknown number. Rs 1.1 lakh debited from my account without my knowledge.", "Kolkata", "Critical", "Under Investigation"),

    # ── Identity Theft ──────────────────────────────────────────────────
    ("Identity Theft", "Someone used my Aadhaar number to get a new SIM card. Using this SIM they accessed my bank account and transferred Rs 85,000 via UPI.", "Delhi", "Critical", "Under Investigation"),
    ("Identity Theft", "A fake Facebook profile was created using my photos and name. The impersonator contacted my friends asking for money claiming I was in a medical emergency.", "Mumbai", "High", "Resolved"),
    ("Identity Theft", "My PAN card was misused to apply for a personal loan of Rs 3 lakh from a digital lending app. I came to know only when I received recovery calls. CIBIL score affected.", "Bengaluru", "Critical", "Under Investigation"),
    ("Identity Theft", "Someone created a matrimonial profile on Shaadi.com using my photos and personal details. Several unknown people are contacting my family using that profile.", "Chennai", "Medium", "Pending Review"),
    ("Identity Theft", "My Aadhaar biometric data was misused at an Aadhaar enabled payment kiosk in another city. Rs 20,000 was withdrawn without my knowledge.", "Hyderabad", "Critical", "Under Investigation"),
    ("Identity Theft", "Discovered an unknown vehicle loan of Rs 4.5 lakh registered in my name using forged documents and my Aadhaar copy obtained from a photocopy shop.", "Pune", "Critical", "Under Investigation"),
    ("Identity Theft", "My passport details were used to book international flight tickets. I received an email confirmation for a flight I never booked to Dubai.", "Delhi", "High", "Under Investigation"),

    # ── Cyber Bullying / Harassment ─────────────────────────────────────
    ("Cyber Bullying / Harassment", "My ex boyfriend is sending me threatening messages daily and has shared morphed intimate photos of me in a WhatsApp group with my family members and colleagues.", "Mumbai", "Critical", "Under Investigation"),
    ("Cyber Bullying / Harassment", "My classmates created a fake Instagram account with my photos and are posting humiliating content. They are also spreading false rumours about me in school WhatsApp groups.", "Delhi", "High", "Pending Review"),
    ("Cyber Bullying / Harassment", "I am receiving hundreds of abusive calls and messages from unknown numbers. Someone posted my phone number on an adult website with my photo saying I am available for services.", "Bengaluru", "Critical", "Under Investigation"),
    ("Cyber Bullying / Harassment", "A former colleague is constantly posting defamatory content about me on LinkedIn and Twitter making false allegations about my professional conduct.", "Hyderabad", "High", "Under Investigation"),
    ("Cyber Bullying / Harassment", "Someone is sending death threats via email and has mentioned knowing my home address. They are threatening to harm my family if I do not pay Rs 5 lakh.", "Chennai", "Critical", "Under Investigation"),
    ("Cyber Bullying / Harassment", "My daughter aged 14 is being bullied in online gaming sessions. Other players are using extremely offensive language, targeting and harassing her specifically.", "Pune", "High", "Pending Review"),
    ("Cyber Bullying / Harassment", "An anonymous account on Twitter is constantly posting edited photos of me in obscene contexts. Despite reporting multiple times Twitter has not taken action.", "Kolkata", "High", "Under Investigation"),

    # ── Data Breach ─────────────────────────────────────────────────────
    ("Data Breach", "Our company CRM database was hacked. Customer data including names, phone numbers, email IDs and transaction history of 50,000 customers was stolen and posted on the dark web.", "Bengaluru", "Critical", "Under Investigation"),
    ("Data Breach", "I received a breach notification that my email and password were found in a data breach from a popular e-commerce website. Same password was used for net banking which was then accessed.", "Delhi", "High", "Resolved"),
    ("Data Breach", "Medical records of patients from our hospital were found being sold on a Telegram channel. Patient names, diagnoses, mobile numbers and Aadhaar numbers were exposed.", "Mumbai", "Critical", "Under Investigation"),
    ("Data Breach", "Employee salary data, PAN numbers, and bank account details of all 200 employees of our company were stolen by an ex-employee before leaving. Data is being misused.", "Pune", "Critical", "Under Investigation"),
    ("Data Breach", "Our school management system was hacked. Student details, parent contact information, and fee payment records of 3,000 students were stolen.", "Hyderabad", "High", "Under Investigation"),
    ("Data Breach", "A SQL injection attack on our startup website exposed all registered user accounts, passwords, and transaction data to the attacker.", "Bengaluru", "Critical", "Under Investigation"),

    # ── Account Takeover ────────────────────────────────────────────────
    ("Account Takeover", "My Instagram account with 50,000 followers was hacked. Password was changed and the account is now posting adult content and scam links to my followers.", "Mumbai", "High", "Under Investigation"),
    ("Account Takeover", "Someone called pretending to be from Google support and convinced me to share a verification code. My Gmail account was taken over and all my business emails accessed.", "Delhi", "High", "Resolved"),
    ("Account Takeover", "My WhatsApp was hacked. The hacker sent messages to all my contacts asking for money claiming I was in trouble. Several contacts transferred money to the hacker.", "Bengaluru", "Critical", "Under Investigation"),
    ("Account Takeover", "My SIM was swapped by someone who visited a mobile store with fake documents. Using the new SIM they took over my net banking and transferred Rs 1.8 lakh.", "Chennai", "Critical", "Under Investigation"),
    ("Account Takeover", "My Zomato account was hacked. The hacker placed orders worth Rs 8,500 using my saved card. Got notification only after multiple orders were placed.", "Hyderabad", "Medium", "Resolved"),
    ("Account Takeover", "My Facebook business page with Rs 50,000 ad credit was taken over. The hacker ran ads on the page and drained all the ad credit.", "Pune", "High", "Under Investigation"),
    ("Account Takeover", "Someone accessed my UPI app after getting OTP through vishing call. Changed the UPI PIN and transferred Rs 35,000 to an unknown account.", "Jaipur", "Critical", "Under Investigation"),

    # ── Social Engineering ──────────────────────────────────────────────
    ("Social Engineering", "Received a call from someone claiming to be from CBI saying my Aadhaar is linked to a drug trafficking case. Demanded Rs 50,000 to clear my name. Paid in fear before realising it was fraud.", "Delhi", "Critical", "Under Investigation"),
    ("Social Engineering", "A person posing as Microsoft technical support called saying my computer had a virus. Asked for remote access and installed software. Later my banking credentials were stolen.", "Mumbai", "High", "Resolved"),
    ("Social Engineering", "Got a call from someone claiming to be from TRAI saying my mobile number is being used for criminal activity and will be blocked in 2 hours unless I pay Rs 15,000 fine.", "Bengaluru", "High", "Pending Review"),
    ("Social Engineering", "Email from someone pretending to be my company CEO asking me to urgently buy 10 Google Play gift cards worth Rs 50,000 for a client meeting. Sent photos before realizing it was fraud.", "Hyderabad", "Critical", "Under Investigation"),
    ("Social Engineering", "Called by fake bank relationship manager who said my FD is maturing and needs to be renewed urgently. Shared OTP thinking it was needed for FD renewal. Rs 1.2 lakh transferred out.", "Chennai", "Critical", "Under Investigation"),
    ("Social Engineering", "A caller posing as customs officer said my parcel from abroad contains drugs and I need to pay clearance fee of Rs 35,000 to avoid arrest. Paid before realising the scam.", "Kolkata", "High", "Under Investigation"),
    ("Social Engineering", "Someone pretending to be from Narcotics Control Bureau called and said I am under surveillance. Demanded Rs 1 lakh to drop the case. Transferred the money in fear.", "Lucknow", "Critical", "Under Investigation"),
    ("Social Engineering", "Received WhatsApp call from someone claiming to be an old friend who needed urgent help. Asked for Rs 20,000 for medical emergency. Transferred before calling back on original number.", "Pune", "Medium", "Resolved"),
]

CITIES = ["Mumbai", "Delhi", "Bengaluru", "Hyderabad", "Chennai", "Pune", "Kolkata",
          "Jaipur", "Lucknow", "Ahmedabad", "Chandigarh", "Gurugram", "Bhopal", "Nagpur",
          "Visakhapatnam", "Kochi", "Indore", "Vadodara", "Surat", "Patna"]


def seed():
    init_db()
    conn = get_db_connection()

    # Check existing data
    existing = conn.execute("SELECT COUNT(*) FROM complaints").fetchone()[0]
    if existing >= 20:
        print(f"Database already has {existing} complaints. Skipping seed.")
        conn.close()
        return

    # Create a demo user if none exists
    demo_user_id = None
    existing_user = conn.execute("SELECT id FROM users WHERE username='demo_user' COLLATE NOCASE").fetchone()
    if not existing_user:
        cursor = conn.execute(
            "INSERT INTO users (full_name, username, email, password_hash, role) VALUES (?,?,?,?,?)",
            ("Demo User", "demo_user", "demo@cybernexa.com",
             generate_password_hash("Demo@Cyber2024", method="scrypt"), "USER")
        )
        conn.commit()
        demo_user_id = cursor.lastrowid
        print(f"Created demo_user (id={demo_user_id})")
    else:
        demo_user_id = existing_user["id"]
        print(f"Using existing demo_user (id={demo_user_id})")

    # Seed complaints spread over last 6 months
    from datetime import datetime, timedelta
    import random
    random.seed(42)

    inserted = 0
    base_date = datetime.now() - timedelta(days=180)

    for i, (category, description, location, severity, status) in enumerate(SAMPLE_COMPLAINTS):
        # Spread dates across last 6 months
        days_offset = int((i / len(SAMPLE_COMPLAINTS)) * 180) + random.randint(0, 5)
        complaint_date = base_date + timedelta(days=days_offset)
        date_str = complaint_date.strftime('%Y-%m-%d %H:%M:%S')

        conn.execute(
            "INSERT INTO complaints (user_id, category, description, location, severity, status, created_at) VALUES (?,?,?,?,?,?,?)",
            (demo_user_id, category, description, location, severity, status, date_str)
        )
        inserted += 1

    conn.commit()
    conn.close()

    print(f"\nSeeded {inserted} real-world cybercrime complaints")
    print(f"Categories covered: Phishing, Financial Fraud, Ransomware, Identity Theft,")
    print(f"                    Cyber Bullying, Data Breach, Account Takeover, Social Engineering")
    print(f"Cities covered: Mumbai, Delhi, Bengaluru, Hyderabad, Chennai, Pune, Kolkata, and more")
    print(f"\nLogin as demo_user / Demo@Cyber2024 to see all data, or login as BINDUSHREE G to see your own.")
    print(f"Admin can see all data after login.")


if __name__ == "__main__":
    seed()
