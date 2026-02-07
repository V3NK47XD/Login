from flask import Blueprint, request, jsonify, make_response
from sqlalchemy import create_engine, text
import bcrypt
import uuid
import datetime
import re
import logging

auth = Blueprint("auth", __name__)

engine = create_engine("sqlite:///login.db", echo=False)

logging.basicConfig(level=logging.INFO)

# ----------------------
# Create Tables
# ----------------------
with engine.connect() as conn:
    conn.execute(text("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            password TEXT,
            failed_attempts INTEGER DEFAULT 0,
            lock_until TEXT
        )
    """))

    conn.execute(text("""
        CREATE TABLE IF NOT EXISTS sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            session_token TEXT,
            expires_at TEXT
        )
    """))
    conn.commit()


# ----------------------
# Password Validation
# ----------------------
def validate_password(password):
    if len(password) < 8:
        return False

    if not re.search(r"[A-Z]", password):
        return False

    if not re.search(r"[a-z]", password):
        return False

    if not re.search(r"[0-9]", password):
        return False

    if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
        return False

    common_passwords = ["password", "12345678", "qwerty123"]
    if password.lower() in common_passwords:
        return False

    return True


# ----------------------
# Cleanup Expired Sessions
# ----------------------
def cleanup_sessions():
    with engine.connect() as conn:
        conn.execute(
            text("DELETE FROM sessions WHERE expires_at < :now"),
            {"now": datetime.datetime.utcnow().isoformat()}
        )
        conn.commit()


# ----------------------
# Register
# ----------------------
@auth.route("/register", methods=["POST"])
def register():
    data = request.json

    if not data or "username" not in data or "password" not in data:
        return jsonify({"message": "Invalid input"}), 400

    username = data["username"].strip()
    password = data["password"]

    if len(username) < 3:
        return jsonify({"message": "Username too short"}), 400

    if not validate_password(password):
        return jsonify({"message": "Weak password"}), 400

    with engine.connect() as conn:
        result = conn.execute(
            text("SELECT * FROM users WHERE username = :username"),
            {"username": username}
        ).fetchone()

        if result:
            return jsonify({"message": "Username already exists"}), 400

        hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

        conn.execute(
            text("""
                INSERT INTO users (username, password)
                VALUES (:username, :password)
            """),
            {"username": username, "password": hashed}
        )
        conn.commit()

    return jsonify({"message": "Registration successful"})


# ----------------------
# Login
# ----------------------
@auth.route("/login", methods=["POST"])
def login():
    cleanup_sessions()

    data = request.json

    if not data or "username" not in data or "password" not in data:
        return jsonify({"message": "Invalid input"}), 400

    username = data["username"]
    password = data["password"]

    with engine.connect() as conn:
        user = conn.execute(
            text("SELECT * FROM users WHERE username = :username"),
            {"username": username}
        ).fetchone()

        if not user:
            logging.warning(f"Login attempt for non-existent user: {username}")
            return jsonify({"message": "Invalid credentials"}), 401

        # Check lock
        if user[4]:
            lock_time = datetime.datetime.fromisoformat(user[4])
            if datetime.datetime.utcnow() < lock_time:
                return jsonify({"message": "Account temporarily locked"}), 403

        if not bcrypt.checkpw(password.encode(), user[2].encode()):
            failed = user[3] + 1
            lock_until = None

            if failed >= 5:
                lock_until = (datetime.datetime.utcnow() + datetime.timedelta(minutes=10)).isoformat()
                failed = 0

            conn.execute(text("""
                UPDATE users
                SET failed_attempts = :failed,
                    lock_until = :lock
                WHERE id = :id
            """), {
                "failed": failed,
                "lock": lock_until,
                "id": user[0]
            })
            conn.commit()

            logging.warning(f"Failed login for {username}")
            return jsonify({"message": "Invalid credentials"}), 401

        # Reset failed attempts
        conn.execute(text("""
            UPDATE users
            SET failed_attempts = 0,
                lock_until = NULL
            WHERE id = :id
        """), {"id": user[0]})
        conn.commit()

        session_token = str(uuid.uuid4())
        expires = (datetime.datetime.utcnow() + datetime.timedelta(days=1)).isoformat()

        conn.execute(text("""
            INSERT INTO sessions (user_id, session_token, expires_at)
            VALUES (:user_id, :token, :expires)
        """), {
            "user_id": user[0],
            "token": session_token,
            "expires": expires
        })
        conn.commit()

        response = make_response(jsonify({"message": "Login successful"}))
        response.set_cookie(
            "session_token",
            session_token,
            httponly=True,
            secure=False,   # Set True in production HTTPS
            samesite="Strict"
        )

        return response


# ----------------------
# Logout
# ----------------------
@auth.route("/logout", methods=["POST"])
def logout():
    session_token = request.cookies.get("session_token")

    if not session_token:
        return jsonify({"message": "Not logged in"}), 400

    with engine.connect() as conn:
        conn.execute(
            text("DELETE FROM sessions WHERE session_token = :token"),
            {"token": session_token}
        )
        conn.commit()

    response = make_response(jsonify({"message": "Logged out"}))
    response.delete_cookie("session_token")

    return response


# ----------------------
# Protected Route
# ----------------------
@auth.route("/dashboard", methods=["GET"])
def dashboard():
    cleanup_sessions()

    session_token = request.cookies.get("session_token")

    if not session_token:
        return jsonify({"message": "Unauthorized"}), 401

    with engine.connect() as conn:
        session = conn.execute(
            text("SELECT * FROM sessions WHERE session_token = :token"),
            {"token": session_token}
        ).fetchone()

        if not session:
            return jsonify({"message": "Invalid or expired session"}), 401

    return jsonify({"message": "Welcome to dashboard!"})
