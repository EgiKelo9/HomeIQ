# Property Scraper — Jabodetabek

Scraper data harga rumah Jabodetabek menggunakan **Scrapy + Playwright**, dikontrol via **FastAPI + Celery**.

---

## Struktur Folder

```
scraper/
├── property_scraper/
│   ├── spiders/
│   │   ├── __init__.py
│   │   ├── rumah123_spider.py
│   │   ├── 99co_spider.py
│   │   ├── pinhome_spider.py
│   │   └── lamudi_spider.py
│   ├── __init__.py
│   ├── items.py          ← Definisi struktur data
│   ├── middlewares.py    ← Logging middleware
│   ├── pipelines.py      ← Validasi, dedup, simpan JSON/PostgreSQL
│   └── settings.py       ← Konfigurasi Scrapy + Playwright
├── source.json           ← Daftar URL per provider
├── worker.py             ← Celery task
├── scraper.py            ← FastAPI router (dipasang di app/scraper/)
└── scrapy.cfg
```

---

## Instalasi

```bash
pip install scrapy scrapy-playwright celery redis
playwright install chromium
```

Jika menggunakan PostgreSQL pipeline:
```bash
pip install psycopg2-binary
```

---

## Menjalankan Secara Manual (tanpa API)

```bash
# Scrape satu kota dari satu provider
cd scraper/property_scraper
scrapy crawl rumah123 -a start_url="https://www.rumah123.com/jual/jakarta-selatan/rumah/" -O output.json

# Scrape semua kota (fallback ke source.json)
scrapy crawl pinhome -O pinhome_all.json
scrapy crawl 99co    -O 99co_all.json
scrapy crawl lamudi  -O lamudi_all.json
```

---

## Menjalankan via API (Celery + FastAPI)

### 1. Jalankan Redis
```bash
docker run -d -p 6379:6379 redis:7-alpine
# atau jika sudah ada di docker-compose: docker compose up -d redis
```

### 2. Jalankan Celery Worker
```bash
# Dari folder scraper/
celery -A worker.celery_app worker --loglevel=info --queues=scraping --concurrency=4
```

### 3. Jalankan FastAPI
```bash
uvicorn app.main:app --reload
```

### 4. Trigger Scraping via API

**Semua provider:**
```bash
curl -X POST http://localhost:8000/scraper/trigger
```

**Provider tertentu saja:**
```bash
curl -X POST http://localhost:8000/scraper/trigger \
  -H "Content-Type: application/json" \
  -d '{"providers": ["rumah123", "pinhome"]}'
```

**Cek status task:**
```bash
curl http://localhost:8000/scraper/status/<task_id>
```

**Batalkan task:**
```bash
curl -X DELETE http://localhost:8000/scraper/cancel/<task_id>
```

**Lihat daftar provider:**
```bash
curl http://localhost:8000/scraper/providers
```

---

## Integrasi di FastAPI `main.py`

```python
from app.scraper.scraper import router as scraper_router

app = FastAPI()
app.include_router(scraper_router)
```

---

## Output

Setiap task menyimpan file di `data_temp/`:
```
data_temp/
├── rumah123_jakarta-selatan.json
├── pinhome_depok.json
├── 99co_bekasi.json
└── lamudi_tangerang.json
```

Setiap baris (JSONL) berisi:
```json
{
  "source": "rumah123",
  "url": "https://...",
  "title": "Rumah 2 Lantai di Kemang",
  "price_in_rp": 3500000000,
  "address": "Kemang, Jakarta Selatan",
  "district": "Kemang",
  "city": "Jakarta Selatan",
  "bedrooms": 4,
  "bathrooms": 3,
  "building_size_m2": 180,
  "land_size_m2": 120,
  "carports": 2,
  "electricity": 2200,
  "scraped_at": "2025-04-25T10:30:00+00:00",
  "hash_id": "a1b2c3d4..."
}
```

---

## Catatan Penting

- **Selector CSS bisa berubah** — situs properti sering update UI. Jika spider berhenti menghasilkan data, buka browser DevTools dan cek ulang selectornya.
- **Playwright headless** — semua spider membutuhkan Playwright karena listing dimuat via JavaScript.
- **Rate limiting** — `DOWNLOAD_DELAY = 2` + `AUTOTHROTTLE` sudah diset agar tidak terlalu agresif.
- **Retry otomatis** — Celery task akan retry 2x jika gagal, dengan jeda 60 detik.
