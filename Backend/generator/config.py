import os
from pathlib import Path

# Base paths
BACKEND_ROOT = Path(__file__).resolve().parent.parent
LISTS_DIR = BACKEND_ROOT / "lists"
OUTPUT_DIR = BACKEND_ROOT / "output"
KEYS_DIR = BACKEND_ROOT / "keys"

# GitHub Pages / distribuzione
GITHUB_PAGES_URL = os.getenv(
    "GITHUB_PAGES_URL",
    "https://turionx.github.io/Pulito/Backend/output"
)

# Versioning
VERSION = os.getenv("PULITO_VERSION", "1.0.0")

# Local input lists (relative to LISTS_DIR) 
INPUT_LIST_FILES = [
    "custom_block.txt",
    "custom_allow.txt",
]

# Remote public lists (EasyList, ecc.)
REMOTE_LIST_SOURCES = {
    # EasyList family
    "easylist": "https://easylist.to/easylist/easylist.txt",
    "easyprivacy": "https://easylist.to/easylist/easyprivacy.txt",
    "easylist_italy": "https://easylist-downloads.adblockplus.org/easylistitaly.txt",

    # uBlock Origin lists (selezionate, non troppo aggressive)
    "ublock_badware": "https://raw.githubusercontent.com/uBlockOrigin/uAssets/master/filters/badware.txt",
    "ublock_privacy": "https://raw.githubusercontent.com/uBlockOrigin/uAssets/master/filters/privacy.txt",

    # Peter Lowe – host list (molto usata, abbastanza conservativa)
    "peterlowe": "https://pgl.yoyo.org/adservers/serverlist.php?hostformat=hosts&showintro=0&mimetype=plaintext",
}