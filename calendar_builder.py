from io import StringIO
from scraper import scrapeGymCalendar
from utils import log

# Create a function to generate iCalendar data for a given event
def build_ics(events):
    calendar = StringIO()
    calendar.write("BEGIN:VCALENDAR\n")
    calendar.write("VERSION:2.0\n")
    calendar.write("CALSCALE:GREGORIAN\n")

    summary = "CrossFit Class"
    location = "CrossFit Wonderland"
    
    for event in events:
        start_time, end_time = event
        calendar.write("BEGIN:VEVENT\n")
        calendar.write(f"SUMMARY:{summary}\n")
        calendar.write(f"DTSTART:{start_time.strftime('%Y%m%dT%H%M%S')}\n")
        calendar.write(f"DTEND:{end_time.strftime('%Y%m%dT%H%M%S')}\n")
        calendar.write(f"LOCATION:{location}\n")
        calendar.write("DESCRIPTION:Crossfit Class. Event generated automatically by calendar_builder.py\n")

        # Add reminders
        calendar.write("BEGIN:VALARM\n")
        calendar.write("TRIGGER:-P0DT1H0M0S\n") # 1 hour before
        calendar.write("ACTION:DISPLAY\n")
        calendar.write(f"DESCRIPTION:Reminder for {summary}\n")
        calendar.write("END:VALARM\n")
        
        calendar.write("BEGIN:VALARM\n")
        calendar.write("TRIGGER:-P0DT0H20M0S\n") # 20min before
        calendar.write("ACTION:DISPLAY\n")
        calendar.write(f"DESCRIPTION:Reminder for {summary}\n")
        calendar.write("END:VALARM\n")

        calendar.write("END:VEVENT\n")
    
    calendar.write("END:VCALENDAR\n")
    
    return calendar.getvalue()


def generate_file(file_name):
    log("Generating calendar file...")
    events = scrapeGymCalendar()
    ics_data = build_ics(events)

    # Save to a .ics file
    with open(file_name, "w") as f:
        f.write(ics_data)
    
    log(f"Calendar file successfully generated: {file_name}")

if __name__ == "__main__":
    generate_file()