import os
import math
import numpy as np
from datetime import datetime, timedelta
from sqlalchemy import func, desc
from database import get_session
from models_db import Complaint

WEATHER_ICONS = {
    "EXTREME": "lightning",
    "HIGH": "storm",
    "MODERATE": "cloud-rain",
    "LOW": "cloud-sun",
    "MINIMAL": "sun"
}

AGE_SPECIFIC_ADVICE = {
    "Senior Citizen (60+)": {
        "vector": "Pension & Electricity Bill Disconnection Hoaxes",
        "tip": "Never install remote desktop apps (AnyDesk/TeamViewer) or click SMS links claiming your power or pension will be stopped today. Electricity boards never call via WhatsApp."
    },
    "Working Professional (26-59)": {
        "vector": "Tax Refund, FedEx Parcel & Digital Arrest Extortion",
        "tip": "Police, CBI, and Customs never conduct interrogation or demand money over Skype or video call. Verify parcel tracking directly on official courier portals."
    },
    "Student / Youth (18-25)": {
        "vector": "Part-Time Review/Telegram Task Scams & Loan APKs",
        "tip": "No legitimate firm pays Rs. 500 for subscribing to YouTube channels. Never pay 'security deposit' to unlock frozen earnings."
    },
    "General": {
        "vector": "UPI QR Code Collect Reversals & Bank KYC SMS",
        "tip": "Entering your UPI PIN always deducts money from your account. You NEVER need to enter your PIN or scan a QR code to receive payments."
    }
}

def get_scam_weather_forecast(state="Karnataka", age_group="Senior Citizen (60+)", language="en"):
    """
    Computes real-time 'Scam Weather' based on complaint count anomalies (z-score),
    recent trend velocity, and dominant threat typologies from the database.
    """
    try:
        with get_session() as session:
            # 1. Total and recent volume for state
            query = session.query(Complaint)
            if state and state != "All India":
                query = query.filter(Complaint.state == state)

            total_state_cases = query.count()
            if total_state_cases == 0:
                # Fallback to All India if state has no data
                query = session.query(Complaint)
                state = "All India"
                total_state_cases = query.count()

            # 2. Daily volume counts to calculate statistical anomaly (z-score)
            daily_counts_rows = session.query(
                Complaint.complaint_date,
                func.count(Complaint.id)
            )
            if state != "All India":
                daily_counts_rows = daily_counts_rows.filter(Complaint.state == state)

            daily_counts_rows = daily_counts_rows.group_by(Complaint.complaint_date).order_by(Complaint.complaint_date).all()

            daily_vals = [r[1] for r in daily_counts_rows] or [10, 12, 14, 15, 11]
            mean_daily = float(np.mean(daily_vals))
            std_daily = float(np.std(daily_vals)) if len(daily_vals) > 1 and np.std(daily_vals) > 0 else 2.5
            recent_daily = float(daily_vals[-1]) if daily_vals else mean_daily

            # Anomaly z-score
            z_score = (recent_daily - mean_daily) / std_daily

            # 3. Dominant threat category in this state
            top_category_row = session.query(
                Complaint.predicted_category,
                func.count(Complaint.id).label('cnt')
            )
            if state != "All India":
                top_category_row = top_category_row.filter(Complaint.state == state)

            top_cat = top_category_row.group_by(Complaint.predicted_category).order_by(desc('cnt')).first()
            dominant_category = top_cat[0] if top_cat else "Online Financial Fraud"

        # Calculate risk gauge (0 to 100)
        base_temp = 55 + int(z_score * 18)
        risk_temp = max(15, min(96, base_temp))

        if risk_temp >= 80:
            condition_level = "EXTREME"
            condition_label = "Severe Threat Gale (Action Required)"
            headline = f"Severe scam weather today in {state}: Critical spike in {dominant_category}."
        elif risk_temp >= 65:
            condition_level = "HIGH"
            condition_label = "High Threat Incline"
            headline = f"High scam alert today in {state}: Surge in fake verification calls and UPI links."
        elif risk_temp >= 45:
            condition_level = "MODERATE"
            condition_label = "Scattered Threat Drizzle"
            headline = f"Moderate scam activity in {state}: Periodic deceptive SMS and APK phishing detected."
        else:
            condition_level = "LOW"
            condition_label = "Mild Activity / Fair Outlook"
            headline = f"Low baseline threat today in {state}: Standard vigil recommended."

        # Age group personalization
        advice_info = AGE_SPECIFIC_ADVICE.get(age_group, AGE_SPECIFIC_ADVICE["General"])

        # 4. Generate 7-day outlook starting from today
        outlook_days = []
        today = datetime.now()
        day_names = ["Today", "Tomorrow", "Wed", "Thu", "Fri", "Sat", "Sun"]

        # Vector rotation for weekly weather outlook
        vectors_pool = [
            ("fake electricity-bill disconnection calls", 78),
            ("instant loan app extortion SMS", 64),
            ("part-time YouTube like task scam on Telegram", 82),
            ("customs/CBI digital arrest video calls", 91),
            ("credit card reward point expiry links", 58),
            ("fake defence personnel QR code on marketplace", 72),
            ("bank KYC document update phishing portals", 66)
        ]

        for i in range(7):
            f_date = today + timedelta(days=i)
            day_label = "Today" if i == 0 else "Tomorrow" if i == 1 else f_date.strftime("%a")
            v_text, base_v_temp = vectors_pool[(i + len(state)) % len(vectors_pool)]

            # Slight daily variance around the state risk temperature
            day_temp = max(20, min(95, risk_temp + int(math.sin(i * 1.5) * 12)))
            day_level = "EXTREME" if day_temp >= 80 else "HIGH" if day_temp >= 65 else "MODERATE" if day_temp >= 45 else "LOW"

            outlook_days.append({
                "date": f_date.strftime("%Y-%m-%d"),
                "day_name": day_label,
                "risk_temp": day_temp,
                "level": day_level,
                "icon": WEATHER_ICONS.get(day_level, "cloud-rain"),
                "primary_vector": v_text if i > 0 else f"{dominant_category.lower()} lures",
                "precipitation_risk_pct": min(98, int(day_temp * 1.05))
            })

        return {
            "status": "success",
            "telemetry_badge": "Simulated / demo data based on NCRB statistical baselines",
            "is_synthetic": True,
            "generated_at": datetime.now().isoformat(),
            "query": {
                "state": state,
                "age_group": age_group,
                "language": language
            },
            "current_weather": {
                "risk_temperature": risk_temp,
                "condition_level": condition_level,
                "condition_label": condition_label,
                "icon": WEATHER_ICONS.get(condition_level, "cloud-rain"),
                "headline": headline,
                "dominant_typology": dominant_category,
                "z_score_anomaly": round(z_score, 2),
                "active_jurisdiction_cases": total_state_cases,
                "trend_indicator": "rising" if z_score > 0.5 else "falling" if z_score < -0.5 else "stable"
            },
            "personalized_advisory": {
                "target_cohort": age_group,
                "dominant_vector_warning": advice_info["vector"],
                "actionable_defense_tip": advice_info["tip"]
            },
            "seven_day_outlook": outlook_days,
            "push_notification_enabled": False
        }

    except Exception as e:
        return {
            "status": "error",
            "message": f"Unable to generate scam weather: {str(e)}"
        }
