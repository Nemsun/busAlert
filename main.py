from selenium import webdriver
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from twilio.rest import Client
import datetime


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
    return driver

def scrape_times():
    # Scrape leave times
    driver = open_driver()
    driver = select_bus_route(driver)
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

def find_earliest_bus(time, leave_times):
    time_obj = datetime.datetime.strptime(time, "%I:%M %p")
    now = (time_obj + datetime.timedelta(minutes=10)).strftime("%I:%M %p")
    if now < leave_times[0]:
        return f'The earliest bus is at {leave_times[0]}'
    else:
        return find_earliest_bus(time, leave_times[1:])


def send_message(message):
    twilio_account_isd = "ACef8559227c18441d69a0cfc984ec5961"
    twilio_account_token = "3f3956fef19ac71dac4e36ce7341bc18"
    twilio_account_phone_num = "+18669395265"
    my_phone_num = "+18323663919"

    client = Client(twilio_account_isd, twilio_account_token)
    client.messages.create(
        to=my_phone_num,
        from_=twilio_account_phone_num,
        body=message
    )

# Check whether it is time to go to class or go home
def check_time():
    now = datetime.datetime.strptime("8:15 PM", "%I:%M %p") # datetime.datetime.now()
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


    find_earliest_bus("8:15 PM", leave_times)
    print(find_earliest_bus("8:15 PM", return_times))
    day_start, day_end = check_time()

    if day_start:
        message = (
            f'Good morning!\n\n'
            f'{find_earliest_bus(leave_times)}'
        )
        # send_message(message)
    if day_end:
        message = (
            f'Good afternoon!\n\n'
            f'{find_earliest_bus(return_times)}'
        )
        # send_message(message)


if __name__ == "__main__":
    main()