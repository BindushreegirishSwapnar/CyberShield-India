"""
Nearest police station lookup by city name.
Includes Cybercrime Police Station contacts for major Indian cities.
Data is for educational/demonstration use.
"""

POLICE_STATIONS = {
    # Karnataka
    "bengaluru": {"city": "Bengaluru", "station": "Bengaluru Cybercrime Police Station", "address": "CID Headquarters, Carlton House, Palace Road, Bengaluru - 560001", "phone": "080-22094498", "email": "cid.cybercrime@ksp.gov.in", "helpline": "1930"},
    "bangalore": {"city": "Bengaluru", "station": "Bengaluru Cybercrime Police Station", "address": "CID Headquarters, Carlton House, Palace Road, Bengaluru - 560001", "phone": "080-22094498", "email": "cid.cybercrime@ksp.gov.in", "helpline": "1930"},
    "mysuru": {"city": "Mysuru", "station": "Mysuru Cybercrime Police Station", "address": "SP Office, Mysuru - 570001", "phone": "0821-2415105", "email": "spmys.ksp@gov.in", "helpline": "1930"},
    "hubli": {"city": "Hubli-Dharwad", "station": "Dharwad Cybercrime Police Station", "address": "SP Office, Dharwad - 580001", "phone": "0836-2747500", "email": "spdwd.ksp@gov.in", "helpline": "1930"},
    "mangaluru": {"city": "Mangaluru", "station": "Mangaluru Cybercrime Police Station", "address": "SP Office, Mangaluru - 575001", "phone": "0824-2220808", "email": "spdkd.ksp@gov.in", "helpline": "1930"},

    # Maharashtra
    "mumbai": {"city": "Mumbai", "station": "Mumbai Cyber Crime Cell", "address": "Annex Building, CST Road, Kalina, Santacruz (East), Mumbai - 400098", "phone": "022-26504213", "email": "cybercell@mumbaipolice.org", "helpline": "1930"},
    "pune": {"city": "Pune", "station": "Pune Cyber Crime Cell", "address": "Cyber Crime Cell, Commissioner Office, 2 Sadhu Vaswani Road, Pune - 411001", "phone": "020-26123346", "email": "cybercell@punepolice.gov.in", "helpline": "1930"},
    "nagpur": {"city": "Nagpur", "station": "Nagpur Cyber Crime Cell", "address": "Commissioner of Police, Nagpur - 440001", "phone": "0712-2562930", "email": "cp.nagpur@mahapolice.gov.in", "helpline": "1930"},
    "nashik": {"city": "Nashik", "station": "Nashik Cyber Crime Cell", "address": "SP Office, Nashik - 422001", "phone": "0253-2578000", "email": "spnashik@mahapolice.gov.in", "helpline": "1930"},

    # Delhi
    "delhi": {"city": "New Delhi", "station": "Delhi Cyber Crime Unit (IFSO)", "address": "IFSO Unit, Cyber Crime Wing, DCP Office, New Delhi - 110001", "phone": "011-26867666", "email": "cybercell@delhipolice.gov.in", "helpline": "1930"},
    "new delhi": {"city": "New Delhi", "station": "Delhi Cyber Crime Unit (IFSO)", "address": "IFSO Unit, Cyber Crime Wing, DCP Office, New Delhi - 110001", "phone": "011-26867666", "email": "cybercell@delhipolice.gov.in", "helpline": "1930"},

    # Telangana
    "hyderabad": {"city": "Hyderabad", "station": "Hyderabad Cyber Crime Police Station", "address": "III Floor, CP Office, Basheerbagh, Hyderabad - 500004", "phone": "040-27852468", "email": "cybercrime@tspolice.gov.in", "helpline": "1930"},
    "warangal": {"city": "Warangal", "station": "Warangal Cyber Crime Cell", "address": "CP Office, Hanamkonda, Warangal - 506001", "phone": "0870-2578900", "email": "cpwngl.tspolice@gov.in", "helpline": "1930"},

    # Tamil Nadu
    "chennai": {"city": "Chennai", "station": "Chennai Cyber Crime Cell", "address": "Commissioner of Police Office, Vepery, Chennai - 600007", "phone": "044-28447777", "email": "addlcp-crime@tnpolice.gov.in", "helpline": "1930"},
    "coimbatore": {"city": "Coimbatore", "station": "Coimbatore Cyber Crime Cell", "address": "SP Office, Race Course Road, Coimbatore - 641018", "phone": "0422-2390000", "email": "spcoimbatore@tnpolice.gov.in", "helpline": "1930"},
    "madurai": {"city": "Madurai", "station": "Madurai Cyber Crime Cell", "address": "SP Office, West Veli Street, Madurai - 625001", "phone": "0452-2530193", "email": "spmadurai@tnpolice.gov.in", "helpline": "1930"},

    # Andhra Pradesh
    "visakhapatnam": {"city": "Visakhapatnam", "station": "Visakhapatnam Cyber Crime PS", "address": "SP Office, Suryabagh, Visakhapatnam - 530020", "phone": "0891-2754460", "email": "spvizag.appolice@gov.in", "helpline": "1930"},
    "vijayawada": {"city": "Vijayawada", "station": "Vijayawada Cyber Crime Cell", "address": "Commissioner of Police, Vijayawada - 520001", "phone": "0866-2427425", "email": "cpvjawada@appolice.gov.in", "helpline": "1930"},

    # Gujarat
    "ahmedabad": {"city": "Ahmedabad", "station": "Ahmedabad Cyber Crime Cell", "address": "Police Commissioner Office, Shahibaug, Ahmedabad - 380004", "phone": "079-25621111", "email": "policecommissioner-ahd@gujarat.gov.in", "helpline": "1930"},
    "surat": {"city": "Surat", "station": "Surat Cyber Crime Cell", "address": "CP Office, Athwa, Surat - 395001", "phone": "0261-2451111", "email": "cp-surat@gujarat.gov.in", "helpline": "1930"},

    # Rajasthan
    "jaipur": {"city": "Jaipur", "station": "Jaipur Cyber Crime PS", "address": "Sawai Ram Singh Road, Jaipur - 302001", "phone": "0141-2744000", "email": "cybercell@rajpolice.gov.in", "helpline": "1930"},
    "jodhpur": {"city": "Jodhpur", "station": "Jodhpur Cyber Crime Cell", "address": "SP Office, Jodhpur - 342001", "phone": "0291-2644444", "email": "spjodh@rajpolice.gov.in", "helpline": "1930"},

    # Uttar Pradesh
    "lucknow": {"city": "Lucknow", "station": "UP Cyber Crime PS, Lucknow", "address": "Vibhuti Khand, Gomtinagar, Lucknow - 226010", "phone": "0522-2302266", "email": "cybercrime@uppolice.gov.in", "helpline": "1930"},
    "kanpur": {"city": "Kanpur", "station": "Kanpur Cyber Crime Cell", "address": "Commissioner of Police, Kanpur - 208001", "phone": "0512-2305555", "email": "cp-kanpur@up.gov.in", "helpline": "1930"},
    "agra": {"city": "Agra", "station": "Agra Cyber Crime Cell", "address": "SP Office, Agra - 282001", "phone": "0562-2330600", "email": "spagra@uppolice.gov.in", "helpline": "1930"},
    "varanasi": {"city": "Varanasi", "station": "Varanasi Cyber Crime Cell", "address": "SP Office, Varanasi - 221001", "phone": "0542-2500061", "email": "spvaranasi@uppolice.gov.in", "helpline": "1930"},

    # West Bengal
    "kolkata": {"city": "Kolkata", "station": "Kolkata Cyber Crime PS", "address": "Detective Department, Lal Bazar, Kolkata - 700001", "phone": "033-22143000", "email": "cybercrime@kolkatapolice.gov.in", "helpline": "1930"},

    # Madhya Pradesh
    "bhopal": {"city": "Bhopal", "station": "Bhopal Cyber Crime Cell", "address": "CP Office, Shivaji Nagar, Bhopal - 462001", "phone": "0755-2443500", "email": "cybercell@mppolice.gov.in", "helpline": "1930"},
    "indore": {"city": "Indore", "station": "Indore Cyber Crime Cell", "address": "CP Office, Indore - 452001", "phone": "0731-2702001", "email": "cpindore@mppolice.gov.in", "helpline": "1930"},

    # Punjab
    "chandigarh": {"city": "Chandigarh", "station": "Chandigarh Cyber Crime Cell", "address": "Sector 9, Chandigarh - 160009", "phone": "0172-2740202", "email": "cybercrime@chd.nic.in", "helpline": "1930"},
    "ludhiana": {"city": "Ludhiana", "station": "Ludhiana Cyber Crime Cell", "address": "Commissioner of Police, Ludhiana - 141001", "phone": "0161-2447025", "email": "cp.ludhiana@punjabpolice.gov.in", "helpline": "1930"},

    # Bihar
    "patna": {"city": "Patna", "station": "Bihar Cyber Crime PS, Patna", "address": "Police Headquarters, Bailey Road, Patna - 800001", "phone": "0612-2225901", "email": "cybercrime@biharpolice.gov.in", "helpline": "1930"},

    # Jharkhand
    "ranchi": {"city": "Ranchi", "station": "Jharkhand Cyber Crime PS", "address": "SP Office, Ranchi - 834001", "phone": "0651-2400600", "email": "cybercrime@jhpolice.gov.in", "helpline": "1930"},

    # Odisha
    "bhubaneswar": {"city": "Bhubaneswar", "station": "Odisha Cyber Crime PS", "address": "CID HQ, Unit-5, Bhubaneswar - 751001", "phone": "0674-2394870", "email": "cybercell@odishapolice.gov.in", "helpline": "1930"},

    # Kerala
    "thiruvananthapuram": {"city": "Thiruvananthapuram", "station": "Kerala Cyber Crime PS", "address": "HIL, Museum Road, Thiruvananthapuram - 695001", "phone": "0471-2331717", "email": "cybercell@keralapolice.gov.in", "helpline": "1930"},
    "kochi": {"city": "Kochi", "station": "Kochi Cyber Crime Cell", "address": "Commissioner of Police, Kochi - 682011", "phone": "0484-2395000", "email": "cpkochi@keralapolice.gov.in", "helpline": "1930"},
    "kozhikode": {"city": "Kozhikode", "station": "Kozhikode Cyber Crime Cell", "address": "SP Office, Kozhikode - 673001", "phone": "0495-2721547", "email": "spkozhikode@keralapolice.gov.in", "helpline": "1930"},

    # Haryana
    "gurgaon": {"city": "Gurugram", "station": "Gurugram Cyber Crime PS", "address": "Sector 17, Gurugram - 122001", "phone": "0124-2309010", "email": "cybercrime@haryanapolice.gov.in", "helpline": "1930"},
    "gurugram": {"city": "Gurugram", "station": "Gurugram Cyber Crime PS", "address": "Sector 17, Gurugram - 122001", "phone": "0124-2309010", "email": "cybercrime@haryanapolice.gov.in", "helpline": "1930"},
    "faridabad": {"city": "Faridabad", "station": "Faridabad Cyber Crime Cell", "address": "CP Office, Faridabad - 121001", "phone": "0129-2237000", "email": "cpfaridabad@haryanapolice.gov.in", "helpline": "1930"},

    # Assam
    "guwahati": {"city": "Guwahati", "station": "Guwahati Cyber Crime PS", "address": "Commissioner of Police, Panbazar, Guwahati - 781001", "phone": "0361-2540153", "email": "cybercrime@assampolice.gov.in", "helpline": "1930"},
}

