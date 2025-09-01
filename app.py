from flask import Flask, render_template, request, redirect, url_for, flash
import sqlite3
import os

# -----------------------------
# Flask App Initialization
# -----------------------------
app = Flask(__name__)
app.secret_key = "your_secret_key"  # Needed for flash messages

# -----------------------------
# Config
# -----------------------------
DATABASE = "bookings.db"
ADMIN_EMAIL = "admin@example.com"

# -----------------------------
# DB Helper Functions
# -----------------------------
def init_db():
    """Create database if not exists"""
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS bookings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT NOT NULL,
                date TEXT NOT NULL,
                time TEXT NOT NULL,
                message TEXT
            )
        """)
        conn.commit()

def get_all_bookings():
    """Fetch all bookings"""
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM bookings ORDER BY date, time")
        return cursor.fetchall()

def add_booking(name, email, date, time, message):
    """Insert new booking"""
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO bookings (name, email, date, time, message)
            VALUES (?, ?, ?, ?, ?)
        """, (name, email, date, time, message))
        conn.commit()

# -----------------------------
# Routes
# -----------------------------
@app.route("/", methods=["GET", "POST"])
def index():
    error = None
    if request.method == "POST":
        try:
            name = request.form["name"]
            email = request.form["email"]
            date = request.form["date"]
            time = request.form["time"]
            message = request.form.get("message", "")

            if not name or not email or not date or not time:
                error = "All required fields must be filled."
            else:
                add_booking(name, email, date, time, message)
                flash("Booking successful!", "success")
                return redirect(url_for("index"))

        except Exception as e:
            error = f"Error: {str(e)}"

    bookings = get_all_bookings()
    return render_template("index.html",
                           bookings=bookings,
                           error=error,
                           admin_email=ADMIN_EMAIL)

# -----------------------------
# Start App
# -----------------------------
if __name__ == "__main__":
    if not os.path.exists(DATABASE):
        init_db()
    app.run(debug=True)
