import mechanize
from bs4 import BeautifulSoup


def fetch_booster_usage(username, password):
    b = mechanize.Browser()
    b.set_handle_robots(False)
    b.open("https://prepaidselfserve.koodomobile.com/Overview/")
    b.select_form(nr=0)
    b.form['ctl00$FullContent$ContentBottom$LoginControl$UserName'] = username
    b.form['ctl00$FullContent$ContentBottom$LoginControl$Password'] = password
    b.submit()
    b.follow_link([x for x in b.links() if x.text == "View Booster Usage"][0])
    return parse_booster_usage(b.response().read())


def parse_booster_usage(data):
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
