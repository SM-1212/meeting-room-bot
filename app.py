from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

# Example data store (in-memory, replace with DB if needed)
bookings = []
ADMIN_EMAIL = "admin@example.com"  # change this to your actual admin email


@app.route("/", methods=["GET", "POST"])
def index():
    error = None

    if request.method == "POST":
        name = request.form.get("name")
        room = request.form.get("room")
        date = request.form.get("date")
        time = request.form.get("time")

        if not name or not room or not date or not time:
            error = "All fields are required!"
        else:
            bookings.append({
                "name": name,
                "room": room,
                "date": date,
                "time": time
            })
            return redirect(url_for("index"))

    return render_template(
        "index.html",
        bookings=bookings,
        error=error,
        admin_email=ADMIN_EMAIL
    )


@app.route("/delete/<int:booking_id>")
def delete_booking(booking_id):
    if 0 <= booking_id < len(bookings):
        bookings.pop(booking_id)
    return redirect(url_for("index"))


@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html"), 404


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
