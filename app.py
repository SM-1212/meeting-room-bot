from flask import Flask, render_template, request, redirect, url_for, send_file
import csv
import os
from datetime import datetime

app = Flask(__name__)

# Store bookings in memory (for production, use a DB)
bookings = []
ADMIN_EMAIL = "saugat.mukherjee@globeteleservices.com"

# ---------- Home ----------
@app.route("/", methods=["GET", "POST"])
def index():
    error = None
    if request.method == "POST":
        from_date = request.form["from_date"]
        to_date = request.form["to_date"]
        name = request.form["name"]
        email = request.form["email"]
        department = request.form["department"]
        attendees = request.form["attendees"]
        room_type = request.form["room_type"]
        start_time = request.form["start_time"]
        end_time = request.form["end_time"]
        details = request.form["details"]

        # ✅ Conflict check: same room, overlapping time
        for booking in bookings:
            if (
                booking["room_type"] == room_type
                and booking["date"] == from_date
                and not (end_time <= booking["start_time"] or start_time >= booking["end_time"])
            ):
                error = f"{room_type} is already booked during this time!"
               return render_template("index.html", bookings=bookings, error=error, admin_email=ADMIN_EMAIL)


        # ✅ Save booking
        bookings.append(
            {
                "date": from_date,
                "to_date": to_date,
                "name": name,
                "email": email,
                "department": department,
                "attendees": attendees,
                "room_type": room_type,
                "start_time": start_time,
                "end_time": end_time,
                "details": details,
            }
        )
        return redirect(url_for("index"))

    return render_template(
        "index.html",
        bookings=bookings,
        error=error,
        admin_email=ADMIN_EMAIL,
        is_admin=True,
    )


# ---------- Cancel Booking ----------
@app.route("/cancel/<int:index>", methods=["POST"])
def cancel_booking(index):
    if 0 <= index < len(bookings):
        bookings.pop(index)
    return redirect(url_for("index"))


# ---------- Download CSV ----------
@app.route("/download")
def download_csv():
    filename = "bookings.csv"
    with open(filename, "w", newline="") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(
            [
                "From Date",
                "To Date",
                "Name",
                "Email",
                "Department",
                "Attendees",
                "Room Type",
                "Start Time",
                "End Time",
                "Details",
            ]
        )
        for b in bookings:
            writer.writerow(
                [
                    b["date"],
                    b["to_date"],
                    b["name"],
                    b["email"],
                    b["department"],
                    b["attendees"],
                    b["room_type"],
                    b["start_time"],
                    b["end_time"],
                    b["details"],
                ]
            )
    return send_file(filename, as_attachment=True)


if __name__ == "__main__":
    app.run(debug=True)
