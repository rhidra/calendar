import requests
from bs4 import BeautifulSoup
import http.cookiejar
from datetime import datetime
from utils import log
import os


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

    # Send an HTTP GET request
    response = session.get(url)

    # Check the response status code
    if response.status_code != 200:
        log(f"Failed with status code: {response.status_code}")
        raise Exception("Failed to fetch calendar")

    #log(response.text)
    soup = BeautifulSoup(response.text, "html.parser")
    divs = soup.find_all("div", class_="item clickable hover-opacity-8 calendar-custom-color-ff00e1")
    appointmentIds = [div["id"] for div in divs if div.find("i", class_="icon-star")]
    for id in appointmentIds:
        log(f"Found appointment with ID: {id}")
    return appointmentIds


def extractAppointment(session, id):
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
    
    # Parse the date and time into datetime objects
    # For the date, we'll use the format that matches 'Monday January 13, 2025'
    date = datetime.strptime(date_str, "%A %B %d, %Y")

    # Parse the time range (assuming format '6:30 PM - 7:30 PM')
    time_parts = time_str.split(" - ")
    start_time = datetime.strptime(date_str + " " + time_parts[0], "%A %B %d, %Y %I:%M %p")
    end_time = datetime.strptime(date_str + " " + time_parts[1], "%A %B %d, %Y %I:%M %p")

    log(f"Appointment {id} is from {start_time} to {end_time}")

    return (start_time, end_time)


# Returns a list of tuples, each containing the start and end time of a class
def scrapeGymCalendar():
    session = requests.Session()
    login(session)
    ids = fetchCalendar(session)
    return [ extractAppointment(session, id) for id in ids ]


if __name__ == "__main__":
    scrapeGymCalendar()