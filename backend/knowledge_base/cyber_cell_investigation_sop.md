# Standard Operating Procedure (SOP) for Cyber Crime Police Stations & Investigation Officers

## Document Reference: POLICE-SOP/CYBER-INV/2026-V3
**Target Audience:** Cyber Crime Police Station IOs, Cyber Forensics Teams, Nodal Triage Officers  
**Subject:** Digital Evidence Seizure, Intermediary Requisitions, and Mule Account Interdiction

---

### Section 1: Digital Evidence Collection & Chain of Custody Protocol
1. **Physical Evidence Seizure:**
   - Always transport seized mobile devices in radio-frequency shielding Faraday bags to prevent remote device wiping via Find My iPhone / Android Device Manager.
   - Maintain a signed Chain of Custody Form (Form CY-04) recording the seizing officer, time, physical condition, IMEI number, and MAC address.
2. **Volatile Memory Acquisition:**
   - In live computers, execute memory dump extraction (using FTK Imager CLI or LiME on Linux) prior to pulling power plugs. Volatile memory holds encryption keys, process memory strings, and active C2 TCP socket connections.
3. **Hash Verification:**
   - Compute SHA-256 and MD5 cryptographic hashes immediately upon raw disk image acquisition. Ensure forensic verification match on working copies.

---

### Section 2: Requisitions to Telecom & Internet Intermediaries (Section 91 CrPC / Section 94 BNSS)
1. **Notice to Telecom Service Providers (TSPs):**
   - Formal requisition to Nodal Officers for Call Detail Records (CDR) and Internet Protocol Detail Records (IPDR) of suspect MSISDNs.
   - Request Cell Site Location Charts and Subscriber Identity Module (SIM) application forms (CAF) with submitted identity proofs.
2. **Notice to Social Media and Email Intermediaries:**
   - Request IP login/logout logs, device identifiers, registration email addresses, and recovery phone numbers.
   - For emergency disclosures involving imminent physical harm, submit an Emergency Disclosure Request (EDR) to expedited law enforcement portals (Meta LERS, Google LERS).

---

### Section 3: Financial Trail Investigation and Mule Account Demolition
1. **Layer 1 to Layer 3 Account Mapping:**
   - Cyber syndicates rarely withdraw funds from the initial recipient account (Layer 1). Funds are split across 5 to 20 mule accounts (Layer 2) within minutes, then moved to crypto exchange wallets or cash P2P withdrawal points (Layer 3).
2. **Requisition to Payment Service Providers:**
   - Requisition statement of accounts, KYC documents of account holders, linked mobile numbers, IP logs of netbanking sessions, and ATM CCTV footage corresponding to withdrawal timestamps.
