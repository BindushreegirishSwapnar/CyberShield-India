"""Create the first administrator using an interactive, local-only setup."""

from getpass import getpass

from auth_service import create_user, validate_signup
from database import get_db_connection, init_db


def main():
    init_db()
    conn = get_db_connection()
    try:
        existing = conn.execute("SELECT 1 FROM users WHERE role = 'ADMIN' LIMIT 1").fetchone()
    finally:
        conn.close()
    if existing:
        print("An administrator already exists. No account was created.")
        return

    print("Create the initial CyberNexa administrator.")
    details = {
        "full_name": input("Admin name: "),
        "email": input("Admin email: "),
        "username": input("Admin username: "),
        "password": getpass("Admin password (12+ chars, upper/lowercase and number): "),
    }
    confirmation = getpass("Confirm admin password: ")
    if details["password"] != confirmation:
        raise SystemExit("Passwords do not match. No account was created.")
    try:
        full_name, username, email, password = validate_signup(details)
        create_user(full_name, username, email, password, role="ADMIN")
    except ValueError as error:
        raise SystemExit(str(error)) from None
    print("Administrator created. Sign in at /login.")


if __name__ == "__main__":
    main()