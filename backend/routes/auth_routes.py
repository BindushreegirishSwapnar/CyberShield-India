import secrets
import json
from datetime import datetime, timedelta
from flask import Blueprint, request, jsonify
from werkzeug.security import check_password_hash, generate_password_hash
from database import get_session
from models_db import User, AuditLog

auth_bp = Blueprint('auth_bp', __name__)

# Active session token store: token -> {user_dict, expires_at}
ACTIVE_SESSIONS = {}

def get_current_user_from_req():
    """Extract authenticated user from Authorization header."""
    auth_header = request.headers.get("Authorization", "")
    token = None
    if auth_header.startswith("Bearer "):
        token = auth_header.split(" ")[1].strip()
    elif "X-Auth-Token" in request.headers:
        token = request.headers.get("X-Auth-Token").strip()

    if token and token in ACTIVE_SESSIONS:
        sess = ACTIVE_SESSIONS[token]
        if datetime.now() < sess["expires_at"]:
            return sess["user"]
        else:
            del ACTIVE_SESSIONS[token]
    return None

def issue_token_for_user(user_obj):
    token = secrets.token_hex(24)
    expires_at = datetime.now() + timedelta(hours=24)
    user_dict = user_obj.to_dict()
    ACTIVE_SESSIONS[token] = {
        "user": user_dict,
        "expires_at": expires_at
    }
    return token, user_dict

@auth_bp.route('/login', methods=['POST'])
def login():
    """Authenticate user with email/username and password."""
    data = request.get_json() or {}
    identifier = data.get('username') or data.get('email', '')
    password = data.get('password', '')

    if not identifier or not password:
        return jsonify({"status": "fail", "message": "Username/email and password are required."}), 400

    identifier_clean = identifier.strip().lower()

    with get_session() as session:
        user = session.query(User).filter(
            (User.email.ilike(identifier_clean)) | (User.username.ilike(identifier_clean))
        ).first()

        if not user or not check_password_hash(user.password_hash, password):
            return jsonify({"status": "unauthorized", "message": "Invalid credentials provided."}), 401

        token, user_info = issue_token_for_user(user)

        # Log audit trail
        session.add(AuditLog(
            timestamp=datetime.now().strftime("%d %b %Y, %I:%M %p"),
            user_email=user.email,
            user_role=user.role,
            action="LOGIN",
            target_entity="User",
            target_id=str(user.id),
            details=f"User {user.full_name} ({user.role}) logged in successfully.",
            ip_address=request.remote_addr or "127.0.0.1"
        ))

    return jsonify({
        "status": "success",
        "message": f"Welcome, {user_info['full_name']}",
        "token": token,
        "user": user_info
    }), 200

@auth_bp.route('/register', methods=['POST'])
def register():
    """Register a new investigator/analyst user account."""
    data = request.get_json() or {}
    full_name = data.get('full_name', '').strip()
    email = data.get('email', '').strip().lower()
    password = data.get('password', '')
    role = data.get('role', 'Analyst').strip()
    designation = data.get('designation', 'Cyber Crime Investigator').strip()
    state = data.get('state', 'General Investigation Division').strip()
    username = data.get('username', '').strip() or email.split('@')[0]

    if not full_name or not email or not password:
        return jsonify({"status": "fail", "message": "Full name, email, and password are required."}), 400

    with get_session() as session:
        existing = session.query(User).filter(
            (User.email.ilike(email)) | (User.username.ilike(username))
        ).first()
        if existing:
            return jsonify({"status": "fail", "message": "An account with this email or username already exists."}), 409

        new_user = User(
            full_name=full_name,
            email=email,
            username=username,
            role=role,
            designation=designation,
            state=state,
            password_hash=generate_password_hash(password),
            permissions=json.dumps(["analyze_complaints", "view_cases", "add_notes", "view_analytics", "export_reports"])
        )
        session.add(new_user)
        session.commit()

        token, user_info = issue_token_for_user(new_user)
        session.add(AuditLog(
            timestamp=datetime.now().strftime("%d %b %Y, %I:%M %p"),
            user_email=new_user.email,
            user_role=new_user.role,
            action="CREATE_ACCOUNT",
            target_entity="User",
            target_id=str(new_user.id),
            details=f"Account created for {new_user.full_name} ({new_user.role}).",
            ip_address=request.remote_addr or "127.0.0.1"
        ))

    return jsonify({
        "status": "success",
        "message": f"Account created successfully. Welcome, {user_info['full_name']}",
        "token": token,
        "user": user_info
    }), 201

@auth_bp.route('/me', methods=['GET'])
def get_me():
    """Return details of currently authenticated user."""
    user = get_current_user_from_req()
    if not user:
        # Default fallback for unauthenticated public preview in demo
        return jsonify({
            "status": "guest",
            "authenticated": False,
            "user": {
                "id": 0,
                "email": "analyst.sharma@cybercrime.gov.in",
                "username": "analyst_sharma",
                "full_name": "Pooja Sharma",
                "role": "Senior Analyst",
                "designation": "Lead Intelligence Analyst",
                "state": "Maharashtra (Cyber Cell Mumbai)",
                "permissions": ["analyze_complaints", "view_cases", "add_notes", "view_analytics", "export_reports"]
            }
        }), 200

    return jsonify({
        "status": "success",
        "authenticated": True,
        "user": user
    }), 200

@auth_bp.route('/users', methods=['GET'])
def list_users():
    """List all registered analyst and administrator users."""
    with get_session() as session:
        users = session.query(User).all()
        return jsonify({
            "status": "success",
            "count": len(users),
            "data": [u.to_dict() for u in users]
        }), 200

@auth_bp.route('/switch-role', methods=['POST'])
def switch_role():
    """Demo helper: Instantly issue valid credentials for role testing."""
    data = request.get_json() or {}
    target_username = data.get('username', 'analyst_sharma')

    with get_session() as session:
        user = session.query(User).filter(User.username == target_username).first()
        if not user:
            user = session.query(User).first()

        if not user:
            return jsonify({"status": "error", "message": "No users found in database."}), 404

        token, user_info = issue_token_for_user(user)

        session.add(AuditLog(
            timestamp=datetime.now().strftime("%d %b %Y, %I:%M %p"),
            user_email=user.email,
            user_role=user.role,
            action="ROLE_SWITCH",
            target_entity="User",
            target_id=str(user.id),
            details=f"Demo workspace switched role to {user.full_name} ({user.role}).",
            ip_address=request.remote_addr or "127.0.0.1"
        ))

    return jsonify({
        "status": "success",
        "token": token,
        "user": user_info
    }), 200

@auth_bp.route('/logout', methods=['POST'])
def logout():
    """Invalidate current user session."""
    auth_header = request.headers.get("Authorization", "")
    token = None
    if auth_header.startswith("Bearer "):
        token = auth_header.split(" ")[1].strip()

    if token and token in ACTIVE_SESSIONS:
        del ACTIVE_SESSIONS[token]

    return jsonify({"status": "success", "message": "Logged out successfully."}), 200
