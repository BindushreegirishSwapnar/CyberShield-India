"""User-scoped personal safety services; external alert delivery is not configured."""

import json
import math
import re

from flask import Blueprint, g, jsonify, request

from auth_service import admin_required, login_required
from database import get_db_connection

safety_api = Blueprint("safety_api", __name__)
DEFAULT_MESSAGE = "I may be in danger and need assistance. Please check on me."
CONTACT_PHONE = re.compile(r"^\+?[0-9][0-9 .()\-]{5,24}$")
SETTING_TYPES = {
    "four_tap_enabled": bool,
    "tap_window_seconds": int,
    "countdown_seconds": int,
    "instant_alert_mode": bool,
    "quick_alert_enabled": bool,
    "loud_alarm_enabled": bool,
    "trip_monitoring_enabled": bool,
    "trip_update_interval": int,
}


class EmergencyNotificationService:
    """Interface point for a future authorized SMS/emergency provider."""

    def create_request(self, recipient_count):
        raise NotImplementedError


class MockEmergencyNotificationService(EmergencyNotificationService):
    """Development-only simulation; this class never sends a notification."""

    def create_request(self, recipient_count):
        return {
            "mode": "DEMO / SIMULATION",
            "delivery_status": "REQUEST_CREATED",
            "recipient_count": recipient_count,
            "message": "Alert request created. No contacts or emergency services were contacted.",
        }


notification_service = MockEmergencyNotificationService()


def _settings_for(user_id, conn):
    conn.execute("INSERT OR IGNORE INTO safety_settings (user_id) VALUES (?)", (user_id,))
    return conn.execute("SELECT * FROM safety_settings WHERE user_id = ?", (user_id,)).fetchone()


def _settings_json(row):
    return {
        "four_tap_enabled": bool(row["four_tap_enabled"]),
        "tap_window_seconds": row["tap_window_seconds"],
        "countdown_seconds": row["countdown_seconds"],
        "instant_alert_mode": bool(row["instant_alert_mode"]),
        "quick_alert_enabled": bool(row["quick_alert_enabled"]),
        "loud_alarm_enabled": bool(row["loud_alarm_enabled"]),
        "trip_monitoring_enabled": bool(row["trip_monitoring_enabled"]),
        "trip_update_interval": row["trip_update_interval"],
        "location_permission": "controlled by the device/browser",
        "local_emergency_number": "112",
    }


def _coordinates(data):
    latitude = data.get("latitude")
    longitude = data.get("longitude")
    accuracy = data.get("location_accuracy")
    if latitude is None and longitude is None:
        return None, None, None
    if latitude is None or longitude is None:
        raise ValueError("Both latitude and longitude are required when including location.")
    if isinstance(latitude, bool) or isinstance(longitude, bool):
        raise ValueError("Location coordinates are invalid.")
    try:
        latitude = float(latitude)
        longitude = float(longitude)
        accuracy = None if accuracy is None else float(accuracy)
    except (TypeError, ValueError):
        raise ValueError("Location coordinates are invalid.") from None
    if not math.isfinite(latitude) or not math.isfinite(longitude) or not -90 <= latitude <= 90 or not -180 <= longitude <= 180:
        raise ValueError("Location coordinates are outside valid ranges.")
    if accuracy is not None and (not math.isfinite(accuracy) or accuracy < 0):
        raise ValueError("Location accuracy must be a non-negative number.")
    return latitude, longitude, accuracy


def _event(conn, user_id, event_type, status, metadata=None):
    conn.execute(
        "INSERT INTO safety_events (user_id, event_type, status, metadata) VALUES (?, ?, ?, ?)",
        (user_id, event_type, status, json.dumps(metadata or {})),
    )


def _contacts_for_ids(conn, user_id, requested_ids):
    if requested_ids is None:
        return conn.execute(
            "SELECT id, name, relationship, phone FROM emergency_contacts WHERE user_id = ? AND is_active = 1 ORDER BY id",
            (user_id,),
        ).fetchall()
    if not isinstance(requested_ids, list) or any(not isinstance(item, int) for item in requested_ids):
        raise ValueError("Contact selection is invalid.")
    if not requested_ids:
        return []
    placeholders = ",".join("?" for _ in requested_ids)
    rows = conn.execute(
        f"SELECT id, name, relationship, phone FROM emergency_contacts WHERE user_id = ? AND is_active = 1 AND id IN ({placeholders})",
        [user_id, *requested_ids],
    ).fetchall()
    if len(rows) != len(set(requested_ids)):
        raise ValueError("Choose only your own active emergency contacts.")
    return rows


