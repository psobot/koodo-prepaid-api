#!/usr/bin/env python

import sys
import time
import json
import datetime
import traceback

from flask import Flask
from sqlalchemy import asc

from scraper import fetch_booster_usage
from database import db_session, LogEntry
from credentials import get_creds

app = Flask(__name__)
app.debug = True


@app.teardown_appcontext
def shutdown_session(exception=None):
    db_session.remove()


@app.route("/koodo.csv")
def csv_data():
    entries = LogEntry.query.order_by(asc(LogEntry.time)).all()
    header = "time,min,mb"
    rows = [
        ','.join([
            str(e.time.strftime('%s')),
            str(e.minutes_remaining),
            str(e.mb_remaining),
        ]) for e in entries
    ]
    return "\n".join([header] + rows)


@app.route("/koodo.json")
def json_data():
    entries = LogEntry.query.order_by(asc(LogEntry.time)).all()
    return json.dumps([x.to_object() for x in entries])


@app.route("/update", methods=['POST'])
def update():
    try:
        return json.dumps(add_data_point().to_object())
    except Exception as e:
        print traceback.format_exc(e)
        raise e


@app.route("/")
def index():
    return open('public/index.html', 'r').read()


def add_data_point():
    creds = get_creds()
    data = fetch_booster_usage(
        creds['username'], creds['password']
    )
    now = datetime.datetime.utcnow()
    le = LogEntry(now, **data)
    db_session.add(le)
    db_session.commit()
    return le

if __name__ == "__main__":
    if ('--fetch' in sys.argv or
            (sys.stdout.isatty() and '--server' not in sys.argv)):
        start_time = time.time()
        print "Fetching data from Koodo..."
        print add_data_point().to_object()
        end_time = time.time()
        print "Done fetching. (Took %2.2f msec.)" % (
            (end_time - start_time) * 1000
        )
    else:
        app.run()
