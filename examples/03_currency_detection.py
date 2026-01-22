import re

# Static mapping for unique symbols
# Ambiguous symbols like '$' default to USD unless overridden by context
CURRENCY_MAP = {
    "$": "USD",  
    "€": "EUR",
    "£": "GBP",
    "¥": "JPY",   # Default to JPY, requires 'CN' context for CNY
    "₹": "INR",
    "₽": "RUB",
    "₩": "KRW",
    "฿": "THB",
    "R$": "BRL",
    "C$": "CAD",
    "A$": "AUD",
    "CHF": "CHF",
    "kr": "SEK",  # Default to SEK, requires 'NO' or 'DK' context
}

def extract_currency(text_snippet, proxy_country=None):
    """
    Resolves ISO 4217 codes using symbol lookup and geo-context.
    
    Args:
        text_snippet: The raw price string (e.g., "C$ 24.99")
        proxy_country: The ISO 3166-1 alpha-2 country code of your proxy (e.g., "CA")
    """
    if not text_snippet:
        return "USD"

    # Strategy 1: Explicit ISO Code Search
    # Some sites display "24.99 USD" directly
    iso_match = re.search(r'\b([A-Z]{3})\b', text_snippet)
    if iso_match:
        code = iso_match.group(1)
        # Validate against a known whitelist to avoid capturing unrelated uppercase words
        if code in ["USD", "EUR", "GBP", "JPY", "CAD", "AUD", "CHF", "CNY", "INR"]:
            return code
    
    # Strategy 2: Symbol Lookup with Geo-Context Override
    for symbol, default_iso in CURRENCY_MAP.items():
        if symbol in text_snippet:
            
            # Handle the generic Dollar Sign '$'
            if symbol == "$" and proxy_country:
                country_upper = proxy_country.upper()
                if country_upper == "CA": return "CAD"
                if country_upper == "AU": return "AUD"
                if country_upper == "SG": return "SGD"
                if country_upper == "MX": return "MXN"
            
            # Handle the Krone 'kr'
            if symbol == "kr" and proxy_country:
                country_upper = proxy_country.upper()
                if country_upper == "NO": return "NOK"
                if country_upper == "DK": return "DKK"

            return default_iso
    
    # Fallback assumption
    return "USD"

# Usage Example
if __name__ == "__main__":
    # Scenario: Scraping a Canadian site using a Canadian Residential Proxy
    raw_price = "$49.99"
    proxy_loc = "CA"
    
    iso_currency = extract_currency(raw_price, proxy_country=proxy_loc)
    print(f"Input: {raw_price} | Proxy: {proxy_loc} | Detected: {iso_currency}")
    # Output: CAD