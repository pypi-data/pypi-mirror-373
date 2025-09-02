import time
import os
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By



def login_to_draftkings(driver, username=None, password=None):
    if not username:
        username = os.environ['DK_USERNAME']
    if not password:
        password = os.environ['DK_PASSWORD']
        
    url = "https://www.draftkings.com/account/sitelogin/false?returnurl=%2Flobby"
    driver.get(url)
    WebDriverWait(driver, 30).until(
        EC.presence_of_element_located((By.NAME, 'EmailOrUsername'))
    )

    username_btn = driver.find_element_by_name('EmailOrUsername')
    password_btn = driver.find_element_by_name('Password')

    submit_btn = driver.find_element_by_id('login-submit')

    username_btn.send_keys(username)
    password_btn.send_keys(password)
    submit_btn.click()
    print('logging in, waiting to see html class: site-nav-list')

    WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.CLASS_NAME, 'site-nav-list'))
    )
    print('Success')
