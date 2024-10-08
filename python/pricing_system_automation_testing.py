from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime, timedelta
import time
import requests
import csv
import os
from dotenv import load_dotenv

# Loading environment variables
load_dotenv()

def get_cookies_as_dict(driver):
    cookies = driver.get_cookies()
    return {cookie['name']: cookie['value'] for cookie in cookies}

def save_price_data_to_csv(price_data, age, period):
    filename = 'price_data.csv'
    file_exists = os.path.isfile(filename)
    with open(filename, mode='a', newline='') as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(['ID', 'priceTotal', 'pricePolicy', 'priceIPT', 'priceNet', 'Age', 'Period'])
        for item_id, item_data in price_data.items():
            writer.writerow([item_id, item_data['priceTotal'], item_data['pricePolicy'], item_data['priceIPT'],
                             item_data['priceNet'], age, period])
    print(f"Data saved to {filename}")

def run_script(age, period):
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')  # Adding headless mode
    options.add_argument('--disable-gpu')  # Disabling GPU usage
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')  # Disabling /dev/shm usage

    driver = webdriver.Chrome(options=options)

    try:
        driver.get("https://XXXXXXXXX.globelink.eu/wizard#/step1.html?country_id=4")
        print("Page loaded")

        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        print("Login successful")

        try:
            alert = WebDriverWait(driver, 10).until(EC.alert_is_present())
            alert.accept()
            print("Alert accepted")
        except Exception as e:
            print(f"No alert found: {e}")

        time.sleep(2)

        # Clicking on 'Single Trip' button
        single_trip_button = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.XPATH, "//button[contains(@class, 'Single Trip')]"))
        )
        single_trip_button.click()
        print("Clicked on 'Single Trip' button")

        WebDriverWait(driver, 20).until(
            EC.text_to_be_present_in_element_attribute((By.XPATH, "//button[contains(@class, 'Single Trip')]"),
                                                       "aria-pressed", "true")
        )
        print("aria-pressed is now 'true' for 'Single Trip' button")

        # Clicking on 'Europe inc. Egypt & Morocco' button
        europe_button = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located(
                (By.XPATH, "//button[contains(@class, 'Europe') and contains(., 'inc. Egypt & Morocco')]"))
        )
        europe_button.click()
        print("Clicked on 'Europe inc. Egypt & Morocco' button")

        # Entering the age
        age_input = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CLASS_NAME, "first__step__age__input"))
        )
        age_input.clear()
        age_input.send_keys(str(age))
        print(f"Entered age {age}")

        # Clicking on body element to proceed
        body_element = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )
        body_element.click()
        print("Clicked on body element to proceed")

        # Clicking on the calendar icon
        calendar_icon = WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.XPATH, "//img[contains(@class, 'date__input__icon__svg')]"))
        )
        driver.execute_script("arguments[0].click();", calendar_icon)
        print("Clicked on calendar icon")

        today = datetime.today().strftime('%d/%m/%Y')
        end_date = (datetime.today() + timedelta(days=period)).strftime('%d/%m/%Y')

        # Entering the start date
        start_date_input = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.ID, "datePickerStart"))
        )
        start_date_input.clear()
        for char in today:
            start_date_input.send_keys(char)
            time.sleep(0.1)
        print(f"Entered start date: {today}")

        WebDriverWait(driver, 20).until(
            EC.text_to_be_present_in_element_value((By.ID, "datePickerStart"), today)
        )
        print("Start date updated successfully")
        print("Start date input value:", start_date_input.get_attribute('value'))

        # Entering the end date
        end_date_input = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.ID, "datePickerEnd"))
        )
        end_date_input.clear()
        for char in end_date:
            end_date_input.send_keys(char)
            time.sleep(0.1)
        print(f"Entered end date: {end_date}")

        WebDriverWait(driver, 20).until(
            EC.text_to_be_present_in_element_value((By.ID, "datePickerEnd"), end_date)
        )
        print("End date updated successfully")
        print("End date input value:", end_date_input.get_attribute('value'))

        try:
            # Scrolling to 'NEXT' button
            next_button = WebDriverWait(driver, 20).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "#firstStepForm > section > div:nth-child(7) > div > div"))
            )
            driver.execute_script("arguments[0].scrollIntoView(true);", next_button)
            print("Scrolled to 'NEXT' button")

            time.sleep(2)

            # Clicking on 'NEXT' button using JavaScript
            if next_button.is_displayed() and next_button.is_enabled():
                print("NEXT button is displayed and enabled")
                driver.execute_script("arguments[0].click();", next_button)
                print("Clicked on 'NEXT' button using JavaScript")
            else:
                print("NEXT button is not clickable")
        except Exception as e:
            print(f"Could not find or click NEXT button: {e}")

        # Waiting for the request to complete
        time.sleep(5)

        # Getting cookies from the current session
        cookies_dict = get_cookies_as_dict(driver)
        cookies = '; '.join([f"{name}={value}" for name, value in cookies_dict.items()])
        print("Cookies:", cookies)

        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36',
            'Cookie': cookies,
            'Authorization': 'XXXXXXXXXX'
        }

        # Fetching data from API
        response = requests.get('https://XXXXX.globelink.eu/api/wizardData', headers=headers)
        print(f"Response Status Code: {response.status_code}")

        if response.status_code == 200:
            preloader_data = response.json()
            print("Fetched preloader data:", preloader_data)

            # Saving price data to CSV
            price_data = preloader_data.get('priceData')
            if price_data:
                save_price_data_to_csv(price_data, age, period)
            else:
                print("No priceData found, here is the fetched data for debugging:")
                print(preloader_data)
        else:
            print(f"Failed to fetch data, status code: {response.status_code}")

        try:
            # Clicking on 'Back to Trip details' button using image selector
            back_button = WebDriverWait(driver, 20).until(
                EC.element_to_be_clickable(
                    (By.CSS_SELECTOR, "#desktop__progress > div:nth-child(1) > span > span > img"))
            )
            back_button.click()
            print("Clicked on 'Back to Trip details' button using image selector")
        except Exception as e:
            print(f"Could not find or click 'Back to Trip details' button using image selector: {e}")

        time.sleep(5)  # Waiting for the previous page to load

    except Exception as e:
        print(f"An error occurred: {e}")
        return False

    finally:
        driver.quit()

    return True

# List of ages to be tested
ages = [16, 51, 66, 71, 75, 80]
# List of periods to be tested
periods = [5, 10, 17, 24, 31, 38, 45, 52, 60]
max_attempts = 2  # Maximum number of attempts per age and period

for age in ages:
    for period in periods:
        attempt = 0
        success = False

        while attempt < max_attempts and not success:
            attempt += 1
            print(f"Attempt {attempt} for age {age} and period {period}...")
            success = run_script(age, period)
            execution_time = end_time - start_time

        if not success:
            print(f"Script failed after {max_attempts} attempts for age {age} and period {period}")
        else:
            print(f"Script completed successfully for age {age} and period {period}")
