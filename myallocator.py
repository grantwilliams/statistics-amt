import re
import json
import mechanicalsoup
from bs4 import BeautifulSoup


def check_cred(login_details):
    browser = mechanicalsoup.Browser()

    login_page = browser.get('https://inbox.myallocator.com/en/login')
    login_form = login_page.soup.select('.login_box')[0].select('form')[0]

    login_form.select('#Username')[0]['value'] = login_details["ma_username"]
    login_form.select('#Password')[0]['value'] = login_details["ma_password"]

    home_page = browser.submit(login_form, login_page.url)

    property_tags = home_page.soup.find_all("a", class_="property-link")

    if len(property_tags) > 0:
        return True
    else:
        return False


def get_properties(login_details, default=None):
    browser = mechanicalsoup.Browser()

    login_page = browser.get('https://inbox.myallocator.com/en/login')
    login_form = login_page.soup.select('.login_box')[0].select('form')[0]

    login_form.select('#Username')[0]['value'] = login_details["ma_username"]
    login_form.select('#Password')[0]['value'] = login_details["ma_password"]

    home_page = browser.submit(login_form, login_page.url)

    property_tags = home_page.soup.find_all("a", class_="property-link")

    properties = {
        "--Select Property--": ""
    }
    for tag in property_tags:
        properties[tag.text] = tag.get("href")

    with open("data_files/properties.json", "w") as outfile:
        json.dump(properties, outfile)


def download_bookings_csv(login_details, url):
    browser = mechanicalsoup.Browser()

    login_page = browser.get('https://inbox.myallocator.com/en/login')
    login_form = login_page.soup.select('.login_box')[0].select('form')[0]

    login_form.select('#Username')[0]['value'] = login_details["ma_username"]
    login_form.select('#Password')[0]['value'] = login_details["ma_password"]

    browser.submit(login_form, login_page.url)

    property_number = re.findall(r'\d+', url)
    browser.get('https://inbox.myallocator.com'.format(url))

    csv_data = {
        'criteria': 'start_days',
        'timespan': '',
        'filter': ''
    }

    response = browser.post(
        "https://inbox.myallocator.com/dispatch/csv_export/{}/bookings.csv".format(property_number[0]), csv_data)

    bookings = open('bookings.csv', 'wb')
    bookings.write(response.content)
    bookings.close()
