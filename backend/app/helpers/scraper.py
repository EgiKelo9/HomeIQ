import json
from pathlib import Path
from fastapi import HTTPException
from app.schemas.scraper import TaskInfo
from app.scraper.worker import TaskStatus

def _load_sources(SOURCE_FILE: Path) -> dict:
    if not SOURCE_FILE.exists():
        raise HTTPException(
            status_code=500,
            detail=f"source.json tidak ditemukan di: {SOURCE_FILE}",
        )
    with open(SOURCE_FILE, "r") as f:
        data = json.load(f)
        
    if isinstance(data, list):
        grouped = {}
        for url in data:
            if "pinhome.id" in url:
                provider = "pinhome"
            else:
                provider = "unknown"
            grouped.setdefault(provider, []).append(url)
        return grouped
        
    return data

def _task_to_info(raw: dict) -> TaskInfo:
    return TaskInfo(
        task_id=raw.get("task_id", ""),
        provider=raw.get("source"),
        city=raw.get("city"),
        url=raw.get("url"),
        status=raw.get("status", TaskStatus.QUEUED),
        queued_at=raw.get("queued_at"),
        started_at=raw.get("started_at"),
        finished_at=raw.get("finished_at"),
        result=raw.get("result"),
        error=raw.get("error"),
    )