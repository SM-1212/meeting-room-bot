from flask import Flask, render_template, request, redirect, url_for, flash
import os

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "defaultsecret")

# Replace with your real admin email
ADMIN_EMAIL = os.getenv("ADMIN_EMAIL", "admin@example.com")


# Dummy function for bookings (replace with DB call or your logic)
def get_all_bookings():
    return [
        {"room": "Meeting Room 1", "time": "10:00 - 11:00"},
        {"room": "Meeting Room 2", "time": "11:30 - 12:30"},
    ]


@app.route("/")
def index():
    bookings = get_all_bookings()
    error = None  # ✅ ensure error is always defined
    return render_template("index.html", bookings=bookings, error=error, admin_email=ADMIN_EMAIL)


@app.route("/book", methods=["POST"])
def book_room():
    try:
        room = request.form["room"]
        time = request.form["time"]

        # Your booking logic here
        flash(f"Room {room} booked for {time}", "success")
        return redirect(url_for("index"))

    except Exception as e:
        error = str(e)
        bookings = get_all_bookings()
        return render_template("index.html", bookings=bookings, error=error, admin_email=ADMIN_EMAIL)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
