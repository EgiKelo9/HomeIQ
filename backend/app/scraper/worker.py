import os
import re
import subprocess
import logging
import uuid
import threading
from datetime import datetime, timezone
from concurrent.futures import ThreadPoolExecutor
from threading import Lock
from enum import Enum

logger = logging.getLogger(__name__)

# ─── Status ───────────────────────────────────────────────────────────────────

class TaskStatus(str, Enum):
    QUEUED  = "QUEUED"
    STARTED = "STARTED"
    SUCCESS = "SUCCESS"
    FAILURE = "FAILURE"
    REVOKED = "REVOKED"

# ─── Task Store ───────────────────────────────────────────────────────────────

_task_store: dict[str, dict] = {}
_store_lock = Lock()

def _set_task(task_id: str, **kwargs):
    with _store_lock:
        if task_id not in _task_store:
            _task_store[task_id] = {"task_id": task_id}
        _task_store[task_id].update(kwargs)

def get_task(task_id: str) -> dict | None:
    return _task_store.get(task_id)

def get_all_tasks() -> list[dict]:
    with _store_lock:
        return sorted(
            list(_task_store.values()),
            key=lambda t: t.get("queued_at", ""),
            reverse=True,
        )

def revoke_task(task_id: str) -> bool:
    task = get_task(task_id)
    if not task:
        return False
    if task["status"] == TaskStatus.QUEUED:
        _set_task(task_id, status=TaskStatus.REVOKED)
        return True
    return False

# ─── Thread Pool ──────────────────────────────────────────────────────────────
_executor = ThreadPoolExecutor(max_workers=1, thread_name_prefix="spider")

CITIES = [
    "jakarta-utara", "jakarta-timur", "jakarta-selatan", "jakarta-barat",
    "jakarta-pusat", "bogor", "depok", "tangerang", "bekasi",
    "dki-jakarta", "jawa-barat", "banten",
]

# ─── Helpers ──────────────────────────────────────────────────────────────────

def _extract_city_name(url: str) -> str:
    url_lower = url.lower()
    for city in CITIES:
        if city in url_lower:
            return city
    parts = [p for p in url_lower.rstrip("/").split("/") if p]
    return parts[-1] if parts else "unknown"

def _count_items_in_file(output_file: str) -> int:
    try:
        if not os.path.exists(output_file):
            return 0
        with open(output_file, "r", encoding="utf-8") as f:
            content = f.read().strip()
        if not content:
            return 0
        if content.startswith("["):
            return content.count("\n{")
        return sum(1 for line in content.splitlines() if line.strip())
    except Exception:
        return 0

def _parse_log_progress(log_file: str) -> dict:
    result = {"pages_crawled": 0, "items_scraped": 0, "last_url": None, "errors": 0}
    try:
        if not os.path.exists(log_file):
            return result
        with open(log_file, "r", encoding="utf-8", errors="ignore") as f:
            lines = f.readlines()
        for line in lines[-150:]:
            if "item_scraped_count" in line:
                m = re.search(r"item_scraped_count['\"]:\s*(\d+)", line)
                if m:
                    result["items_scraped"] = int(m.group(1))
            if "downloader/request_count" in line:
                m = re.search(r"downloader/request_count['\"]:\s*(\d+)", line)
                if m:
                    result["pages_crawled"] = max(0, int(m.group(1)) - 1)
            if "downloader/exception_count" in line:
                m = re.search(r"downloader/exception_count['\"]:\s*(\d+)", line)
                if m:
                    result["errors"] = int(m.group(1))
            if "Crawling" in line or "Scraped from" in line:
                m = re.search(r"(https?://[^\s'\"]+)", line)
                if m:
                    result["last_url"] = m.group(1)
    except Exception as e:
        logger.debug("Gagal parse log: %s", e)
    return result

# ─── Core Runner ───────────────────────────────────────────────────────

