import mechanize
import getpass
import json
import csv
import sys
import time
from bs4 import BeautifulSoup


CSV_FILE = "public/koodo.csv"
CSV_HEADER = "time,mb,min"


def fetch_html(username, password):
    b = mechanize.Browser()
    b.open("https://prepaidselfserve.koodomobile.com/Overview/")
    b.select_form(nr=0)
    b.form['ctl00$FullContent$ContentBottom$LoginControl$UserName'] = username
    b.form['ctl00$FullContent$ContentBottom$LoginControl$Password'] = password
    b.submit()
    b.follow_link([x for x in b.links() if x.text == "View Booster Usage"][0])
    return b.response().read()


def distill_html(data):
    soup = BeautifulSoup(data)
    dp = soup.find(id='FullContent_DashboardContent_ViewBundleUsagePanel')
    
    return {
        "mb_remaining": sum(
            float(x.contents[0])
            for x in dp.findAll(id="DataRemainingLiteral")
        ),
        "minutes_remaining": sum(
            float(x.contents[0])
            for x in dp.findAll(id="CrossServiceRemainingLiteral")
        )
    }


def log_values(data):
    try:
        write_header = False
        with open(CSV_FILE, 'r') as f:
            firstLine = next(f).strip()
            if firstLine != CSV_HEADER:
                write_header = True
        if write_header:
            with open(CSV_FILE, 'w') as f:
                f.write(CSV_HEADER + "\r\n")
    except Exception as e:
        print e
        
    with open(CSV_FILE, 'a') as f:
        writer = csv.writer(f)
        writer.writerow([
            time.time(),
            data['mb_remaining'],
            data['minutes_remaining']
        ])


if __name__ == "__main__":
    try:
        creds = json.loads(open('credentials.json').read())
    except IOError:
        creds = {
            "username": raw_input("Your Koodo Prepaid email address:"),
            "password": getpass.getpass("Your Koodo Prepaid password:")
        }
    data = distill_html(fetch_html(
        creds['username'], creds['password']
    ))
    if sys.stdout.isatty():
        sys.stdout.write(str(data) + "\n")
    else:
        log_values(data)
