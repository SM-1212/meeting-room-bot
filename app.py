HEAD
from flask import Flask, render_template, request, redirect, url_for
import sqlite3
from datetime import datetime

app = Flask(__name__)
DB_NAME = 'bookings.db'

# ---------- Database Setup ----------
def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS bookings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            email TEXT,
            date TEXT,
            start_time TEXT,
            end_time TEXT,
            purpose TEXT,
            department TEXT,
            room_type TEXT
        )
    ''')
    conn.commit()
    conn.close()

# ---------- Load Bookings ----------
def load_bookings():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT * FROM bookings")
    rows = c.fetchall()
    conn.close()
    return rows

# ---------- Save Booking ----------
def save_booking(data):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''
        INSERT INTO bookings (name, email, date, start_time, end_time, purpose, department, room_type)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', data)
    conn.commit()
    conn.close()

# ---------- Delete Booking ----------
def delete_booking(booking_id):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("DELETE FROM bookings WHERE id = ?", (booking_id,))
    conn.commit()
    conn.close()

@app.route('/', methods=['GET', 'POST'])
def index():
    message = ''
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        date = request.form['date']
        start_time = request.form['start_time']
        end_time = request.form['end_time']
        purpose = request.form['purpose']
        department = request.form['department']
        room_type = request.form['room_type']

        new_start = datetime.strptime(start_time, "%H:%M").time()
        new_end = datetime.strptime(end_time, "%H:%M").time()

        bookings = load_bookings()

        for booking in bookings:
            b_date = booking[3]
            b_start = datetime.strptime(booking[4], "%H:%M").time()
            b_end = datetime.strptime(booking[5], "%H:%M").time()

            if date == b_date and (
                (new_start >= b_start and new_start < b_end) or
                (new_end > b_start and new_end <= b_end) or
                (new_start <= b_start and new_end >= b_end)
            ):
                message = 'This time slot is already booked.'
                break
        else:
            save_booking((name, email, date, start_time, end_time, purpose, department, room_type))
            return redirect(url_for('index'))

    all_bookings = load_bookings()
    today = datetime.now().date()

    upcoming_bookings = [b for b in all_bookings if datetime.strptime(b[3], "%Y-%m-%d").date() >= today]
    upcoming_bookings.sort(key=lambda x: (x[3], x[4]))  # sort by date and start time

    return render_template("index.html", bookings=upcoming_bookings, message=message)

@app.route('/cancel/<int:booking_id>')
def cancel_booking(booking_id):
    delete_booking(booking_id)
    return redirect(url_for('index'))

if __name__ == '__main__':
    init_db()
    app.run(debug=True, port=10000)

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
df9d9ec (Initial commit: Meeting Room Booking Bot with cancel + CSV)
from flask import Flask

app = Flask(__name__)

@app.route('/')
def home():
    return "Meeting Room Bot is Live!"

