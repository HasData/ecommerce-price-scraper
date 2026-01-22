import requests
from bs4 import BeautifulSoup
from decimal import Decimal
import re
import json

# Configuration
API_KEY = "YOUR_HASDATA_API_KEY"
TARGET_URL = "https://demo.evershop.io/accessories/modern-ceramic-vase-green"

def scrape_price_with_fallbacks():
    """
    Implements the 'Hierarchy of Reliability':
    1. Structured Data (JSON-LD). Most stable, machine-readable.
    2. Semantic HTML (Meta Tags). Very stable, used for SEO.
    3. Data Attributes. Stable, used for internal JS logic.
    4. CSS Classes. Fragile, prone to design changes.
    """
    payload = {
        "url": TARGET_URL,
        "proxyType": "residential", 
        "proxyCountry": "US",       # Ensures currency is in USD
        "jsRendering": True,        # Essential for modern React/Vue sites
        "outputFormat": ["html"]    # We want the raw HTML to parse locally
    }

    print(f"Fetching {TARGET_URL}...")
    response = requests.post(
        "https://api.hasdata.com/scrape/web",
        headers={"x-api-key": API_KEY, "Content-Type": "application/json"},
        json=payload,
        timeout=30
    )
    
    if response.status_code != 200:
        raise ConnectionError(f"API Error: {response.status_code}")

    # Use the 'html' field from HasData response
    soup = BeautifulSoup(response.content, "html.parser")
    
    # Priority 1: JSON-LD Structured Data
    # E-commerce sites use this for Google Shopping. It rarely changes.
    json_ld = soup.find("script", {"type": "application/ld+json"})
    if json_ld:
        try:
            data = json.loads(json_ld.string)
            # JSON-LD structures vary; look for 'offers' key
            if "offers" in data:
                offer = data["offers"]
                # Handle list of offers (variants) vs single offer
                if isinstance(offer, list):
                    offer = offer[0]
                
                price_str = str(offer.get("price", ""))
                currency = offer.get("priceCurrency", "USD")
                
                if price_str:
                    print("Source: JSON-LD (Priority 1)")
                    return Decimal(price_str), currency
        except json.JSONDecodeError:
            pass
    
    # Priority 2: Semantic HTML (Schema.org microdata)
    # SEO tags like <meta itemprop="price" content="1200.00">
    price_meta = soup.find("meta", {"itemprop": "price"})
    if price_meta and price_meta.get("content"):
        currency_meta = soup.find("meta", {"itemprop": "priceCurrency"})
        currency = currency_meta.get("content", "USD") if currency_meta else "USD"
        print("Source: Meta Tags (Priority 2)")
        return Decimal(price_meta["content"]), currency
    
    # Priority 3: Common data-* attributes
    # Developers often put raw numbers in data attributes for JS calculations
    for attr in ["data-price", "data-product-price", "data-price-amount"]:
        elem = soup.find(attrs={attr: True})
        if elem:
            price_str = elem.get(attr)
            clean = re.sub(r'[^\d.]', '', price_str)
            if clean:
                print(f"Source: Attribute [{attr}] (Priority 3)")
                return Decimal(clean), "USD"
    
    # Priority 4: Class-based selectors (Fragile fallback)
    # Only use this if all above fail.
    price_selectors = [
        ".product-price", ".price-value-2", ".projected-price", ".money", ".price", ".product__single__price"
    ]
    for selector in price_selectors:
        elem = soup.select_one(selector)
        if elem:
            text = elem.get_text(strip=True)
            # Remove currency symbols and non-numeric chars
            clean = re.sub(r'[^\d.]', '', text)
            if clean:
                print(f"Source: CSS Selector [{selector}] (Priority 4)")
                return Decimal(clean), "USD"
    
    raise ValueError(f"No price found on {TARGET_URL}")

# Usage
if __name__ == "__main__":
    try:
        price, currency = scrape_price_with_fallbacks()
        print(f"Final Result: {price} {currency}")
    except Exception as e:
        print(f"Extraction failed: {e}")