@safety_api.get("/api/safety/status")
@login_required
def safety_status():
    conn = get_db_connection()
    try:
        active_trip = conn.execute(
            "SELECT id, started_at, location_updated_at, last_latitude IS NOT NULL AS has_location "
            "FROM safety_trips WHERE user_id = ? AND status = 'ACTIVE' ORDER BY id DESC LIMIT 1",
            (g.current_user["id"],),
        ).fetchone()
        contacts = conn.execute(
            "SELECT COUNT(*) FROM emergency_contacts WHERE user_id = ? AND is_active = 1",
            (g.current_user["id"],),
        ).fetchone()[0]
        settings = _settings_for(g.current_user["id"], conn)
        conn.commit()
        return jsonify({
            "status": "success",
            "trip": dict(active_trip) if active_trip else None,
            "active_contact_count": contacts,
            "settings": _settings_json(settings),
            "notification_mode": "DEMO / SIMULATION",
        }), 200
    finally:
        conn.close()


@safety_api.route("/api/safety/contacts", methods=["GET", "POST"])
@login_required
def safety_contacts():
    user_id = g.current_user["id"]
    conn = get_db_connection()
    try:
        if request.method == "GET":
            rows = conn.execute(
                "SELECT id, name, relationship, phone, is_active, created_at, updated_at "
                "FROM emergency_contacts WHERE user_id = ? ORDER BY id DESC", (user_id,),
            ).fetchall()
            return jsonify({"status": "success", "data": [dict(row) | {"is_active": bool(row["is_active"])} for row in rows]}), 200
        data = request.get_json(silent=True) or {}
        name = str(data.get("name") or "").strip()
        relationship = str(data.get("relationship") or "").strip()
        phone = str(data.get("phone") or "").strip()
        if not name or len(name) > 100 or not relationship or len(relationship) > 60 or not CONTACT_PHONE.fullmatch(phone) or sum(char.isdigit() for char in phone) < 7:
            return jsonify({"status": "fail", "message": "Provide a contact name, relationship, and valid phone number."}), 400
        cursor = conn.execute(
            "INSERT INTO emergency_contacts (user_id, name, relationship, phone) VALUES (?, ?, ?, ?)",
            (user_id, name, relationship, phone),
        )
        conn.commit()
        contact = conn.execute(
            "SELECT id, name, relationship, phone, is_active, created_at, updated_at FROM emergency_contacts WHERE id = ? AND user_id = ?",
            (cursor.lastrowid, user_id),
        ).fetchone()
        return jsonify({"status": "success", "data": dict(contact) | {"is_active": True}}), 201
    finally:
        conn.close()


@safety_api.patch("/api/safety/contacts/<int:contact_id>")
@login_required
def update_safety_contact(contact_id):
    data = request.get_json(silent=True) or {}
    allowed = {"name", "relationship", "phone", "is_active"}
    if not data or set(data) - allowed:
        return jsonify({"status": "fail", "message": "Only contact name, relationship, phone, and active status can be changed."}), 400
    conn = get_db_connection()
    try:
        row = conn.execute("SELECT * FROM emergency_contacts WHERE id = ? AND user_id = ?", (contact_id, g.current_user["id"])).fetchone()
        if row is None:
            return jsonify({"status": "fail", "message": "Emergency contact not found."}), 404
        values = {key: row[key] for key in allowed}
        values.update(data)
        values["name"] = str(values["name"]).strip()
        values["relationship"] = str(values["relationship"]).strip()
        values["phone"] = str(values["phone"]).strip()
        if not values["name"] or len(values["name"]) > 100 or not values["relationship"] or len(values["relationship"]) > 60 or not CONTACT_PHONE.fullmatch(values["phone"]) or sum(char.isdigit() for char in values["phone"]) < 7 or not isinstance(values["is_active"], (int, bool)):
            return jsonify({"status": "fail", "message": "Contact details are invalid."}), 400
        conn.execute(
            "UPDATE emergency_contacts SET name = ?, relationship = ?, phone = ?, is_active = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ? AND user_id = ?",
            (values["name"], values["relationship"], values["phone"], int(bool(values["is_active"])), contact_id, g.current_user["id"]),
        )
        conn.commit()
        return jsonify({"status": "success"}), 200
    finally:
        conn.close()


