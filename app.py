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
                department TEXT NOT NULL,
                attendees INTEGER NOT NULL,
                room_type TEXT NOT NULL,
                date TEXT NOT NULL,
                to_date TEXT NOT NULL,
                start_time TEXT NOT NULL,
                end_time TEXT NOT NULL,
                details TEXT
            )
        """)
        conn.commit()

def get_all_bookings():
    """Fetch all bookings"""
    with sqlite3.connect(DATABASE) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM bookings ORDER BY date, start_time")
        return cursor.fetchall()

def add_booking(data):
    """Insert new booking"""
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO bookings (name, email, department, attendees, room_type, date, to_date, start_time, end_time, details)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, data)
        conn.commit()

def delete_booking_db(booking_id):
    """Delete booking by ID"""
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM bookings WHERE id = ?", (booking_id,))
        conn.commit()

# -----------------------------
# Routes
# -----------------------------
@app.route("/", methods=["GET", "POST", "HEAD"])
def index():
    if request.method == "HEAD":
        return "", 200  # Return empty response for HEAD requests
    return render_template("index.html")

    if request.method == "POST":
        try:
            from_date = request.form["from_date"]
            to_date = request.form["to_date"]
            name = request.form["name"]
            email = request.form["email"]
            department = request.form["department"]
            attendees = request.form["attendees"]
            room_type = request.form["room_type"]
            start_time = request.form["start_time"]
            end_time = request.form["end_time"]
            details = request.form.get("details", "")

            if not (from_date and to_date and name and email and department and attendees and room_type and start_time and end_time):
                error = "All required fields must be filled."
            else:
                add_booking((name, email, department, attendees, room_type, from_date, to_date, start_time, end_time, details))
                success = "Booking successful!"
                return redirect(url_for("index"))

        except Exception as e:
            error = f"Error: {str(e)}"

    bookings = get_all_bookings()
    return render_template("index.html", bookings=bookings, error=error, success=success)

@app.route("/delete/<int:booking_id>", methods=["POST"])
def delete_booking(booking_id):
    try:
        delete_booking_db(booking_id)
        flash("Booking cancelled successfully!", "success")
    except Exception as e:
        flash(f"Error cancelling booking: {str(e)}", "danger")
    return redirect(url_for("index"))

# -----------------------------
# Start App
# -----------------------------
if __name__ == "__main__":
    if not os.path.exists(DATABASE):
        init_db()
    app.run(debug=True)
