import re
import os
import json
import scrapy
from scrapy_playwright.page import PageMethod

# ─── Helpers ──────────────────────────────────────────────────────────────────

def parse_price(price_str: str | None) -> int | None:
    """Konversi string harga Rupiah ke integer. Contoh: 'Rp 1,5 Miliar' → 1500000000."""
    if not price_str:
        return None
    price_str = price_str.strip()

    def _to_int(s: str) -> int | None:
        s = s.replace("Rp", "").replace("\xa0", " ").strip()
        multiplier = 1
        if "Miliar" in s or "miliar" in s:
            multiplier = 1_000_000_000
            s = re.sub(r"[Mm]iliar", "", s)
        elif "Juta" in s or "juta" in s:
            multiplier = 1_000_000
            s = re.sub(r"[Jj]uta", "", s)
        m = re.search(r"[\d.,]+", s)
        if not m:
            return None
        val = m.group(0).replace(".", "").replace(",", ".")
        try:
            return int(float(val) * multiplier)
        except ValueError:
            return None

    if "-" in price_str:
        parts = price_str.split("-", 1)
        p1, p2 = _to_int(parts[0]), _to_int(parts[1])
        if p1 and p2:
            return (p1 + p2) // 2
        return p1 or p2
    return _to_int(price_str)


def extract_number(text: str | None) -> int | None:
    if not text:
        return None
    text = text.replace(".", "")
    m = re.search(r"\d+", text)
    return int(m.group()) if m else None

# ─── Spider ───────────────────────────────────────────────────────────────────

class PinhomeSpider(scrapy.Spider):
    """Spider untuk pinhome.id."""

    name = "pinhome"
    allowed_domains = ["pinhome.id"]
    custom_settings = {
        "DOWNLOAD_DELAY": 4,
        "RANDOMIZE_DOWNLOAD_DELAY": True,
        "PLAYWRIGHT_DEFAULT_NAVIGATION_TIMEOUT": 60_000,
        "USER_AGENT": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
        "PLAYWRIGHT_LAUNCH_OPTIONS": {
            "headless": True,
            "args": [
                "--disable-blink-features=AutomationControlled",
                "--disable-infobars",
                "--no-sandbox",
            ],
        },
    }

    def start_requests(self):
        start_url = getattr(self, "start_url", None)

        if start_url:
            urls = [start_url]
        else:
            root_dir = _find_root(os.path.abspath(__file__), "source.json")
            with open(os.path.join(root_dir, "source.json")) as f:
                urls = json.load(f).get("pinhome", [])

        for url in urls:
            yield scrapy.Request(
                url=url,
                callback=self.parse,
                meta=_playwright_meta("div[class*='pin-card__info']"),
            )

    async def parse(self, response):
        page = response.meta["playwright_page"]

        await page.evaluate("window.scrollTo(0, document.body.scrollHeight / 2)")
        await page.wait_for_timeout(1000)
        await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        await page.wait_for_timeout(1500)

        cards = response.css("div[class*='pin-card__info']")
        self.logger.info("Pinhome: %d kartu di %s", len(cards), response.url)

        for card in cards:
            listing_url = card.css("a[class*='pin-card__link']::attr(href)").get()
            if not listing_url:
                continue

            title = card.css("a[class*='pin-card__link']::text").get("").strip()
            price_raw = card.css("div[class*='pin-card__price']::text").get()

            # ── Lokasi ───────────────────────────────────────────────────────
            address_raw = card.css("div[class*='pin-card__location-info']::text").get("").strip()
            address_parts = [p.strip() for p in address_raw.split(",")]
            district = address_parts[0] if address_parts else None
            city = address_parts[-1] if len(address_parts) > 1 else None

            # ── Spesifikasi ──────────────────────────────────────────────────
            specs = [
                node.xpath("string()").get("").strip()
                for node in card.css("div[class*='pin-card__specs'] li")
            ]
            # Pisahkan angka dari teks "LT" dan "LB"
            digit_specs = [
                extract_number(s)
                for s in specs
                if "LT" not in s.upper() and "LB" not in s.upper()
                and extract_number(s) is not None
            ]

            lb_raw = card.xpath(".//li[contains(., 'LB')]/text()").get()
            lt_raw = card.xpath(".//li[contains(., 'LT')]/text()").get()

            # ── Info tambahan ────────────────────────────────────────────────
            info_texts = [
                node.xpath("string()").get("").strip()
                for node in card.css("ul[class*='pin-card__property-info'] div[class*='pin-label']")
            ]

            certificate = None
            carports = None
            furnishing = None
            electricity = None

            for info in info_texts:
                info_upper = info.upper()
                if info_upper in ["SHM", "HGB", "STRATA TITLE", "AJB"]:
                    certificate = info
                elif "V" in info_upper and "FURNISHED" not in info_upper and "MILIAR" not in info_upper and "JUTA" not in info_upper and any(c.isdigit() for c in info):
                    electricity = extract_number(info)
                elif info_upper in ["FURNISHED", "SEMI-FURNISHED", "UNFURNISHED"]:
                    furnishing = info
                elif info.isdigit():
                    carports = int(info)

            yield {
                "source": "pinhome",
                "url": response.urljoin(listing_url),
                "title": title,
                "price_in_rp": parse_price(price_raw),
                "address": address_raw or None,
                "district": district,
                "city": city,
                "bedrooms": digit_specs[0] if len(digit_specs) > 0 else None,
                "bathrooms": digit_specs[1] if len(digit_specs) > 1 else None,
                "building_size_m2": extract_number(lb_raw),
                "land_size_m2": extract_number(lt_raw),
                "carports": carports,
                "certificate": certificate,
                "furnishing": furnishing,
                "electricity": electricity,
            }

        await page.close()

        # Pagination: cari semua link halaman berikutnya, hindari duplikat
        visited = response.url
        next_pages = response.css("a[href*='?page=']::attr(href)").getall()
        seen = set()
        for href in next_pages:
            abs_url = response.urljoin(href)
            if abs_url != visited and abs_url not in seen:
                seen.add(abs_url)
                yield scrapy.Request(
                    url=abs_url,
                    callback=self.parse,
                    meta=_playwright_meta("div[class*='pin-card__info']"),
                )

# ─── Utils ────────────────────────────────────────────────────────────────────

def _playwright_meta(wait_selector: str) -> dict:
    return {
        "playwright": True,
        "playwright_include_page": True,
        "playwright_page_methods": [
            PageMethod("wait_for_selector", wait_selector, timeout=20_000),
            PageMethod("wait_for_timeout", 1500),
        ],
    }

def _find_root(start: str, target_file: str) -> str:
    path = start
    for _ in range(8):
        path = os.path.dirname(path)
        if os.path.exists(os.path.join(path, target_file)):
            return path
    raise FileNotFoundError(f"{target_file} tidak ditemukan dari {start}")