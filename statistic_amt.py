import selenium
from selenium import webdriver
from selenium.common import exceptions
import psutil


def check_cred(login_details):
    print(login_details)
    driver = webdriver.PhantomJS(executable_path="phantomjs/bin/phantomjs")

    driver.get("https://www.idev.nrw.de/idev/OnlineMeldung?inst=")
    driver.find_element_by_link_text(login_details["bundesland"]).click()
    driver.set_window_size(1920, 1080)
    print("hello")
    user_id = driver.find_element_by_id("loginid")
    user_id.send_keys(login_details["sa_user_id"])
    password = driver.find_element_by_id("password")
    password.send_keys(login_details["sa_password"])
    password.submit()

    try:
        driver.find_element_by_id("logoutButton")
        return True
    except exceptions.ElementNotVisibleException and exceptions.NoSuchElementException:
        return False


# for process in psutil.process_iter():
#     if process.name() == "phantomjs":
#         process.kill()