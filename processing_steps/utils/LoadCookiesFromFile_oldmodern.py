import os

def load_cookies_from_file():
    try:
        with open('cookies.txt', 'r') as f:
            cookies_str = f.read()
            cookies = eval(cookies_str)  # Convert string representation of dict back to dict
            print(f"Loaded cookies: {cookies}")
            return cookies
    except FileNotFoundError:
        print("Cookies file not found. Please run generate_session() first.")
        return None
    except Exception as e:
        print(f"An error occurred while loading cookies: {e}")
        return None

if __name__ == "__main__":
    cookies = load_cookies_from_file()
    print(cookies)