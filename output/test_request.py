import requests

def main():
    try:
        response = requests.get("https://www.google.com", timeout=10)
        print(f"Status code: {response.status_code}")
        if response.ok:
            print("Request successful!")
        else:
            print("Request failed.")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
