# HomeIQ

HomeIQ adalah aplikasi analitik properti dan prediksi harga rumah berbasis AI untuk wilayah Jabodetabek.
Project ini terdiri dari:

- Backend: FastAPI untuk API, training model, analitik data, dan orkestrasi scraper.
- Frontend: Next.js + TypeScript untuk dashboard interaktif (overview, analytics, model, scraper).

## Arsitektur Singkat

- `backend/`
	- API FastAPI di `backend/app/main.py`
	- Data mentah hasil scraping di `backend/data/*.jsonl`
	- Artefak model ML di `backend/models/*.joblib`
	- Pipeline training/prediksi di `backend/app/ml_pipeline/`
	- Modul scraper Scrapy + Playwright di `backend/app/scraper/`
- `frontend/`
	- Aplikasi Next.js (App Router) di `frontend/src/app/`
	- Service API client di `frontend/src/services/`
	- Komponen UI di `frontend/src/components/`

## Teknologi

- Backend: FastAPI, Uvicorn, Pandas, NumPy, scikit-learn, Scrapy, scrapy-playwright
- Frontend: Next.js 16, React 19, TypeScript, Tailwind CSS, Recharts, Axios

## Prasyarat

- Python 3.10+ (disarankan 3.11)
- Node.js 20+ dan npm
- Git

## Instalasi

### 1. Clone repository

```bash
git clone https://github.com/EgiKelo9/HomeIQ.git
cd HomeIQ
```

### 2. Setup backend

```bash
cd backend
python -m venv .venv
```

Aktifkan virtual environment:

- Windows (PowerShell):

```bash
.\.venv\Scripts\Activate.ps1
```

- macOS/Linux:

```bash
source .venv/bin/activate
```

Install dependensi backend:

```bash
pip install -r requirements.txt
```

Install browser Playwright untuk scraper:

```bash
playwright install chromium
```

### 3. Setup frontend

```bash
cd ../frontend
npm install
```

Buat file environment frontend:

```bash
cp .env.example .env
```

Isi `NEXT_PUBLIC_API_URL` (default lokal):

```env
NEXT_PUBLIC_API_URL=http://localhost:8000/api
```

Catatan: di Windows jika `cp` tidak tersedia, salin manual `.env.example` menjadi `.env`.

## Menjalankan Aplikasi

Jalankan backend dan frontend di terminal terpisah.

### 1. Jalankan backend

Dari folder `backend/`:

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Backend tersedia di:

- API root: `http://localhost:8000/`
- API docs (Swagger): `http://localhost:8000/docs`

### 2. Jalankan frontend

Dari folder `frontend/`:

```bash
npm run dev
```

Frontend tersedia di `http://localhost:3000`.

## Fitur Backend (Lengkap)

Semua endpoint backend di-prefix `/api` dari aplikasi FastAPI.

### 1. Health Check

- `GET /api/health/`
	- Mengecek status service backend.
	- Response berisi status, nama service, dan versi.

### 2. Overview Statistik Data Properti

- `GET /api/overview/summary?top_cities=9`
	- Membaca semua file JSONL pada `backend/data/`.
	- Menghasilkan metrik utama:
		- total listing
		- rata-rata harga
		- median harga
		- harga tertinggi
	- Menghasilkan data chart rata-rata harga per kota.
	- Menyertakan `last_updated` berdasarkan waktu scraping terakhir.

### 3. Model Machine Learning

- `POST /api/model/train`
	- Menjalankan training model Random Forest di background task.
	- Menggunakan pipeline data cleaning, encoding, scaling, training, dan export artefak.
- `GET /api/model/status`
	- Melihat status training saat ini/terakhir (`IDLE`, `RUNNING`, `SUCCESS`, `FAILED`).
- `POST /api/model/predict`
	- Prediksi harga rumah berdasarkan input:
		- bedrooms
		- bathrooms
		- building_size_m2
		- land_size_m2
		- city
		- district

Artefak model yang dipakai/disimpan antara lain:

- `best_rf_model.joblib`
- `X_scaler.joblib`, `y_scaler.joblib`
- `city_encoder.joblib`, `district_encoder.joblib`
- `model_metadata.joblib`

### 4. Analytics (Model + Data)

