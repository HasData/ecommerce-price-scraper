![Python](https://img.shields.io/badge/python-3.11+-blue)

# Price Scraping Toolkit

[![HasData_bannner](banner.png)](https://hasdata.com/)

A production-grade collection of Python scripts for extracting, normalizing, and monitoring e-commerce pricing data.

## Features

- **Multi-locale price normalization** (US/EU formats)
- **Marketing noise removal** ("Was $X", "Save Y%")
- **Currency detection** with geo-context
- **Hierarchical selector strategies** (JSON-LD → microdata → CSS)
- **API interception** via Playwright
- **AI-powered extraction** for complex layouts
- **Price drop monitoring** with SQLite

## Project Structure

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

## Quick Start

### Installation

```bash
pip install -r requirements.txt
```

### Example 1: Normalize International Prices

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

### Example 2: Clean Marketing Noise

```python
from examples.marketing_cleanup import extract_clean_price

html = "Was $129.99 Now $99.99 (Save $30)"
clean_price = extract_clean_price(html)
# → Decimal('99.99')
```

### Example 3: Monitor Price Drops

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

## Configuration

### For HasData API Examples

Replace `YOUR_HASDATA_API_KEY` in scripts with your actual key:

```python
API_KEY = "YOUR_HASDATA_API_KEY"
```

### For Geo-Pricing Audits

Specify target markets in `08_geo_pricing_audit.py`:

```python
TARGET_REGIONS = ["US", "DE", "IN", "BR"]
```

## Use Cases

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

## Important Notes

### Financial Precision
Always use `Decimal` for price calculations, never `float`:

```python
# ❌ BAD
price = 19.99 * 0.85  # → 16.991499999999997

# ✅ GOOD
from decimal import Decimal
price = Decimal("19.99") * Decimal("0.85")  # → 16.9915
```

## Tech Stack

- **Requests** - HTTP client
- **BeautifulSoup4** - HTML parsing
- **Playwright** - Browser automation
- **SQLite** - Price history storage
- **HasData API** - Proxy & AI extraction

## Disclaimer

These scripts are for **educational purposes** only. Check our [legal guidance on web scraping](https://hasdata.com/blog/is-web-scraping-legal).

## Notes

* Use random delays to mimic human behavior and avoid blocks.
* Proxy support helps reduce rate limits and IP bans.
* Scrapers export data in JSON format, ready to parse for further use.
* Adjust max pages and URLs according to your scraping needs.

## 📎 More Resources

* Guide: [How to Scrape Prices with Python](https://hasdata.com/blog/price-scraping?utm_source=github&utm_medium=syndication&utm_campaign=price-scraping)
* Discord: [Join the community](https://discord.com/invite/QeuPtWpkAt)
* Star this repo if helpful ⭐
