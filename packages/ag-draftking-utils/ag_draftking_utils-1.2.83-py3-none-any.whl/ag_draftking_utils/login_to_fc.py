import os
import time
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

USERNAME = os.environ['FC_USERNAME']
PASSWORD = os.environ['FC_PASSWORD']


def click_login_button(driver):
    login_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CLASS_NAME, 'mvp-login-button'))
        )
    login_button.click()


def login_to_fc(driver, username=USERNAME, password=PASSWORD, logger=None):
    try:
        driver.get('https://www.fantasycruncher.com/login?referer=/')
        time.sleep(2)
    except Exception as e:
        print(e)

    username_btn = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, 'user_email'))
    )
    print('Found username buttons')
    password_btn = driver.find_element_by_id('user_password')
    submit_btn = driver.find_element_by_id('submit')

    username_btn.send_keys(username)
    password_btn.send_keys(password)
    print('Sent username and password to site')
    submit_btn.click()
    print('Clicked submit button')
