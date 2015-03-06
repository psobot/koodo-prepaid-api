import os
import json
import getpass


def get_creds():
    if ('KOODO_USERNAME' in os.environ
            and 'KOODO_PASSWORD' in os.environ):
        return {
            "username": os.environ['KOODO_USERNAME'],
            "password": os.environ['KOODO_PASSWORD'],
        }
    try:
        return json.loads(open('credentials.json').read())
    except IOError:
        return {
            "username": raw_input("Your Koodo Prepaid email address:"),
            "password": getpass.getpass("Your Koodo Prepaid password:"),
        }
