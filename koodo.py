#!/usr/bin/env python

import sys
import time
import json
import datetime

from flask import Flask, render_template, Response
from sqlalchemy import asc

from scraper import Scraper
from database import db_session, UsageDataPoint, KoodoTransaction
from credentials import get_creds

app = Flask(__name__)
app.debug = True


@app.teardown_appcontext
def shutdown_session(exception=None):
    db_session.remove()


@app.route("/usage.csv")
def usage_csv():
    entries = UsageDataPoint.query.order_by(asc(UsageDataPoint.time)).all()
    header = "time,min,mb"
    rows = [
        ','.join([
            str(e.time.strftime('%s')),
            str(e.minutes_remaining),
            str(e.mb_remaining),
        ]) for e in entries
    ]
    return Response("\n".join([header] + rows), mimetype='text/csv')


@app.route("/usage.json")
def usage_json():
    entries = UsageDataPoint.query.order_by(asc(UsageDataPoint.time)).all()
    return Response(
        json.dumps([x.to_object() for x in entries]),
        mimetype='application/json'
    )


@app.route("/transactions.csv")
def transactions_csv():
    entries = KoodoTransaction.query.order_by(asc(KoodoTransaction.date)).all()
    header = "date,description,credit,debit"
    rows = [
        ','.join([
            unicode(e.date.strftime('%s')),
            unicode(e.description),
            unicode(e.credit),
            unicode(e.debit),
        ]) for e in entries
    ]
    return Response("\n".join([header] + rows), mimetype='text/csv')


@app.route("/transactions.json")
def transactions_json():
    entries = KoodoTransaction.query.order_by(asc(KoodoTransaction.date)).all()
    return Response(
        json.dumps([x.to_object() for x in entries]),
        mimetype='application/json'
    )


@app.route("/")
def index():
    return render_template('index.html')


def scrape():
    scraper = Scraper(**get_creds())

    #   Fetch usage info re: boosters.
    le = UsageDataPoint(
        time=datetime.datetime.utcnow(),
        **scraper.fetch_booster_usage()
    )

    db_session.add(le)
    yield le

    #   Fetch latest transactions and put these in the DB,
    #   but only if we don't already have them.
    for transaction in scraper.fetch_most_recent_transactions():
        existing = KoodoTransaction \
            .query \
            .filter_by(koodo_id=transaction['koodo_id']) \
            .first()
        if not existing:
            kt = KoodoTransaction(**transaction)
            db_session.add(kt)
            yield kt

    db_session.commit()


if __name__ == "__main__":
    if ('--fetch' in sys.argv or
            (sys.stdout.isatty() and '--server' not in sys.argv)):
        start_time = time.time()
        print "Fetching latest data from Koodo..."
        for row in scrape():
            print dict(row.to_object())
        end_time = time.time()
        print "Done fetching. (Took %2.2f msec.)" % (
            (end_time - start_time) * 1000
        )
    else:
        app.run()
