import re
from decimal import Decimal

# Ensure you import normalize_price from the previous section
# from normalization import normalize_price 

def extract_clean_price(html_snippet):
    """
    Isolates the transactional price by scrubbing marketing copy.
    
    Logic:
    1. Lowercase the input for case-insensitive matching.
    2. Aggressively remove "noise phrases" AND the numbers following them.
    3. Extract the remaining valid price.
    """
    if not html_snippet:
        return None

    cleaned = html_snippet.lower()

    # Noise patterns to strip entirely
    # We include the number pattern within the removal regex to delete "Was $129.99"
    # Not just the word "Was"
    noise_patterns = [
        # Remove "Was $129.99" or "MSRP $50"
        r'\b(was|originally|msrp|rrp|old price)\s*[:\s]?\s*[\$£€¥]?\s*\d+(?:[.,]\d+)*',
        
        # Remove "(Save $10)" savings claims
        r'\(save\s*[\$£€¥]?\s*\d+(?:[.,]\d+)*\)',
        
        # Remove "From" or "As low as" (Misleading unit prices)
        r'\b(from|as low as|starting at)\b',
        
        # Remove per-unit qualifiers which skew logic
        r'\b(per\s+\w+|each)\b'
    ]
    
    for pattern in noise_patterns:
        cleaned = re.sub(pattern, '', cleaned, flags=re.IGNORECASE)
    
    # Extract the remaining numeric price with currency symbol
    # This regex looks for currency symbols followed by standard digit formats
    price_match = re.search(r'[\$£€¥]\s*(\d{1,3}(?:[,\s]\d{3})*(?:[.,]\d{2})?)', cleaned)
    
    if price_match:
        price_str = price_match.group(1)
        # Use the locale-aware normalizer from the previous section
        return normalize_price(price_str)
    
    # Fallback: Try finding numbers without currency symbols if strict match fails
    loose_match = re.search(r'(\d{1,3}(?:[,\s]\d{3})*(?:[.,]\d{2})?)', cleaned)
    if loose_match:
         return normalize_price(loose_match.group(1))

    raise ValueError(f"No valid price found after cleaning: {html_snippet}")

# Usage Example
if __name__ == "__main__":
    test_snippets = [
        "Was $129.99 Now $99.99",       # Should extract 99.99
        "$49.99 (Save $10.00)",         # Should extract 49.99
        "MSRP $199.00 Our Price $149",  # Should extract 149
        "From $29.99",                  # Should extract 29.99 (stripped 'from')
    ]

    for snippet in test_snippets:
        try:
            price = extract_clean_price(snippet)
            print(f"Input: {snippet:35} -> Parsed: ${price}")
        except ValueError as e:
            print(f"Error: {e}")