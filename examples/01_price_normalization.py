from decimal import Decimal, InvalidOperation
import re

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

# Unit Tests for Validation
if __name__ == "__main__":
    test_cases = [
        ("$1,234.56", "US", Decimal("1234.56")),
        ("€ 1.234,56", "EU", Decimal("1234.56")),
        ("Price: 1,200", "US", Decimal("1200")),    # US Integer
        ("1,20 €", "AUTO", Decimal("1.20")),        # EU Decimal
    ]

    for raw, locale, expected in test_cases:
        result = normalize_price(raw, locale)
        print(f"Input: {raw:15} | Mode: {locale:4} | Result: {result}")
        assert result == expected