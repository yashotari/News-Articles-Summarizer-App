import os.path
import pandas as pd
from bs4 import BeautifulSoup
from newspaper import Article
import requests
from categorize_text import classify_text_domain

visited_links = {}  # Dictionary to track visited links and their domains

def categorize_articles_new(domain_links):
    domain_lists = {
        'India': [],
        'World': [],
        'Business': [],
        'Technology': [],
        'Sports': []
    }

    for domain, link_list in domain_links.items():
        for url in link_list:
            response = requests.get(url)
            web_page = response.text
            soup = BeautifulSoup(web_page, 'html.parser')
            for article_tag in soup.find_all('a', href=True):
                link = article_tag['href']
                if link.startswith("https://timesofindia.indiatimes.com/") and "articleshow" in link:
                    if any(domain in url for domain in link_list):
                        if link not in visited_links:
                            try:
                                visited_links[link] = domain
                                domain_lists[domain].append(link)  # Append the link to the respective domain list
                                print(link, " is ", domain) 
                            except Exception as e:
                                print(f"Error downloading article from {link}  : {e}\n")
                                continue

    return domain_lists

