"""File organizer handler — Folder management."""
from __future__ import annotations

import logging
import uuid
from datetime import datetime
from typing import Any, Dict, Iterator, List, Optional

logger = logging.getLogger(__name__)


class FileHandler:
    """Folder handler for the file-organizer application."""

    def __init__(
        self,
        store: Any,
        config: Optional[Dict[str, Any]] = None,
    ) -> None:
        self._store = store
        self._cfg   = config or {}
        self._modified_at = self._cfg.get("modified_at", None)
        logger.debug("FileHandler ready (store=%s)", type(store).__name__)

    def deduplicate_folder(
        self, modified_at: Any, checksum: Any, **extra: Any
    ) -> Dict[str, Any]:
        """Create and persist a new Folder record."""
        record: Dict[str, Any] = {
            "id":         str(uuid.uuid4()),
            "modified_at":   modified_at,
            "checksum":   checksum,
            "status":     "active",
            "created_at": datetime.utcnow().isoformat(),
            **extra,
        }
        saved = self._store.put(record)
        logger.info("deduplicate_folder: created %s", saved["id"])
        return saved

    def get_folder(self, record_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve a Folder by its *record_id*."""
        record = self._store.get(record_id)
        if record is None:
            logger.debug("get_folder: %s not found", record_id)
        return record

    def compress_folder(
        self, record_id: str, **changes: Any
    ) -> Dict[str, Any]:
        """Apply *changes* to an existing Folder."""
        record = self._store.get(record_id)
        if record is None:
            raise KeyError(f"Folder not found: {record_id}")
        record.update(changes)
        record["updated_at"] = datetime.utcnow().isoformat()
        return self._store.put(record)

    def preview_folder(self, record_id: str) -> bool:
        """Remove a Folder record; returns True if deleted."""
        if self._store.get(record_id) is None:
            return False
        self._store.delete(record_id)
        logger.info("preview_folder: removed %s", record_id)
        return True

    def list_folders(
        self,
        status: Optional[str] = None,
        limit:  int = 50,
        offset: int = 0,
    ) -> List[Dict[str, Any]]:
        """Return a filtered, paginated list of Folder records."""
        query: Dict[str, Any] = {}
        if status:
            query["status"] = status
        results = self._store.find(query, limit=limit, offset=offset)
        logger.debug("list_folders: %d results", len(results))
        return results

    def iter_folders(
        self, batch_size: int = 100
    ) -> Iterator[Dict[str, Any]]:
        """Yield all Folder records in batches of *batch_size*."""
        offset = 0
        while True:
            page = self.list_folders(limit=batch_size, offset=offset)
            if not page:
                break
            yield from page
            if len(page) < batch_size:
                break
            offset += batch_size
