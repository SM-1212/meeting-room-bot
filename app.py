from flask import Flask, render_template, request, redirect, url_for
import csv
import os

app = Flask(__name__)

BOOKINGS_FILE = "bookings.csv"


def read_bookings():
    bookings = []
    if os.path.exists(BOOKINGS_FILE):
        with open(BOOKINGS_FILE, mode="r", newline="") as file:
            reader = csv.DictReader(file)
            for row in reader:
                bookings.append(row)
    return bookings


def write_booking(data):
    file_exists = os.path.exists(BOOKINGS_FILE)
    with open(BOOKINGS_FILE, mode="a", newline="") as file:
        fieldnames = ["name", "email", "phone", "date", "time", "purpose"]
        writer = csv.DictWriter(file, fieldnames=fieldnames)

        if not file_exists:
            writer.writeheader()
        writer.writerow(data)


@app.route("/", methods=["GET", "POST"])
def index():
    error = None
    bookings = read_bookings()

    if request.method == "POST":
        name = request.form.get("name")
        email = request.form.get("email")
        phone = request.form.get("phone")
        date = request.form.get("date")
        time = request.form.get("time")
        purpose = request.form.get("purpose")

        if not name or not email or not phone or not date or not time or not purpose:
            error = "All fields are required."
        else:
            write_booking(
                {
                    "name": name,
                    "email": email,
                    "phone": phone,
                    "date": date,
                    "time": time,
                    "purpose": purpose,
                }
            )
            return redirect(url_for("index"))

    return render_template("index.html", bookings=bookings, error=error)


@app.route("/search", methods=["GET", "POST"])
def search():
    error = None
    bookings = read_bookings()

    if request.method == "POST":
        query = request.form.get("query")
        if not query:
            error = "Please enter a search term."
        else:
            filtered_bookings = [
                b
                for b in bookings
                if query.lower() in b["name"].lower()
                or query.lower() in b["email"].lower()
                or query.lower() in b["phone"].lower()
            ]
            return render_template("index.html", bookings=filtered_bookings, error=error)

    return render_template("index.html", bookings=bookings, error=error)


if __name__ == "__main__":
    app.run(debug=True)
