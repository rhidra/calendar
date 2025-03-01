from flask import Flask, send_file
import threading
import time
from calendar_builder import generate_file
from utils import log
from dotenv import load_dotenv


port = 5000
file_name = "calendar.ics"

app = Flask(__name__)

def update_ics_file():
    while True:
        # Sleep for 5 minutes before regenerating
        time.sleep(5 * 60)
        generate_file(file_name)


@app.route("/calendar.ics")
def serve_ics():
    log("Serving calendar file...")
    return send_file(file_name, mimetype="text/calendar", as_attachment=True, download_name="calendar.ics")

@app.route('/')
def hello():
    log("Hello !")
    return 'Hello !'

if __name__ == "__main__":
    # load .env file
    load_dotenv()

    # Start the background thread to periodically regenerate the ICS file
    threading.Thread(target=update_ics_file, daemon=True).start()
    
    # Run the Flask server
    app.run(debug=True, host='0.0.0.0', port=port)