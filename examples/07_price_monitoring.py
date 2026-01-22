import sqlite3
from datetime import datetime
from decimal import Decimal

class PriceTracker:
    """
    Minimal price monitoring system using SQLite.
    
    Architecture Note:
    In production (Postgres/MySQL), use the DECIMAL/NUMERIC type for the 'price' column.
    SQLite stores this as REAL (float), so we cast back to Decimal in Python 
    to ensure calculation precision.
    """
    
    def __init__(self, db_path="prices.db"):
        self.conn = sqlite3.connect(db_path)
        self._setup()
    
    def _setup(self):
        """Initializes the time-series schema."""
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS price_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                url TEXT NOT NULL,
                price REAL NOT NULL,
                currency TEXT DEFAULT 'USD',
                scraped_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        # Indexing URL is critical for fast history lookups
        self.conn.execute("CREATE INDEX IF NOT EXISTS idx_url ON price_history(url)")
        self.conn.commit()
    
    def save(self, url, price, currency="USD"):
        """
        Persists a price snapshot. 
        Never updates old records; always appends new history.
        """
        self.conn.execute(
            "INSERT INTO price_history (url, price, currency) VALUES (?, ?, ?)",
            (url, float(price), currency)
        )
        self.conn.commit()
    
    def check_drop(self, url, threshold_percent=10):
        """
        Calculates variance between the latest two snapshots.
        Returns an alert dict if the drop exceeds the threshold.
        """
        cursor = self.conn.execute(
            "SELECT price FROM price_history WHERE url = ? ORDER BY scraped_at DESC LIMIT 2",
            (url,)
        )
        # Fetch latest two prices and convert back to Decimal for precise math
        prices = [Decimal(str(row[0])) for row in cursor.fetchall()]
        
        # Need at least two data points to compare
        if len(prices) < 2:
            return None
        
        current, previous = prices[0], prices[1]
        
        # Sanity Check: Ignore 0.00 prices (often scraping errors)
        if current <= 0 or previous <= 0:
            return None

        # Calculate percentage drop
        if current < previous:
            drop_percent = ((previous - current) / previous) * 100
            
            if drop_percent >= threshold_percent:
                return {
                    "previous": previous,
                    "current": current,
                    "savings": previous - current,
                    "discount": drop_percent
                }
        return None

# Usage: Monitor product prices
if __name__ == "__main__":
    tracker = PriceTracker()

    # Simulated Scrape Event
    target_url = "https://demo.hyva.io/default/chaz-kangeroo-hoodie.html"
    
    # Assume we scraped these values over time
    # tracker.save(target_url, Decimal("249.99")) # Yesterday
    tracker.save(target_url, Decimal("199.99"))   # Today (Sale)

    # Check for price drops
    alert = tracker.check_drop(target_url, threshold_percent=10)
    if alert:
        print(f"ALERT: Price dropped for {target_url}")
        print(f"Old: ${alert['previous']} | New: ${alert['current']}")
        print(f"Savings: ${alert['savings']} ({alert['discount']:.1f}% off)")