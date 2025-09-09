from flask import Flask, render_template, request, redirect, url_for, send_file
import csv
import os
from datetime import datetime

app = Flask(__name__)

BOOKINGS_FILE = "bookings.csv"

# Ensure bookings.csv exists with headers
if not os.path.exists(BOOKINGS_FILE):
    with open(BOOKINGS_FILE, mode="w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["Name", "Email", "Date", "Time", "Guests", "Timestamp"])

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        # Get form data
        name = request.form["name"]
        email = request.form["email"]
        date = request.form["date"]
        time = request.form["time"]
        guests = request.form["guests"]
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Append booking to CSV
        with open(BOOKINGS_FILE, mode="a", newline="") as file:
            writer = csv.writer(file)
            writer.writerow([name, email, date, time, guests, timestamp])

        return redirect(url_for("index"))

    # Load existing bookings
    bookings = []
    with open(BOOKINGS_FILE, mode="r") as file:
        reader = csv.reader(file)
        next(reader)  # Skip header
        bookings = list(reader)

    return render_template("index.html", bookings=bookings)

@app.route("/download")
def download():
    return send_file(BOOKINGS_FILE, as_attachment=True)

if __name__ == "__main__":
    app.run(debug=True)
