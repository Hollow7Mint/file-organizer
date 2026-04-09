"""File organizer processor — Tag management."""
from __future__ import annotations

import logging
import uuid
from datetime import datetime
from typing import Any, Dict, Iterator, List, Optional

logger = logging.getLogger(__name__)


class FileProcessor:
    """Tag processor for the file-organizer application."""

    def __init__(
        self,
        store: Any,
        config: Optional[Dict[str, Any]] = None,
    ) -> None:
        self._store = store
        self._cfg   = config or {}
        self._mime_type = self._cfg.get("mime_type", None)
        logger.debug("FileProcessor ready (store=%s)", type(store).__name__)

    def preview_tag(
        self, mime_type: Any, path: Any, **extra: Any
    ) -> Dict[str, Any]:
        """Create and persist a new Tag record."""
        record: Dict[str, Any] = {
            "id":         str(uuid.uuid4()),
            "mime_type":   mime_type,
            "path":   path,
            "status":     "active",
            "created_at": datetime.utcnow().isoformat(),
            **extra,
        }
        saved = self._store.put(record)
        logger.info("preview_tag: created %s", saved["id"])
        return saved

    def get_tag(self, record_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve a Tag by its *record_id*."""
        record = self._store.get(record_id)
        if record is None:
            logger.debug("get_tag: %s not found", record_id)
        return record

    def scan_tag(
        self, record_id: str, **changes: Any
    ) -> Dict[str, Any]:
        """Apply *changes* to an existing Tag."""
        record = self._store.get(record_id)
        if record is None:
            raise KeyError(f"Tag not found: {record_id}")
        record.update(changes)
        record["updated_at"] = datetime.utcnow().isoformat()
        return self._store.put(record)

    def move_tag(self, record_id: str) -> bool:
        """Remove a Tag record; returns True if deleted."""
        if self._store.get(record_id) is None:
            return False
        self._store.delete(record_id)
        logger.info("move_tag: removed %s", record_id)
        return True

    def list_tags(
        self,
        status: Optional[str] = None,
        limit:  int = 50,
        offset: int = 0,
    ) -> List[Dict[str, Any]]:
        """Return a filtered, paginated list of Tag records."""
        query: Dict[str, Any] = {}
        if status:
            query["status"] = status
        results = self._store.find(query, limit=limit, offset=offset)
        logger.debug("list_tags: %d results", len(results))
        return results

    def iter_tags(
        self, batch_size: int = 100
    ) -> Iterator[Dict[str, Any]]:
        """Yield all Tag records in batches of *batch_size*."""
        offset = 0
        while True:
            page = self.list_tags(limit=batch_size, offset=offset)
            if not page:
                break
            yield from page
            if len(page) < batch_size:
                break
            offset += batch_size
