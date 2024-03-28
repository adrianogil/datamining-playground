from dataminingtools.basic.browserdrivertools import download_html

from bs4 import BeautifulSoup
import json
import os

def scrape_proceedings(url):

    base_url = url.replace('index.html', '')

    # html_content = download_html(url)

    # # Save html to a file
    # with open('output.html', 'w', encoding='utf-8') as f:
    #     f.write(html_content)

    # read html from file
    with open('output.html', 'r', encoding='utf-8') as f:
        html_content = f.read()

    # import pdb; pdb.set_trace() # Start debugger

    soup = BeautifulSoup(html_content, 'html.parser')

    data = {}

    current_issue_title = soup.find('main', {'class': 'proceedings-contents'}).find('h1').text.strip()
    data["current_issue_title"] = current_issue_title
    print(current_issue_title)

    papers_data = []

    for proceeding_list in soup.find_all('ul', {'class': 'proceedings-list'}):
        for article_div in proceeding_list.find_all('li'):

            proceedings_title_authors_div = article_div.find('div', {'class': 'proceedings-title-authors'})
            title_link_a = proceedings_title_authors_div.find('a', {'class': 'title-link'})

            paper_data = {}
            paper_title = title_link_a.text.strip()
            print("Title: ", paper_title)
            paper_data["title"] = paper_title

            paper_link = title_link_a['href'].replace('./', base_url)
            print("Link: ", paper_link)
            paper_data["link"] = paper_link

            paper_authors = proceedings_title_authors_div.text.split("|")
            paper_authors = [author.replace(paper_title, "").strip() for author in paper_authors]
            print("Authors: ", paper_authors)
            paper_data["authors"] = paper_authors

            proceedings_extras_div = article_div.find('div', {'class': 'proceedings-extras'})

            paper_pdf_link = proceedings_extras_div.find('a', {'class': 'pdf-link'})['href'].replace('./', base_url)
            print("PDF link: ", paper_pdf_link)
            paper_data["pdf_link"] = paper_pdf_link

            paper_doi_link = proceedings_extras_div.find('a', {'class': 'doi-link'})['href'].replace('./', base_url)
            print("DOI link: ", paper_doi_link)
            paper_data["doi_link"] = paper_doi_link

            paper_bib_link = proceedings_extras_div.find('a', {'class': 'bib-link'})['href'].replace('./', base_url)
            print("Bib link: ", paper_bib_link)
            paper_data["bib_link"] = paper_bib_link

            # Download BibTex content
            bibtex_html_content = download_html(paper_bib_link, load_pause_time=0)
            bib_soup = BeautifulSoup(bibtex_html_content, 'html.parser')
            bibtex_content = bib_soup.find('pre').text
            paper_data["bibtx"] = bibtex_content

            print()

            papers_data.append(paper_data)

    data["papers"] = papers_data

    # Convert data to JSON
    json_data = json.dumps(data, indent=4, ensure_ascii=False)

    # Save the JSON data to a file
    with open('output.json', 'w', encoding='utf-8') as f:
        f.write(json_data)

    print("Data extracted and saved to JSON.")


if __name__ == "__main__":
    url = "https://educationaldatamining.org/EDM2023/proceedings/index.html"
    scrape_proceedings(url)
