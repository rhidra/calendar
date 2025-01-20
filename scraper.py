import requests
from bs4 import BeautifulSoup
import http.cookiejar
from datetime import datetime, timedelta
from utils import log
import os
from dotenv import load_dotenv


def login(session):
    login_page_url = "https://crossfitwonderland.sites.zenplanner.com/login.cfm?VIEW=cookies&LOGOUT=false&message=NONE"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:133.0) Gecko/20100101 Firefox/133.0",
        "Content-Type": "application/x-www-form-urlencoded",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "Referer": login_page_url
    }

    session.cookies = http.cookiejar.CookieJar()

    # There was a xsToken, but it was not necessary to login
    # The 2 requests are necessary to get the cookies or something like that. It doesn't work without them.
    login_page = session.get(login_page_url, headers=headers)
    login_page = session.get(login_page_url, headers=headers) # 2nd time to get the cookies
    #soup = BeautifulSoup(login_page.text, "html.parser")
    #xs_token = soup.find("input", {"name": "__xsToken"})["value"]
    
    # Load username and password from .env file
    username = os.getenv("MY_USERNAME")
    password = os.getenv("MY_PASSWORD")

    if username is None or password is None:
        raise Exception("Username or password not found in environment variables")
    
    login_url = "https://crossfitwonderland.sites.zenplanner.com/login.cfm?VIEW=login&LOGOUT=false&message=multiProfile"
    payload = {
        "username": username,
        "password": password,
        #"__xsToken": "67CF7046037C569C95A3DDFA26602612"
    }

    response = session.post(login_url, data=payload, headers=headers)
    
    if response.status_code == 200:
        log("Login successful!")
        #log(response.text)
    else:
        raise Exception("Login failed")


def fetchCalendar(session):
    url = "https://crossfitwonderland.sites.zenplanner.com/calendar.cfm?calendarType=PERSON:748B1290-6359-43ED-A907-D7A0475906ED"
    log(f"Fetching calendar from: {url}")
    response = session.get(url)

    if response.status_code != 200:
        log(f"Failed with status code: {response.status_code}")
        raise Exception("Failed to fetch calendar")

    #print(response.text)
    soup = BeautifulSoup(response.text, "html.parser")
    divs = soup.select("div.item.clickable.hover-opacity-8.calendar-custom-color-ff00e1")
    appointmentData = [(div["id"], div.text.strip()) for div in divs if div.find("i", class_="icon-star")]
    for id, desc in appointmentData:
        log(f"Found appointment: {id}, {desc}")
    return appointmentData


def fetchCalendarNextWeek(session):
    today = datetime.today()
    days_until_sunday = 7 - today.weekday() if today.weekday() != 6 else 7  # Always get the next Sunday
    sunday = today + timedelta(days=days_until_sunday)
    sunday = sunday.strftime("%Y-%m-%d")

    url = f"https://crossfitwonderland.sites.zenplanner.com/calendar.cfm?calendarType=PERSON:748B1290-6359-43ED-A907-D7A0475906ED&DATE={sunday}"
    log(f"Fetching calendar from: {url}")
    response = session.get(url)

    if response.status_code != 200:
        log(f"Failed with status code: {response.status_code}")
        raise Exception("Failed to fetch next week calendar")

    #print(response.text)
    soup = BeautifulSoup(response.text, "html.parser")
    divs = soup.select("div.item.clickable.hover-opacity-8.calendar-custom-color-ff00e1")
    appointmentData = [(div["id"], div.text.strip()) for div in divs if div.find("i", class_="icon-star")]
    for id, desc in appointmentData:
        log(f"Found appointment: {id}, {desc}")
    return appointmentData


def extractAppointment(session, id, description):
    url = f'https://crossfitwonderland.sites.zenplanner.com/enrollment.cfm?appointmentId={id}'
    log(f"Fetching appointment {id}")

    response = session.get(url)

    if response.status_code != 200:
        log(f"Failed with status code: {response.status_code}")
        raise Exception("Failed to fetch appointment")
    
    #log(response.text)
    soup = BeautifulSoup(response.text, "html.parser")
    date_str = soup.find("td", string="Date").find_next("td").get_text(strip=True)
    time_str = soup.find("td", string="Time").find_next("td").get_text(strip=True)
    
    # Parse the time range (assuming format '6:30 PM - 7:30 PM')
    time_parts = time_str.split(" - ")
    start_time = datetime.strptime(date_str + " " + time_parts[0], "%A %B %d, %Y %I:%M %p")
    end_time = datetime.strptime(date_str + " " + time_parts[1], "%A %B %d, %Y %I:%M %p")

    log(f"Appointment {id} is from {start_time} to {end_time}")

    return (start_time, end_time, description)


# Returns a list of tuples, each containing the start and end time of a class
def scrapeGymCalendar():
    session = requests.Session()
    login(session)
    aptData = fetchCalendar(session) + fetchCalendarNextWeek(session)
    aptData = list(dict(aptData).items())  # Remove duplicates
    return [ extractAppointment(session, id, description) for id, description in aptData ]


if __name__ == "__main__":
    load_dotenv()
    scrapeGymCalendar()