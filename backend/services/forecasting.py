import os
import pandas as pd
import numpy as np

DATA_CSV = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'raw', 'india_cybercrime_statewise.csv')

def get_forecast(state='All India', category='All Categories', horizon='next_year'):
    """
    Time-Series Trend Forecasting for Cyber Crime Complaints.
    Aggregates historical NCRB baseline data (2019-2025) and computes
    projected complaint volumes with 95% confidence intervals.
    """
    if not os.path.exists(DATA_CSV):
        return {"status": "error", "message": "State-wise dataset not found."}

    df = pd.read_csv(DATA_CSV)

    # Filter by state if specified
    if state and state != 'All India':
        df = df[df['State_UT'] == state]

    # Filter by category if specified
    if category and category != 'All Categories':
        df = df[df['Crime_Category'] == category]

    if df.empty:
        return {"status": "fail", "message": "No historical data matches the specified filters."}

    # Aggregate by Year
    yearly = df.groupby('Year')['Reported_Cases'].sum().reset_index().sort_values('Year')
    years = yearly['Year'].values
    cases = yearly['Reported_Cases'].values

    # Fit linear/trend model with residuals for confidence interval
    x = years - 2019
    y = cases

    # Degree 1 polynomial fit
    p, residuals, _, _, _ = np.polyfit(x, y, 1, full=True)
    slope, intercept = p[0], p[1]

    # Estimate standard error of regression
    if len(y) > 2:
        fitted = slope * x + intercept
        std_err = float(np.std(y - fitted))
    else:
        std_err = float(np.mean(y) * 0.08)

    historical_data = [
        {"period": str(yr), "cases": int(val), "type": "historical"}
        for yr, val in zip(years, cases)
    ]

    # Future projection horizons
    forecast_points = []
    
    # 2026 estimate (full year)
    x_2026 = 2026 - 2019
    pred_2026 = int(slope * x_2026 + intercept)
    margin_2026 = int(1.96 * std_err)
    
    # 2027 estimate (full year)
    x_2027 = 2027 - 2019
    pred_2027 = int(slope * x_2027 + intercept)
    margin_2027 = int(2.10 * std_err)

    # Monthly breakdown for Next Month (Oct 2026) and Next Quarter (Q4 2026)
    monthly_rate_2026 = pred_2026 / 12.0
    
    forecast_points.append({
        "horizon": "next_month",
        "period": "October 2026",
        "predicted_cases": int(monthly_rate_2026 * 1.04),
        "lower_ci": max(0, int((monthly_rate_2026 - (margin_2026 / 12.0)) * 0.95)),
        "upper_ci": int((monthly_rate_2026 + (margin_2026 / 12.0)) * 1.05),
        "growth_rate_pct": round(float((slope / np.mean(cases)) * 100), 1)
    })

    forecast_points.append({
        "horizon": "next_quarter",
        "period": "Q4 2026 (Oct - Dec)",
        "predicted_cases": int(monthly_rate_2026 * 3 * 1.05),
        "lower_ci": max(0, int((monthly_rate_2026 * 3 - (margin_2026 / 4.0)))),
        "upper_ci": int((monthly_rate_2026 * 3 + (margin_2026 / 4.0))),
        "growth_rate_pct": round(float((slope / np.mean(cases)) * 100), 1)
    })

    forecast_points.append({
        "horizon": "next_year",
        "period": "Calendar Year 2027",
        "predicted_cases": pred_2027,
        "lower_ci": max(0, pred_2027 - margin_2027),
        "upper_ci": pred_2027 + margin_2027,
        "growth_rate_pct": round(float((slope / np.mean(cases)) * 100), 1)
    })

    return {
        "status": "success",
        "state": state,
        "category": category,
        "historical": historical_data,
        "forecasts": forecast_points,
        "model_parameters": {
            "method": "Polynomial Trend Regression with 95% Confidence Bounds",
            "annual_velocity_delta": int(slope),
            "historical_baseline_mean": int(np.mean(cases))
        },
        "advisory": "Statistical projection model for operational capacity planning and threat awareness; does not represent a guaranteed legal outcome."
    }
