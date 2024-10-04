import requests
from bs4 import BeautifulSoup
import chromadb


def get_links(url, keyword):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    links = soup.find_all('a', href=True)
    results = []
    for link in links:
        title = link.get_text(strip=True)
        href = link['href']
        if keyword in href:
            full_url = href if href.startswith('http') else url + href
            results.append((title, full_url))
    return results
    

def get_page(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    article_header = soup.find('div', class_='article-heading')
    article_content = soup.find('div', class_='content')
    if article_header is None or article_content is None:
        return ""

    content = article_header.get_text(strip=True) + '\n' + article_content.get_text(strip=True)
    return content


def make_vector_db(contents):
    chroma_client = chromadb.PersistentClient("/Users/kamielfokkink/Documents/Kansha/Zerodha/database/")
    collection = chroma_client.create_collection(name="zerodhadb")
    collection.add(
        documents=list(contents.values()),
        ids=list(contents.keys())
    )


if __name__ == '__main__':
    url = "https://support.zerodha.com"
    home_links = get_links(url, 'category')
    content_pages = set()
    for _, link in home_links:
        page_links = get_links(link, 'article')
        content_pages.update({t[1] for t in page_links})

    contents = {}
    for i, page in enumerate(list(content_pages)):
        if i % 10 == 0:
            print(f"{(i / len(content_pages)) * 100:.2f}% done")
        contents[page] = get_page(page)
    unique_contents = {k: v for k, v in contents.items() if list(contents.values()).count(v) == 1}

    make_vector_db(contents)

    