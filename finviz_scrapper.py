import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from loguru import logger
import time
import pickle
import datetime
import argparse


def login(driver, email, password):
    driver.get("https://finviz.com/login.ashx")

    # Wait for the login page to load completely
    wait = WebDriverWait(driver, 120)
    wait.until(EC.presence_of_element_located((By.NAME, "email")))

    # Enter login credentials
    email_field = driver.find_element(By.NAME, "email")
    password_field = driver.find_element(By.NAME, "password")
    login_button = driver.find_element(By.XPATH, "//input[@value='Log in']")

    email_field.send_keys(email)  
    password_field.send_keys(password)        
    login_button.click()

    # Wait for the main page to load after login
    wait.until(EC.presence_of_element_located((By.ID, "account-dropdown")))
    
    driver.get("https://finviz.com/login.ashx")
    # Save cookies to a file
    with open("login_credentials/cookies.pkl", "wb") as file:
        pickle.dump(driver.get_cookies(), file)


def load_cookies(driver):
    driver.get("https://finviz.com/login.ashx")
    with open("login_credentials/cookies.pkl", "rb") as file:
        cookies = pickle.load(file)
        for cookie in cookies:
            driver.add_cookie(cookie)
    driver.refresh()


def attempt_login(driver, email, password):
    try:
        # Check if cookies file exists
        if os.path.exists("login_credentials/cookies.pkl"):
            load_cookies(driver)
            logger.success("Logged in with cookies.")
        else:
            raise FileNotFoundError("Cookies file does not exist.")
    except Exception as e:
        logger.error(f"Failed to log in with cookies: {e}. Retrying with credentials.")
        login(driver, email, password)
        logger.success("Logged in with credentials.")


def main():
    # Set up argument parser
    parser = argparse.ArgumentParser(description="Scrape data from Finviz screener.")
    parser.add_argument("--url", required=False, default="https://elite.finviz.com/screener.ashx?v=152&p=i1&f=cap_0.01to,geo_usa|china|france|europe|australia|belgium|canada|chinahongkong|germany|hongkong|iceland|japan|newzealand|ireland|netherlands|norway|singapore|southkorea|sweden|taiwan|unitedarabemirates|unitedkingdom|switzerland|spain,sh_curvol_o100,sh_relvol_o1,ta_change_u&ft=4&o=sharesfloat&ar=10&c=0,1,2,5,6,25,26,27,28,29,30,84,45,50,51,68,60,61,63,64,67,65,66", help="The screener URL")
    parser.add_argument("--username", required=False, default="-", help="Your username")
    parser.add_argument("--password", required=False, default="-", help="Your password")
    parser.add_argument("--driver-path", required=False, default="/usr/local/bin/chromedriver", help="Path to chromedriver")
    args = parser.parse_args()

    chrome_options = Options()
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")

    # Set the download directory
    current_directory = os.path.abspath(os.getcwd())
    output_directory = os.path.abspath(os.path.join(current_directory, "data/finviz"))

    prefs = {
        "download.default_directory": output_directory,
        "download.prompt_for_download": False,
        "download.directory_upgrade": True,
        "safebrowsing.enabled": True
    }
    chrome_options.add_experimental_option("prefs", prefs)

    driver_path = args.driver_path
    service = Service(driver_path)
    driver = webdriver.Chrome(service=service, options=chrome_options)

    email = args.username
    password = args.password

    attempt_login(driver, email, password)

    driver.get(args.url)

    wait = WebDriverWait(driver, 50)
    wait.until(EC.presence_of_element_located((By.ID, "screener-content")))
    logger.info("Screener loaded.")

    before_download = set(os.listdir(output_directory))
    downloaded_files = {}
    retry_no = 1

    try:
        while len(downloaded_files) == 0 : 
            export_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//a[contains(@href, 'export.ashx')]")))
            actions = ActionChains(driver)
            actions.move_to_element(export_button).click().perform()
            logger.info("Export button clicked.")
            # Sleep to allow time for download to complete
            time.sleep(5)
            # List all files in the directory after download
            after_download = set(os.listdir(output_directory))
            downloaded_files = after_download - before_download
            
            if len(downloaded_files) >= 1:
                downloaded_file = downloaded_files.pop()
                # Rename the downloaded file with current date and time
                current_time = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
                new_file_name = f"finviz_data_{current_time}.csv"
                old_file_path = os.path.join(output_directory, downloaded_file)
                new_file_path = os.path.join(output_directory, new_file_name)
                os.rename(old_file_path, new_file_path)
                logger.info(f"File renamed to: {new_file_name}")
                logger.success(f"Files downloaded to: {output_directory}")
                break
            else:
                logger.error("Download failed or multiple files downloaded.")
                if retry_no == 6:
                    print("Retried 5 times and failed.")
                    break
                logger.warning(f"Retrying... [{retry_no}/5]")
                retry_no = retry_no = retry_no + 1
                
    except Exception as e:
        logger.error("Failed to find the export button:", e)

    # Close the browser
    driver.quit()


if __name__ == "__main__":
    main()