# koodo-prepaid-api

by Peter Sobot (psobot.com). Licensed under MIT.

---

A tiny Python program to scrape [Koodo Mobile](http://koodomobile.com)'s
prepaid billing dashboard and return data therein as a JSON blob (or CSV) over
HTTP. Super rough, lightweight, and brittle. Currently only fetches data about
usage - how many minutes and how many megabytes you have left on your mobile
"Boosters."

Includes a D3.js graph that you can look at to view your usage over time, as
well as a cronjob that can automatically fetch data from Koodo.

Runs well (and for free) on Heroku:
[![Deploy](https://www.herokucdn.com/deploy/button.png)](https://heroku.com/deploy)

---

##Local installation

    git clone https://github.com/psobot/koodo-prepaid-api.git
    cd koodo-prepaid-api
    pip install -r requirements.txt

To run the server locally:

    python koodo.py --server

To fetch a single data point from Koodo:

    python koodo.py --fetch

##Configuration

Important variables - like the username and password you use to log into
Koodo's prepaid billing dashboard - need to be stored somewhere. What better
place than in environment variables?

  - `KOODO_USERNAME` stores the user name (i.e. email address) used to log
  	into your Koodo prepaid account.

  - `KOODO_PASSWORD` stores the password you use to log into your Koodo
  	prepaid account. (~~super secure~~)

  - `DATABASE_URL` stores the DB connection string used to connect to some
  	sort of a database. If you don't provide this, a SQLite DB called
  	`koodo.db` will be created in the current directory and used instead.
  	(Note that this won't work on Heroku.)


##TODO

Tons of cool stuff could be done with this data. Scrape another page to find out
things like:

  - How much am I actually spending on my Koodo prepaid account, on average?
  - Is Prepaid still cheaper than Postpaid, given my usage patterns?
