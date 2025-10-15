import requests
import pickle
from bs4 import BeautifulSoup
from urllib.parse import urljoin

# Use a Session object to persist cookies across requests
session = requests.Session()

# Set a browser-like User-Agent header
session.headers.update({
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
})

# The starting URL
base_url = 'https://www.bundesnetzagentur.de/DE/Vportal/TK/Funktechnik/EMF/start.html'

try:
    # 1. Download the main HTML page
    print(f"Fetching main HTML from {base_url}...")
    response = session.get(base_url)
    response.raise_for_status()

    # 2. Parse the HTML to find linked resources (CSS, JS)
    soup = BeautifulSoup(response.text, 'html.parser')

    # Find all <script> tags with a 'src' attribute
    for script_tag in soup.find_all('script', src=True):
        script_url = urljoin(base_url, script_tag['src'])
        print(f"  - Downloading script: {script_url}")
        session.get(script_url) # The session automatically handles cookies

    # Find all <link> tags for stylesheets
    for link_tag in soup.find_all('link', rel='stylesheet', href=True):
        css_url = urljoin(base_url, link_tag['href'])
        print(f"  - Downloading CSS: {css_url}")
        session.get(css_url) # The session automatically handles cookies

    # 3. After all requests, the session object holds the cookies
    cookies = session.cookies.get_dict()
    print(f"\nFound {len(cookies)} cookies.")

    # 4. Save the cookies to a file
    with open('cookies.pkl', 'wb') as file:
        pickle.dump(cookies, file)

    print("Successfully saved cookies to cookies.pkl")

except requests.exceptions.RequestException as e:
    print(f"An error occurred: {e}")
