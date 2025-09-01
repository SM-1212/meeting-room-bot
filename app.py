from flask import Flask, render_template, request, redirect, url_for, send_file
from io import StringIO, BytesIO
from datetime import datetime
import csv
import os

app = Flask(__name__)

# In-memory store
bookings = []  # each item is a dict with keys shown below


def dates_overlap(a_start: str, a_end: str, b_start: str, b_end: str) -> bool:
    """Check if two date ranges (YYYY-MM-DD) overlap."""
    a0 = datetime.strptime(a_start, "%Y-%m-%d").date()
    a1 = datetime.strptime(a_end, "%Y-%m-%d").date()
    b0 = datetime.strptime(b_start, "%Y-%m-%d").date()
    b1 = datetime.strptime(b_end, "%Y-%m-%d").date()
    return not (a1 < b0 or a0 > b1)


def times_overlap(a_start: str, a_end: str, b_start: str, b_end: str) -> bool:
    """Check if two time ranges (HH:MM, 24h) overlap.
       Works with strings because inputs are zero-padded, but parse for safety."""
    t = lambda s: datetime.strptime(s, "%H:%M").time()
    return not (t(a_end) <= t(b_start) or t(a_start) >= t(b_end))


@app.route("/", methods=["GET", "POST"])
def index():
    error = None

    if request.method == "POST":
        # Read form fields (strip to avoid accidental spaces)
        from_date = (request.form.get("from_date") or "").strip()
        to_date = (request.form.get("to_date") or "").strip()
        name = (request.form.get("name") or "").strip()
        email = (request.form.get("email") or "").strip()
        department = (request.form.get("department") or "").strip()
        attendees = (request.form.get("attendees") or "").strip()
        room_type = (request.form.get("room_type") or "").strip()
        start_time = (request.form.get("start_time") or "").strip()
        end_time = (request.form.get("end_time") or "").strip()
        details = (request.form.get("details") or "").strip()

        # Required field check (details optional)
        required = [from_date, to_date, name, email, department, attendees, room_type, start_time, end_time]
        if not all(required):
            error = "All fields are required."
            return render_template("index.html", bookings=bookings, error=error)

        # Date order validation
        try:
            if datetime.strptime(from_date, "%Y-%m-%d") > datetime.strptime(to_date, "%Y-%m-%d"):
                error = "From Date must be on or before To Date."
                return render_template("index.html", bookings=bookings, error=error)
        except Exception:
            error = "Invalid date format."
            return render_template("index.html", bookings=bookings, error=error)

        # Time order validation
        try:
            if datetime.strptime(start_time, "%H:%M") >= datetime.strptime(end_time, "%H:%M"):
                error = "End Time must be after Start Time."
                return render_template("index.html", bookings=bookings, error=error)
        except Exception:
            error = "Invalid time format."
            return render_template("index.html", bookings=bookings, error=error)

        # Conflict check: same room type, overlapping date range AND overlapping time range
        for b in bookings:
            if b["room_type"] == room_type and dates_overlap(from_date, to_date, b["from_date"], b["to_date"]) \
               and times_overlap(start_time, end_time, b["start_time"], b["end_time"]):
                error = "Room already booked for the selected time slot."
                return render_template("index.html", bookings=bookings, error=error)

        # Save booking
        bookings.append({
            "from_date": from_date,
            "to_date": to_date,
            "name": name,
            "email": email,
            "department": department,
            "attendees": attendees,
            "room_type": room_type,
            "start_time": start_time,
            "end_time": end_time,
            "details": details
        })

        return redirect(url_for("index"))

    # GET
    return render_template("index.html", bookings=bookings, error=error)


@app.route("/cancel/<int:index>", methods=["POST"])
def cancel_booking(index: int):
    if 0 <= index < len(bookings):
        bookings.pop(index)
    return redirect(url_for("index"))


@app.route("/download", methods=["GET"])
def download_csv():
    si = StringIO()
    writer = csv.writer(si)
    writer.writerow([
        "From Date", "To Date", "Name", "Email", "Department",
        "Attendees", "Room Type", "Start Time", "End Time", "Details"
    ])
    for b in bookings:
        writer.writerow([
            b["from_date"], b["to_date"], b["name"], b["email"], b["department"],
            b["attendees"], b["room_type"], b["start_time"], b["end_time"], b["details"]
        ])

    output = BytesIO(si.getvalue().encode("utf-8"))
    output.seek(0)
    return send_file(output, mimetype="text/csv", as_attachment=True, download_name="meeting_bookings.csv")


if __name__ == "__main__":
    # Works locally and on Render
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
@app.route('/cancel/<int:index>', methods=['POST'])
def cancel_booking(index):
    email = request.form.get("email")
    if email == ADMIN_EMAIL:  # ✅ Only Admin can cancel
        if 0 <= index < len(bookings):
            bookings.pop(index)
    else:
        return "Unauthorized: Only Admin can cancel bookings", 403
    return redirect(url_for('index'))
return render_template("index.html", bookings=bookings, error=error, admin_email=ADMIN_EMAIL)
