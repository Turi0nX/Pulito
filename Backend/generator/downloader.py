import logging
import requests
from pathlib import Path
from typing import Dict, Optional

from generator.config import LISTS_DIR, REMOTE_LIST_SOURCES

logger = logging.getLogger(__name__)

# --- NETWORK HEADERS ---
# Ci presentiamo come un browser reale (Safari su Mac) per evitare blocchi 403
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15"
}


class DownloadError(RuntimeError):
    """Raised when a download fails."""
    pass


def download_source(url: str, timeout: int = 30) -> str:
    """
    Scarica il contenuto testuale da un URL con timeout e headers corretti.
    """
    try:
        logger.info(f"☁️  GET {url}")
        response = requests.get(url, timeout=timeout, headers=HEADERS)
        response.raise_for_status()
        return response.text
    except requests.RequestException as e:
        raise DownloadError(f"Network error downloading {url}: {e}")


def refresh_remote_lists() -> Dict[str, Optional[Path]]:
    """
    Scarica tutte le liste configurate.
    Ritorna un dizionario {nome_lista: path_file}.
    Se un download fallisce, il valore è None (il generatore gestirà l'errore).
    """
    LISTS_DIR.mkdir(parents=True, exist_ok=True)
    results = {}

    for name, url in REMOTE_LIST_SOURCES.items():
        destination = LISTS_DIR / f"{name}.txt"
        try:
            content = download_source(url)
            with open(destination, "w", encoding="utf-8") as f:
                f.write(content)
            results[name] = destination
            logger.info(f"✅ Downloaded: {name}")
        except DownloadError as e:
            logger.error(f"❌ Failed to download {name}: {e}")
            # Ritorniamo None per segnalare il fallimento.
            # La validazione finale bloccherà il rilascio se mancano troppe regole.
            results[name] = None

    return results