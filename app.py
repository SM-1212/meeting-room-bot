from flask import Flask, render_template, request, redirect, url_for, send_file
import pandas as pd
from datetime import datetime

app = Flask(__name__)
BOOKINGS_FILE = 'bookings.csv'

def load_bookings():
    try:
        df = pd.read_csv(BOOKINGS_FILE)
        df['Date'] = pd.to_datetime(df['Date'])
        df['Start Time'] = pd.to_datetime(df['Start Time'], format='%H:%M').dt.time
        df['End Time'] = pd.to_datetime(df['End Time'], format='%H:%M').dt.time
        return df
    except FileNotFoundError:
        return pd.DataFrame(columns=['Name', 'Email', 'Room Type', 'Date', 'Start Time', 'End Time', 'Purpose', 'Department'])

def save_bookings(df):
    df.to_csv(BOOKINGS_FILE, index=False)

@app.route('/', methods=['GET', 'POST'])
def index():
    message = ''
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        room_type = request.form['room_type']
        date = request.form['date']
        start_time = request.form['start_time']
        end_time = request.form['end_time']
        purpose = request.form['purpose']
        department = request.form['department']

        new_booking = {
            'Name': name,
            'Email': email,
            'Room Type': room_type,
            'Date': pd.to_datetime(date),
            'Start Time': pd.to_datetime(start_time, format='%H:%M').time(),
            'End Time': pd.to_datetime(end_time, format='%H:%M').time(),
            'Purpose': purpose,
            'Department': department
        }

        bookings = load_bookings()

        # Check for room & time conflict
        conflicting = bookings[
            (bookings['Room Type'] == room_type) &
            (bookings['Date'] == new_booking['Date']) &
            (bookings['Start Time'] < new_booking['End Time']) &
            (bookings['End Time'] > new_booking['Start Time'])
        ]

        if not conflicting.empty:
            message = f'{room_type} is already booked for this time slot.'
        else:
            bookings = pd.concat([bookings, pd.DataFrame([new_booking])], ignore_index=True)
            save_bookings(bookings)
            return redirect(url_for('index'))

    bookings = load_bookings()
    today = pd.to_datetime(datetime.now().date())
    upcoming = bookings[(bookings['Date'] >= today)]
    upcoming = upcoming.sort_values(by=['Date', 'Start Time'])

    return render_template('index.html', bookings=upcoming, message=message)

@app.route('/cancel/<int:booking_index>')
def cancel_booking(booking_index):
    bookings = load_bookings()
    if 0 <= booking_index < len(bookings):
        bookings = bookings.drop(bookings.index[booking_index])
        bookings.reset_index(drop=True, inplace=True)
        save_bookings(bookings)
    return redirect(url_for('index'))

@app.route('/download')
def download_csv():
    return send_file(BOOKINGS_FILE, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True, port=10000)
