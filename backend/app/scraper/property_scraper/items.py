import scrapy


class PropertyItem(scrapy.Item):
    """
    Struktur data standar untuk satu listing properti dari semua spider.

    Field ini konsisten di semua spider (rumah123, 99co, pinhome, lamudi)
    agar output bisa di-merge dan diproses dalam satu pipeline.
    """

    # ── Identitas listing ──────────────────────────────────────────────────────
    source       = scrapy.Field()   # str  : "rumah123" | "99co" | "pinhome" | "lamudi"
    url          = scrapy.Field()   # str  : URL lengkap halaman listing
    title        = scrapy.Field()   # str  : Judul listing

    # ── Harga ──────────────────────────────────────────────────────────────────
    price_in_rp  = scrapy.Field()   # int  : Harga dalam Rupiah (sudah dikonversi)

    # ── Lokasi ─────────────────────────────────────────────────────────────────
    address      = scrapy.Field()   # str  : Teks alamat mentah dari listing
    district     = scrapy.Field()   # str  : Kecamatan / kelurahan
    city         = scrapy.Field()   # str  : Kota (Jakarta Selatan, Bogor, dst)

    # ── Spesifikasi fisik ──────────────────────────────────────────────────────
    bedrooms         = scrapy.Field()   # int  : Jumlah kamar tidur
    bathrooms        = scrapy.Field()   # int  : Jumlah kamar mandi
    building_size_m2 = scrapy.Field()   # int  : Luas bangunan (LB) dalam m²
    land_size_m2     = scrapy.Field()   # int  : Luas tanah (LT) dalam m²
    carports         = scrapy.Field()   # int  : Jumlah carport / garasi
    
    # ── Fitur tambahan ─────────────────────────────────────────────────────────
    certificate      = scrapy.Field()   # str  : Sertifikat (SHM, HGB, dll)
    electricity      = scrapy.Field()   # int  : Daya listrik dalam watt
    furnishing       = scrapy.Field()   # str  : Furnished / Semi Furnished / Unfurnished

    # ── Metadata ───────────────────────────────────────────────────────────────
    scraped_at   = scrapy.Field()   # str  : ISO timestamp saat di-scrape
    hash_id      = scrapy.Field()   # str  : Hash unik untuk deduplication