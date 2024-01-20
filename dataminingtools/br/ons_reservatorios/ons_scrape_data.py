from selenium import webdriver
from bs4 import BeautifulSoup
import json
import time

# example of text: "Subsistema Sudeste / Centro-Oeste - EAR atual60,60%"
def get_percentage(text):

    percentage_str = ''

    for s in text:
        if s.isdigit() or s in [',', '%']:
            percentage_str += s

    return percentage_str



# URL of the page
url = 'https://www.ons.org.br/paginas/energia-agora/reservatorios'

# Set up the webdriver (this example uses Chrome)
browser = webdriver.Chrome()

try:
    # Navigate to the page
    browser.get(url)

    # Wait for the content to load
    time.sleep(5)  # Adjust the sleep time as needed

    # Now the page is fully loaded, get the page source
    html_content = browser.page_source
    browser.quit()

    # # Save html to a file
    # with open('output.html', 'w', encoding='utf-8') as f:
    #     f.write(html_content)

    # read html from file
    # with open('output.html', 'r', encoding='utf-8') as f:
    #     html_content = f.read()

    # import pdb; pdb.set_trace() # Start debugger

    soup = BeautifulSoup(html_content, 'html.parser')

    # Example of how to find data in the HTML structure.
    # This will vary based on the actual structure of your HTML.
    data = {}

    div1 = soup.find('div', {'id': 'reservatorios_ctl00_ctl64_g_342da078_b4ba_4aeb_af3c_19e03ab7d3f6'})

    # get text from first h1 from div1
    last_updated_html_text = div1.find('h1').text
    last_updated_date = last_updated_html_text.split(':')[1].strip()
    data['last_updated'] = last_updated_date

    regions = []
    for region in soup.find_all('div', {'class': 'box'}):
        region_name = region.find('h5').text
        region_percentage = get_percentage(region_name)
        region_name = region_name.replace(region_percentage, '').strip()
        print("Region: ", region_name, "Percentage: ", region_percentage)
        EAR_current = region_percentage

        if region_name == 'Capacidade máxima de armazenamento MWmês':
            continue

        basins = []
        for basin in region.find_all('div', {'class': 'bacia'}):
            all_spans = basin.find('div', {'class': 'titulo'}).find_all('span')
            basin_name = all_spans[0].text
            percentage_of_subsystem = all_spans[1].text.replace(' do subsistema*', '')
            print("Basin: ", basin_name, "Percentage: ", percentage_of_subsystem)

            reservoirs = []
            div_reservoir = basin.find('div', {'class': 'reservatorio'})
            if div_reservoir:
                for reservoir in div_reservoir.find_all('li'):
                    all_reservoir_span = reservoir.find_all('span')
                    reservoir_name = all_reservoir_span[0].text
                    current_useful_volume = all_reservoir_span[1].text.replace(' do subsistema*', '')
                    reservoirs.append({'name': reservoir_name, 'current_useful_volume': current_useful_volume})

            basins.append({'name': basin_name, 'percentage_of_subsystem': percentage_of_subsystem, 'reservoirs': reservoirs})

        regions.append({'name': region_name, 'EAR_current': EAR_current, 'basins': basins})

    data['regions'] = regions

    # Convert data to JSON
    json_data = json.dumps(data, indent=4, ensure_ascii=False)

    # Save the JSON data to a file
    with open('output.json', 'w', encoding='utf-8') as f:
        f.write(json_data)

    print("Data extracted and saved to JSON.")
except Exception as e:
    print("Error occurred while scraping the page: ", e)
    browser.quit()
