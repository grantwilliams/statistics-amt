import re
import os
import json
import socket
import requests.exceptions, requests.packages
import mechanicalsoup


def check_cred(login_details, ma_cred_queue, call_origin):
    browser = mechanicalsoup.Browser(soup_config={"features": "html.parser"})
    try:
        login_page = browser.get('https://inbox.myallocator.com/en/login')
    except Exception:
        ma_cred_queue.put(["exit", "Connection error, could not connect to internet"])
        return
    else:
        login_form = login_page.soup.select('.login_box')[0].select('form')[0]
        login_form.select('#Username')[0]['value'] = login_details["ma_username"]
        login_form.select('#Password')[0]['value'] = login_details["ma_password"]

        home_page = browser.submit(login_form, login_page.url)

        property_tags = home_page.soup.find_all("a", class_="property-link")

        if len(property_tags) > 0:
            ma_cred_queue.put("ma ok {}".format(call_origin))
        else:
            ma_cred_queue.put("ma not ok {}".format(call_origin))


def get_properties(login_details, default=None):
    browser = mechanicalsoup.Browser(soup_config={"features": "html.parser"})

    login_page = browser.get('https://inbox.myallocator.com/en/login')
    login_form = login_page.soup.select('.login_box')[0].select('form')[0]

    login_form.select('#Username')[0]['value'] = login_details["ma_username"]
    login_form.select('#Password')[0]['value'] = login_details["ma_password"]

    home_page = browser.submit(login_form, login_page.url)

    property_tags = home_page.soup.find_all("a", class_="property-link")

    properties = {
        "--Select Property--": ["", ""]
    }
    for tag in property_tags:
        properties[tag.text] = [tag.get("href"), ""]

    with open("data_files/properties.json", "w") as outfile:
        json.dump(properties, indent=4, sort_keys=True, fp=outfile)


def download_bookings_csv(login_details, url, download_queue):
    if os.path.isfile("bookings.csv"):
        download_queue.put(99)
        download_queue.put("Finished!")
        return
    browser = mechanicalsoup.Browser(soup_config={"features": "html.parser"})
    download_queue.put(20)
    try:
        login_page = browser.get('https://inbox.myallocator.com/en/login')

        login_form = login_page.soup.select('.login_box')[0].select('form')[0]
        download_queue.put(20)
        login_form.select('#Username')[0]['value'] = login_details["ma_username"]
        login_form.select('#Password')[0]['value'] = login_details["ma_password"]
        download_queue.put(20)
        browser.submit(login_form, login_page.url)
        download_queue.put(20)
        property_number = re.findall(r'\d+', url)
        browser.get('https://inbox.myallocator.com'.format(url))

        csv_data = {
            'criteria': 'start_days',
            'timespan': '',
            'filter': ''
        }

        response = browser.post(
            "https://inbox.myallocator.com/dispatch/csv_export/{}/bookings.csv".format(property_number[0]), csv_data)
        download_queue.put(19)
        bookings = open('bookings.csv', 'wb')
        bookings.write(response.content)
        bookings.close()
        download_queue.put("Finished!")
        return
    except Exception:
        download_queue.put(["exit", "Connection error, could not connect to internet"])