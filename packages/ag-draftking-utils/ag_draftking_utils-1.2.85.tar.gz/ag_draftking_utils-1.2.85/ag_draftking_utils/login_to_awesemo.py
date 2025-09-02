import os
import time
import logging
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

USERNAME = os.environ.get('AWESEMO_USERNAME', '')
PASSWORD = os.environ.get('AWESEMO_PASSWORD', '')


def click_login_button(driver):
    login_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CLASS_NAME, 'mvp-login-button'))
        )
    login_button.click()


def login_to_awesemo(driver, username=USERNAME, password=PASSWORD, logger=None):

    try:
        click_login_button(driver)
        logging.info('Clicked Login Button')
    except:
        close_ad_button(driver)
        click_login_button(driver)

    username_btn = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, 'user_login'))
    )
    logging.info('Found username buttons')
    password_btn = driver.find_element_by_id('user_pass')
    submit_btn = driver.find_element_by_name('submit')

    username_btn.send_keys(username)
    password_btn.send_keys(password)
    logging.info('Sent username and password to site')
    try:
        submit_btn.click()
        logging.info('Clicked submit button')
    except:
        close_ad_button(driver)
        submit_btn.click()
    if logger:
        logger.info('Successfully logged in')
    else:
        logging.info('Successfully logged in')


def close_ad_button(driver, logger=None, ad_button_class='advads-close-button'):
    """Sometimes ad button is present, othertimes not"""
    ad_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.CLASS_NAME, ad_button_class))
    )
    ad_button.click()
    if logger:
        logger.info('Successfully located ad button, and closed it')


def close_march_28_ad(driver):
    """Leave this in for historical context"""
    btn = driver.find_element_by_css_selector("[title='Close']")
    btn.click()
    time.sleep(3)
