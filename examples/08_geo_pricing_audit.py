import requests
import json
from decimal import Decimal
import re

# Configuration
API_KEY = "YOUR_HASDATA_API_KEY"
TARGET_URL = "https://www.amazon.com/dp/B0DMXKG2QL/" 

# We want to audit pricing across these specific markets
TARGET_REGIONS = ["US", "DE", "IN", "BR"]

def normalize_price(raw_text, locale_hint="AUTO"):
    """
    Converts localized price strings to precise Decimal objects.
    
    Args:
        raw_text: Dirty strings like "€ 1.234,56", "$1,234.56", or "£1 234.56"
        locale_hint: "US", "EU", or "AUTO" for heuristic detection
    
    Returns:
        Decimal: Safe for financial calculations (never float)
    """
    if not raw_text:
        return None

    # Step 1: Remove artifacts
    # We strip everything except digits, commas, and dots
    # This handles space separators (e.g., "1 200.00" becomes "1200.00")
    cleaned = re.sub(r'[^\d.,]', '', raw_text)
    
    if not cleaned:
        raise ValueError(f"No numeric data found in: {raw_text}")
    
    # Step 2: Detect Format
    if locale_hint == "AUTO":
        # If both separators exist, the right-most one is the decimal
        if ',' in cleaned and '.' in cleaned:
            last_comma = cleaned.rfind(',')
            last_period = cleaned.rfind('.')
            locale_hint = "EU" if last_comma > last_period else "US"
        
        # If only comma exists, check context
        elif ',' in cleaned:
            # Ambiguous Case: "1,234"
            # Logic: If exactly 2 digits follow the comma, assume EU (cents)
            # Otherwise assume US thousands separator
            parts = cleaned.split(',')
            locale_hint = "EU" if len(parts[-1]) == 2 else "US"
        
        else:
            # Default to US if no comma is present
            locale_hint = "US"
    
    # Step 3: Normalize to Python Standard (US)
    if locale_hint == "EU":
        # Convert "1.234,56" -> "1234.56"
        normalized = cleaned.replace('.', '').replace(',', '.')
    else:
        # Convert "1,234.56" -> "1234.56"
        normalized = cleaned.replace(',', '')
    
    try:
        return Decimal(normalized)
    except InvalidOperation:
        raise ValueError(f"Normalization failed: {raw_text} -> {normalized}")


def get_price_from_region(country_code):
    """
    Fetches the price as seen by a user in a specific country.
    """
    payload = {
        "url": TARGET_URL,
        "proxyType": "residential",
        # This parameter routes traffic through a physical ISP in the target nation
        "proxyCountry": country_code, 
        "jsRendering": True,
        # Using AI extraction to handle different layouts/languages per region automatically
        "aiExtractRules": {
            "price": {
                "type": "string",
                "description": "The price of current product variant"
            }
        }
    }

    try:
        response = requests.post(
            "https://api.hasdata.com/scrape/web",
            headers={"x-api-key": API_KEY, "Content-Type": "application/json"},
            json=payload,
            timeout=45
        )
        
        if response.status_code == 200:
            data = response.json()
            raw_price = data.get("aiResponse", {}).get("price")
            return raw_price
        else:
            return f"Error {response.status_code}"
            
    except Exception as e:
        return f"Failed: {str(e)}"

# Execution Loop
print(f"{'Region':6} | {'Detected Price':20}")
print("-" * 30)

for region in TARGET_REGIONS:
    price_display = get_price_from_region(region)
    print(f"{region:6} | {str(price_display):20}")


# Example Output Logic:
# Region | Detected Price      
# ------------------------------
# US     | $24.69
# DE     | EUR 17.56
# IN     | INR 1,848.03 
# BR     | $24.69