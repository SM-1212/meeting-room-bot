from flask import Flask, render_template, request, redirect, url_for, send_file
import csv
from io import StringIO, BytesIO
from datetime import datetime

app = Flask(__name__)

# In-memory list to store bookings
bookings = []

# Admin email (only this user can cancel bookings)
ADMIN_EMAIL = "sougat@globeteleservices.com"  # <-- change to your email

@app.route('/', methods=['GET', 'POST'])
def index():
    error = None
    filtered_bookings = bookings

    # ✅ Handle new booking submission
    if request.method == 'POST' and "filter" not in request.form:
        date = request.form['date']
        name = request.form['name']
        email = request.form['email']
        department = request.form['department']
        attendees = request.form['attendees']
        room_type = request.form['room_type']
        start_time = request.form['start_time']
        end_time = request.form['end_time']
        details = request.form['details']

        # Check for conflicts
        for booking in bookings:
            if (
                booking['date'] == date and
                booking['room_type'] == room_type and
                not (end_time <= booking['start_time'] or start_time >= booking['end_time'])
            ):
                error = "Room already booked for the selected time slot."
                return render_template("index.html", bookings=filtered_bookings, error=error, admin_email=ADMIN_EMAIL)

        # Save booking
        bookings.append({
            'date': date,
            'name': name,
            'email': email,
            'department': department,
            'attendees': attendees,
            'room_type': room_type,
            'start_time': start_time,
            'end_time': end_time,
            'details': details
        })
        return redirect(url_for('index'))

    # ✅ Handle date filtering (from_date / to_date)
    from_date = request.args.get('from_date')
    to_date = request.args.get('to_date')
    if from_date and to_date:
        try:
            from_dt = datetime.strptime(from_date, "%Y-%m-%d")
            to_dt = datetime.strptime(to_date, "%Y-%m-%d")
            filtered_bookings = [
                b for b in bookings
                if from_dt <= datetime.strptime(b['date'], "%Y-%m-%d") <= to_dt
            ]
        except Exception as e:
            print("Date filter error:", e)

    return render_template("index.html", bookings=filtered_bookings, error=error, admin_email=ADMIN_EMAIL)


@app.route('/cancel/<int:index>', methods=['POST'])
def cancel_booking(index):
    email = request.form.get("email")
    if email == ADMIN_EMAIL:  # ✅ Only Admin can cancel
        if 0 <= index < len(bookings):
            bookings.pop(index)
    else:
        return "Unauthorized: Only Admin can cancel bookings", 403
    return redirect(url_for('index'))


@app.route('/download')
def download_csv():
    si = StringIO()
    writer = csv.writer(si)
    writer.writerow(['Date', 'Name', 'Email', 'Department', 'Attendees', 'Room Type', 'Start', 'End', 'Details'])
    for booking in bookings:
        writer.writerow([
            booking['date'],
            booking['name'],
            booking['email'],
            booking['department'],
            booking['attendees'],
            booking['room_type'],
            booking['start_time'],
            booking['end_time'],
            booking['details']
        ])
    
    output = BytesIO()
    output.write(si.getvalue().encode('utf-8'))
    output.seek(0)

    return send_file(
        output,
        mimetype='text/csv',
        as_attachment=True,
        download_name='meeting_bookings.csv'
    )


if __name__ == '__main__':
    app.run(debug=True)
