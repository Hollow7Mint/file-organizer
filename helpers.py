"""File organizer helpers — utility helpers."""
from __future__ import annotations

import hashlib
import logging
import re
from typing import Any, Dict, Iterable, List, Optional

logger = logging.getLogger(__name__)

_SLUG_RE = re.compile(r"[^\w-]+")


def deduplicate_rule(data: Dict[str, Any]) -> Dict[str, Any]:
    """Rule deduplicate helper — validates and normalises *data*."""
    result = {k: v for k, v in data.items() if v is not None}
    if "modified_at" not in result:
        raise ValueError(f"Rule must have a 'modified_at'")
    result["id"] = result.get("id") or hashlib.md5(
        str(result["modified_at"]).encode()).hexdigest()[:12]
    return result


def compress_rules(
    items: Iterable[Dict[str, Any]],
    *,
    status: Optional[str] = None,
    limit: int = 100,
) -> List[Dict[str, Any]]:
    """Filter and page through a list of Rule records."""
    out = [i for i in items if status is None or i.get("status") == status]
    logger.debug("compress_rules: %d items after filter", len(out))
    return out[:limit]


def preview_rule(record: Dict[str, Any], **overrides: Any) -> Dict[str, Any]:
    """Return a shallow copy of *record* with *overrides* applied."""
    updated = dict(record)
    updated.update(overrides)
    if "checksum" in updated and not isinstance(updated["checksum"], (int, float)):
        try:
            updated["checksum"] = float(updated["checksum"])
        except (TypeError, ValueError):
            pass
    return updated


def slugify_rule(text: str) -> str:
    """Convert *text* to a URL-safe Rule slug."""
    slug = _SLUG_RE.sub("-", text.lower().strip())
    return slug.strip("-")[:64]


def validate_rule(record: Dict[str, Any]) -> bool:
    """Return True if *record* satisfies all Rule invariants."""
    required = ["modified_at", "checksum", "mime_type"]
    for field in required:
        if field not in record or record[field] is None:
            logger.warning("validate_rule: missing field %r", field)
            return False
    return isinstance(record.get("id"), str)


def scan_rule_batch(
    records: List[Dict[str, Any]],
    batch_size: int = 50,
) -> List[List[Dict[str, Any]]]:
    """Split *records* into chunks of *batch_size* for bulk scan."""
    return [records[i : i + batch_size]
            for i in range(0, len(records), batch_size)]
