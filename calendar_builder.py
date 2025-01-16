from io import StringIO
from scraper import scrapeGymCalendar
from utils import log
from dotenv import load_dotenv

# Create a function to generate iCalendar data for a given event
def build_ics(events):
    calendar = StringIO()
    calendar.write("BEGIN:VCALENDAR\n")
    calendar.write("VERSION:2.0\n")
    calendar.write("CALSCALE:GREGORIAN\n")
    
    # Define VTIMEZONE for America/New_York
    calendar.write("BEGIN:VTIMEZONE\n")
    calendar.write("TZID:America/New_York\n")
    calendar.write("X-LIC-LOCATION:America/New_York\n")
    calendar.write("BEGIN:DAYLIGHT\n")
    calendar.write("TZOFFSETFROM:-0500\n")
    calendar.write("TZOFFSETTO:-0400\n")
    calendar.write("TZNAME:EDT\n")
    calendar.write("DTSTART:19700308T020000\n")
    calendar.write("RRULE:FREQ=YEARLY;BYMONTH=3;BYDAY=2SU\n")
    calendar.write("END:DAYLIGHT\n")
    calendar.write("BEGIN:STANDARD\n")
    calendar.write("TZOFFSETFROM:-0400\n")
    calendar.write("TZOFFSETTO:-0500\n")
    calendar.write("TZNAME:EST\n")
    calendar.write("DTSTART:19701101T020000\n")
    calendar.write("RRULE:FREQ=YEARLY;BYMONTH=11;BYDAY=1SU\n")
    calendar.write("END:STANDARD\n")
    calendar.write("END:VTIMEZONE\n")

    summary = "CrossFit Class"
    location = "CrossFit Wonderland"
    
    for event in events:
        start_time, end_time, description = event
        calendar.write("BEGIN:VEVENT\n")
        calendar.write(f"SUMMARY:{summary}\n")
        calendar.write(f"DTSTART;TZID=America/New_York:{start_time.strftime('%Y%m%dT%H%M%S')}\n")
        calendar.write(f"DTEND;TZID=America/New_York:{end_time.strftime('%Y%m%dT%H%M%S')}\n")
        calendar.write(f"LOCATION:{location}\n")
        calendar.write(f"DESCRIPTION:{description}\n")

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
    load_dotenv()

    generate_file('calendar.ics')