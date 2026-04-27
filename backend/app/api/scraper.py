import json
import logging
from pathlib import Path
from typing import Optional
from fastapi import APIRouter, HTTPException, Query
from app.helpers.scraper import _load_sources, _task_to_info
from app.schemas.scraper import TaskInfo, TriggerResponse
from app.scraper.worker import TaskStatus, dispatch_spider, get_task, get_all_tasks, revoke_task

logger = logging.getLogger(__name__)
router = APIRouter()

_THIS_DIR  = Path(__file__).parent.parent
SOURCE_FILE = _THIS_DIR / "scraper" / "source.json"

# ─── Endpoints ────────────────────────────────────────────────────────────────

@router.post("/trigger", response_model=TriggerResponse)
def trigger_scraping(max_pages: Optional[int] = Query(0, description="Batas maksimal halaman per URL (0 = semua). Maksimal 100 untuk mencegah overload.")):
    """
    Antri scraping untuk semua URL di source.json secara paralel.
    """
    sources = _load_sources(SOURCE_FILE)

    dispatched: list[TaskInfo] = []

    for provider, urls in sources.items():
        for url in urls:
            task_id = dispatch_spider(city_url=url, source=provider, max_pages=max_pages)
            raw = get_task(task_id)
            dispatched.append(_task_to_info(raw))
            logger.info("Task %s diantri: %s — %s", task_id, provider, url)

    return TriggerResponse(
        message=f"{len(dispatched)} task berhasil diantri.",
        total_tasks=len(dispatched),
        tasks=dispatched,
    )

@router.get("/tasks", response_model=list[TaskInfo])
def list_all_tasks(
    status: Optional[str] = Query(None, description="Filter: QUEUED | STARTED | SUCCESS | FAILURE | REVOKED"),
    provider: Optional[str] = Query(None, description="Filter by provider name"),
):
    """
    Tampilkan semua task yang pernah di-dispatch sejak server terakhir jalan.
    Mendukung filter opsional by status dan provider.
    """
    tasks = get_all_tasks()

    if status:
        tasks = [t for t in tasks if t.get("status", "").upper() == status.upper()]
    if provider:
        tasks = [t for t in tasks if t.get("source", "").lower() == provider.lower()]

    return [_task_to_info(t) for t in tasks]

@router.get("/tasks/{task_id}", response_model=TaskInfo)
def get_task_status(task_id: str):
    """Cek status satu task berdasarkan task_id."""
    raw = get_task(task_id)
    if not raw:
        raise HTTPException(status_code=404, detail=f"Task '{task_id}' tidak ditemukan.")
    return _task_to_info(raw)

@router.delete("/tasks/{task_id}/cancel")
def cancel_task(task_id: str):
    """
    Batalkan task yang masih QUEUED.
    Task yang sudah STARTED tidak bisa dihentikan (subprocess sudah berjalan).
    """
    raw = get_task(task_id)
    if not raw:
        raise HTTPException(status_code=404, detail=f"Task '{task_id}' tidak ditemukan.")

    current_status = raw.get("status")
    if current_status in (TaskStatus.SUCCESS, TaskStatus.FAILURE, TaskStatus.REVOKED):
        return {
            "task_id": task_id,
            "status": current_status,
            "message": f"Task sudah dalam status final '{current_status}', tidak perlu dibatalkan.",
        }

    if current_status == TaskStatus.STARTED:
        return {
            "task_id": task_id,
            "status": current_status,
            "message": "Task sudah STARTED (subprocess berjalan). Tidak bisa dibatalkan.",
        }

    revoke_task(task_id)
    return {"task_id": task_id, "status": TaskStatus.REVOKED, "message": "Task berhasil dibatalkan."}

@router.get("/providers")
def list_providers():
    """Tampilkan daftar provider dan jumlah URL yang tersedia."""
    sources = _load_sources(SOURCE_FILE)
    return {
        provider: {"url_count": len(urls), "urls": urls}
        for provider, urls in sources.items()
    }

@router.get("/summary")
def task_summary():
    """Ringkasan jumlah task per status."""
    tasks = get_all_tasks()
    summary = {s.value: 0 for s in TaskStatus}
    for t in tasks:
        s = t.get("status", TaskStatus.QUEUED)
        if s in summary:
            summary[s] += 1
    return {"total": len(tasks), "by_status": summary}