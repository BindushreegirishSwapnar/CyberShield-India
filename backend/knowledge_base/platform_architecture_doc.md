# Platform Architecture, Risk Scoring Methodology & ML Specifications

## Document Reference: ARCH/TECH-SPEC/2026-V2
**Platform Title:** Predictive Cyber Crime Intelligence, Risk Assessment and Complaint Analytics Platform  
**Purpose:** Technical Specification of Explainable Risk Engine, Classification Pipeline, and Grounded RAG Architecture

---

### Section 1: Multi-Factor Risk Assessment Mathematical Formulation
The platform evaluates an incident's Composite Cyber Risk Score $R \in [0, 100]$ using a multi-factor weighted equation:
$$R = \min\left(100, W_{cat} + W_{conf} + W_{sev} + W_{loss} + W_{pii} + W_{takeover} + \sum_{i} W_{ind,i}\right)$$

Where:
- $W_{cat} \in [10, 20]$: Base structural threat rating of the predicted cybercrime taxonomy (e.g. Ransomware = 20, Data Breach = 20, Financial Fraud = 18, Phishing = 15).
- $W_{conf} \in [0, 15]$: Model classification probability scaled via $15 \cdot (C^{1.5})$.
- $W_{sev} \in [5, 25]$: Reported incident severity (Critical = 25, High = 20, Medium = 12, Low = 5).
- $W_{loss} \in [0, 20]$: Quantified financial loss tier (Loss > ₹1,00,000 = 20 pts; > ₹25,000 = 15 pts; > 0 = 10 pts).
- $W_{pii} = 12$: Binary indicator for compromise of Aadhaar, PAN, passport, or biometric credentials.
- $W_{takeover} = 15$: Active account or device compromise verified.
- $W_{ind}$: Sum of extracted threat indicator severities (Critical indicator = 7 pts, High = 4 pts, Medium = 2 pts, capped at 15 pts total).

Risk Classification Tiers:
- **Low Risk:** $0 \le R < 30$ (Routine advisory, general monitoring)
- **Moderate Risk:** $30 \le R < 60$ (Standard investigation, desk inquiry)
- **High Risk:** $60 \le R < 80$ (Priority cyber cell intervention, suspect account freeze)
- **Critical Risk:** $80 \le R \le 100$ (Immediate triage alert, inter-agency Golden Hour freeze via 1930 / CFCFRMS, forensics disk preservation)

---

### Section 2: Grounded RAG Vector Retrieval Architecture
1. **Semantic Ingestion:** All official documentation in `/backend/knowledge_base/` is partitioned into granular semantic units (chunks of 300 to 500 characters) preserving heading context.
2. **Dense Vector Indexing:** Chunks are indexed using sublinear TF-IDF n-gram vector representations with cosine similarity metrics for robust, deterministic local execution.
3. **Relevance Gating:** Only document chunks surpassing the minimum cosine threshold ($\ge 0.18$) are admitted into the synthesis context.
4. **Attribution & Transparency:** Responses must explicitly cite the document reference, section number, and authority to guarantee non-hallucinatory compliance.
