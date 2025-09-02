import os
from selenium import webdriver
import boto3
from selenium.webdriver import Remote, DesiredCapabilities

PROXY_USERNAME = os.environ.get('PROXY_USERNAME', '')
PROXY_PASSWORD = os.environ.get('PROXY_PASSWORD', '')
PROXY_HOST = os.environ.get('PROXY_HOST', '')
PROXY_PORT = os.environ.get('PROXY_PORT', '')


def get_driver(option='cloud',
               projectArn=os.environ['DEVICE_FARM_SCRAPER_ARN'],
               expiresInSeconds=360,
               username=PROXY_USERNAME,
               password=PROXY_PASSWORD,
               port=PROXY_PORT,
               host=PROXY_PORT):
    if option == 'cloud':
        # hardcoded to us-west-2 since devicefarm only functions there
        devicefarm_client = boto3.client('devicefarm', region_name='us-west-2', verify=False)
        testgrid_url_response = devicefarm_client.create_test_grid_url(
            projectArn=projectArn,
            expiresInSeconds=expiresInSeconds
        )

        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_extension('proxy_auth_plugin.zip')
        desired_capabilities = DesiredCapabilities.CHROME
        desired_capabilities['platform'] = 'windows'
        return Remote(testgrid_url_response['url'], desired_capabilities, options=chrome_options)

    elif option == 'cloud_noproxy':
        # hardcoded to us-west-2 since devicefarm only functions there
        devicefarm_client = boto3.client('devicefarm', region_name='us-west-2', verify=False)
        testgrid_url_response = devicefarm_client.create_test_grid_url(
            projectArn=projectArn,
            expiresInSeconds=expiresInSeconds
        )
        desired_capabilities = DesiredCapabilities.CHROME
        desired_capabilities['platform'] = 'windows'
        return Remote(testgrid_url_response['url'], desired_capabilities)

    elif option == 'local':
        return webdriver.Chrome()
    elif option == 'proxy_local':
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_extension('proxy_auth_plugin.zip')
        return webdriver.Chrome(options=chrome_options)

    elif option == 'headless':
        from seleniumwire import webdriver as webdriver_wire
        options = {
            'proxy': {
                'http': f'http://{username}:{password}@{host}:{port}',
                'https': f'https://{username}:{password}@{host}:{port}',
                'no_proxy': 'localhost,127.0.0.1'  # excludes
            }
        }
        chrome_options = webdriver_wire.ChromeOptions()
        chrome_options.add_argument('--headless')
        browser = webdriver_wire.Chrome(seleniumwire_options=options, options=chrome_options)
        return browser

    else:
        raise Exception(f'Only "cloud", "local", and "cloud_noproxy" are currently supported')