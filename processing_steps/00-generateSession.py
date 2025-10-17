import requests
import pickle
from utils.cookieManager import *

def generate_session():
    headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:143.0) Gecko/20100101 Firefox/143.0',
    'Accept': '*/*',
    'Accept-Language': 'en-US,en;q=0.5',
    'Accept-Encoding': 'gzip, deflate, br, zstd',
    'Referer': 'https://bundesnetzagentur.de/DE/Vportal/TK/Funktechnik/EMF/start.html/jscontent',
    'Sec-GPC': '1',
    'Connection': 'keep-alive',
    'Sec-Fetch-Dest': 'script',
    'Sec-Fetch-Mode': 'no-cors',
    'Sec-Fetch-Site': 'same-origin',
    'Priority': 'u=4',
    'Pragma': 'no-cache',
    'Cache-Control': 'no-cache'
    }
    response = requests.get('https://www.bundesnetzagentur.de/DE/Vportal/TK/Funktechnik/EMF/start.html', headers=headers)
    print(response)
    write_cookies_to_file(response.cookies)


def generate_key_from_session():
    url = 'https://www.bundesnetzagentur.de/emf-karte/js.asmx/jscontent'
    params = {
        'set': 'gsb2021'
    }

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:143.0) Gecko/20100101 Firefox/143.0',
        'Accept': '*/*',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate, br, zstd',
        'Referer': 'https://bundesnetzagentur.de/DE/Vportal/TK/Funktechnik/EMF/start.html/jscontent',
        'Sec-GPC': '1',
        'Connection': 'keep-alive',
        'Sec-Fetch-Dest': 'script',
        'Sec-Fetch-Mode': 'no-cors',
        'Sec-Fetch-Site': 'same-origin',
        'Priority': 'u=4',
        'Pragma': 'no-cache',
        'Cache-Control': 'no-cache'
    }

    filename = '../assets/jscontent.js'

    try:

        print(f"Requesting data from {url}...")
        response = requests.get(url, params=params, headers=headers, cookies=load_cookies_from_file("../assets/initial-cookies.pkl"))
        response.raise_for_status()
        print("Request successful. Status code:", response.status_code)

        with open(filename, 'w', encoding='utf-8') as f:
            f.write(response.text)

        print(f"Successfully downloaded and saved content to '{filename}'")
        write_cookies_to_file(response.cookies, "../assets/final-cookies.pkl")
        print(response.cookies)

    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

        

if __name__ == "__main__":
    generate_session()
    generate_key_from_session()