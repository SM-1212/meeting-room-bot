from flask import Flask, request, jsonify, render_template
import os

app = Flask(__name__)

# In-memory storage for meeting room bookings (you can later replace with DB if needed)
bookings = []

@app.route("/")
def home():
    return render_template("index.html")  # Make sure you have a templates/index.html

@app.route("/book", methods=["POST"])
def book_meeting():
    try:
        data = request.get_json()
        room = data.get("room")
        date = data.get("date")
        start_time = data.get("start_time")
        end_time = data.get("end_time")
        booked_by = data.get("booked_by")

        # Validation
        if not all([room, date, start_time, end_time, booked_by]):
            return jsonify({"error": "Missing required fields"}), 400

        # Check for conflicts
        for b in bookings:
            if b["room"] == room and b["date"] == date:
                if not (end_time <= b["start_time"] or start_time >= b["end_time"]):
                    return jsonify({"error": "Room already booked for this slot"}), 400

        booking = {
            "room": room,
            "date": date,
            "start_time": start_time,
            "end_time": end_time,
            "booked_by": booked_by
        }
        bookings.append(booking)

        return jsonify({"message": "Room booked successfully!", "booking": booking})

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/bookings", methods=["GET"])
def get_bookings():
    return jsonify(bookings)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))  # Render uses dynamic PORT
    app.run(host="0.0.0.0", port=port, debug=True)
