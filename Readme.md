# koodo-prepaid-api

by Peter Sobot (psobot.com). Licensed under MIT.

---

A simple script to scrape [Koodo Mobile](http://koodomobile.com)'s Prepaid billing dashboard
and return the data therein as a JSON blob. Super rough, lightweight, and brittle.

Includes a D3.js graph that you can look at to view your usage over time,
as well as a cronjob that can automatically fetch data from Koodo.

---

##How to use

    git clone https://github.com/psobot/koodo-prepaid-api.git
    pip install mechanize beautifulsoup4
    python koodo.py


##`credentials.json` example

    {
      "username": "me@mydomain.com",
      "password": "blahblahblah"  
    }
