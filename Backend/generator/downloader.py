import logging
from pathlib import Path
from typing import Dict

import requests

from generator.config import LISTS_DIR, REMOTE_LIST_SOURCES

logger = logging.getLogger(__name__)


class DownloadError(RuntimeError):
    pass


def download_source(url: str, timeout: int = 20) -> str:
    """
    Download the content from the given URL.

    Raises:
        DownloadError: on network/HTTP failures.
    """
    try:
        response = requests.get(url, timeout=timeout)
        response.raise_for_status()
        return response.text
    except requests.RequestException as exc:
        logger.error("Failed to download %s: %s", url, exc)
        raise DownloadError(f"failed to download {url}") from exc


def refresh_remote_lists() -> Dict[str, Path]:
    """
    Download all remote public lists and save them under LISTS_DIR.

    Returns:
        mapping: list_name -> local file path
    """
    LISTS_DIR.mkdir(parents=True, exist_ok=True)
    result: Dict[str, Path] = {}

    for name, url in REMOTE_LIST_SOURCES.items():
        logger.info("Downloading %s from %s", name, url)
        text = download_source(url)
        target = LISTS_DIR / f"{name}.txt"
        target.write_text(text, encoding="utf-8")
        logger.info("Saved %s (%d bytes) to %s", name, len(text), target)
        result[name] = target

    return result