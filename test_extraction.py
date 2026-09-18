"""
Standalone test: can we reliably extract article body text from the
URLs GDELT gives us? This does NOT touch collect_gdelt.py -- it's a
separate, small test before we decide on a text-retrieval strategy.

Usage:
    pip install trafilatura --break-system-packages
    python test_extraction.py
"""

import trafilatura

# Picked a text-heavy news article, not the photo essay --
# photo essays are mostly captions/images and are a bad first test.
TEST_URLS = [
    "https://www.rappler.com/philippines/visayas/what-we-know-so-far-fault-caused-cebu-earthquake-september-2025/",
    "https://www.rappler.com/philippines/visayas/death-toll-cebu-earthquake-october-2-2025/",
    "https://www.philstar.com/headlines/2025/10/02/2477014/marcos-orders-tent-city-cebu-quake-victims",
]

for url in TEST_URLS:
    print(f"\n{'=' * 60}")
    print(f"URL: {url}")
    downloaded = trafilatura.fetch_url(url)
    if downloaded is None:
        print("  -> could not fetch the page (blocked, dead link, or network issue)")
        continue

    text = trafilatura.extract(downloaded)
    if text is None:
        print("  -> page fetched, but no article text could be extracted")
        continue

    print(f"  -> extracted {len(text)} characters")
    print(f"  -> first 300 chars:\n  {text[:300]}")