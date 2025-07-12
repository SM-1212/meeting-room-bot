from flask import Flask, render_template, request, redirect
import csv
import uuid
from datetime import datetime

app = Flask(__name__)
BOOKING_FILE = 'bookings.csv'

def read_bookings():
    bookings = []
    try:
        with open(BOOKING_FILE, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                bookings.append(row)
    except FileNotFoundError:
        pass
    return bookings

def write_bookings(bookings):
    with open(BOOKING_FILE, 'w', newline='') as f:
        fieldnames = ['id', 'name', 'email', 'room_type', 'date', 'start_time', 'end_time', 'purpose', 'department']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in bookings:
            writer.writerow(row)

@app.route('/', methods=['GET', 'POST'])
def index():
    message = ''
    if request.method == 'POST':
        data = {
            'id': str(uuid.uuid4()),
            'name': request.form['name'],
            'email': request.form['email'],
            'room_type': request.form['room_type'],
            'date': request.form['date'],
            'start_time': request.form['start_time'],
            'end_time': request.form['end_time'],
            'purpose': request.form.get('purpose', ''),
            'department': request.form.get('department', '')
        }
        bookings = read_bookings()

        # Prevent overlapping bookings for the same room
        for b in bookings:
            if (b['room_type'] == data['room_type'] and b['date'] == data['date'] and
                not (data['end_time'] <= b['start_time'] or data['start_time'] >= b['end_time'])):
                message = "❌ This room is already booked during the selected time."
                return render_template('index.html', message=message, bookings=bookings)

        bookings.append(data)
        write_bookings(bookings)
        message = "✅ Room booked successfully!"

    bookings = read_bookings()
    bookings = sorted(bookings, key=lambda b: (b['date'], b['start_time']))
    return render_template('index.html', message=message, bookings=bookings)

@app.route('/cancel', methods=['POST'])
def cancel():
    cancel_id = request.form['cancel_id']
    bookings = read_bookings()
    bookings = [b for b in bookings if b['id'] != cancel_id]
    write_bookings(bookings)
    return redirect('/')

if __name__ == '__main__':
    app.run(debug=True)
