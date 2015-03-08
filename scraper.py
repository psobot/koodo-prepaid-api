from datetime import datetime

import mechanize
from bs4 import BeautifulSoup


def requires_login(fn):
    def ensure_logged_in(self, *args, **kwargs):
        if not self.logged_in:
            self.login()
        return fn(self, *args, **kwargs)
    return ensure_logged_in


class MissingCredentialsException(Exception):
    pass


class LoginFailure(Exception):
    pass


class Scraper(object):
    ROOT_URL = "https://prepaidselfserve.koodomobile.com/Overview/"

    def __init__(self, username=None, password=None):
        self.username = username
        self.password = password
        self.browser = mechanize.Browser()
        self.logged_in = False

    def login(self, username=None, password=None):
        if username is None:
            username = self.username
        if password is None:
            password = self.password

        if not username or not password:
            raise MissingCredentialsException()

        self.browser.set_handle_robots(False)
        self.browser.open(self.ROOT_URL)
        self.browser.select_form(nr=0)

        usernameControl = \
            'ctl00$FullContent$ContentBottom$LoginControl$UserName'
        passwordControl = \
            'ctl00$FullContent$ContentBottom$LoginControl$Password'

        self.browser.form[usernameControl] = username
        self.browser.form[passwordControl] = password
        self.browser.submit()

        if 'Logged in as:' not in self.browser.response().read():
            raise LoginFailure()
        self.logged_in = True

    @requires_login
    def fetch_booster_usage(self):
        booster_url = "products-and-services/view-bundle-usage/"
        self.browser.open(self.ROOT_URL + booster_url)

        soup = BeautifulSoup(self.browser.response().read())
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

    TRANSACTION_ATTRIBUTE_MAP = {
        'koodo_id': 'gvIDHeader',
        'date': 'gvTransactionDateCol',
        'description': 'gvTransactionTypeCol',
        'credit': 'gvCreditCol',
        'debit': 'gvDebitCol',
    }

    @requires_login
    def fetch_most_recent_transactions(self):
        transactions_url = 'billing/transaction-history/'
        self.browser.open(self.ROOT_URL + transactions_url)
        self.browser.select_form(nr=0)

        dateModeButton = \
            'ctl00$ctl00$FullContent$DashboardContent$SearchType'
        dateSelectDropdown = \
            'ctl00$ctl00$FullContent$DashboardContent$DateSelectDropDownList'
        searchButton = (
            'ctl00$ctl00$FullContent$DashboardContent$'
            'ViewTransactionHistoryButton'
        )
        searchValue = 'Search'

        self.browser.form[dateModeButton] = ['UseDropDownRadioButton']

        #   Select the third item in the dropdown list, which is
        #   the search filter that returns the most results
        self.browser.form[dateSelectDropdown] = ['3']
        self.browser.submit(name=searchButton, label=searchValue)

        soup = BeautifulSoup(self.browser.response().read())
        transactions = (
            soup.findAll('tr', {'class': 'gvTransactionHistoryRow'}) +
            soup.findAll('tr', {'class': 'gvTransactionHistoryAltRow'})
        )
        return [self._parse_transaction_history_row(t) for t in transactions]

    def _parse_transaction_history_row(self, row):
        data = []
        for attribute, cssClass in self.TRANSACTION_ATTRIBUTE_MAP.iteritems():
            value = row.find('td', {'class': cssClass}).text.strip()

            #   Normalize dates to datetimes
            if attribute == 'date':
                value = datetime.strptime(value, '%b %d, %Y')

            #   Convert dollar values to integer values of cents,
            #   assuming that the maximum dollar value is less than $1000
            elif value.startswith('$') and len(value) <= len('$999.99'):
                value = int(value.replace('$', '').replace('.', ''))

            elif attribute == 'koodo_id':
                value = int(value)

            #   Convert &nbsp rows to NULLs
            if value == "" or value == '&nbsp':
                value = None

            data.append((attribute, value))
        return dict(data)
