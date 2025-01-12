from datetime import datetime

# Log function to always add the current time to the log message
def log(message):
    print(f"[{datetime.now()}] {message}")