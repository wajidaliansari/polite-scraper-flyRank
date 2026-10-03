import os
import requests
import time
import json
import re
from datetime import datetime, timezone
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from pydantic import BaseModel, HttpUrl, ValidationError

HEADERS = {
    "User-Agent": "FlyRankInternshipA9/1.0 (+https://github.com/yourusername/yourrepo)"
}
TIMEOUT = 10 

class BookRecord(BaseModel):
    title: str
    product_url: HttpUrl
    price_text: str
    price_gbp: float
    availability_text: str
    rating_text: str | None
    description: str | None
    source_page: HttpUrl
    fetched_at: str

def fetch_page(url, cache_filepath, report_stats):
    
    if os.path.exists(cache_filepath):
        report_stats["cache_hits"] += 1
        with open(cache_filepath, "r", encoding="utf-8") as f:
            return f.read()

    
    for attempt in range(2):
        try:
            time.sleep(0.5) 
            response = requests.get(url, headers=HEADERS, timeout=TIMEOUT)
            
            if response.status_code == 200:
                report_stats["pages_fetched"] += 1
                os.makedirs(os.path.dirname(cache_filepath), exist_ok=True)
                with open(cache_filepath, "w", encoding="utf-8") as f:
                    f.write(response.text)
                return response.text
                
            elif response.status_code in [403, 404]:
                
                print(f"Skipping {url} (Status: {response.status_code})")
                report_stats["failed_pages"] += 1
                return None
                
            elif response.status_code >= 500:
                
                if attempt == 0:
                    print(f"Server error {response.status_code}. Retrying...")
                    time.sleep(1)
                    continue
                report_stats["failed_pages"] += 1
                return None
                
        except requests.exceptions.RequestException as e:
            
            if attempt == 0:
                print(f"Request failed: {e}. Retrying...")
                time.sleep(1)
                continue
            report_stats["failed_pages"] += 1
            return None
            
    report_stats["failed_pages"] += 1
    return None

def extract_book_links(html, base_url):
    soup = BeautifulSoup(html, "html.parser")
    book_links = []
    for h3_tag in soup.find_all("h3"):
        a_tag = h3_tag.find("a")
        if a_tag and "href" in a_tag.attrs:
            book_links.append(urljoin(base_url, a_tag["href"]))
            
    next_page_url = None
    next_button = soup.select_one("li.next a")
    if next_button and "href" in next_button.attrs:
        next_page_url = urljoin(base_url, next_button["href"])
    return book_links, next_page_url

def extract_book_details(html, book_url, source_url):
    soup = BeautifulSoup(html, "html.parser")
    
    title_tag = soup.select_one("div.product_main h1")
    price_tag = soup.select_one("p.price_color")
    avail_tag = soup.select_one("p.availability")
    rating_tag = soup.select_one("p.star-rating")
    desc_tag = soup.select_one("#product_description ~ p")
    
    price_text = price_tag.text if price_tag else None
    price_gbp = None
    if price_text:
        match = re.search(r"[\d\.]+", price_text)
        if match: price_gbp = float(match.group())
        
    return {
        "title": title_tag.text if title_tag else None,
        "product_url": book_url,
        "price_text": price_text,
        "price_gbp": price_gbp,
        "availability_text": avail_tag.text.strip() if avail_tag else None,
        "rating_text": rating_tag["class"][1] if rating_tag and len(rating_tag["class"]) > 1 else None,
        "description": desc_tag.text if desc_tag else None,
        "source_page": source_url,
        "fetched_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    }

if __name__ == "__main__":
    start_time = time.time()
    
    
    run_report = {
        "start_time": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "duration_seconds": 0,
        "pages_fetched": 0,
        "cache_hits": 0,
        "valid_records": 0,
        "invalid_records": 0,
        "failed_pages": 0
    }

    current_url = "https://books.toscrape.com/catalogue/page-1.html"
    unique_books = []
    pages_visited = 0
    print("Fetching catalogue pages...")
    
    while current_url and pages_visited < 3:
        pages_visited += 1
        filename = current_url.split("/")[-1]
        cache_file = f"cache/catalogue-{filename}"
        
        html_data = fetch_page(current_url, cache_file, run_report)
        if not html_data: break
            
        books, next_url = extract_book_links(html_data, current_url)
        for book in books:
            if book not in [b[0] for b in unique_books]: 
                unique_books.append((book, current_url))
        current_url = next_url

    
    unique_books.append(("https://books.toscrape.com/catalogue/fake-broken-book_9999/index.html", "fake_source"))

    print("\nExtracting book details...")
    valid_records = []
    errors = []
    
    for book_url, source_url in unique_books:
        book_filename = book_url.split("/")[-2] + ".html"
        book_cache_file = f"cache/books/{book_filename}"
        
        html_data = fetch_page(book_url, book_cache_file, run_report)
        
        
        if html_data:
            try:
                raw_record = extract_book_details(html_data, book_url, source_url)
                validated_data = BookRecord(**raw_record)
                valid_records.append(validated_data.model_dump(mode='json'))
                run_report["valid_records"] += 1
            except ValidationError as e:
                errors.append({"url": book_url, "error": json.loads(e.json())})
                run_report["invalid_records"] += 1
        else:
            
            pass

    
    run_report["duration_seconds"] = round(time.time() - start_time, 2)
    os.makedirs("output", exist_ok=True)
    
    with open("output/books.json", "w", encoding="utf-8") as f:
        json.dump(valid_records, f, indent=4, ensure_ascii=False)
        
    if errors:
        with open("output/errors.json", "w", encoding="utf-8") as f:
            json.dump(errors, f, indent=4, ensure_ascii=False)
            
    with open("output/run-report.json", "w", encoding="utf-8") as f:
        json.dump(run_report, f, indent=4)

   
    print(f"\n--- Stage 5 Checkpoint ---")
    print(f"Valid books saved: {len(valid_records)}")
    print("Run Report:")
    print(json.dumps(run_report, indent=4))