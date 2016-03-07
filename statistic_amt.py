from selenium import webdriver
from selenium.common import exceptions
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup


def check_cred(login_details, sa_cred_queue, call_origin, ma_property):
    driver = webdriver.PhantomJS(executable_path="phantomjs/bin/phantomjs")
    # driver = webdriver.Firefox()
    driver.set_page_load_timeout(15)
    try:
        driver.get("https://www.idev.nrw.de/idev/OnlineMeldung?inst=")
    except exceptions.TimeoutException:
        sa_cred_queue.put("sa page timeout {}".format(call_origin))
        return
    try:
        WebDriverWait(driver, 10).until(EC.visibility_of_element_located((
            By.LINK_TEXT, login_details[ma_property]["bundesland"]))).click()
    except exceptions.TimeoutException:
        sa_cred_queue.put("sa page timeout {}".format(call_origin))
        return
    driver.set_window_size(1920, 1080)

    user_id = driver.find_element_by_id("loginid")
    user_id.send_keys(login_details[ma_property]["sa_user_id"])
    password = driver.find_element_by_id("password")
    password.send_keys(login_details[ma_property]["sa_password"])
    password.submit()

    try:
        driver.find_element_by_id("logoutButton")
    except exceptions.NoSuchElementException:
        sa_cred_queue.put(["sa not ok {}".format(call_origin), "{}".format(ma_property)])
        return
    except exceptions.ElementNotVisibleException:
        sa_cred_queue.put(["sa not ok {}".format(call_origin), "{}".format(ma_property)])
        return
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
    driver.quit()


def send(login_details, options_details, progress_queue, ma_property, statistics_results, already_sent_continue):
    progress_queue.put("Openings virtual browser...")
    def stats_generator():
        for item in statistics_results.keys():
            yield [statistics_results[item][0], statistics_results[item][1]]
    statistics_generator = stats_generator()

    if options_details["open on"] == "..":
        open_on = ""
    else:
        open_on = options_details["open on"]
    driver = webdriver.PhantomJS(executable_path="phantomjs/bin/phantomjs")
    driver.set_window_size(1920, 1080)
    # driver = webdriver.Firefox()
    driver.set_page_load_timeout(15)
    progress_queue.put(10)

    try:
        driver.get("https://www.idev.nrw.de/idev/OnlineMeldung?inst=")
    except exceptions.TimeoutException:
        progress_queue.put("timed out")
        return
    try:
        WebDriverWait(driver, 10).until(EC.visibility_of_element_located((
            By.LINK_TEXT, login_details[ma_property]["bundesland"]))).click()
    except exceptions.TimeoutException:
        progress_queue.put("timed out")

    user_id = driver.find_element_by_id("loginid")
    user_id.send_keys(login_details[ma_property]["sa_user_id"])
    password = driver.find_element_by_id("password")
    password.send_keys(login_details[ma_property]["sa_password"])
    password.submit()
    progress_queue.put("Logging into Statistiks Amt site...")
    progress_queue.put(10)

    try:
        driver.find_element_by_link_text(options_details["sub month"]).click()
    except exceptions.NoSuchElementException:
        progress_queue.put("no date")
        driver.quit()
        return

    if len(BeautifulSoup(driver.page_source, "html.parser").find_all("div", {"id": "app_message"})) > 0:
        if not already_sent_continue:
            progress_queue.put("already sent")
            driver.quit()
            return
    progress_queue.put(10)
    progress_queue.put("Entering number of beds and closure dates...")
    driver.find_element_by_id("confirmButton").click()
    driver.find_element_by_link_text("Angebot").click()
    driver.find_element_by_name("AnzBetten").send_keys(options_details["beds"])
    driver.find_element_by_link_text("Schließung/Abmeldung").click()
    driver.find_element_by_name("Schliessung").send_keys(options_details["closed on"], Keys.TAB, open_on, Keys.TAB,
                                                         options_details["force closure"])
    progress_queue.put(10)
    driver.find_element_by_link_text("Gäste aus Europa").click()

    info_button_classes = ["class275", "class280", "class285", "class290"]
    progress_queue.put("Entering statistics for guests from Europe...")
    current_field = driver.find_element_by_name("ANK_Deutschland")
    for i in range(20):
        progress_queue.put(1)
        current_stats = next(statistics_generator)
        if current_field.get_attribute("class") in info_button_classes:
            current_field.send_keys(Keys.TAB, current_stats[0], Keys.TAB, current_stats[1], Keys.TAB)
            current_field = driver.switch_to.active_element
        else:
            current_field.send_keys(current_stats[0], Keys.TAB, current_stats[1], Keys.TAB)
            current_field = driver.switch_to.active_element

    driver.find_element_by_link_text("Gäste aus Europa, Afrika").click()

    progress_queue.put("Entering statistics for guests from Europe and Africa...")
    current_field = driver.find_element_by_name("ANK_Polen")
    for i in range(17):
        progress_queue.put(1)
        current_stats = next(statistics_generator)
        if current_field.get_attribute("class") in info_button_classes:
            current_field.send_keys(Keys.TAB, current_stats[0], Keys.TAB, current_stats[1], Keys.TAB)
            current_field = driver.switch_to.active_element
        else:
            current_field.send_keys(current_stats[0], Keys.TAB, current_stats[1], Keys.TAB)
            current_field = driver.switch_to.active_element

    driver.find_element_by_link_text("Gäste aus Amerika, Asien, u. a.").click()

    progress_queue.put("Entering statistics for guests from America, Asia etc...")
    current_field = driver.find_element_by_name("ANK_Kanada")
    for i in range(17):
        progress_queue.put(1)
        current_stats = next(statistics_generator)
        if current_field.get_attribute("class") in info_button_classes:
            current_field.send_keys(Keys.TAB, current_stats[0], Keys.TAB, current_stats[1], Keys.TAB)
            current_field = driver.switch_to.active_element
        else:
            current_field.send_keys(current_stats[0], Keys.TAB, current_stats[1], Keys.TAB)
            current_field = driver.switch_to.active_element

    statistics_generator.close()
    progress_queue.put(5)
    try:
        assert driver.find_element_by_name("ANK_Insgesamt").get_attribute('value') == str(statistics_results["TOTAL"][0])
        assert driver.find_element_by_name("UEB_Insgesamt").get_attribute('value') == str(statistics_results["TOTAL"][1])
    except AssertionError:
        progress_queue.put("assertion error")
        return
    progress_queue.put(["Finished", options_details["sub month"], statistics_results])
    # driver.quit()
