from dataminingtools.basic.browserdrivertools import download_html
from bs4 import BeautifulSoup


def scrape_paper_bibtex(sbc_paper_view_url):
    html_content = download_html(sbc_paper_view_url) #, use_backup_html='sbc_paper_view.html')
    soup = BeautifulSoup(html_content, 'html.parser')
    bibtex_page_url = soup.find('li', {'class': 'BibtexCitationPlugin'}).find('a')['href']
    print(bibtex_page_url)
    bibtex_html_content = download_html(bibtex_page_url) #, use_backup_html='bibtex_page.html')
    bibtex_soup = BeautifulSoup(bibtex_html_content, 'html.parser')
    bibtex = bibtex_soup.find('textarea').text

    return bibtex

if __name__ == '__main__':
    # URL of the page
    url = input('Url of target SBC paper: ')
    url = url.strip()
    # url = "https://sol.sbc.org.br/index.php/sbie/article/view/26808"

    bibtex = scrape_paper_bibtex(url)
    print(bibtex)
