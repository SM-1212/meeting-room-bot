from flask import Flask, render_template, request, redirect, url_for, send_file
import csv
import io

app = Flask(__name__)
app.secret_key = "your_secret_key"

# Store bookings in memory for now
bookings = []
ADMIN_EMAIL = "admin@example.com"

@app.route("/", methods=["GET", "POST"])
def index():
    error = None
    if request.method == "POST":
        try:
            from_date = request.form.get("from_date", "").strip()
            to_date = request.form.get("to_date", "").strip()
            name = request.form.get("name", "").strip()
            email = request.form.get("email", "").strip()
            department = request.form.get("department", "").strip()
            attendees = request.form.get("attendees", "").strip()
            room_type = request.form.get("room_type", "").strip()
            start_time = request.form.get("start_time", "").strip()
            end_time = request.form.get("end_time", "").strip()
            details = request.form.get("details", "").strip()

            if not all([from_date, to_date, name, email, department, attendees, room_type, start_time, end_time]):
                error = "All required fields must be filled."
            else:
                booking = {
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
                bookings.append(booking)
                return redirect(url_for("index"))
        except Exception as e:
            error = f"Error: {str(e)}"

    return render_template("index.html", bookings=bookings, error=error, admin_email=ADMIN_EMAIL)


@app.route("/delete/<int:booking_id>")
def delete_booking(booking_id):
    if 0 <= booking_id < len(bookings):
        bookings.pop(booking_id)
    return redirect(url_for("index"))


@app.route("/download")
def download_csv():
    si = io.StringIO()
    writer = csv.writer(si)
    writer.writerow(["From Date", "To Date", "Name", "Email", "Department",
                     "Attendees", "Room Type", "Start Time", "End Time", "Details"])
    for b in bookings:
        writer.writerow([b["date"], b["to_date"], b["name"], b["email"], b["department"],
                         b["attendees"], b["room_type"], b["start_time"], b["end_time"], b["details"]])
    si.seek(0)
    return send_file(io.BytesIO(si.getvalue().encode("utf-8")),
                     mimetype="text/csv",
                     as_attachment=True,
                     download_name="bookings.csv")


if __name__ == "__main__":
    app.run(debug=True)
