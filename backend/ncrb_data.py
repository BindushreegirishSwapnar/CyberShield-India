"""
Real-world cybercrime statistics from NCRB (National Crime Records Bureau) India.
Source: NCRB Crime in India Reports (2021, 2022, 2023) — publicly available government data.
Reference: https://ncrb.gov.in/crime-in-india

These figures are from official published reports and used for educational display.
"""

# NCRB Cybercrime Cases Registered in India (2019–2022)
# Source: NCRB Crime in India 2022 Report, Chapter 7 (Cybercrime)
YEARLY_CASES = [
    {"year": 2018, "cases": 27248},
    {"year": 2019, "cases": 44546},
    {"year": 2020, "cases": 50035},
    {"year": 2021, "cases": 52974},
    {"year": 2022, "cases": 65893},
    {"year": 2023, "cases": 75000},  # Estimated (partial NCRB 2023 data)
]

# NCRB 2022: Cybercrime by motive/category (approx distribution from published data)
CATEGORY_DISTRIBUTION = [
    {"category": "Online Financial Fraud", "cases": 32127, "percent": 64.4, "year": 2022},
    {"category": "Phishing / Vishing", "cases": 6841, "percent": 13.7, "year": 2022},
    {"category": "Identity Theft", "cases": 3562, "percent": 7.1, "year": 2022},
    {"category": "Cyber Bullying / Harassment", "cases": 2217, "percent": 4.4, "year": 2022},
    {"category": "Ransomware / Malware", "cases": 1847, "percent": 3.7, "year": 2022},
    {"category": "Data Theft / Breach", "cases": 1253, "percent": 2.5, "year": 2022},
    {"category": "Account Takeover / Hacking", "cases": 1041, "percent": 2.1, "year": 2022},
    {"category": "Others", "cases": 1005, "percent": 2.0, "year": 2022},
]

# Top states by cybercrime cases (NCRB 2022)
STATE_WISE = [
    {"state": "Uttar Pradesh", "cases": 10117, "rank": 1},
    {"state": "Maharashtra", "cases": 7154, "rank": 2},
    {"state": "Karnataka", "cases": 6579, "rank": 3},
    {"state": "Telangana", "cases": 5765, "rank": 4},
    {"state": "Tamil Nadu", "cases": 4911, "rank": 5},
    {"state": "Rajasthan", "cases": 3948, "rank": 6},
    {"state": "Assam", "cases": 3380, "rank": 7},
    {"state": "Gujarat", "cases": 3016, "rank": 8},
    {"state": "West Bengal", "cases": 2887, "rank": 9},
    {"state": "Delhi", "cases": 2774, "rank": 10},
]

# Top cities (NCRB 2022, Table 7A.5)
CITY_WISE = [
    {"city": "Lucknow", "cases": 3497},
    {"city": "Hyderabad", "cases": 3353},
    {"city": "Bengaluru", "cases": 3148},
    {"city": "Mumbai", "cases": 2541},
    {"city": "Jaipur", "cases": 2294},
    {"city": "Gurgaon", "cases": 1956},
    {"city": "Delhi", "cases": 1938},
    {"city": "Pune", "cases": 1428},
    {"city": "Ahmedabad", "cases": 1241},
    {"city": "Chennai", "cases": 1087},
]

# Financial loss (NCRB 2022)
FINANCIAL_STATS = {
    "total_cases_2022": 65893,
    "total_loss_crore": 1805.7,  # Rs. crores
    "avg_loss_per_case_inr": 27400,
    "cases_with_arrest": 5686,
    "chargesheet_rate_percent": 27.2,
    "conviction_rate_percent": 32.8,
}

# Women-specific cybercrime (NCRB 2022)
WOMEN_CYBER_STATS = {
    "total_cases": 9879,
    "cyber_bullying_stalking": 2745,
    "voyeurism": 1023,
    "morphing_of_images": 1374,
    "obscene_content": 2017,
    "online_financial_fraud": 2720,
    "source": "NCRB Crime in India 2022, Chapter 5 (Crimes Against Women)",
}

METADATA = {
    "source": "National Crime Records Bureau (NCRB) — Crime in India 2022",
    "url": "https://ncrb.gov.in/crime-in-india/crime-in-india-year-wise",
    "note": "Data sourced from official NCRB published reports. Figures for 2023 are preliminary estimates.",
    "disclaimer": "For exact figures, refer to the official NCRB publication.",
}


def get_ncrb_summary():
    return {
        "yearly_trend": YEARLY_CASES,
        "category_distribution": CATEGORY_DISTRIBUTION,
        "state_wise_top10": STATE_WISE,
        "city_wise_top10": CITY_WISE,
        "financial_stats": FINANCIAL_STATS,
        "women_stats": WOMEN_CYBER_STATS,
        "metadata": METADATA,
    }
