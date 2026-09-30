# CyberShield India — Power BI Enterprise Star Schema Analytics Guide

## Platform: National Cybercrime Intelligence, Risk Assessment & Complaint Analytics (CyberShield India)
**Document Reference:** CS-IN/POWERBI/2026-V2  
**Dataset Architecture:** Star Schema OLAP Model (5,000 complaints, 20 States & UTs, 52 Mule Rings)  
**Directory:** `powerbi/datasets/`
**SQL Views:** `powerbi/views/powerbi_star_schema_views.sql`

---

## 1. Star Schema Relational Model

```text
               ┌───────────────┐
               │    DimDate    │
               │───────────────│
               │ DateKey (PK)  │
               └───────┬───────┘
                       │ 1:N
┌───────────────┐      │      ┌───────────────┐
│  DimLocation  │      │      │  DimCrimeType │
│───────────────│      │      │───────────────│
│LocationKey(PK)├──────┼──────┤ CrimeKey (PK) │
└───────┬───────┘      │      └───────┬───────┘
        │ 1:N          │              │ 1:N
        │      ┌───────▼───────┐      │
        └─────►│ FactComplaints│◄─────┘
               │───────────────│
        ┌─────►│  Fact Record  │◄─────┐
        │ 1:N  └───────▲───────┘      │ 1:N
        │              │              │
┌───────┴───────┐      │ 1:N  ┌───────┴───────┐
│   DimVictim   │      │      │   DimStatus   │
│───────────────│      │      │───────────────│
│ VictimKey(PK) │      │      │ StatusKey(PK) │
└───────────────┘      │      └───────────────┘
               ┌───────┴───────┐
               │   DimOfficer  │
               │───────────────│
               │ OfficerKey(PK)│
               └───────────────┘
```

---

## 2. Core DAX Calculations for Power BI Desktop

Enter the following measures into your Power BI model under the `FactComplaints` table:

```dax
// 1. Total Complaint Volume
Total Complaints = COUNTROWS(FactComplaints)

// 2. High-Risk & Critical Case Volumes
Critical Cases = 
CALCULATE(
    COUNTROWS(FactComplaints),
    FactComplaints[risk_score] >= 80
)

High Risk Cases = 
CALCULATE(
    COUNTROWS(FactComplaints),
    FactComplaints[risk_score] >= 60 && FactComplaints[risk_score] < 80
)

// 3. Average Composite Risk Score
Average Risk Score = AVERAGE(FactComplaints[risk_score])

// 4. Financial Loss Aggregations (in INR ₹)
Total Financial Loss INR = SUM(FactComplaints[reported_amount])
Total Financial Loss Cr = DIVIDE([Total Financial Loss INR], 10000000, 0)

// 5. Case Resolution Efficiency
Resolved Cases = 
CALCULATE(
    COUNTROWS(FactComplaints),
    DimStatus[current_status] = "Resolved"
)

Resolution Rate Pct = 
DIVIDE([Resolved Cases], [Total Complaints], 0) * 100
```

---

## 3. How to Connect Power BI Desktop to This Project

### Method A: Connect Directly to Processed Star Schema CSVs (Recommended)
1. Open **Power BI Desktop**.
2. Click **Get Data** $\rightarrow$ **Folder** (or **Text/CSV**).
3. Browse to the folder:
   `c:\Users\Admin\Desktop\CyberCrimePredict\powerbi\datasets\`
4. Select all 7 tables (`FactComplaints`, `DimDate`, `DimLocation`, `DimCrimeType`, `DimVictim`, `DimStatus`, `DimOfficer`).
5. Click **Load**.
6. Switch to the **Model View** tab in Power BI:
   * Drag `LocationKey` from `DimLocation` to `FactComplaints[LocationKey]`.
   * Drag `CrimeKey` from `DimCrimeType` to `FactComplaints[CrimeKey]`.
   * Drag `StatusKey` from `DimStatus` to `FactComplaints[StatusKey]`.
   * Drag `DateKey` from `DimDate` to `FactComplaints[ComplaintDateKey]`.
   * Drag `OfficerKey` from `DimOfficer` to `FactComplaints[OfficerKey]`.
   * Drag `VictimKey` from `DimVictim` to `FactComplaints[VictimKey]`.
7. Relationships will automatically establish as 1-to-many (1:*), single cross-filter direction.

### Method B: DirectQuery to SQLite Database via ODBC
1. Install the SQLite ODBC Driver on Windows.
2. In Power BI Desktop, select **Get Data** $\rightarrow$ **ODBC**.
3. Connection String: `Driver={SQLite3 ODBC Driver};Database=c:\Users\Admin\Desktop\CyberCrimePredict\backend\cybercrime.db;`
4. Select the created views `v_FactComplaints` and `v_ExecutiveKPIs`.

---

## 4. Suggested Multi-Page Dashboard Layouts

1. **Page 1: Executive Overview** — Top KPIs (Total Complaints, Critical Cases, Total Loss ₹, Resolution Rate), Crime Category Bar Chart, State-wise Volume Heatmap.
2. **Page 2: Geographic Intelligence** — Interactive India State map slicer, District hot-spots, Cyber Cell Station load distribution.
3. **Page 3: Crime Pattern Analysis** — Cross-filtering Crime Types by Payment Method (UPI, RTGS, Credit Card), Platform (WhatsApp, Telegram, APK, Cloned Site), and Modus Operandi.
4. **Page 4: Risk Intelligence** — Risk Score Distribution histogram, Contributing Factors Pareto chart, Prediction Confidence vs Severity matrix.
5. **Page 5: Investigation Analytics** — Case aging funnel (New $\rightarrow$ Under Review $\rightarrow$ Investigating $\rightarrow$ Resolved), Officer caseload table, Priority distribution.
6. **Page 6: Forecasting** — 2019–2025 Historical trajectory with 2026–2027 polynomial projected baseline and 95% confidence intervals.
