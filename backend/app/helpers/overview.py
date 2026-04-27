def _format_rupiah(value: float) -> str:
	integer_value = int(round(value))
	return f"Rp {integer_value:,}".replace(",", ".")

def _normalize_city(city: str | None) -> str:
	if not city:
		return "Lainnya"

	normalized = city.strip()
	normalized = normalized.replace("Kota ", "")
	normalized = normalized.replace("Kabupaten ", "")
	return normalized if normalized else "Lainnya"