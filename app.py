from flask import Flask, render_template, request, redirect, url_for, flash
import os

app = Flask(__name__)
app.secret_key = "supersecretkey"

# ✅ Define your admin email once
ADMIN_EMAIL = "your_admin_email@example.com"

# ✅ Context processor: injects admin_email into ALL templates
@app.context_processor
def inject_admin_email():
    return dict(admin_email=ADMIN_EMAIL)

# -------------------------
# Routes
# -------------------------

@app.route("/")
def home():
    bookings = []  # TODO: replace with actual booking list (from DB or file)
    error = None
    return render_template("index.html", bookings=bookings, error=error)

@app.route("/filter")
def filter_bookings():
    query = request.args.get("q", "")
    # TODO: replace with actual filtering logic
    bookings = []  
    error = None if bookings else "No results found"
    return render_template("index.html", bookings=bookings, error=error)

@app.route("/add", methods=["GET", "POST"])
def add_booking():
    if request.method == "POST":
        # Example form handling (replace with DB/file logic)
        name = request.form.get("name")
        date = request.form.get("date")
        flash(f"Booking added for {name} on {date}", "success")
        return redirect(url_for("home"))
    return render_template("add_booking.html")

@app.route("/delete/<int:booking_id>")
def delete_booking(booking_id):
    # TODO: implement delete logic
    flash(f"Booking {booking_id} deleted.", "warning")
    return redirect(url_for("home"))

# -------------------------
# Run app
# -------------------------
if __name__ == "__main__":
    # Set host to 0.0.0.0 for deployment (e.g., Render, Heroku)
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), debug=True)