- `GET /api/analytics/metrics`
	- Menampilkan metrik performa model (R2, RMSE, MAE) dan waktu training terakhir.
- `GET /api/analytics/feature-importance`
	- Menampilkan bobot pengaruh fitur dari model Random Forest.
- `GET /api/analytics/distribution`
	- Distribusi jumlah listing dan rata-rata harga per kota.
- `GET /api/analytics/segments`
	- Segmentasi pasar dengan K-Means menjadi 3 cluster (`Entry Level`, `Mid Range`, `Premium`).

### 5. Scraper Management

- `POST /api/scraper/trigger?max_pages=0`
	- Men-trigger scraping semua URL dari `backend/app/scraper/source.json`.
	- Menjalankan task paralel berbasis thread pool dan subprocess Scrapy.
- `GET /api/scraper/tasks`
	- Daftar seluruh task scraping dengan filter opsional status/provider.
- `GET /api/scraper/tasks/{task_id}`
	- Detail status per task.
- `DELETE /api/scraper/tasks/{task_id}/cancel`
	- Membatalkan task yang masih `QUEUED`.
- `GET /api/scraper/providers`
	- Menampilkan provider dan URL sumber scraping.
- `GET /api/scraper/summary`
	- Ringkasan jumlah task berdasarkan status (`QUEUED`, `STARTED`, `SUCCESS`, `FAILURE`, `REVOKED`).

Fitur teknis scraper:

- Scrapy + Playwright (render JavaScript)
- Logging progress task
- Retry otomatis dan timeout
- Output data JSONL per kota/provider di `backend/data/`

## Fitur Frontend (Lengkap)

Frontend menyediakan dashboard dengan sidebar menu:

- Overview
- Analytics
- Model
- Scraper

Semua halaman mengonsumsi API backend melalui Axios (`NEXT_PUBLIC_API_URL`).

### 1. Overview Page (`/overview`)

- Menampilkan 4 kartu metrik utama (total listing, rata-rata, median, maksimum).
- Menampilkan chart perbandingan rata-rata harga per kota.
- Menampilkan waktu update data terakhir.
- Loading state dan error state jika backend/data belum siap.

### 2. Analytics Page (`/analytics`)

- Kartu metrik performa model: R2 Score, MAE, RMSE.
- Tab Insight:
	- chart volume listing per kota
	- chart rata-rata harga per kota
- Tab Performa Model:
	- chart feature importance Random Forest
- Tab Segmentasi:
	- visualisasi pie chart cluster pasar
	- deskripsi tiap cluster

### 3. Model Page (`/model`)

- Tab Prediksi:
	- form input fitur rumah
	- pemilihan kota dan kecamatan (dependent select)
	- hasil prediksi harga dalam format Rupiah
- Tab Training:
	- trigger training model backend
	- cek status training dan refresh status
- Tab Riwayat:
	- menyimpan riwayat prediksi (localStorage)
	- mekanisme expiry 24 jam untuk cache riwayat/status

### 4. Scraper Page (`/scraper`)

- Tab Scraping Panel:
	- trigger scraping dengan parameter `max pages`
	- ringkasan status task server
- Tab Data Provider & URL:
	- daftar provider dan URL target scraping
- Tab Riwayat & Log:
	- daftar task scraping (status, waktu, URL, error)
	- aksi cancel task `QUEUED`
	- refresh data task
- Sinkronisasi data task dari backend + cache localStorage (expiry 24 jam).

## Struktur Data Utama

Setiap listing rumah hasil scraper umumnya memuat field seperti:

- `source`, `url`, `title`
- `price_in_rp`
- `address`, `district`, `city`
- `bedrooms`, `bathrooms`
- `building_size_m2`, `land_size_m2`
- `carports`, `certificate`, `furnishing`, `electricity`
- `scraped_at`, `hash_id`

## Catatan Penggunaan

- Jalankan scraper terlebih dahulu agar data pada overview/analytics tersedia.
- Jalankan training model minimal sekali sebelum menggunakan fitur prediksi.
- Jika frontend tidak bisa terhubung backend, cek nilai `NEXT_PUBLIC_API_URL` di `frontend/.env`.

## Lisensi

Belum ditentukan.
