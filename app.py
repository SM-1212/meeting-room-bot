from flask import Flask, render_template, request, redirect, url_for
import json
import os
from datetime import datetime

app = Flask(__name__)

BOOKING_FILE = "bookings.json"
ADMIN_EMAIL = "admin@example.com"  # Change this to your real admin email


def load_bookings():
    if os.path.exists(BOOKING_FILE):
        with open(BOOKING_FILE, "r") as f:
            return json.load(f)
    return []


def save_bookings(bookings):
    with open(BOOKING_FILE, "w") as f:
        json.dump(bookings, f, indent=4)


@app.route("/", methods=["GET", "POST"])
def index():
    error = None
    bookings = load_bookings()

    if request.method == "POST":
        name = request.form.get("name")
        email = request.form.get("email")
        date = request.form.get("date")
        start_time = request.form.get("start_time")
        end_time = request.form.get("end_time")

        # Validate required fields
        if not (name and email and date and start_time and end_time):
            error = "All fields are required."
        else:
            # Convert to datetime for validation
            new_start = datetime.strptime(f"{date} {start_time}", "%Y-%m-%d %H:%M")
            new_end = datetime.strptime(f"{date} {end_time}", "%Y-%m-%d %H:%M")

            # Check for overlap
            overlap = False
            for booking in bookings:
                if booking["date"] == date:
                    existing_start = datetime.strptime(
                        f"{booking['date']} {booking['start_time']}", "%Y-%m-%d %H:%M"
                    )
                    existing_end = datetime.strptime(
                        f"{booking['date']} {booking['end_time']}", "%Y-%m-%d %H:%M"
                    )
                    if new_start < existing_end and new_end > existing_start:
                        overlap = True
                        break

            if overlap:
                error = "This time slot is already booked."
            else:
                bookings.append(
                    {
                        "name": name,
                        "email": email,
                        "date": date,
                        "start_time": start_time,
                        "end_time": end_time,
                    }
                )
                save_bookings(bookings)
                return redirect(url_for("index"))

    # Pass admin email to template
    return render_template(
        "index.html", bookings=bookings, error=error, admin_email=ADMIN_EMAIL
    )


@app.route("/cancel/<int:booking_id>", methods=["POST"])
def cancel_booking(booking_id):
    bookings = load_bookings()
    if 0 <= booking_id < len(bookings):
        bookings.pop(booking_id)
        save_bookings(bookings)
    return redirect(url_for("index"))


import os

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
