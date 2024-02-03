from dataminingtools.basic.browserdrivertools import download_html

from bs4 import BeautifulSoup
import json

# URL of the page
url = input('Url of target SBC proceedings: ')
url = url.strip()

html_content = download_html(url)

# Save html to a file
# with open('output.html', 'w', encoding='utf-8') as f:
#     f.write(html_content)

# read html from file
# with open('output.html', 'r', encoding='utf-8') as f:
#     html_content = f.read()

# import pdb; pdb.set_trace() # Start debugger

soup = BeautifulSoup(html_content, 'html.parser')

data = {}

current_issue_title_div = soup.find('div', {'class': 'current_issue_title'})
if not current_issue_title_div:
    current_issue_title_div = soup.find('nav', {'class': 'cmp_breadcrumbs'}).find('li', {'class': 'current'})
current_issue_title = current_issue_title_div.text.strip()
data["current_issue_title"] = current_issue_title
print(current_issue_title)

papers_data = []
for article_div in soup.find_all('div', {'class': 'obj_article_summary'}):
    paper_data = {}
    paper_title = article_div.find('div', {'class': 'title'}).text.strip()
    print("Title: ", paper_title)
    paper_data["title"] = paper_title

    paper_link = article_div.find('div', {'class': 'title'}).find('a')['href']
    print("Link: ", paper_link)
    paper_data["link"] = paper_link

    paper_authors = article_div.find('div', {'class': 'authors'}).text.strip().split(',')
    paper_authors = [author.strip() for author in paper_authors]
    print("Authors: ", paper_authors)
    paper_data["authors"] = paper_authors

    paper_pages = article_div.find('div', {'class': 'pages'}).text.strip()
    print("Pages: ", paper_pages)
    paper_data["pages"] = paper_pages

    paper_pdf_link = article_div.find('a', {'class': 'obj_galley_link pdf'})['href']
    print("PDF link: ", paper_pdf_link)
    paper_data["pdf_link"] = paper_pdf_link

    print()

    papers_data.append(paper_data)

data["papers"] = papers_data

# Convert data to JSON
json_data = json.dumps(data, indent=4, ensure_ascii=False)

# Save the JSON data to a file
with open('output.json', 'w', encoding='utf-8') as f:
    f.write(json_data)

print("Data extracted and saved to JSON.")
