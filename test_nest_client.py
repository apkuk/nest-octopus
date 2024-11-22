# test_nest_client.py
from nest_client import NestClient

def test_auth():
    client = NestClient()
    if client.credentials and client.credentials.valid:
        print("Credentials loaded successfully.")
    else:
        print("Failed to load credentials.")

if __name__ == "__main__":
    test_auth()