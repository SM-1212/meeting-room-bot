from flask import Flask, render_template, request, redirect, url_for, flash, Response
import sqlite3
import os
import csv
import io

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
@app.route("/", methods=["GET", "POST"])
def index():
    error = None
    success = None

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
                flash("Booking successful!", "success")
                return redirect(url_for("index"))

        except Exception as e:
            error = f"Error: {str(e)}"
            flash(error, "danger")

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


@app.route("/download_csv")
def download_csv():
    """Download all bookings as CSV"""
    bookings = get_all_bookings()

    # Create CSV in memory
    output = io.StringIO()
    writer = csv.writer(output)

    # Write header
    writer.writerow(["From Date", "To Date", "Name", "Email", "Department", "Attendees", "Room Type", "Start Time", "End Time", "Details"])

    # Write rows
    for b in bookings:
        writer.writerow([b["date"], b["to_date"], b["name"], b["email"], b["department"], b["attendees"], b["room_type"], b["start_time"], b["end_time"], b["details"]])

    output.seek(0)

    return Response(output, mimetype="text/csv", headers={"Content-Disposition": "attachment;filename=bookings.csv"})


# -----------------------------
# Start App
# -----------------------------
if __name__ == "__main__":
    if not os.path.exists(DATABASE):
        init_db()
    app.run(debug=True)