def _run_spider(task_id: str, city_url: str, source: str, max_pages: int = 0):
    """
    Menjalankan spider dengan subprocess.Popen (non-blocking).
    """
    task = get_task(task_id)
    if task and task["status"] == TaskStatus.REVOKED:
        return

    _set_task(task_id,
        status=TaskStatus.STARTED,
        started_at=_now(),
        progress={
            "items_scraped": 0, "pages_crawled": 0, "progress_pct": 0,
            "eta_human": "menghitung...", "elapsed_human": "0d",
            "rate_items_per_min": 0, "last_url": None, "errors": 0,
        },
    )
    logger.info("[%s] Mulai (Popen): %s — %s", task_id, source, city_url)

    scraper_dir = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "property_scraper"
    )
    city_name = _extract_city_name(city_url)
    root_dir  = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    temp_dir  = os.path.join(root_dir, "data")
    os.makedirs(temp_dir, exist_ok=True)

    output_file = os.path.join(temp_dir, f"{source}_{city_name}.jsonl")
    log_file    = os.path.join(temp_dir, f"{source}_{city_name}.log")

    command = [
        "scrapy", "crawl", source,
        "-a", f"start_url={city_url}",
        "-a", f"output_file={output_file}",
        "--logfile", log_file,
        "--loglevel", "INFO",
    ]
    
    if max_pages > 0:
        command.extend(["-s", f"CLOSESPIDER_PAGECOUNT={max_pages}"])

    try:
        # ── Popen: mulai proses, jangan tunggu ────────────────────────────
        proc = subprocess.Popen(
            command,
            cwd=scraper_dir,
            stdout=subprocess.DEVNULL,  # log sudah ke file, stdout tidak perlu
            stderr=subprocess.PIPE,     # stderr tetap dicapture untuk error handling
            text=True,
        )

        # ── Loop pemantau: poll setiap 5 detik ────────────────────────────
        # proc.poll() = None  # proses masih berjalan
        # proc.poll() = 0     # proses selesai dengan sukses
        # proc.poll() = N     # selesai dengan error code N
        timeout_seconds = 3600
        start_time      = _now_ts()

        while proc.poll() is None:
            # Cek timeout
            if (_now_ts() - start_time) > timeout_seconds:
                proc.terminate()
                proc.wait(timeout=10)
                _set_task(task_id,
                    status=TaskStatus.FAILURE,
                    finished_at=_now(),
                    error="Timeout setelah 1 jam.",
                )
                return

            # Cek apakah di-revoke saat sedang berjalan
            current = get_task(task_id)
            if current and current.get("status") == TaskStatus.REVOKED:
                proc.terminate()
                proc.wait(timeout=10)
                logger.info("[%s] Di-revoke saat STARTED, proses dihentikan.", task_id)
                return

            # Update progress dari log file
            log_data      = _parse_log_progress(log_file)
            items_scraped = log_data["items_scraped"] or _count_items_in_file(output_file)

            _set_task(task_id, progress={
                "items_scraped":      items_scraped,
                "pages_crawled":      log_data["pages_crawled"],
                "last_url":           log_data.get("last_url"),
                "errors":             log_data.get("errors", 0),
            })

            threading.Event().wait(5)  # tunggu 5 detik lalu poll lagi

        # ── Proses selesai — baca return code ─────────────────────────────
        returncode = proc.returncode
        _, stderr  = proc.communicate()  # ambil sisa stderr

        final_log   = _parse_log_progress(log_file)
        final_items = final_log["items_scraped"] or _count_items_in_file(output_file)

        if returncode != 0:
            error_snippet = (stderr or "")[-1000:]
            logger.error("[%s] Gagal (returncode=%d): %s", task_id, returncode, error_snippet)
            _set_task(task_id,
                status=TaskStatus.FAILURE,
                finished_at=_now(),
                error=f"Exit code {returncode}: {error_snippet}",
            )
        else:
            logger.info("[%s] Selesai: %s — %s | %d item | %s",
                        task_id, source, city_name, final_items,)
            _set_task(task_id,
                status=TaskStatus.SUCCESS,
                finished_at=_now(),
                progress={
                    "items_scraped":      final_items,
                    "pages_crawled":      final_log["pages_crawled"],
                    "progress_pct":       100,
                    "last_url":           final_log.get("last_url"),
                    "errors":             final_log.get("errors", 0),
                },
                result={
                    "source": source, "city": city_name, "url": city_url,
                    "output_file": output_file, "items_scraped": final_items,
                    "message": f"Selesai: {source} — {city_name} ({final_items} item)",
                },
            )

    except Exception as exc:
        logger.exception("[%s] Exception tidak terduga: %s", task_id, exc)
        _set_task(task_id,
            status=TaskStatus.FAILURE,
            finished_at=_now(),
            error=str(exc),
        )

# ─── Public API ───────────────────────────────────────────────────────────────

def dispatch_spider(city_url: str, source: str, max_pages: int) -> str:
    task_id = str(uuid.uuid4())
    _set_task(task_id,
        source=source, city=_extract_city_name(city_url), url=city_url,
        status=TaskStatus.QUEUED, queued_at=_now(),
        started_at=None, finished_at=None, progress=None, result=None, error=None,
    )
    _executor.submit(_run_spider, task_id, city_url, source, max_pages)
    return task_id

def shutdown_executor():
    _executor.shutdown(wait=False, cancel_futures=True)

def _now() -> str:
    return datetime.now(timezone.utc).isoformat()

def _now_ts() -> float:
    return datetime.now(timezone.utc).timestamp()