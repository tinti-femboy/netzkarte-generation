import requests
import time
import base64

from tqdm import tqdm

from utils.cookieManager import *
from utils.loadKeyFromFile import *

from datetime import datetime
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad
from Crypto.Protocol.KDF import PBKDF2

def decryptBase64String(encoded_string):
    password = get_key()
    salt = b'cryptography123example'
    iv = bytes.fromhex('a5a8d2e9c1721ae0e84ad660c472b1f3')
    iterations = 1000
    key_size_bytes = 16  

    key = PBKDF2(password, salt, dkLen=key_size_bytes, count=iterations, hmac_hash_module=None)
    ciphertext = base64.b64decode(encoded_string)
    cipher = AES.new(key, AES.MODE_CBC, iv)
    decrypted_data = unpad(cipher.decrypt(ciphertext), AES.block_size)
    decrypted_string = decrypted_data.decode('utf-8')
    return(decrypted_string)


def scrapeStandorteFreigabe(sued, west, nord, ost, downloadType="GetStandorteFreigabe", cookies=load_cookies_from_file("./assets/final-cookies.pkl")):
    
    url = f"https://www.bundesnetzagentur.de/emf-karte/Standortservice.asmx/{downloadType}"
    payload = {
        "Box": {
            "sued": float(sued),
            "west": float(west),
            "nord": float(nord),
            "ost": float(ost)
        }
    }


    
    headers = {
        'Host': 'www.bundesnetzagentur.de',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:143.0) Gecko/20100101 Firefox/143.0',
        'Accept': 'application/json',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate, br, zstd',
        'dataType': 'json',
        'Content-Type': 'application/json',
        'Content-Length': '108',
        'Origin': 'https://www.bundesnetzagentur.de',
        'Sec-GPC': '1',
        'Connection': 'keep-alive',
        'Referer': 'https://www.bundesnetzagentur.de/DE/Vportal/TK/Funktechnik/EMF/start.html/jscontent',
        
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-origin'
    }

    try:
        response = requests.post(url, json=payload, headers=headers, cookies=cookies)
        print(response.status_code)
        if response.status_code == 200:
            data = response.json()
            if data == {'d': []}:
                return
                print("no data")
            result_string = data["d"]["Result"]
            
            print(f"\nDecypted string: {decryptBase64String(result_string)}")
            return(decryptBase64String(result_string))

        else:
            print(f"Request failed with status code: {response.status_code}")
            print(f"Response body: {response.text}")

    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")


def get_initial_position_data_dump(downloadType="GetStandorteFreigabe"):
    startlngrad = 47
    startbngrad = 5

    stoplngrad = 56
    stopbngrad = 16

    with open("./assets/smallcell-standortdumps.txt", "a") as myfile:
        myfile.write(f"\nrun from {datetime.now()}\n")
        cookies_to_use = load_cookies_from_file("./assets/final-cookies.pkl")
        myfile.write(f"\n using Cookies {cookies_to_use}")
        total_iterations = (stoplngrad - startlngrad) * 10 * (stopbngrad - startbngrad) * 5
        with tqdm(total=total_iterations) as pbar:
            for lngrad in range((stoplngrad - startlngrad) * 10):
                for bngrad in range((stopbngrad - startbngrad) * 5):
                    sued = lngrad * 0.1 + startlngrad
                    west = bngrad * 0.2 + startbngrad
                    nord = sued + 0.1
                    ost = west + 0.2
                    myfile.write(f"sued: {sued}, west: {west}, nord: {nord}, ost: {ost}\n ")
                    nextToWrite = f"{scrapeStandorteFreigabe(sued, west, nord, ost, downloadType, cookies=cookies_to_use)}\n"
                    myfile.write(nextToWrite)
                    time.sleep(0.1)
                    pbar.update(1)  

if __name__ == "__main__":
    get_initial_position_data_dump("GetStandorteSmallCellFreigabe")
