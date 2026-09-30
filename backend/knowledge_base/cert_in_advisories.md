# Indian Computer Emergency Response Team (CERT-In) Technical Advisories

## Document Reference: CERT-IN/ADV/2026-CYBER-09
**Issuing Authority:** Indian Computer Emergency Response Team (CERT-In), Ministry of Electronics & IT (MeitY)  
**Classification:** Public Security Advisory  
**Subject:** Triage and Mitigation of Social Engineering, UPI Fraud, and High-Impact Cyber Attacks

---

### Section 1: Advisory on UPI and Payment Gateway Fraud
1. **Attack Vectors:** Threat actors exploit user trust through fake customer support numbers published on web mapping services and search engines, manipulated QR codes, and fraudulent collect requests.
2. **Key Indicators:**
   - Request to scan a QR code to "receive money" or refunds (technically, QR scanning only authorizes outgoing debits).
   - Coercion to enter UPI PIN into any form claiming to verify credit or claim lottery rewards.
   - Remote screen sharing application installation prompts (e.g. AnyDesk, RustDesk, TeamViewer QuickSupport) to capture SMS authentication and 2-factor OTPs.
3. **Emergency Countermeasures:**
   - Immediately dial the National Cyber Crime Reporting Portal helpline 1930 within the "Golden Hour" (first 2 hours of transaction) to trigger automated account freezing via the Indian Cyber Crime Coordination Centre (I4C) Citizen Financial Cyber Fraud Reporting and Management System (CFCFRMS).
   - De-register UPI application and revoke net-banking device registration.

---

### Section 2: Advisory on Ransomware Incident Triage & Forensic Containment
1. **Attack Vectors:** Phishing emails containing weaponized ZIP or ISO containers, vulnerable exposed RDP ports (TCP 3389), unpatched VPN appliances, and software supply chain compromises.
2. **Key Indicators:**
   - Sudden mass file extension transformations (e.g., .locked, .lockbit, .enc).
   - Ransom notes dropped in root directories (e.g., README_DECRYPT.txt) containing TOR negotiation links.
   - Volume Shadow Copy deletion commands executed via vssadmin or PowerShell.
3. **First Responder SOP:**
   - **Isolation:** Sever all network interfaces (unplug Ethernet cables and disable Wi-Fi adapters) immediately. Do NOT power off systems abruptly if RAM triage is planned, as volatile memory contains cryptographic keys and active network sockets.
   - **Preservation:** Capture physical RAM dumps and disk image duplicates using write-blocking hardware.
   - **Policy:** CERT-In strictly advises against paying ransoms, as payments encourage criminal syndicates and offer no guarantee of data recovery.

---

### Section 3: Advisory on SIM Swap and Account Takeover Attacks
1. **Mechanism:** Attackers obtain forged identity documents of the victim and submit fraudulent duplicate SIM requests to telecom service providers to intercept SMS OTPs.
2. **Detection:** Sudden unexplained loss of cellular network connectivity ("No Service" status) during business hours followed by password reset notifications on primary email accounts.
3. **Immediate Action:** Inform telecom operator customer care from an alternate number to lock the SIM card; contact banks to block all digital transactions.
