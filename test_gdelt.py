import requests

url = "https://api.gdeltproject.org/api/v2/doc/doc"

params = {
    "query": '"Cebu earthquake"',
    "mode": "artlist",
    "format": "json",
    "maxrecords": 20,
    "startdatetime": "20250930000000",
    "enddatetime": "20251007000000"
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
print("CONTENT TYPE:", response.headers.get("content-type"))
print()
print(response.text[:2000])