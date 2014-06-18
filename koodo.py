import mechanize
import getpass
import json
from bs4 import BeautifulSoup


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

if __name__ == "__main__":
    try:
        creds = json.loads(open('credentials.json').read())
    except IOError:
        creds = {
            "username": raw_input("Your Koodo Prepaid email address:"),
            "password": getpass.getpass("Your Koodo Prepaid password:")
        }
    print distill_html(fetch_html(
        creds['username'], creds['password']
    ))
