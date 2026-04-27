import os
import json
import hashlib
import logging
from datetime import datetime, timezone
from pathlib import Path

logger = logging.getLogger(__name__)

# ─── 1. Validasi ──────────────────────────────────────────────────────────────

class ValidatePipeline:
    """
    Buang item yang tidak memiliki field wajib.
    Tambahkan timestamp scraping dan hash_id.
    """

    REQUIRED_FIELDS = ("url", "price_in_rp")

    def process_item(self, item, spider):
        # Validasi field wajib
        for field in self.REQUIRED_FIELDS:
            if not item.get(field):
                raise DropItem(f"[{spider.name}] Field '{field}' kosong — item dibuang: {item.get('url', '-')}")

        # Tambahkan timestamp
        item["scraped_at"] = datetime.now(timezone.utc).isoformat()

        # Buat hash_id untuk deduplication lintas sumber
        raw = f"{item.get('url', '')}{item.get('price_in_rp', '')}{item.get('land_size_m2', '')}"
        item["hash_id"] = hashlib.md5(raw.encode()).hexdigest()

        return item

# ─── 2. Deduplication ─────────────────────────────────────────────────────────

class DeduplicationPipeline:
    """
    Buang listing yang sudah pernah di-scrape dalam satu sesi (in-memory).
    Untuk deduplication lintas sesi, gunakan database.
    """

    def open_spider(self, spider):
        self._seen: set[str] = set()

    def process_item(self, item, spider):
        hash_id = item.get("hash_id")
        if hash_id in self._seen:
            raise DropItem(f"[{spider.name}] Duplikat ditemukan: {item.get('url', '-')}")
        self._seen.add(hash_id)
        return item

# ─── 3. JSONl Exporter ─────────────────────────────────────────────────────────

class JsonlExportPipeline:
    """
    Pipeline kustom untuk menyimpan item ke format JSONL secara manual.
    Mengatasi masalah:
    1. Kurung kurawal menempel (}{) saat append file.
    2. Menghindari baris kosong (extra newline) di akhir file.
    """
    def open_spider(self, spider):
        # Ambil path output_file dari argumen spider (-a output_file=...)
        self.output_file = getattr(spider, 'output_file', None)
        
        if not self.output_file:
            # Fallback aman jika argumen output_file tidak diberikan
            self.output_file = os.path.join("data", f"{spider.name}_output.jsonl")
            os.makedirs(os.path.dirname(self.output_file), exist_ok=True)
        
        # 1. Cegah kurung kurawal menempel (}{)
        if os.path.exists(self.output_file) and os.path.getsize(self.output_file) > 0:
            with open(self.output_file, 'rb+') as f:
                f.seek(-1, os.SEEK_END)
                last_char = f.read(1)
                # Jika file tidak diakhiri baris baru, tambahkan secara manual
                if last_char != b'\n':
                    f.write(b'\n')

        # Buka file untuk proses tulis (append)
        self.file = open(self.output_file, 'a', encoding='utf-8')

    def close_spider(self, spider):
        if hasattr(self, 'file') and not self.file.closed:
            self.file.close()

            # 2. Hapus baris kosong (newline) terakhir di paling bawah file
            try:
                with open(self.output_file, 'rb+') as f:
                    f.seek(-1, os.SEEK_END)
                    if f.read(1) == b'\n':
                        f.seek(-1, os.SEEK_END)
                        f.truncate()  # Potong 1 byte terakhir (\n)
            except Exception as e:
                logger.debug(f"Gagal memotong newline terakhir: {e}")

    def process_item(self, item, spider):
        # Konversi dict ke string JSON, dan pastikan karakter non-ASCII (seperti é, ㎡) aman
        line = json.dumps(dict(item), ensure_ascii=False) + '\n'
        self.file.write(line)
        self.file.flush() # Segera simpan ke disk untuk mencegah data hilang jika crash
        return item

# Import DropItem di sini agar tidak circular
from scrapy.exceptions import DropItem  # noqa: E402