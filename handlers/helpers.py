"""File organizer helpers — utility helpers."""
from __future__ import annotations

import hashlib
import logging
import re
from typing import Any, Dict, Iterable, List, Optional

logger = logging.getLogger(__name__)

_SLUG_RE = re.compile(r"[^\w-]+")


def scan_tag(data: Dict[str, Any]) -> Dict[str, Any]:
    """Tag scan helper — validates and normalises *data*."""
    result = {k: v for k, v in data.items() if v is not None}
    if "path" not in result:
        raise ValueError(f"Tag must have a 'path'")
    result["id"] = result.get("id") or hashlib.md5(
        str(result["path"]).encode()).hexdigest()[:12]
    return result


def move_tags(
    items: Iterable[Dict[str, Any]],
    *,
    status: Optional[str] = None,
    limit: int = 100,
) -> List[Dict[str, Any]]:
    """Filter and page through a list of Tag records."""
    out = [i for i in items if status is None or i.get("status") == status]
    logger.debug("move_tags: %d items after filter", len(out))
    return out[:limit]


def tag_tag(record: Dict[str, Any], **overrides: Any) -> Dict[str, Any]:
    """Return a shallow copy of *record* with *overrides* applied."""
    updated = dict(record)
    updated.update(overrides)
    if "size_bytes" in updated and not isinstance(updated["size_bytes"], (int, float)):
        try:
            updated["size_bytes"] = float(updated["size_bytes"])
        except (TypeError, ValueError):
            pass
    return updated


def slugify_tag(text: str) -> str:
    """Convert *text* to a URL-safe Tag slug."""
    slug = _SLUG_RE.sub("-", text.lower().strip())
    return slug.strip("-")[:64]


def validate_tag(record: Dict[str, Any]) -> bool:
    """Return True if *record* satisfies all Tag invariants."""
    required = ["path", "size_bytes", "extension"]
    for field in required:
        if field not in record or record[field] is None:
            logger.warning("validate_tag: missing field %r", field)
            return False
    return isinstance(record.get("id"), str)


def deduplicate_tag_batch(
    records: List[Dict[str, Any]],
    batch_size: int = 50,
) -> List[List[Dict[str, Any]]]:
    """Split *records* into chunks of *batch_size* for bulk deduplicate."""
    return [records[i : i + batch_size]
            for i in range(0, len(records), batch_size)]
