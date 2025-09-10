from flask import Flask, request, jsonify, render_template
import sqlite3

app = Flask(__name__)

# Initialize DB
def init_db():
    with sqlite3.connect("bookings.db") as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS bookings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                room TEXT NOT NULL,
                start_time TEXT NOT NULL,
                end_time TEXT NOT NULL
            )
        """)
    print("Database initialized.")

init_db()


@app.route("/")
def index():
    return render_template("index.html")


# Book a room
@app.route("/book", methods=["POST"])
def book_room():
    data = request.get_json()
    room = data.get("room")
    start_time = data.get("start_time")
    end_time = data.get("end_time")

    if not room or not start_time or not end_time:
        return jsonify({"error": "Missing required fields"}), 400

    with sqlite3.connect("bookings.db") as conn:
        conn.execute(
            "INSERT INTO bookings (room, start_time, end_time) VALUES (?, ?, ?)",
            (room, start_time, end_time),
        )
        conn.commit()

    return jsonify({"message": "Room booked successfully!"})


# View all bookings
@app.route("/bookings", methods=["GET"])
def view_bookings():
    with sqlite3.connect("bookings.db") as conn:
        cursor = conn.execute("SELECT id, room, start_time, end_time FROM bookings")
        bookings = [
            {
                "id": row[0],
                "room": row[1],
                "start_time": row[2],
                "end_time": row[3],
            }
            for row in cursor.fetchall()
        ]
    return jsonify(bookings)


# Cancel a booking
@app.route("/cancel/<int:booking_id>", methods=["DELETE"])
def cancel_booking(booking_id):
    with sqlite3.connect("bookings.db") as conn:
        cursor = conn.execute("DELETE FROM bookings WHERE id = ?", (booking_id,))
        conn.commit()
        if cursor.rowcount == 0:
            return jsonify({"error": "Booking not found"}), 404

    return jsonify({"message": f"Booking ID {booking_id} cancelled successfully!"})


if __name__ == "__main__":
    app.run(debug=True)
