import os
import json
import logging
from datetime import datetime
from dotenv import load_dotenv
from flask import Flask, jsonify, request
from flask_cors import CORS

# Load environment configuration
load_dotenv()

from database import init_db, get_db_status
from routes.auth_routes import auth_bp
from routes.cases_routes import cases_bp
from routes.analysis_routes import analysis_bp
from routes.risk_routes import risk_bp
from routes.investigations_routes import investigations_bp
from routes.evidence_routes import evidence_bp
from routes.intelligence_routes import intelligence_bp
from routes.rag_routes import rag_bp
from routes.analytics_routes import analytics_bp
from routes.powerbi_routes import powerbi_bp
from routes.reports_routes import reports_bp
from routes.system_routes import system_bp

from routes.bi_routes import bi_bp
from routes.graph_routes import graph_bp
from modules.weather.weather_routes import weather_bp
from modules.dojo.dojo_routes import dojo_bp
from modules.safescan.safescan_routes import safescan_bp
from modules.moneytrail.moneytrail_routes import moneytrail_bp
from modules.threats.threat_routes import threat_bp
from modules.agent.agent_routes import agent_bp






# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s'
)
logger = logging.getLogger("CyberCrimePredict")

def create_app():
    """Application factory for Cyber Crime Intelligence & Investigation Platform."""
    app = Flask(__name__)

    # Configuration
    app.config['SECRET_KEY'] = os.getenv("SECRET_KEY", "cybercrime_secret_key_default_2026")
    app.config['JSON_SORT_KEYS'] = False

    # Universal CORS: support public PWA domains, localhost dev, and Capacitor mobile schemes
    CORS(
        app,
        resources={r"/*": {"origins": "*"}},
        methods=["GET", "POST", "PATCH", "DELETE", "OPTIONS"],
        allow_headers=["Content-Type", "Authorization", "X-Auth-Token"]
    )

    # Initialize Database Schema & Synthetic Records
    try:
        init_db()
        logger.info("Database schema and synthetic demonstration data confirmed.")
    except Exception as e:
        logger.error(f"Error initializing database: {e}")

    # Register Blueprints for /api/v1
    app.register_blueprint(auth_bp, url_prefix='/api/v1/auth', name='auth_v1_bp')
    app.register_blueprint(cases_bp, url_prefix='/api/v1/cases', name='cases_v1_bp')
    app.register_blueprint(cases_bp, url_prefix='/api/v1/complaints', name='complaints_v1_bp')
    app.register_blueprint(analysis_bp, url_prefix='/api/v1/analysis', name='analysis_v1_bp')
    app.register_blueprint(analysis_bp, url_prefix='/api/v1/analyze', name='analyze_v1_bp')
    app.register_blueprint(risk_bp, url_prefix='/api/v1/risk', name='risk_v1_bp')
    app.register_blueprint(investigations_bp, url_prefix='/api/v1/investigations', name='investigations_v1_bp')
    app.register_blueprint(evidence_bp, url_prefix='/api/v1/evidence', name='evidence_v1_bp')
    app.register_blueprint(intelligence_bp, url_prefix='/api/v1/intelligence', name='intelligence_v1_bp')
    app.register_blueprint(rag_bp, url_prefix='/api/v1/rag', name='rag_v1_bp')
    app.register_blueprint(analytics_bp, url_prefix='/api/v1/analytics', name='analytics_v1_bp')
    app.register_blueprint(powerbi_bp, url_prefix='/api/v1/powerbi', name='powerbi_v1_bp')
    app.register_blueprint(reports_bp, url_prefix='/api/v1/reports', name='reports_v1_bp')
    app.register_blueprint(system_bp, url_prefix='/api/v1/system', name='system_v1_bp')

    # Register Blueprints for legacy /api backwards-compatibility
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(cases_bp, url_prefix='/api/cases')
    app.register_blueprint(cases_bp, url_prefix='/api/complaints', name='complaints_legacy_bp')
    app.register_blueprint(analysis_bp, url_prefix='/api/analysis')
    app.register_blueprint(analysis_bp, url_prefix='/api/analyze', name='analysis_legacy_bp')
    app.register_blueprint(risk_bp, url_prefix='/api/risk')
    app.register_blueprint(investigations_bp, url_prefix='/api/investigations')
    app.register_blueprint(evidence_bp, url_prefix='/api/evidence')
    app.register_blueprint(intelligence_bp, url_prefix='/api/intelligence')
    app.register_blueprint(rag_bp, url_prefix='/api/rag')
    app.register_blueprint(analytics_bp, url_prefix='/api/analytics')
    app.register_blueprint(bi_bp, url_prefix='/api/v1/bi', name='bi_v1_bp')
    app.register_blueprint(bi_bp, url_prefix='/api/bi', name='bi_legacy_bp')
    app.register_blueprint(graph_bp, url_prefix='/api/v1/graph', name='graph_v1_bp')
    app.register_blueprint(graph_bp, url_prefix='/api/graph', name='graph_legacy_bp')
    app.register_blueprint(weather_bp, url_prefix='/api/v1/weather', name='weather_v1_bp')
    app.register_blueprint(weather_bp, url_prefix='/api/weather', name='weather_legacy_bp')
    app.register_blueprint(dojo_bp, url_prefix='/api/v1/dojo', name='dojo_v1_bp')
    app.register_blueprint(dojo_bp, url_prefix='/api/dojo', name='dojo_legacy_bp')
    app.register_blueprint(safescan_bp, url_prefix='/api/v1/safescan', name='safescan_v1_bp')
    app.register_blueprint(safescan_bp, url_prefix='/api/safescan', name='safescan_legacy_bp')
    app.register_blueprint(moneytrail_bp, url_prefix='/api/v1/moneytrail', name='moneytrail_v1_bp')
    app.register_blueprint(moneytrail_bp, url_prefix='/api/moneytrail', name='moneytrail_legacy_bp')
    app.register_blueprint(threat_bp, url_prefix='/api/v1/threats', name='threat_v1_bp')
    app.register_blueprint(threat_bp, url_prefix='/api/threats', name='threat_legacy_bp')
    app.register_blueprint(agent_bp, url_prefix='/api/v1/agent', name='agent_v1_bp')
    app.register_blueprint(agent_bp, url_prefix='/api/agent', name='agent_legacy_bp')






    # Root Health Check endpoints
    @app.route('/api/v1/health', methods=['GET'])
    @app.route('/api/health', methods=['GET'])
    @app.route('/health', methods=['GET'])
    def root_health():
        from routes.system_routes import get_system_health
        return get_system_health()

    # Root endpoint
    @app.route('/', methods=['GET'])
    def root():
        return jsonify({
            "project": "CyberShield India — Predictive Cyber Crime Intelligence & Investigation Platform",
            "description": "Production Government / Law Enforcement Operational Suite — Synthetic Research Data",
            "status": "online",
            "version": "3.5.0",
            "api_version": "v1",
            "timestamp": datetime.now().isoformat(),
            "endpoints": {
                "auth": "/api/v1/auth/*",
                "cases": "/api/v1/cases/*",
                "analysis": "/api/v1/analysis/*",
                "risk": "/api/v1/risk/*",
                "investigations": "/api/v1/investigations/*",
                "evidence": "/api/v1/evidence/*",
                "intelligence": "/api/v1/intelligence/*",
                "link_graph": "/api/v1/intelligence/link-graph",
                "rag": "/api/v1/rag/*",
                "analytics": "/api/v1/analytics/*",
                "powerbi": "/api/v1/powerbi/*",
                "reports": "/api/v1/reports/*",
                "system": "/api/v1/system/*"
            }
        }), 200

    # Provenance Endpoint
    @app.route('/api/v1/provenance', methods=['GET'])
    @app.route('/api/provenance', methods=['GET'])
    def get_provenance():
        prov_path = os.path.join(os.path.dirname(__file__), 'data', 'metadata', 'provenance.json')
        if os.path.exists(prov_path):
            with open(prov_path, 'r', encoding='utf-8') as f:
                return jsonify(json.load(f)), 200
        return jsonify({"status": "error", "message": "Provenance metadata file not found"}), 404

    # Backwards-compatible legacy status & model endpoints
    @app.route('/api/v1/status', methods=['GET'])
    @app.route('/api/status', methods=['GET'])
    def legacy_status():
        db_stat = get_db_status()
        return jsonify({
            "status": "success",
            "backend": "CyberShield India Production API online",
            "database": f"{db_stat.get('dialect', 'sqlite').title()} connected successfully",
            "model_ready": True,
            "total_complaints": db_stat.get("complaint_count", 0),
            "critical_complaints": db_stat.get("critical_count", 0)
        }), 200

    @app.route('/api/v1/model-info', methods=['GET'])
    @app.route('/api/model-info', methods=['GET'])
    def legacy_model_info():
        from routes.system_routes import load_metrics_file
        metrics = load_metrics_file()
        return jsonify({
            "status": "success",
            "data": metrics
        }), 200

    # Global Error Handlers (Structured JSON - Section 40)
    @app.errorhandler(400)
    def handle_bad_request(e):
        return jsonify({
            "status": "error",
            "code": "BAD_REQUEST",
            "message": str(e.description) if hasattr(e, 'description') else "Invalid request parameters."
        }), 400

    @app.errorhandler(404)
    def handle_not_found(e):
        return jsonify({
            "status": "error",
            "code": "RESOURCE_NOT_FOUND",
            "message": "The requested API endpoint or case entity does not exist."
        }), 404

    @app.errorhandler(500)
    def handle_server_error(e):
        logger.error(f"Internal server error: {e}")
        return jsonify({
            "status": "error",
            "code": "INTERNAL_SERVER_ERROR",
            "message": "An internal operational error occurred while processing the request."
        }), 500

    return app

app = create_app()

if __name__ == '__main__':
    port = int(os.getenv("PORT", 5000))
    host = os.getenv("HOST", "0.0.0.0")
    debug_mode = os.getenv("DEBUG", "False").lower() in ("true", "1")
    print(f"Starting CyberCrimePredict Intelligence Platform on http://{host}:{port}...")
    app.run(host=host, port=port, debug=debug_mode)
