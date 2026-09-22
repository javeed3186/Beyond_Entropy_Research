import requests

url = "https://api.gdeltproject.org/api/v2/doc/doc"

params = {
    "query": '"government shutdown" reopens',
    "mode": "artlist",
    "format": "json",
    "maxrecords": 5,
    "startdatetime": "20251112000000",
    "enddatetime": "20251119000000",
}

headers = {
    "User-Agent": "Mozilla/5.0"
}

response = requests.get(
    url,
    params=params,
    headers=headers,
    timeout=30
)

print("STATUS:", response.status_code)
print()
print("RETRY-AFTER:", response.headers.get("Retry-After"))
print()
print("ALL HEADERS:")
for key, value in response.headers.items():
    print(f"{key}: {value}")

print()
print("RESPONSE:")
print(response.text[:1000])