import os
import pickle

def write_cookies_to_file(cookies, path='./assets/initial-cookies.pkl'):
    try:
        with open(path, 'wb') as f:
            pickle.dump(cookies, f)
            print(f"Cookies saved to {path}")
    except Exception as e:
        print(f"An error occurred while saving cookies: {e}")
    
    
def load_cookies_from_file(path='./assets/initial-cookies.pkl'):
    try:
        with open(path, 'rb') as f:
            cookies = pickle.load(f)  # Convert representation of dict back to dict
            print(f"Successfully loaded cookies: {cookies}")
            return cookies
    except FileNotFoundError:
        print("Cookies file not found. Run generate_session() first.")
        return None
    except Exception as e:
        print(f"An error occurred while loading cookies: {e}")
        return None

if __name__ == "__main__":
    cookies = load_cookies_from_file()
    print(cookies)