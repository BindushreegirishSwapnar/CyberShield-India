# CyberShield India (साइबर शील्ड भारत)
### National Cyber Incident Intelligence, Risk Interdiction & Decision Support Platform

[![CI & Build (PWA + APK)](https://github.com/cybershield-india/cybershield-india/actions/workflows/deploy.yml/badge.svg)](.github/workflows/deploy.yml)
[![PWA Ready](https://img.shields.io/badge/PWA-Installable-1F6F6B.svg)](https://developer.mozilla.org/en-US/docs/Web/Progressive_web_apps)
[![Android APK](https://img.shields.io/badge/Android%20APK-Capacitor%208.5-8FB59B.svg)](frontend/android)
[![WCAG AA Compliant](https://img.shields.io/badge/Accessibility-WCAG%20AA-E3A83B.svg)](frontend/src/index.css)
[![Dataset Provenance](https://img.shields.io/badge/Data%20Provenance-NCRB%2FNCRP%20Synthetic-D9825B.svg)](backend/data/metadata/provenance.json)

---

## 🏛️ Executive Summary

**CyberShield India** is an enterprise-grade digital public infrastructure (DPI) platform engineered for rapid cyber incident intake, predictive triage, mule syndicate interdiction, and automated legal drafting for law enforcement officers and citizens across India.

Transitioning cybercrime reporting from static, delayed complaint logs into active, real-time intervention:
- **For Citizens:** Low-friction, multilingual (English, हिन्दी, ಕನ್ನಡ) guided incident wizard with speech-to-text narration, OCR screenshot extraction, an active **Golden Hour 1930** interdiction countdown, scam URL/message checker, cyber hygiene assessment, and tamper-evident PDF receipts.
- **For Cyber Cell Officers:** A military-grade Operations Console featuring SLA triage queues, Explainable AI (LIME/SHAP-style feature attribution), an interactive force-directed **Mule Ring Link Analysis Graph**, a counterfactual **What-If Risk Simulator**, and automated **Draft FIR Summaries** citing the Information Technology Act 2000 and Bharatiya Nyaya Sanhita (BNS) 2023.
- **Cyber Cell Copilot (RAG):** Hybrid BM25 + Vector Search + Reciprocal Rank Fusion (RRF) intelligence retrieval grounded in CERT-In advisories, RBI SOPs, and IT Acts with verifiable source citations and Gemini API reasoning.
- **Power BI Intelligence Studio:** In-app OLAP star schema analytical studio featuring cross-filtering slicers, state ranking, decomposition trees, financial loss heatmaps, and polynomial trend forecasting with 95% confidence bands backed by a 5,000-complaint database.

---

## 🎨 Design Philosophy & Accessibility

CyberShield India deliberately eschews clichéd dark neon "hacker" tropes in favor of an **accessible, humane, trustworthy civic design system**:
- **Palette:** Soft Ivory (`#FAF7F2`), Sand (`#F1EBDD`), Deep Sovereign Teal (`#1F6F6B`), Sage (`#8FB59B`), Terracotta (`#D9825B`), Amber (`#E3A83B`), and Brick Red (`#C8553D`).
- **Typography:** Lora serif headings for civic authority paired with Inter / Nunito sans-serif for legible scanning.
- **Readability & Ergonomics:** Strict **18px base typography**, minimum **48px touch targets**, high-contrast WCAG 2.1 AA compliance, and full keyboard/screen-reader navigation.
- **Responsive Form Factors:** Adaptive desktop console with persistent navigation and mobile-first bottom bar with emergency drawer.

---

## 🧩 Architectural Overview

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                             CLIENT ECOSYSTEM                                │
│                                                                             │
│   ┌───────────────────────────┐         ┌───────────────────────────────┐   │
│   │   Installable Web PWA     │         │      Android Mobile APK       │   │
│   │  (Workbox ServiceWorker)  │         │   (Capacitor 8.5 Native API)  │   │
│   └─────────────┬─────────────┘         └───────────────┬───────────────┘   │
└─────────────────┼───────────────────────────────────────┼───────────────────┘
                  │                                       │
                  ▼                                       ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                           FRONTEND (React 18 + Vite)                        │
│                                                                             │
│  • Citizen Portal (Voice STT, Tesseract OCR, Golden Hour Timer, PDF)        │
│  • Officer Console (SLA Triage, XAI Feature Breakdown, Counterfactuals)     │
│  • Force-Directed Link Graph (Canvas BFS Mule Ring Detection)               │
│  • Cyber Cell Copilot (Hybrid BM25 + Vector RRF + Citations)                │
│  • Power BI Studio (Recharts OLAP Slicers, DAX Explorer, Star Schema Export)│
└──────────────────────────────────────┬──────────────────────────────────────┘
                                       │ HTTPS REST / JSON
                                       ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                     BACKEND ENGINE (Python 3.11 + Flask)                    │
│                                                                             │
│  ┌───────────────────────┐ ┌────────────────────────┐ ┌───────────────────┐ │
│  │   AI Risk Engine      │ │  Cyber Copilot RAG     │ │ Intelligence API  │ │
│  │ • Calibrated Classifier│ │ • BM25 + Cosine TF-IDF │ │ • BFS Graph Clust │ │
│  │ • Multi-factor Scoring │ │ • RRF Hybrid Ranker    │ │ • Mule Accounts   │ │
│  │ • Threat Regex Mining  │ │ • Gemini LLM Synthesis │ │ • Syndicate Hubs  │ │
│  └───────────────────────┘ └────────────────────────┘ └───────────────────┘ │
│                                      │                                      │
│  ┌───────────────────────────────────▼───────────────────────────────────┐  │
│  │              Enterprise Data Layer (SQLite / PostgreSQL)              │  │
│  │  • 5,000 Seeded Incidents across 20 States  • 52 Coordinated Syndicates│  │
│  │  • 6,700+ Extracted Threat Indicators       • Immutable Audit Ledger  │  │
│  └───────────────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 📱 Deliverables: PWA & Android APK

### 1. Progressive Web App (PWA)
- **Installability:** Fully complies with W3C Web App Manifest v2 and PWA install criteria.
- **Offline Resilience:** Pre-caches app shell, assets, and standard operational guides via Workbox service worker (`sw.js`).
- **One-Click Install Banner:** Automatically prompts users on supported desktop and mobile browsers.

### 2. Native Android Application (APK)
- **Framework:** Powered by Capacitor 8.5 native bridge (`gov.in.cybershield`).
- **Native Permissions Enabled:**
  - `RECORD_AUDIO` for native voice-to-text incident narration.
  - `CALL_PHONE` for direct one-tap dialing to the **1930 National Cyber Helpline**.
  - `READ_MEDIA_IMAGES` / `READ_EXTERNAL_STORAGE` for fraud screenshot analysis.
- **Building the APK:**
  ```bash
  # 1. Sync React build to Android assets
  cd frontend
  npm run cap:build

  # 2. Open in Android Studio to build signed APK
  npm run cap:open

  # Or build directly via Gradle wrapper (requires JDK 17+ and Android SDK)
  cd android
  ./gradlew assembleDebug
  ```
- **Automated CI/CD:** Every push to `main` executes `.github/workflows/deploy.yml` which compiles and uploads `app-debug.apk` directly to GitHub Releases/Artifacts.

---

## 🌐 Public Deployment (Zero Localhost Dependency)

CyberShield India is designed to run in any cloud environment without hardcoded `localhost` references. The frontend dynamically resolves its API endpoint via `VITE_API_URL` or defaults to relative `/api/v1` routing.

### Option A: Docker Compose (Full Stack)
```bash
# Clone the repository
git clone https://github.com/cybershield-india/cybershield-india.git
cd cybershield-india

# Launch backend (Gunicorn) and frontend (Nginx)
docker-compose up --build -d
```
- Frontend will be live at `http://<your-server-ip>:80`
- Backend API will be live at `http://<your-server-ip>:5000/api/v1`

### Option B: Render Blueprint (1-Click Free Cloud Hosting)
1. Fork or push this repository to GitHub.
2. Log in to [Render.com](https://render.com) and click **New +** $\rightarrow$ **Blueprint**.
3. Select this repository; Render will automatically detect `render.yaml` and configure:
   - `cybershield-api`: Python 3.11 Web Service running Gunicorn.
   - `cybershield-web`: Static Site serving the Vite PWA with client-side SPA routing.

---

## 🔍 Core Capabilities & Modules

### 1. Citizen Assistance Portal
- **Multilingual Support:** Instant UI translation in English, Hindi (हिंदी), and Kannada (ಕನ್ನಡ).
- **Incident Narration Voice STT:** Uses Web Speech Recognition API allowing victims in distress to narrate incidents hands-free.
- **OCR Screenshot Extraction:** On-device client-side OCR via `Tesseract.js` automatically scans scam screenshots, bank debit alerts, or phishing SMS messages for amounts, UTR numbers, UPI IDs, and phone numbers.
- **Golden Hour 1930 Interdiction:** A persistent 2-hour countdown timer emphasizing the critical window to freeze fraudulent transactions via the National Cybercrime Reporting Portal (NCRP) / Indian Cybercrime Coordination Centre (I4C).
- **Scam Checker:** Instant client-side heuristic scanner for suspicious URLs, SMS texts, and phishing domains.
- **Tamper-Evident Complaint Receipt:** Generates an official, download-ready PDF acknowledgement with verification timestamp and reference ID via `jsPDF`.

### 2. Cyber Cell Officer Console
- **Role-Based Access Control:** Secure authentication for Duty Officers, Senior Investigators, and Intelligence Analysts (`inspector@cybercell.gov.in` / `admin@cybercell.gov.in`).
- **SLA Triage Queue:** Priority triage list featuring dynamic urgency timers, severity badges, and quick status actions.
- **Explainable AI (XAI):** Visual factor decomposition showing top positive and negative drivers contributing to the composite risk score (0–100).
- **Counterfactual What-If Simulator:** Interactive sliders allowing analysts to model how changes in stolen amount, credential exposure, or suspect cooperation affect risk level and priority.
- **Automated Draft FIR Summary:** One-click legal briefing document auto-citing relevant sections of:
  - **Information Technology Act, 2000** (Sections 43, 66, 66C, 66D, 67, 72A)
  - **Bharatiya Nyaya Sanhita, 2023** (Sections 316, 318, 319, 336, 340)

### 3. Mule Syndicate Link Analysis Graph
- **Graph Topology:** Force-directed Canvas simulation modeling 5,000 incidents, 6,700+ indicators, and 52 mule account clusters.
- **BFS Mule Ring Detection:** Traverses shared UPI handles, bank accounts, IFSC routing codes, and fraudulent phone numbers to isolate coordinated financial laundering rings.
- **Entity Inspector:** Real-time side drawer revealing account transaction velocity, linked complaint count, and freeze status.

### 4. Cyber Cell Copilot (Hybrid RAG)
- **Multi-Source Knowledge Corpus:** Grounded in CERT-In advisory bulletins, RBI Cyber Security Framework SOPs, IT Act 2000, and State Cyber Cell guidelines.
- **Hybrid Search Architecture:** Structure-aware chunking (300–500 tokens, 15% overlap) combined with Reciprocal Rank Fusion (RRF) across BM25 keyword matching and TF-IDF cosine vector similarity.
- **Strict Grounding & Citations:** Every Copilot statement includes verifiable superscript citations `[1]`, `[2]` linking directly to knowledge base documents.
- **LLM Integration:** Optional Gemini 1.5 Flash synthesis with seamless local fallback to extractive grounding when API keys are absent.

### 5. Power BI Studio & OLAP Star Schema
- **Interactive Recharts Dashboard:** Real-time slicers for State, Crime Category, and Priority.
- **Advanced Visualizations:** YoY volume comparison sparklines, India State distribution ranking, Category decomposition tree, financial loss heatmap, and time-series polynomial forecasting with 95% confidence intervals.
- **DAX Formula Explorer:** In-app inspection drawer containing standard DAX measures (`Total Financial Loss Cr`, `Resolution Rate Pct`, `Critical Case Ratio`).
- **Star Schema CSV Package:** One-click generation and download of complete OLAP datasets:
  - `FactComplaints.csv` (5,000 records)
  - `DimLocation.csv`, `DimCrimeType.csv`, `DimVictim.csv`, `DimStatus.csv`, `DimOfficer.csv`, `DimDate.csv`
  - `powerbi_star_schema_views.sql` for enterprise SQL databases.

---

## 📊 Model Evaluation & Benchmarks

### 1. Incident Classification Model (Calibrated Linear SVC)
Trained on domain-specific complaint narrations across 10 cybercrime categories:
- **Test Accuracy:** `88.0%`
- **Precision (Macro):** `90.38%`
- **Recall (Macro):** `88.00%`
- **F1-Score (Macro):** `88.13%`
- **F1-Score (Weighted):** `88.13%`
- *Metrics are dynamically loaded from `backend/models/model_metrics.json`.*

### 2. Cyber Cell Copilot RAG Evaluation Benchmark
Evaluated across 20 curated Golden Q&A evaluation pairs spanning Indian cyber laws, CERT-In guidelines, and banking SOPs:
- **Retrieval Top-1 Accuracy:** `85.0%`
- **Retrieval Top-3 Recall:** `95.0%`
- **Faithfulness Score:** `65.8%`
- **Mean Retrieval Latency:** `2.8 ms`
- *Full evaluation suite available in `backend/rag/evaluate_rag.py` and dynamic metrics in `backend/models/rag_evaluation_metrics.json`.*

---

## 🛡️ Synthetic Data Provenance & Ethics Disclosure

> **Provenance Notice:**  
> The 5,000 complaint records, mule bank accounts, and victim details contained in this system are **synthetically generated** for demonstration, stress testing, and development purposes in accordance with the specifications in [`backend/data/metadata/provenance.json`](backend/data/metadata/provenance.json).  
> Complaint distributions and category frequencies are statistically calibrated to mirror public statistical aggregates published in the **National Crime Records Bureau (NCRB) 'Crime in India 2022–2023'** reports and **Indian Cybercrime Coordination Centre (I4C)** operational bulletins. No real Personally Identifiable Information (PII) or classified law enforcement data is utilized.

---

## 🛠️ Local Development & Quickstart

### Prerequisites
- Python 3.11+
- Node.js 18+ and npm
- (Optional) Docker & Docker Compose

### 1. Backend Setup
```bash
cd backend
python -m venv venv
# On Windows:
venv\Scripts\activate
# On Linux/macOS:
source venv/bin/activate

pip install -r requirements.txt
python app.py
```
*Backend runs at `http://127.0.0.1:5000`.*

### 2. Frontend Setup
```bash
cd frontend
npm install
npm run dev
```
*Frontend runs at `http://127.0.0.1:5173`.*

### 3. Running Pytest Suite
```bash
cd backend
pytest tests/ -v
```

---

## 📜 Regulatory Citations & Statutory References
- **Information Technology Act, 2000** (amended 2008), Ministry of Electronics & IT, Government of India.
- **Bharatiya Nyaya Sanhita, 2023 (BNS)**, Ministry of Home Affairs, Government of India.
- **Reserve Bank of India (RBI)**: Circular on Limiting Liability of Customers in Unauthorised Electronic Banking Transactions (RBI/2017-18/15).
- **Indian Computer Emergency Response Team (CERT-In)**: Incident Reporting Guidelines & Cybersecurity Directions under Sec 70B.
- **Indian Cybercrime Coordination Centre (I4C)**: Citizen Financial Cyber Fraud Reporting and Management System (CFCFRMS / 1930 Helpline).

---

## ⚖️ License
Released under the **MIT License**. Engineered for civic security and public safety technology research.