@safety_api.delete("/api/safety/contacts/<int:contact_id>")
@login_required
def delete_safety_contact(contact_id):
    conn = get_db_connection()
    try:
        cursor = conn.execute("DELETE FROM emergency_contacts WHERE id = ? AND user_id = ?", (contact_id, g.current_user["id"]))
        if cursor.rowcount == 0:
            return jsonify({"status": "fail", "message": "Emergency contact not found."}), 404
        conn.commit()
        return jsonify({"status": "success"}), 200
    finally:
        conn.close()


@safety_api.route("/api/safety/settings", methods=["GET", "PATCH"])
@login_required
def safety_settings():
    conn = get_db_connection()
    try:
        row = _settings_for(g.current_user["id"], conn)
        if request.method == "GET":
            conn.commit()
            return jsonify({"status": "success", "data": _settings_json(row)}), 200
        data = request.get_json(silent=True) or {}
        if not data or set(data) - set(SETTING_TYPES):
            return jsonify({"status": "fail", "message": "One or more safety settings are unsupported."}), 400
        values = {}
        for key, value in data.items():
            expected = SETTING_TYPES[key]
            if expected is bool and not isinstance(value, bool):
                return jsonify({"status": "fail", "message": f"{key} must be true or false."}), 400
            if expected is int and (isinstance(value, bool) or not isinstance(value, int)):
                return jsonify({"status": "fail", "message": f"{key} must be a whole number."}), 400
            if key == "tap_window_seconds" and not 2 <= value <= 8:
                return jsonify({"status": "fail", "message": "Tap sensitivity must be between 2 and 8 seconds."}), 400
            if key == "countdown_seconds" and not 3 <= value <= 15:
                return jsonify({"status": "fail", "message": "Countdown must be between 3 and 15 seconds."}), 400
            if key == "trip_update_interval" and not 30 <= value <= 600:
                return jsonify({"status": "fail", "message": "Trip location interval must be between 30 and 600 seconds."}), 400
            values[key] = int(value) if expected is bool else value
        assignments = ", ".join(f"{key} = ?" for key in values)
        conn.execute(f"UPDATE safety_settings SET {assignments}, updated_at = CURRENT_TIMESTAMP WHERE user_id = ?", [*values.values(), g.current_user["id"]])
        conn.commit()
        updated = conn.execute("SELECT * FROM safety_settings WHERE user_id = ?", (g.current_user["id"],)).fetchone()
        return jsonify({"status": "success", "data": _settings_json(updated)}), 200
    finally:
        conn.close()


@safety_api.post("/api/safety/alert")
@login_required
def create_safety_alert():
    data = request.get_json(silent=True) or {}
    try:
        latitude, longitude, accuracy = _coordinates(data)
        alert_type = str(data.get("alert_type") or "EMERGENCY").strip().upper()
        if alert_type not in {"EMERGENCY", "QUICK_ALERT", "FOUR_TAP"}:
            raise ValueError("Alert type is invalid.")
        message = str(data.get("message") or DEFAULT_MESSAGE).strip()
        if len(message) > 280:
            raise ValueError("Emergency message must be 280 characters or fewer.")
        conn = get_db_connection()
        try:
            recipients = _contacts_for_ids(conn, g.current_user["id"], data.get("contact_ids"))
            simulated = notification_service.create_request(len(recipients))
            cursor = conn.execute(
                "INSERT INTO safety_alerts (user_id, alert_type, latitude, longitude, location_accuracy, status, notification_mode, recipient_contact_ids, message) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (g.current_user["id"], alert_type, latitude, longitude, accuracy, simulated["delivery_status"], simulated["mode"], json.dumps([row["id"] for row in recipients]), message),
            )
            alert_id = cursor.lastrowid
            _event(conn, g.current_user["id"], "EMERGENCY_ALERT", simulated["delivery_status"], {"alert_id": alert_id, "location_available": latitude is not None, "active_contact_count": len(recipients), "notification_mode": simulated["mode"]})
            conn.commit()
            return jsonify({
                "status": "success", "alert_id": alert_id, "alert_status": simulated["delivery_status"],
                "notification_mode": simulated["mode"], "contact_count": len(recipients),
                "location_available": latitude is not None, "message": simulated["message"],
                "contacts": [{"id": row["id"], "name": row["name"], "relationship": row["relationship"], "phone": row["phone"]} for row in recipients],
            }), 201
        finally:
            conn.close()
    except ValueError as error:
        return jsonify({"status": "fail", "message": str(error)}), 400


