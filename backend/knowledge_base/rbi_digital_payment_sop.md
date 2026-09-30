# Reserve Bank of India (RBI) Master Directions on Digital Payment Security & Fraud Redressal

## Document Reference: RBI/DPSS/2026/CIR-14
**Issuing Authority:** Reserve Bank of India (Department of Payment and Settlement Systems)  
**Applicability:** Commercial Banks, Payment Aggregators, Prepaid Payment Instruments (PPIs), UPI Networks  
**Subject:** Limiting Liability of Customers in Unauthorized Electronic Banking Transactions and Fraud SOP

---

### Section 1: Customer Liability Framework in Fraudulent Transactions
1. **Zero Customer Liability:**
   - Applicable when the unauthorized transaction occurs due to contributory fraud, negligence, or deficiency on the part of the bank (irrespective of whether or not the transaction is reported by the customer).
   - Applicable in third-party breaches where the deficiency lies neither with the bank nor with the customer, but lies elsewhere in the system, and the customer notifies the bank within **three working days** of receiving the communication from the bank regarding the unauthorized transaction.
2. **Limited Customer Liability:**
   - Where the responsibility for the unauthorized transaction lies neither with the customer nor with the bank, but lies elsewhere in the system and the customer reports the transaction with a delay of **four to seven working days**, the per-transaction liability of the customer is capped according to account type (Basic Savings Bank Deposit: max ₹5,000; Savings Bank/Credit Card with limit up to ₹5 lakh: max ₹10,000; Current Accounts: max ₹25,000).
3. **Beyond Seven Working Days:**
   - Determined in accordance with the bank’s board-approved fraud compensation policy.

---

### Section 2: Financial Freeze Protocol via 1930 Helpline (CFCFRMS System)
1. **Golden Hour Intervention:**
   - The first two hours after financial debit constitute the crucial window to stop the inter-bank movement of funds.
   - When a complaint is logged on helpline 1930 or the portal cybercrime.gov.in, a ticket is automatically generated on the Citizen Financial Cyber Fraud Reporting and Management System (CFCFRMS).
   - CFCFRMS pushes real-time transactional alert API requests directly to the nodal officers of the beneficiary banks, payment gateways, and wallet service providers.
   - Beneficiary institutions are mandated to place an immediate debit freeze / lien on the beneficiary account to prevent cash withdrawals via ATM or transfer to subsequent mule accounts (Layer 2 and Layer 3 accounts).

---

### Section 3: Evidence Mandated for Dispute Lodgement
- Detailed bank account statement highlighting the unauthorized transaction with UTR / RRN numbers.
- Transaction SMS alert screenshots containing timestamps and originating sender IDs.
- Acknowledgement receipt copy of the National Cyber Crime Reporting Portal (NCRP) complaint or police cyber cell FIR.
