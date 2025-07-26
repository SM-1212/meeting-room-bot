from flask import Flask, render_template, request, redirect, url_for, send_file
import csv
from io import StringIO, BytesIO

app = Flask(__name__)

# In-memory list to store bookings
bookings = []

@app.route('/', methods=['GET', 'POST'])
def index():
    error = None
    if request.method == 'POST':
        # Extract form data
        date = request.form['date']
        name = request.form['name']
        email = request.form['email']
        department = request.form['department']
        attendees = request.form['attendees']
        room_type = request.form['room_type']
        start_time = request.form['start_time']
        end_time = request.form['end_time']
        details = request.form['details']

        # Check for booking conflicts
        for booking in bookings:
            if (
                booking['date'] == date and
                booking['room_type'] == room_type and
                not (end_time <= booking['start_time'] or start_time >= booking['end_time'])
            ):
                error = "Room already booked for the selected time slot."
                return render_template("index.html", bookings=bookings, error=error)

        # Add to bookings
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

    return render_template("index.html", bookings=bookings, error=error)

@app.route('/cancel/<int:index>', methods=['POST'])
def cancel_booking(index):
    if 0 <= index < len(bookings):
        bookings.pop(index)
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
