"""File organizer schemas — scan configuration."""
from __future__ import annotations

import logging
import os
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)

_DEFAULTS: Dict[str, Any] = {
    "path": None,
    "size_bytes": 30,
    "extension": True,
    "max_retries": 3,
    "timeout":     60,
}


class FileSchemas:
    """Rule schemas for the file-organizer system."""

    def __init__(self, **kwargs: Any) -> None:
        self._data: Dict[str, Any] = dict(_DEFAULTS)
        self._data.update(kwargs)
        self._from_env()
        logger.debug("FileSchemas initialised")

    def _from_env(self) -> None:
        prefix = "FILE_ORGANIZER_"
        for key in _DEFAULTS:
            val = os.environ.get(prefix + key.upper())
            if val is not None:
                self._data[key] = val

    def get(self, key: str, default: Any = None) -> Any:
        """Return the path value for *key*."""
        return self._data.get(key, default)

    def update(self, **kwargs: Any) -> None:
        """Update schemas settings in place."""
        self._data.update(kwargs)

    def to_dict(self) -> Dict[str, Any]:
        """Serialise schemas to a plain dict."""
        return dict(self._data)

    def __repr__(self) -> str:
        return f"FileSchemas({self._data!r})"


def load_rule_schemas(path: Optional[str] = None) -> FileSchemas:
    """Load Rule schemas from *path* or environment."""
    kwargs: Dict[str, Any] = {}
    if path and os.path.exists(path):
        import json
        with open(path) as fh:
            kwargs = json.load(fh)
        logger.info("Loaded schemas from %s", path)
    return FileSchemas(**kwargs)
