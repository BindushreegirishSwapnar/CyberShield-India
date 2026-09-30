"""Authentication helpers for the Flask session-based API."""

import re
from functools import wraps

from flask import g, jsonify, session
from werkzeug.security import check_password_hash, generate_password_hash

from database import get_db_connection

EMAIL_PATTERN = re.compile(r"^[^\s@]+@[^\s@]+\.[^\s@]+$")
USERNAME_PATTERN = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.-]{2,23}$")


def public_user(row):
    if row is None:
        return None
    return {
        "id": row["id"],
        "full_name": row["full_name"],
        "username": row["username"],
        "email": row["email"],
        "role": row["role"],
        "is_active": bool(row["is_active"]),
        "created_at": row["created_at"],
    }


def validate_signup(data):
    full_name = str(data.get("full_name") or "").strip()
    username = str(data.get("username") or "").strip()
    email = str(data.get("email") or "").strip().lower()
    password = data.get("password")

    if not full_name or len(full_name) > 100:
        raise ValueError("Enter a name between 1 and 100 characters.")
    if not USERNAME_PATTERN.fullmatch(username):
        raise ValueError("Username must be 3-24 characters and use letters, numbers, dots, dashes, or underscores.")
    if len(email) > 254 or not EMAIL_PATTERN.fullmatch(email):
        raise ValueError("Enter a valid email address.")
    if not isinstance(password, str) or len(password) < 12 or len(password) > 128:
        raise ValueError("Password must be between 12 and 128 characters.")
    if not re.search(r"[a-z]", password) or not re.search(r"[A-Z]", password) or not re.search(r"\d", password):
        raise ValueError("Password must include an uppercase letter, a lowercase letter, and a number.")
    return full_name, username, email, password


def create_user(full_name, username, email, password, role="USER"):
    conn = get_db_connection()
    try:
        duplicate_email = conn.execute("SELECT 1 FROM users WHERE email = ? COLLATE NOCASE", (email,)).fetchone()
        if duplicate_email:
            raise ValueError("An account with this email already exists.")
        duplicate_username = conn.execute("SELECT 1 FROM users WHERE username = ? COLLATE NOCASE", (username,)).fetchone()
        if duplicate_username:
            raise ValueError("This username is already taken.")
        cursor = conn.execute(
            "INSERT INTO users (full_name, username, email, password_hash, role) VALUES (?, ?, ?, ?, ?)",
            (full_name, username, email, generate_password_hash(password, method="scrypt"), role),
        )
        conn.commit()
        return cursor.lastrowid
    finally:
        conn.close()


def load_session_user():
    user_id = session.get("user_id")
    if not user_id:
        g.current_user = None
        return
    conn = get_db_connection()
    try:
        row = conn.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
    finally:
        conn.close()
    if row is None or not row["is_active"]:
        session.clear()
        g.current_user = None
        return
    g.current_user = dict(row)


def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if getattr(g, "current_user", None) is None:
            return jsonify({"status": "unauthorized", "message": "Please sign in to continue."}), 401
        return view(*args, **kwargs)
    return wrapped


def admin_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        user = getattr(g, "current_user", None)
        if user is None:
            return jsonify({"status": "unauthorized", "message": "Please sign in to continue."}), 401
        if user["role"] != "ADMIN":
            return jsonify({"status": "forbidden", "message": "You do not have permission to access this resource."}), 403
        return view(*args, **kwargs)
    return wrapped


def verify_credentials(identifier, password):
    conn = get_db_connection()
    try:
        user = conn.execute(
            "SELECT * FROM users WHERE email = ? COLLATE NOCASE OR username = ? COLLATE NOCASE",
            (str(identifier or "").strip(), str(identifier or "").strip()),
        ).fetchone()
    finally:
        conn.close()
    if user is None or not isinstance(password, str) or not check_password_hash(user["password_hash"], password):
        return None, "Invalid email/username or password.", 401
    if not user["is_active"]:
        return None, "This account is inactive. Contact an administrator.", 403
    return dict(user), None, None