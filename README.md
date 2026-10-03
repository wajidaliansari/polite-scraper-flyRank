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