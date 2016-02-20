import selenium
from selenium import webdriver
from selenium.common import exceptions
import psutil


def check_cred(login_details, sa_cred_queue, call_origin):
    driver = webdriver.PhantomJS(executable_path="phantomjs/bin/phantomjs")

    driver.get("https://www.idev.nrw.de/idev/OnlineMeldung?inst=")
    driver.find_element_by_link_text(login_details["bundesland"][0]).click()
    driver.set_window_size(1920, 1080)

    user_id = driver.find_element_by_id("loginid")
    user_id.send_keys(login_details["sa_user_id"])
    password = driver.find_element_by_id("password")
    password.send_keys(login_details["sa_password"])
    password.submit()

    try:
        driver.find_element_by_id("logoutButton")
        sa_cred_queue.put("sa ok {}".format(call_origin))
    except exceptions.ElementNotVisibleException and exceptions.NoSuchElementException:
        sa_cred_queue.put("sa not ok {}".format(call_origin))


# for process in psutil.process_iter():
#     if process.name() == "phantomjs":
#         process.kill()