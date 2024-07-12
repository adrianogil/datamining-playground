
from selenium import webdriver
import time
import os


def download_html(url, load_pause_time=5, use_backup_html=None):
    html_content = None

    if use_backup_html and os.path.exists(use_backup_html):
        with open(use_backup_html, 'r', encoding='utf-8') as f:
            html_content = f.read()
        return html_content

    try:
        # Set up the webdriver (this example uses Chrome)
        browser = webdriver.Chrome()

        # Navigate to the page
        browser.get(url)

        # Wait for the content to load
        if load_pause_time > 0:
            time.sleep(load_pause_time)  # Adjust the sleep time as needed

        # Now the page is fully loaded, get the page source
        html_content = browser.page_source

        if use_backup_html:
            with open(use_backup_html, 'w', encoding='utf-8') as f:
                f.write(html_content)
    except Exception as e:
        print("Error occurred while scraping the page: ", e)
        browser.quit()

    return html_content