DEFAULT_STATION = {
    "city": "National",
    "station": "National Cyber Crime Reporting Portal",
    "address": "Online reporting portal — available 24/7",
    "phone": "1930",
    "email": "cybercrime@gov.in",
    "helpline": "1930",
    "note": "No specific cybercrime station found for this city. File online at cybercrime.gov.in or call 1930.",
    "online_portal": "https://cybercrime.gov.in",
}

# What to do after each crime type
CRIME_ACTIONS = {
    "Phishing Attack": [
        "Do NOT click any links in the suspicious message.",
        "Forward the phishing message to your bank's fraud number (printed on your card).",
        "Change your email and banking passwords from a secure device immediately.",
        "Report at cybercrime.gov.in under 'Other Cyber Crime' → 'Phishing'.",
        "Call the National Cyber Crime Helpline: 1930.",
        "Preserve the original message as evidence (screenshot + headers).",
    ],
    "Online Financial Fraud": [
        "Immediately call your bank's 24/7 helpline to freeze the account.",
        "File a complaint at cybercrime.gov.in within 24 hours for faster action.",
        "Call 1930 (National Cyber Crime Helpline) — faster resolution within 24 hours.",
        "Note all transaction IDs, reference numbers, and timestamps.",
        "File an FIR at your nearest cybercrime police station.",
        "Do NOT transfer any more money, even if asked to recover the lost amount.",
    ],
    "Ransomware / Malware": [
        "Disconnect the infected device from the internet and all networks IMMEDIATELY.",
        "Do NOT pay the ransom — it does not guarantee file recovery.",
        "Report to CERT-In at incident@cert-in.org.in.",
        "Restore files from a clean, offline backup if available.",
        "Contact your organization's IT security team or a certified cybersecurity professional.",
        "File a complaint at cybercrime.gov.in.",
    ],
    "Identity Theft": [
        "File a complaint immediately at cybercrime.gov.in.",
        "For Aadhaar misuse: lock your biometrics at uidai.gov.in → 'Lock/Unlock Biometrics'.",
        "Contact the bank/service using your identity via their official channel.",
        "For fake profiles: report to the platform (Instagram/Facebook/WhatsApp).",
        "File an FIR at your nearest cybercrime police station.",
        "Monitor your CIBIL/credit score for unauthorized loan applications.",
    ],
    "Cyber Bullying / Harassment": [
        "Do NOT respond or engage with the harasser — block them on all platforms.",
        "Screenshot and preserve all threatening messages as evidence.",
        "Report the account/content to the platform immediately.",
        "File a complaint at cybercrime.gov.in under 'Women/Child Related Crime' if applicable.",
        "Contact NCW helpline: 7827170170 (women) or Childline: 1098 (children).",
        "File an FIR under IT Act Section 67 / IPC 354D at the nearest police station.",
    ],
    "Data Breach": [
        "Change passwords for all affected accounts immediately.",
        "Enable two-factor authentication (2FA) on all important accounts.",
        "Report the breach to CERT-In at incident@cert-in.org.in.",
        "Notify affected users if you are responsible for the breached system.",
        "Monitor bank statements and credit reports for unauthorized activity.",
        "File a complaint at cybercrime.gov.in.",
    ],
    "Account Takeover": [
        "Use the official 'Forgot Password' or account recovery option on the platform.",
        "Recover from a trusted device not used by the attacker.",
        "Change passwords on all accounts where you reused the same password.",
        "Revoke all active sessions in account security settings.",
        "Enable 2FA on the recovered account.",
        "File a complaint at cybercrime.gov.in if money or data was compromised.",
    ],
    "Social Engineering": [
        "Do NOT transfer money or share OTPs with anyone calling claiming to be from a government agency.",
        "Hang up and call the organization directly using the official number from their website.",
        "Report fake government callers at cybercrime.gov.in.",
        "Call 1930 if money was transferred.",
        "File an FIR at your nearest police station.",
        "Warn friends and family about the scam.",
    ],
    "Cybercrime Report": [
        "File a complaint at the National Cyber Crime Reporting Portal: cybercrime.gov.in.",
        "Call the National Cyber Crime Helpline: 1930 (available 24/7).",
        "Preserve all evidence: screenshots, transaction IDs, messages, and timestamps.",
        "Visit your nearest cybercrime police station.",
        "Do NOT delete any messages or evidence until police advise you to.",
    ],
}


def find_station(city: str) -> dict:
    """Return the nearest cybercrime police station for a given city."""
    if not city:
        return DEFAULT_STATION
    key = city.strip().lower()
    # Direct match
    if key in POLICE_STATIONS:
        return POLICE_STATIONS[key]
    # Partial match
    for k, v in POLICE_STATIONS.items():
        if k in key or key in k:
            return v
    return {**DEFAULT_STATION, "searched_city": city}


def get_action_steps(category: str) -> list:
    """Return what-to-do steps for a given crime category."""
    return CRIME_ACTIONS.get(category, CRIME_ACTIONS["Cybercrime Report"])
