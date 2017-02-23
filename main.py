#! /usr/local/bin/python3
# coding: utf-8

import requests
from bs4 import BeautifulSoup as bs
import feedparser
import configparser

config_file = 'config.ini'

config = configparser.RawConfigParser()
config.read(config_file)

def get_text(url):
    data = requests.get(url).text
    soup = bs(data, 'html.parser')
    text = soup.find(id='mmread')
    return str(text)

def get_cursor():
    return config.get('Settings', 'cursor')

def set_cursor(entry_id):
    config.set('Settings', 'cursor', entry_id)
    with open(config_file, 'w') as cfg:
        config.write(cfg)
    return

def send_email(subject, body, recipient):
    return requests.post(
        config.get('MailGun','api'),
        auth=("api", config.get('MailGun', 'key')),
        data={"from": "Kotek Server <admin@kotek.co>",
              "to": [recipient],
              "subject": subject,
              "html": body})

def check_entries(entries):

    for entry in entries:
        # Check authors
        if not "Любовь Комарова" in entry['summary']:
            continue

        if entry['id'] == get_cursor():
            break

        print(entry['id'])

        email = [
            entry['id'],
            get_text(entry['link'])
        ]

        send_email(
            entry['title'],
            "<hr>".join(email),
            config.get('Settings','recipient')
        )

        set_cursor(entry['id'])
        break

def run():
    url = config.get('Settings', 'url')
    d = feedparser.parse(url)
    entries = d['entries']
    check_entries(entries)

if __name__ == '__main__':
    run()
