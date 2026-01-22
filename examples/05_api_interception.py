from playwright.sync_api import sync_playwright

TARGET_URL = "https://www.nike.com/us/w/futbol-1gdj0"
API_PART = "product-proxy-v2.adtech-prod.nikecloud.com/products"

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()

    seen_ids = set()

    def handle_response(response):
        if API_PART in response.url:
            try:
                data = response.json()
                products = data.get("hydratedProducts", [])

                for p in products:
                    pid = p.get("cloudProductId")
                    if pid in seen_ids:
                        continue
                    seen_ids.add(pid)

                    current = p.get("currentPrice")
                    full = p.get("fullPrice")

                    discount = None
                    if current and full and full > current:
                        discount = round((1 - current / full) * 100, 1)

                    print(
                        f"Name: {p.get('name')}\n"
                        f"Brand: {p.get('brand')}\n"
                        f"Category: {p.get('category')}\n"
                        f"Color: {p.get('color')}\n"
                        f"Current price: {current} USD\n"
                        f"Full price: {full} USD\n"
                        f"On sale: {p.get('isOnSale')}\n"
                        f"Discount: {discount}%\n"
                        f"{'-'*40}"
                    )
            except Exception:
                pass

    page.on("response", handle_response)
    page.goto(TARGET_URL, wait_until="networkidle")
    page.wait_for_timeout(8000)

    browser.close()
