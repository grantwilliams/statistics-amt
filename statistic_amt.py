from selenium import webdriver
from selenium.common import exceptions
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup


def check_cred(login_details, sa_cred_queue, call_origin, ma_property):
    print(login_details)
    print(call_origin)
    print(ma_property)
    driver = webdriver.PhantomJS(executable_path="phantomjs/bin/phantomjs")

    driver.get("https://www.idev.nrw.de/idev/OnlineMeldung?inst=")
    driver.find_element_by_link_text(login_details[ma_property]["bundesland"]).click()
    driver.set_window_size(1920, 1080)

    user_id = driver.find_element_by_id("loginid")
    user_id.send_keys(login_details[ma_property]["sa_user_id"])
    password = driver.find_element_by_id("password")
    password.send_keys(login_details[ma_property]["sa_password"])
    password.submit()

    try:
        driver.find_element_by_id("logoutButton")
    except exceptions.NoSuchElementException:
        sa_cred_queue.put("sa not ok {}".format(call_origin))
    except exceptions.ElementNotVisibleException:
        sa_cred_queue.put("sa not ok {}".format(call_origin))
    else:
        driver.find_element_by_id("menu300").click()
        driver.find_element_by_id("menu301").click()
        address_fields = ["Adresse.URS1", "Adresse.URS2", "Adresse.URS3", "Adresse.URS4", "Adresse.URS5",
                          "Adresse.URS6", "Adresse.URS7"]
        address_field_gets = []
        empty_list = ["", "", "", "", "", "", ""]
        for field in address_fields:
            address_field_gets.append(driver.find_element_by_name(field).get_attribute("value"))
        if address_field_gets == empty_list:
            sa_cred_queue.put("sa address bad {}".format(call_origin))
        else:
            sa_cred_queue.put("sa ok {}".format(call_origin))


def send(login_details, options_details, progress_queue, ma_property):
    if options_details["open on"] == "..":
        open_on = ""
    else:
        open_on = options_details["open on"]
    driver = webdriver.Firefox()
    driver.maximize_window()

    driver.get("https://www.idev.nrw.de/idev/OnlineMeldung?inst=")
    driver.find_element_by_link_text(login_details[ma_property]["bundesland"]).click()

    user_id = driver.find_element_by_id("loginid")
    user_id.send_keys(login_details[ma_property]["sa_user_id"])
    password = driver.find_element_by_id("password")
    password.send_keys(login_details[ma_property]["sa_password"])
    password.submit()

    driver.find_element_by_link_text(options_details["sub month"]).click()

    if len(BeautifulSoup(driver.page_source, "html.parser").find_all("div", {"id": "app_message"})) > 0:
        progress_queue.put("already sent")
        return
    driver.find_element_by_id("confirmButton").click()
    driver.find_element_by_link_text("Angebot").click()
    driver.find_element_by_name("AnzBetten").send_keys(options_details["beds"])
    driver.find_element_by_link_text("Schließung/Abmeldung").click()
    driver.find_element_by_name("Schliessung").send_keys(options_details["closed on"], Keys.TAB, open_on, Keys.TAB,
                                                         options_details["force closure"])

    driver.find_element_by_link_text("Gäste aus Europa").click()


send({'Jetpak Alternative': {'beds': 51, 'bundesland': 'Berlin', 'sa_password': 'Jetpak1969@', 'sa_user_id': '1102523001'}},
     {'open on': '11.03.2016', 'beds': 51, 'closed on': '04', 'sub month': 'Januar 2016', 'force closure': '28'},
     None, "Jetpak Alternative")