@safety_api.post("/api/safety/alert/cancel-pending")
@login_required
def cancel_pending_safety_alert():
    conn = get_db_connection()
    try:
        _event(conn, g.current_user["id"], "ALERT_CANCELLED", "ALERT_CANCELLED", {"reason": "cancelled during local confirmation countdown"})
        conn.commit()
        return jsonify({"status": "success", "status_label": "ALERT_CANCELLED", "message": "No emergency alert request was created."}), 200
    finally:
        conn.close()


@safety_api.post("/api/safety/alert/<int:alert_id>/cancel")
@login_required
def cancel_created_safety_alert(alert_id):
    conn = get_db_connection()
    try:
        alert = conn.execute("SELECT id FROM safety_alerts WHERE id = ? AND user_id = ? AND status = 'REQUEST_CREATED'", (alert_id, g.current_user["id"])).fetchone()
        if alert is None:
            return jsonify({"status": "fail", "message": "Pending alert request not found."}), 404
        conn.execute("UPDATE safety_alerts SET status = 'ALERT_CANCELLED', cancelled_at = CURRENT_TIMESTAMP WHERE id = ?", (alert_id,))
        _event(conn, g.current_user["id"], "ALERT_CANCELLED", "ALERT_CANCELLED", {"alert_id": alert_id})
        conn.commit()
        return jsonify({"status": "success", "status_label": "ALERT_CANCELLED", "message": "Simulation request cancelled; no message had been sent."}), 200
    finally:
        conn.close()


@safety_api.post("/api/safety/safe")
@login_required
def mark_safety_safe():
    data = request.get_json(silent=True) or {}
    conn = get_db_connection()
    try:
        recipients = _contacts_for_ids(conn, g.current_user["id"], data.get("contact_ids"))
        _event(conn, g.current_user["id"], "I_AM_SAFE", "SAFE", {"selected_contact_count": len(recipients), "notification_mode": "DEMO / SIMULATION"})
        conn.execute("UPDATE safety_alerts SET status = 'SAFE', resolved_at = CURRENT_TIMESTAMP WHERE user_id = ? AND status = 'REQUEST_CREATED'", (g.current_user["id"],))
        conn.execute("UPDATE safety_trips SET status = 'COMPLETED', ended_at = CURRENT_TIMESTAMP WHERE user_id = ? AND status = 'ACTIVE'", (g.current_user["id"],))
        conn.commit()
        return jsonify({"status": "success", "event_status": "SAFE", "notification_mode": "DEMO / SIMULATION", "contact_count": len(recipients), "message": "Safe status recorded. No contacts were messaged."}), 200
    except ValueError as error:
        return jsonify({"status": "fail", "message": str(error)}), 400
    finally:
        conn.close()


@safety_api.post("/api/safety/trip/start")
@login_required
def start_safety_trip():
    data = request.get_json(silent=True) or {}
    try:
        latitude, longitude, accuracy = _coordinates(data)
        conn = get_db_connection()
        try:
            cursor = conn.execute(
                "INSERT INTO safety_trips (user_id, last_latitude, last_longitude, location_accuracy, location_updated_at) VALUES (?, ?, ?, ?, CASE WHEN ? IS NULL THEN NULL ELSE CURRENT_TIMESTAMP END)",
                (g.current_user["id"], latitude, longitude, accuracy, latitude),
            )
            trip_id = cursor.lastrowid
            _event(conn, g.current_user["id"], "TRIP_STARTED", "TRIP_ACTIVE", {"trip_id": trip_id, "location_available": latitude is not None})
            conn.commit()
            trip = conn.execute("SELECT id, status, started_at, ended_at, location_updated_at, last_latitude IS NOT NULL AS has_location FROM safety_trips WHERE id = ?", (trip_id,)).fetchone()
            return jsonify({"status": "success", "trip": dict(trip)}), 201
        finally:
            conn.close()
    except ValueError as error:
        return jsonify({"status": "fail", "message": str(error)}), 400
    except Exception:
        conn = get_db_connection()
        active = conn.execute("SELECT id FROM safety_trips WHERE user_id = ? AND status = 'ACTIVE'", (g.current_user["id"],)).fetchone()
        conn.close()
        if active:
            return jsonify({"status": "fail", "message": "A trip is already active."}), 409
        raise


