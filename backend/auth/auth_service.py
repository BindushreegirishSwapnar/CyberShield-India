import secrets
from datetime import datetime, timedelta
from functools import wraps
from flask import request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash

# In-memory active session token store (token -> {user_dict, expires_at})
ACTIVE_SESSIONS = {}

DEMO_USERS = [
    {
        "id": 1,
        "email": "admin@cybercrime.gov.in",
        "username": "sysadmin",
        "full_name": "Dr. Rajeshwar Rao, IPS",
        "role": "Administrator",
        "designation": "Director General (Cyber Operations & I4C)",
        "state": "National Headquarters (New Delhi)",
        "password_hash": generate_password_hash("Admin@2026"),
        "permissions": ["all", "manage_users", "override_status", "view_audit_logs", "retrain_models"]
    },
    {
        "id": 2,
        "email": "analyst.sharma@cybercrime.gov.in",
        "username": "analyst_sharma",
        "full_name": "Pooja Sharma",
        "role": "Cyber Crime Analyst",
        "designation": "Lead Intelligence Analyst",
        "state": "Maharashtra (Cyber Cell Mumbai)",
        "password_hash": generate_password_hash("Analyst@2026"),
        "permissions": ["analyze_complaints", "view_risk", "query_rag", "view_analytics", "export_reports"]
    },
    {
        "id": 3,
        "email": "io.patil@cybercrime.gov.in",
        "username": "io_patil",
        "full_name": "Inspector Anand Patil",
        "role": "Investigation Officer",
        "designation": "Station House Officer (Cyber Crime PS)",
        "state": "Karnataka (Bengaluru Cyber PS)",
        "password_hash": generate_password_hash("Officer@2026"),
        "permissions": ["view_assigned_cases", "update_case_status", "add_investigation_notes", "query_rag"]
    },
    {
        "id": 4,
        "email": "auditor@cybercrime.gov.in",
        "username": "auditor_verma",
        "full_name": "Vikram Verma",
        "role": "Viewer",
        "designation": "State Compliance & Oversight Auditor",
        "state": "Telangana (Hyderabad)",
        "password_hash": generate_password_hash("Viewer@2026"),
        "permissions": ["view_dashboard", "view_complaints_readonly", "export_summary"]
    }
]

def authenticate_user(email, password):
    """Authenticate credentials against stored user accounts."""
    email_clean = email.strip().lower()
    for user in DEMO_USERS:
        if user["email"].lower() == email_clean or user["username"].lower() == email_clean:
            if check_password_hash(user["password_hash"], password):
                # Issue session token valid for 24 hours
                token = secrets.token_hex(24)
                expires_at = datetime.now() + timedelta(hours=24)
                
                user_info = {
                    "id": user["id"],
                    "email": user["email"],
                    "username": user["username"],
                    "full_name": user["full_name"],
                    "role": user["role"],
                    "designation": user["designation"],
                    "state": user["state"],
                    "permissions": user["permissions"],
                    "last_login": datetime.now().strftime("%d %b %Y, %I:%M %p")
                }
                
                ACTIVE_SESSIONS[token] = {
                    "user": user_info,
                    "expires_at": expires_at
                }
                return token, user_info
    return None, None

def get_current_user():
    """Extract authenticated user from Authorization Bearer token header."""
    auth_header = request.headers.get("Authorization", "")
    token = None
    if auth_header.startswith("Bearer "):
        token = auth_header.split(" ")[1].strip()
    elif "X-Auth-Token" in request.headers:
        token = request.headers.get("X-Auth-Token").strip()
    
    if token and token in ACTIVE_SESSIONS:
        session = ACTIVE_SESSIONS[token]
        if datetime.now() < session["expires_at"]:
            return session["user"]
        else:
            del ACTIVE_SESSIONS[token]
    return None

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user = get_current_user()
        if not user:
            return jsonify({
                "status": "unauthorized",
                "message": "Authentication required. Please log in with valid credentials."
            }), 401
        return f(*args, **kwargs)
    return decorated_function

def role_required(allowed_roles):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            user = get_current_user()
            if not user:
                return jsonify({"status": "unauthorized", "message": "Authentication required."}), 401
            if user["role"] not in allowed_roles:
                return jsonify({
                    "status": "forbidden",
                    "message": f"Access denied. Requires one of roles: {', '.join(allowed_roles)}"
                }), 403
            return f(*args, **kwargs)
        return decorated_function
    return decorator
