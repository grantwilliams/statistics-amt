import re
import csv
import datetime
import calendar
import mechanicalsoup
import requests.exceptions


def check_cred(login_details, hw_cred_queue, call_origin):
    browser = mechanicalsoup.Browser(soup_config={"features": "html.parser"})
    try:
        login_page = browser.get('https://inbox.hostelworld.com/inbox/', timeout=15)
    except requests.exceptions.Timeout:
        hw_cred_queue.put("hw page timeout {}".format(call_origin))
        return
    except requests.exceptions.ConnectionError:
        hw_cred_queue.put("Could not connect to internet, please check your internet connection and try again.")
        return

    login_form = login_page.soup.form
    login_form.find("input", {"id": "HostelNumber"})['value'] = login_details["hostel number"]
    login_form.find("input", {"id": "Username"})['value'] = login_details["username"]
    login_form.find("input", {"id": "Password"})['value'] = login_details["password"]

    home_page = browser.submit(login_form, login_page.url)

    if len(home_page.soup.find_all("div", {"id": "loginInfo"})) < 1:
        hw_cred_queue.put("hw not ok {}".format(call_origin))
        return
    else:
        password_expire = home_page.soup.find_all("div", {"class": "message-password-expire"})

        if len(password_expire) > 0:
            pass_expire_in = re.findall(r'\d+', password_expire[0].text)
            hw_cred_queue.put(["hw pass expire {}".format(call_origin), pass_expire_in[0]])
        else:
            hw_cred_queue.put("hw ok {}".format(call_origin))


def get_bookings(login_details, month_chosen, hw_bookings_queue):
    start_date = month_chosen
    end_date = month_chosen.replace(day=calendar.monthrange(month_chosen.year, month_chosen.month)[1])
    bar_total = 0
    hw_bookings_queue.put("Downloading your bookings for Hostel World first, this may take a while.")
    browser = mechanicalsoup.Browser(soup_config={"features": "html.parser"})
    hw_bookings_queue.put(5)
    bar_total += 5

    login_page = browser.get('https://inbox.hostelworld.com/inbox/', timeout=15)

    login_form = login_page.soup.form
    login_form.find("input", {"id": "HostelNumber"})['value'] = login_details["hostel number"]
    login_form.find("input", {"id": "Username"})['value'] = login_details["username"]
    login_form.find("input", {"id": "Password"})['value'] = login_details["password"]

    home_page = browser.submit(login_form, login_page.url)

    bookings_page = browser.get(
        "https://inbox.hostelworld.com/booking/search/date?DateType=arrivaldate&dateFrom={}&dateTo={}".format(
            datetime.datetime.strftime(start_date, "%Y-%m-%d"), datetime.datetime.strftime(end_date, "%Y-%m-%d")))
    hw_bookings_queue.put(5)
    bar_total += 5

    bookings_table = bookings_page.soup.find_all("table", {"class": "bookings_container"})

    bookings = []
    for row in bookings_table:
        results = row.find_all("tr", {"class": ["bookings-odd", "bookings-even"]})
        for item in results:
            bookings.append(item)

    bookings_dict = dict()
    for item in bookings:
        fields = item.find_all('td')
        links = item.find_all('a')

        bookings_dict[fields[0].text.strip()] = dict()
        bookings_dict[fields[0].text.strip()]["Booking ID"] = fields[0].text.strip()
        bookings_dict[fields[0].text.strip()]["Href"] = "https://inbox.hostelworld.com{}".format(links[0].get('href'))
        bookings_dict[fields[0].text.strip()]["Name"] = fields[1].text.strip()
        bookings_dict[fields[0].text.strip()]["Arrival Date"] = fields[2].text.strip()
        bookings_dict[fields[0].text.strip()]["Nights"] = fields[5].text.strip()
        bookings_dict[fields[0].text.strip()]["Guests"] = fields[6].text.strip()
        bookings_dict[fields[0].text.strip()]["Nationality"] = ""
    hw_bookings_queue.put(5)
    bar_total += 5

    step = len(bookings_dict) // 80 if len(bookings_dict) >= 80 else 1
    i = 1
    for key in bookings_dict.keys():
        customer_page = browser.get(bookings_dict[key]["Href"])

        customer_details = customer_page.soup.find_all("ul", {"class": "customer-details"})

        for details in customer_details:
            list_items = details.find_all("li")
            bookings_dict[key]["Nationality"] = list_items[7].text.strip()
        if i % step == 0:
            hw_bookings_queue.put(1)
            bar_total += 1
        i += 1

    with open("hw_bookings.csv", 'w', newline="", encoding='utf-8') as write_file:
        hw_bookings_write = csv.writer(write_file)

        hw_bookings_write.writerow(["Booking ID", "Name", "Arrival Date", "Guests", "Nights", "Nationality"])

        for key in bookings_dict.keys():
            hw_bookings_write.writerow([bookings_dict[key]["Booking ID"]] +
                                       [bookings_dict[key]["Name"]] +
                                       [bookings_dict[key]["Arrival Date"]] +
                                       [bookings_dict[key]["Guests"]] +
                                       [bookings_dict[key]["Nights"]] +
                                       [bookings_dict[key]["Nationality"]])
    hw_bookings_queue.put(99 - bar_total)
    hw_bookings_queue.put("Finished")
