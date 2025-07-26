from flask import Flask, render_template, request, redirect, send_file
import csv
import os
from datetime import datetime

app = Flask(__name__)
BOOKINGS_FILE = "bookings.csv"

# Load bookings from file
def load_bookings():
    if not os.path.exists(BOOKINGS_FILE):
        return []
    with open(BOOKINGS_FILE, newline='') as f:
        reader = csv.DictReader(f)
        return list(reader)

# Save bookings to file
def save_bookings(bookings):
    with open(BOOKINGS_FILE, "w", newline='') as f:
        writer = csv.DictWriter(f, fieldnames=bookings[0].keys())
        writer.writeheader()
        writer.writerows(bookings)

@app.route("/")
def index():
    bookings = load_bookings()
    return render_template("index.html", bookings=bookings, error=None)

@app.route("/book", methods=["POST"])
def book():
    new = {
        "Date": request.form["date"],
        "Name": request.form["name"],
        "Email": request.form["email"],
        "Department": request.form["department"],
        "Attendees": request.form["attendees"],
        "Room Type": request.form["room_type"],
        "Start Time": request.form["start_time"],
        "End Time": request.form["end_time"],
        "Details": request.form["details"]
    }

    bookings = load_bookings()

    # Check for conflict
    for b in bookings:
        if (b["Date"] == new["Date"] and
            b["Room Type"] == new["Room Type"] and
            not (new["End Time"] <= b["Start Time"] or new["Start Time"] >= b["End Time"])):
            return render_template("index.html", bookings=bookings, error="Room already booked for this time slot.")

    bookings.append(new)
    save_bookings(bookings)
    return redirect("/")

@app.route("/cancel/<int:index>", methods=["POST"])
def cancel(index):
    bookings = load_bookings()
    if 0 <= index < len(bookings):
        bookings.pop(index)
        save_bookings(bookings)
    return redirect("/")

@app.route("/download")
def download():
    return send_file(BOOKINGS_FILE, as_attachment=True)

if __name__ == "__main__":
    app.run(debug=True)
