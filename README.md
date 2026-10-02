# Price Scraping Toolkit

![Python 3.11 or newer badge](https://img.shields.io/badge/python-3.11+-blue)

[![HasData, the web scraping API behind the proxy and AI examples](banner.png)](https://hasdata.com/?utm_source=github&utm_medium=syndication&utm_campaign=price-scraping&utm_content=ecommerce-price-scraper-readme)

Eight Python scripts for extracting, normalizing, and monitoring e-commerce pricing data. Each one is a standalone example around a single failure mode of price scraping.

## Features

- **Multi-locale price normalization** (US/EU formats)
- **Marketing noise removal** ("Was $X", "Save Y%")
- **Currency detection** with geo-context
- **Hierarchical selector strategies** (JSON-LD first, then microdata, then CSS)
- **API interception** via Playwright
- **AI-powered extraction** for complex layouts
- **Price drop monitoring** with SQLite

## Project Structure

The numbering follows the pipeline order.

```
examples/
├── 01_price_normalization.py    # Handle "1,234.56" vs "1.234,56"
├── 02_marketing_cleanup.py      # Remove "Was $X Now $Y" noise
├── 03_currency_detection.py     # Resolve $ → USD/CAD/AUD via geo-hints
├── 04_selector_hierarchy.py     # Fallback strategy for robust extraction
├── 05_api_interception.py       # Capture Nike's internal API calls
├── 06_ai_extraction.py          # LLM-based multi-variant extraction
├── 07_price_monitoring.py       # Track price drops over time
└── 08_geo_pricing_audit.py      # Compare prices across regions
```

Scripts 05 through 08 need either Playwright or an API key, the rest run offline.

## Quick Start

Install once, then import any example as a module.

### Installation

One requirements file, nothing global.

```bash
pip install -r requirements.txt
```

Playwright users also run `playwright install chromium` once.

### Normalizing International Prices

The same function reads US and EU formats.

```python
from decimal import Decimal
from examples.price_normalization import normalize_price

# US format
price_us = normalize_price("$1,234.56", locale_hint="US")
# → Decimal('1234.56')

# EU format
price_eu = normalize_price("€ 1.234,56", locale_hint="EU")
# → Decimal('1234.56')

# Auto-detection
price_auto = normalize_price("1.234,56", locale_hint="AUTO")
# → Decimal('1234.56') (detects EU from comma placement)
```

AUTO mode reads the separator order instead of trusting a locale.

### Cleaning Marketing Noise

Deal pages bury the live price in was-now strings.

```python
from examples.marketing_cleanup import extract_clean_price

html = "Was $129.99 Now $99.99 (Save $30)"
clean_price = extract_clean_price(html)
# → Decimal('99.99')
```

The cleaner keeps the last price in the string, which is the live one on deal layouts.

### Monitoring Price Drops

Two saves and a check is the whole loop.

```python
from examples.price_monitoring import PriceTracker

tracker = PriceTracker()
tracker.save("https://demo.nopcommerce.com/camera-photo", Decimal("249.99"))
tracker.save("https://demo.nopcommerce.com/camera-photo", Decimal("199.99"))

alert = tracker.check_drop("https://demo.nopcommerce.com/camera-photo", threshold_percent=10)
if alert:
    print(f"Price dropped {alert['discount']:.1f}%!")
    # → "Price dropped 20.0%!"
```

History lives in a local SQLite file, no service to run.

## Configuration

Both settings sit at the top of the scripts.

### For HasData API Examples

Replace `YOUR_HASDATA_API_KEY` in scripts with your actual key:

```python
API_KEY = "YOUR_HASDATA_API_KEY"
```

The key comes free with sign-up.

### For Geo-Pricing Audits

Specify target markets in `08_geo_pricing_audit.py`:

```python
TARGET_REGIONS = ["US", "DE", "IN", "BR"]
```

Each region resolves to a residential exit in that country.

## Use Cases

Pick the script by the store you face.

| Script | Best For | Key Technique |
|--------|----------|---------------|
| `01_price_normalization.py` | Multi-region stores | Locale-aware parsing |
| `02_marketing_cleanup.py` | Deal/coupon sites | Regex noise removal |
| `03_currency_detection.py` | Global marketplaces | Symbol + geo mapping |
| `04_selector_hierarchy.py` | Resilient scraping | Structured data fallbacks |
| `05_api_interception.py` | React/Vue SPAs | Network request capture |
| `06_ai_extraction.py` | Complex variants | LLM schema extraction |
| `07_price_monitoring.py` | Deal alerts | Time-series analysis |
| `08_geo_pricing_audit.py` | Price discrimination | Residential proxy rotation |

The techniques compose, monitoring usually sits on top of one extractor.

## Important Notes

One rule outranks the rest.

### Financial Precision
Always use `Decimal` for price calculations, never `float`:

```python
# ❌ BAD
price = 19.99 * 0.85  # → 16.991499999999997

# ✅ GOOD
from decimal import Decimal
price = Decimal("19.99") * Decimal("0.85")  # → 16.9915
```

The float error lands inside real invoices, which is why the rule has no exceptions.

## Tech Stack

- **Requests** - HTTP client
- **BeautifulSoup4** - HTML parsing
- **Playwright** - Browser automation
- **SQLite** - Price history storage
- **HasData API** - Proxy & AI extraction

## Disclaimer

These scripts are for **educational purposes** only. Check our [legal guidance on web scraping](https://hasdata.com/blog/is-web-scraping-legal?utm_source=github&utm_medium=syndication&utm_campaign=price-scraping&utm_content=ecommerce-price-scraper-readme).

## Notes

* Use random delays to mimic human behavior and avoid blocks.
* Proxy support helps reduce rate limits and IP bans.
* Scrapers export data in JSON format, ready to parse for further use.
* Adjust max pages and URLs according to your scraping needs.

## 📎 More Resources

* Guide: [How to Scrape Prices with Python](https://hasdata.com/blog/price-scraping?utm_source=github&utm_medium=syndication&utm_campaign=price-scraping&utm_content=ecommerce-price-scraper-readme)
* Discord: [Join the community](https://discord.com/invite/QeuPtWpkAt)
* Star this repo if helpful ⭐
