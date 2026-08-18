from flask import Flask, send_from_directory, request, jsonify
import sqlite3
import os
from datetime import date

app = Flask(__name__)

# -----------------------------
# FOLDERS
# -----------------------------

FRONTEND_FOLDER = "../frontend"
DATABASE_FILE = "../database/attendance.db"


# -----------------------------
# DATABASE CONNECTION
# -----------------------------

def get_db():
    conn = sqlite3.connect(DATABASE_FILE)
    conn.row_factory = sqlite3.Row
    return conn


# -----------------------------
# CREATE TABLE
# -----------------------------

def init_db():
    conn = get_db()

    conn.execute("""
        CREATE TABLE IF NOT EXISTS attendance (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_name TEXT NOT NULL,
            status TEXT NOT NULL,
            date TEXT NOT NULL
        )
    """)

    conn.commit()
    conn.close()


# -----------------------------
# FRONTEND
# -----------------------------

@app.route("/")
def home():
    return send_from_directory(FRONTEND_FOLDER, "index.html")


@app.route("/<path:filename>")
def frontend_files(filename):
    return send_from_directory(FRONTEND_FOLDER, filename)


# -----------------------------
# MARK ATTENDANCE
# -----------------------------

@app.route("/api/attendance", methods=["POST"])
def mark_attendance():

    data = request.get_json()

    student_name = data.get("student_name")
    status = data.get("status")

    if not student_name or not status:
        return jsonify({
            "error": "Student name and status are required"
        }), 400

    today = date.today().isoformat()

    conn = get_db()

    conn.execute(
        """
        INSERT INTO attendance
        (student_name, status, date)
        VALUES (?, ?, ?)
        """,
        (student_name, status, today)
    )

    conn.commit()
    conn.close()

    return jsonify({
        "message": "Attendance marked successfully"
    })


# -----------------------------
# GET ATTENDANCE RECORDS
# -----------------------------

@app.route("/api/attendance", methods=["GET"])
def get_attendance():

    conn = get_db()

    records = conn.execute(
        """
        SELECT student_name, status, date
        FROM attendance
        ORDER BY id DESC
        """
    ).fetchall()

    conn.close()

    return jsonify([
        {
            "student_name": row["student_name"],
            "status": row["status"],
            "date": row["date"]
        }
        for row in records
    ])


# -----------------------------
# DASHBOARD STATISTICS
# -----------------------------

@app.route("/api/stats", methods=["GET"])
def get_stats():

    conn = get_db()

    total = conn.execute(
        "SELECT COUNT(DISTINCT student_name) FROM attendance"
    ).fetchone()[0]

    present = conn.execute(
        """
        SELECT COUNT(*)
        FROM attendance
        WHERE status = 'Present'
        """
    ).fetchone()[0]

    absent = conn.execute(
        """
        SELECT COUNT(*)
        FROM attendance
        WHERE status = 'Absent'
        """
    ).fetchone()[0]

    percentage = 0

    if total > 0:
        percentage = round((present / (present + absent)) * 100)

    conn.close()

    return jsonify({
        "totalStudents": total,
        "present": present,
        "absent": absent,
        "percentage": percentage
    })


# -----------------------------
# START APPLICATION
# -----------------------------

if __name__ == "__main__":
    init_db()
    app.run(debug=True)