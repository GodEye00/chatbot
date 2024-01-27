
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse
import os

def get_domain(url):
    """Extract the domain of a URL."""
    parsed_url = urlparse(url)
    return f"{parsed_url.scheme}://{parsed_url.netloc}"

def is_image_url(url):
    """Check if a URL points to an image."""
    image_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.svg']
    return any(url.lower().endswith(ext) for ext in image_extensions)

def get_all_links(url, domain, visited=set()):
    """Crawl a website and return all unique links."""
    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.content, "html.parser")
        print(url)
        for link in soup.find_all("a", href=True):
            href = link['href']

            if href.startswith(domain) and not is_image_url(href) and href not in visited:
                visited.add(href)
                get_all_links(href, domain, visited)

    except requests.exceptions.RequestException:
        pass  # or you can log the error if you want

    return visited

def extract_data(url):
    """Extract data from a page and return as a string."""
    data = ""
    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.content, "html.parser")
        # Implement your data extraction logic here
        data = soup.get_text()
    except requests.exceptions.RequestException:
        pass  # or you can log the error if you want

    return data

def safe_filename(url):
    """Create a safe filename from a URL."""
    return url.replace('http://', '').replace('https://', '').replace('/', '_').replace(':', '_')


# URL to start crawling
start_url = "https://itconsortiumgh.com"

# Create a directory to store the files
os.makedirs("extracted_pages", exist_ok=True)

# Get all links
domain = get_domain(start_url)
all_links = get_all_links(start_url, domain)

# Extract data and write to separate text files
for link in all_links:
    page_data = extract_data(link)
    filename = safe_filename(link) + ".txt"
    file_path = os.path.join("extracted_pages", filename)
    with open(file_path, 'w', encoding='utf-8') as file:
        file.write(f"Data scraped from: {link}\n\n\n"+page_data)
