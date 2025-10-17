def get_key():
    search_str = 'c=CryptoJS.enc.Utf8.parse(\"'
    with open('./assets/jscontent.js', 'r') as f:
        content = f.read()

    idx = content.find(search_str)
    if idx != -1:
        start = idx + len(search_str)
        next_12 = content[start:start+12]
        return next_12
    else:
        print("Fatal error: Key not found in jscontent.js")
        raise ValueError("Key not found in jscontent.js")
    
if __name__ == "__main__":
    print(get_key())