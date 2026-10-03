# The Polite Scraper (Python Lane)

## Target Classification
* **Target Site:** books.toscrape.com
* **Reason:** It is a public practice sandbox built exactly for people to practice scraping.
* **Scope:** The first 3 catalogue pages only (60 books).
* **Data Collected:** Book title, product URL, price, availability, rating, and description.
* **Appropriateness:** Since the site is a dedicated sandbox, collecting this small amount of data is perfectly appropriate.
* **Robots.txt:** Checked `https://books.toscrape.com/robots.txt` - No robots file found (Status 404).

*I will not reuse this code on another site without checking its rules and terms first.*

## How to Install and Run
This project uses Python.
1. Create a virtual environment and activate it.
2. Install the requirements:
   ```bash
   pip install requests beautifulsoup4 pydantic

## Run the scraper: 
python src/main.py

## Politeness Rules Followed
User-Agent: Sends a custom, identifying User-Agent with a GitHub link.

Delay: Waits 0.5 seconds between real requests to the server.

Timeout: Implements a 10-second timeout on all requests.

Caching: Saves all HTML locally. Reruns read entirely from the cache/ folder instead of hitting the live server.

Failure Handling: Retries 5xx server errors once, but skips 404/403 pages without retrying.

## Record Schema
Validated using Pydantic:

title (string)

product_url (url)

price_text (string)

price_gbp (float)

availability_text (string)

rating_text (string or null)

description (string or null)

source_page (url)

fetched_at (ISO 8601 timestamp)

## Limitations
This scraper is hardcoded to stop after 3 catalogue pages.

It relies on the exact current HTML structure of books.toscrape.com. If the site changes its class names, the CSS selectors will break

## Browser Explanation
This assignment needed no browser (like Selenium or Playwright) because all the required data is fully present in the raw HTML returned by the server. Using a headless browser would only add unnecessary memory cost and slow down the execution.

## Ethics Note
Always check a site's terms and robots.txt before scraping. If an official API exists, use it instead. Never bypass logins, paywalls, or blocks, and only collect the data you strictly need.

## Sample Run Report

{
    "start_time": "2026-10-03T15:35:08.095665Z",
    "duration_seconds": 3.6,
    "pages_fetched": 0,
    "cache_hits": 63,
    "valid_records": 60,
    "invalid_records": 0,
    "failed_pages": 1
}