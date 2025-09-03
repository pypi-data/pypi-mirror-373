import random

domain = "https://www.google.com"
cookie_name = "zx"
payload_length = 4000

def make_payload():
    payload = ""
    for i in range(payload_length):
        payload += f"{random.randint(1, 9)}"
    return f"{domain}/?{cookie_name}={payload}"

if __name__ == "__main__":
    print(make_payload())