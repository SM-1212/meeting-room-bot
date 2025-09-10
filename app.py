from flask import Flask, render_template, request, redirect, url_for, flash, Response
from flask_sqlalchemy import SQLAlchemy
import csv
from io import StringIO

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///bookings.db"
app.config["SECRET_KEY"] = "your_secret_key"
db = SQLAlchemy(app)


class Booking(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.String(20), nullable=False)
    to_date = db.Column(db.String(20), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    department = db.Column(db.String(100), nullable=False)
    attendees = db.Column(db.Integer, nullable=False)
    room_type = db.Column(db.String(50), nullable=False)
    start_time = db.Column(db.String(10), nullable=False)
    end_time = db.Column(db.String(10), nullable=False)
    details = db.Column(db.String(200), nullable=True)


@app.route("/", methods=["GET", "POST"])
def index():
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

        new_booking = Booking(
            date=from_date,
            to_date=to_date,
            name=name,
            email=email,
            department=department,
            attendees=attendees,
            room_type=room_type,
            start_time=start_time,
            end_time=end_time,
            details=details,
        )
        db.session.add(new_booking)
        db.session.commit()
        flash("Booking added successfully!", "success")
        return redirect(url_for("index"))

    bookings = Booking.query.all()
    return render_template("index.html", bookings=bookings)


@app.route("/cancel/<int:booking_id>", methods=["POST"])
def cancel_booking(booking_id):
    booking = Booking.query.get_or_404(booking_id)
    db.session.delete(booking)
    db.session.commit()
    flash("Booking canceled successfully!", "info")
    return redirect(url_for("index"))


@app.route("/download")
def download_csv():
    bookings = Booking.query.all()

    si = StringIO()
    cw = csv.writer(si)
    cw.writerow(
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
        cw.writerow(
            [
                b.date,
                b.to_date,
                b.name,
                b.email,
                b.department,
                b.attendees,
                b.room_type,
                b.start_time,
                b.end_time,
                b.details,
            ]
        )

    output = si.getvalue()
    return Response(
        output,
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment;filename=bookings.csv"},
    )


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
