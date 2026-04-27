import json
from datetime import datetime
from pathlib import Path
from statistics import median
from fastapi import APIRouter, HTTPException, Query
from app.helpers.overview import _format_rupiah, _normalize_city
from app.schemas.overview import OverviewResponse, OverviewMetric, CityPricePoint

router = APIRouter()

_THIS_DIR = Path(__file__).parent.parent
DATA_DIR = _THIS_DIR.parent / "data"

@router.get("/summary", response_model=OverviewResponse)
def get_overview_summary(top_cities: int = Query(9, ge=3, le=20)):
	"""
	Ringkasan statistik harga rumah dari seluruh file JSONL hasil scraping.
	Mengembalikan 4 metrik utama dan data chart per kota.
	"""
	try:
		if not DATA_DIR.exists():
			raise FileNotFoundError(f"Folder data tidak ditemukan di: {DATA_DIR}")

		jsonl_files = sorted(DATA_DIR.glob("*.jsonl"))
		if not jsonl_files:
			raise ValueError("Belum ada file JSONL untuk dihitung.")

		prices: list[float] = []
		city_bucket: dict[str, dict[str, float]] = {}
		latest_scraped_at: datetime | None = None

		for jsonl_file in jsonl_files:
			with jsonl_file.open("r", encoding="utf-8") as handler:
				for line in handler:
					raw_line = line.strip()
					if not raw_line:
						continue

					item = json.loads(raw_line)
					price = item.get("price_in_rp")
					if not isinstance(price, (int, float)) or price <= 0:
						continue

					prices.append(float(price))

					city = _normalize_city(item.get("city"))
					city_state = city_bucket.setdefault(city, {"sum": 0.0, "count": 0.0})
					city_state["sum"] += float(price)
					city_state["count"] += 1.0

					scraped_at = item.get("scraped_at")
					if isinstance(scraped_at, str) and scraped_at:
						try:
							parsed_dt = datetime.fromisoformat(scraped_at)
							if latest_scraped_at is None or parsed_dt > latest_scraped_at:
								latest_scraped_at = parsed_dt
						except ValueError:
							continue

		if not prices:
			raise ValueError("Data harga rumah belum tersedia atau tidak valid.")

		total_listings = len(prices)
		average_price = sum(prices) / total_listings
		median_price = float(median(prices))
		max_price = max(prices)

		sorted_city = sorted(
			city_bucket.items(),
			key=lambda item: (item[1]["sum"] / item[1]["count"]),
			reverse=True,
		)

		chart: list[CityPricePoint] = []
		for city_name, state in sorted_city[:top_cities]:
			average_city_price = state["sum"] / state["count"]
			chart.append(
				CityPricePoint(
					city=city_name,
					average_price=average_city_price,
					listing_count=int(state["count"]),
					formatted_average_price=_format_rupiah(average_city_price),
				)
			)

		cards = [
			OverviewMetric(
				key="total_listings",
				label="Total Listing",
				value=float(total_listings),
				formatted_value=f"{total_listings:,}".replace(",", "."),
				note="Jumlah listing rumah dari seluruh kota.",
			),
			OverviewMetric(
				key="average_price",
				label="Rata-rata Harga",
				value=average_price,
				formatted_value=_format_rupiah(average_price),
				note="Harga rata-rata dari semua listing.",
			),
			OverviewMetric(
				key="median_price",
				label="Median Harga",
				value=median_price,
				formatted_value=_format_rupiah(median_price),
				note="Nilai tengah harga listing rumah.",
			),
			OverviewMetric(
				key="max_price",
				label="Harga Tertinggi",
				value=max_price,
				formatted_value=_format_rupiah(max_price),
				note="Harga listing rumah tertinggi saat ini.",
			),
		]

		return OverviewResponse(
			total_listings=total_listings,
			average_price=average_price,
			median_price=median_price,
			max_price=max_price,
			cards=cards,
			chart=chart,
			last_updated=latest_scraped_at.isoformat() if latest_scraped_at else None,
		)
	except FileNotFoundError as exc:
		raise HTTPException(
			status_code=404,
			detail=f"Sumber data overview tidak ditemukan: {exc}",
		)
	except ValueError as exc:
		raise HTTPException(
			status_code=400,
			detail=f"Data overview tidak siap: {exc}",
		)
	except Exception as exc:
		raise HTTPException(
			status_code=500,
			detail=f"Gagal memuat data overview: {exc}",
		)
