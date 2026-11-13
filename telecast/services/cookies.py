# Copyright (C) @itsSmartDev

import os
import shutil
from typing import Optional
from telecast.core.config import Config
from telecast.core.logging import logger

_SOURCE_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'cookies', 'yt.txt'
)

_resolved: Optional[str] = None
_resolved_done = False


def _is_writable(path: str) -> bool:
    return os.access(path, os.W_OK) and os.access(os.path.dirname(path), os.W_OK)


def get_cookies_path() -> Optional[str]:
    global _resolved, _resolved_done
    if _resolved_done:
        return _resolved
    _resolved_done = True

    if not os.path.exists(_SOURCE_PATH):
        logger.warning(f"YouTube cookies file not found at: {_SOURCE_PATH}")
        return None

    if _is_writable(_SOURCE_PATH):
        _resolved = _SOURCE_PATH
        return _resolved

    target = os.path.join(os.path.abspath(Config.SESSION_DIR), 'yt_cookies.txt')
    try:
        os.makedirs(os.path.dirname(target), exist_ok=True)
        shutil.copyfile(_SOURCE_PATH, target)
        _resolved = target
        logger.info(f"Cookies at {_SOURCE_PATH} are read-only; using writable copy at {target}")
    except OSError as e:
        logger.error(f"Could not copy read-only cookies to {target}: {e}; continuing without cookies")
        _resolved = None
    return _resolved
