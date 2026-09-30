from flask import Blueprint, request, jsonify
from modules.weather.weather_service import get_scam_weather_forecast

weather_bp = Blueprint('weather_bp', __name__)

@weather_bp.route('/forecast', methods=['GET'])
def get_weather():
    """
    Get scam weather forecast by jurisdiction, age cohort, and language.
    """
    state = request.args.get('state', 'Karnataka')
    age_group = request.args.get('age_group', 'Senior Citizen (60+)')
    language = request.args.get('language', 'en')

    result = get_scam_weather_forecast(state=state, age_group=age_group, language=language)
    status_code = 200 if result.get('status') == 'success' else 500
    return jsonify(result), status_code

@weather_bp.route('/subscribe', methods=['POST'])
def subscribe_push():
    """
    Register or simulate web push subscription for scam weather spike alerts.
    """
    data = request.get_json() or {}
    state = data.get('state', 'Karnataka')
    cohort = data.get('age_group', 'General')
    fcm_token = data.get('token', 'simulated-pwa-token-1930')

    return jsonify({
        "status": "success",
        "message": f"Successfully subscribed to High/Extreme Scam Weather Alerts for {state} ({cohort}).",
        "disclaimer": "Simulated / demo data notification subscription active for demonstration.",
        "active_subscription": {
            "state": state,
            "cohort": cohort,
            "threshold": "Risk Temperature >= 75",
            "channel": "PWA Web Push Notification"
        }
    }), 200