@safety_api.post("/api/safety/trip/<int:trip_id>/location")
@login_required
def update_trip_location(trip_id):
    data = request.get_json(silent=True) or {}
    try:
        latitude, longitude, accuracy = _coordinates(data)
        if latitude is None:
            raise ValueError("Location coordinates are required for a trip update.")
        conn = get_db_connection()
        try:
            cursor = conn.execute(
                "UPDATE safety_trips SET last_latitude = ?, last_longitude = ?, location_accuracy = ?, location_updated_at = CURRENT_TIMESTAMP WHERE id = ? AND user_id = ? AND status = 'ACTIVE'",
                (latitude, longitude, accuracy, trip_id, g.current_user["id"]),
            )
            if cursor.rowcount == 0:
                return jsonify({"status": "fail", "message": "Active trip not found."}), 404
            conn.commit()
            return jsonify({"status": "success", "location_updated_at": conn.execute("SELECT location_updated_at FROM safety_trips WHERE id = ?", (trip_id,)).fetchone()[0]}), 200
        finally:
            conn.close()
    except ValueError as error:
        return jsonify({"status": "fail", "message": str(error)}), 400


@safety_api.post("/api/safety/trip/<int:trip_id>/end")
@login_required
def end_safety_trip(trip_id):
    conn = get_db_connection()
    try:
        cursor = conn.execute("UPDATE safety_trips SET status = 'COMPLETED', ended_at = CURRENT_TIMESTAMP WHERE id = ? AND user_id = ? AND status = 'ACTIVE'", (trip_id, g.current_user["id"]))
        if cursor.rowcount == 0:
            return jsonify({"status": "fail", "message": "Active trip not found."}), 404
        _event(conn, g.current_user["id"], "TRIP_COMPLETED", "COMPLETED", {"trip_id": trip_id})
        conn.commit()
        return jsonify({"status": "success", "status_label": "TRIP_COMPLETED"}), 200
    finally:
        conn.close()


@safety_api.post("/api/safety/events")
@login_required
def create_safety_event():
    data = request.get_json(silent=True) or {}
    event_type = str(data.get("event_type") or "").upper()
    allowed = {"ALARM_ACTIVATED", "ALARM_STOPPED", "EMERGENCY_TRIGGERED"}
    if event_type not in allowed:
        return jsonify({"status": "fail", "message": "Safety event type is invalid."}), 400
    conn = get_db_connection()
    try:
        _event(conn, g.current_user["id"], event_type, event_type, {})
        conn.commit()
        return jsonify({"status": "success"}), 201
    finally:
        conn.close()


@safety_api.get("/api/safety/history")
@login_required
def safety_history():
    conn = get_db_connection()
    try:
        rows = conn.execute(
            "SELECT id, event_type, event_time, status, metadata FROM safety_events WHERE user_id = ? ORDER BY id DESC LIMIT 200",
            (g.current_user["id"],),
        ).fetchall()
        return jsonify({"status": "success", "data": [dict(row) | {"metadata": json.loads(row["metadata"])} for row in rows]}), 200
    finally:
        conn.close()


@safety_api.get("/api/admin/safety-alerts")
@admin_required
def admin_safety_alerts():
    conn = get_db_connection()
    try:
        rows = conn.execute(
            "SELECT a.id AS alert_id, a.alert_type, a.triggered_at, a.status, "
            "CASE WHEN a.latitude IS NULL THEN 0 ELSE 1 END AS location_available, "
            "CASE WHEN a.cancelled_at IS NULL THEN 0 ELSE 1 END AS cancelled, u.username AS user_identifier "
            "FROM safety_alerts a JOIN users u ON u.id = a.user_id ORDER BY a.id DESC LIMIT 200"
        ).fetchall()
        return jsonify({"status": "success", "data": [dict(row) for row in rows]}), 200
    finally:
        conn.close()