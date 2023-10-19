from selenium import webdriver
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from twilio.rest import Client
from dotenv import load_dotenv
import os
import datetime

load_dotenv()

def open_driver():
    # Target URL
    url = "https://transport.tamu.edu/busroutes.web/BusTimes?r=40/robots.txt"

    # Opening URL in Chrome
    driver = webdriver.Chrome()
    driver.get(url)
    return driver

def select_bus_route(driver):
    # Selecting my bus route
    dropdown = driver.find_element('xpath', '//*[@id="routeSelect"]')
    select = Select(dropdown)
    select.select_by_visible_text("40 Century Tree")
    return driver, select

def scrape_times():
    # Scrape leave times
    driver = open_driver()
    driver, _ = select_bus_route(driver)
    wait = WebDriverWait(driver, 10)
    table_body = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="timeTable"]/tbody')))
    # Getting bus times that arrive at my bus stop (Holleman South)
    table_rows = table_body.find_elements(By.TAG_NAME, "tr")
    return driver, table_rows

# This function returns all the non-expired bus times
def available_bus_times(driver, table_rows):
    holleman_south_times = []
    msc_times = []
    for row in table_rows:
        if 'PastLeaveTime' not in row.get_attribute("class"):
            column_data = row.find_elements(By.TAG_NAME, "td")
            msc_times_text = column_data[0].text # MSC is the 1st column
            msc_times.append(msc_times_text)
            holleman_south_time_text = column_data[1].text # Holleman South is the 2nd column
            holleman_south_times.append(holleman_south_time_text)
    driver.close()
    return msc_times, holleman_south_times

def find_earliest_bus(leave_times):
    now = datetime.datetime.now()
    current_time = now.strftime("%I:%M %p")
    current_time_obj = datetime.datetime.strptime(current_time, "%I:%M %p")
    leave_times_obj = [datetime.datetime.strptime(time, "%I:%M %p") for time in leave_times if time]

    earliest_bus = None
    for time in leave_times_obj:
        if time > current_time_obj:
            earliest_bus = time
            break

    if earliest_bus:
        return f'The earliest bus is at {earliest_bus.strftime("%I:%M %p")}'
    else:
        return "No more buses today."

def send_message(message):
    twilio_account_isd = os.getenv("TWILIO_ACCOUNT_ISD")
    twilio_account_token = os.getenv("TWILIO_ACCOUNT_TOKEN")
    twilio_account_phone_num = os.getenv("TWILIO_ACCOUNT_PHONE_NUM")
    my_phone_num = os.getenv("MY_PHONE_NUM")

    client = Client(twilio_account_isd, twilio_account_token)
    client.messages.create(
        to = my_phone_num,
        from_ = twilio_account_phone_num,
        body = message
    )

# Check whether it is time to go to class or go home
def check_time():
    now = datetime.datetime.now()
    go_to_class = False
    go_home = False
    class_time = datetime.datetime.strptime("06:45 AM", "%I:%M %p")
    home_time = datetime.datetime.strptime("11:10 AM", "%I:%M %p")

    if now.time() == class_time.time():
        go_to_class = True
    if now.time() == home_time.time():
        go_home = True

    return go_to_class, go_home


def main():
    driver, table_rows = scrape_times()
    return_times, leave_times = available_bus_times(driver, table_rows)

    find_earliest_bus(leave_times)
    find_earliest_bus(return_times)
    day_start, day_end = check_time()
    if day_start:
        message = (
            f'Good morning!\n\n'
            f'{find_earliest_bus(leave_times)}'
        )
        send_message(message)
    if day_end:
        message = (
            f'Good afternoon! I see you\'re done with class. \n\n'
            f'{find_earliest_bus(return_times)}'
        )
        send_message(message)


if __name__ == "__main__":
    main()