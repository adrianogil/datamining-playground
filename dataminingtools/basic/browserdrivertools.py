
from selenium import webdriver
import time


def download_html(url):
    html_content = None

    # Set up the webdriver (this example uses Chrome)
    browser = webdriver.Chrome()

    try:
        # Navigate to the page
        browser.get(url)

        # Wait for the content to load
        time.sleep(5)  # Adjust the sleep time as needed

        # Now the page is fully loaded, get the page source
        html_content = browser.page_source
    except Exception as e:
        print("Error occurred while scraping the page: ", e)
        browser.quit()

    return html_content