import os

def load_cookies_from_file(filename="assets/cookies.txt"):
    """
    Reads a string of cookies separated by semicolons from a file
    and returns a dictionary of cookies.
    """
    cookies_dict = {}
    try:
        if not os.path.exists(filename):
            print(f"Error: The file '{filename}' was not found.")
            return None

        with open(filename, 'r') as f:
            cookie_string = f.read().strip()

        cookie_parts = cookie_string.split(';')
        for part in cookie_parts:
            if '=' in part:
                name, value = part.strip().split('=', 1)
                cookies_dict[name] = value

    except Exception as e:
        print(f"An error occurred while reading the cookie file: {e}")
        return None

    return cookies_dict