
from selenium import webdriver
import time


def download_html(url, load_pause_time=5):
    html_content = None

    # Set up the webdriver (this example uses Chrome)
    browser = webdriver.Chrome()

    try:
        # Navigate to the page
        browser.get(url)

        # Wait for the content to load
        if load_pause_time > 0:
            time.sleep(load_pause_time)  # Adjust the sleep time as needed

        # Now the page is fully loaded, get the page source
        html_content = browser.page_source
    except Exception as e:
        print("Error occurred while scraping the page: ", e)
        browser.quit()

    return html_content