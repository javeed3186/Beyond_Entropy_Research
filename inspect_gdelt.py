import json

file = "data/raw/online/E005_gdelt.json"

with open(file, "r", encoding="utf-8") as f:
    data = json.load(f)

articles = data.get("articles", [])

print("Number of articles:", len(articles))
print()

for i, article in enumerate(articles, 1):
    print(f"{i}. {article.get('title')}")
    print(f"   Source: {article.get('domain')}")
    print(f"   Date:   {article.get('seendate')}")
    print(f"   URL:    {article.get('url')}")
    print()